#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
import subprocess
import socket
import psutil
import time
import datetime
import logging
import json
import re
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import pandas as pd
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('inspection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SystemInspector:
    """系统信息检查"""

    @staticmethod
    def get_system_info():
        """获取系统基本信息"""
        info = {
            'system': platform.system(),
            'node': platform.node(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'cpu_count': os.cpu_count(),
            'boot_time': datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        }
        return info

    @staticmethod
    def get_cpu_info():
        """获取CPU信息"""
        cpu_info = {
            'physical_cores': psutil.cpu_count(logical=False),
            'total_cores': psutil.cpu_count(logical=True),
            'cpu_usage': psutil.cpu_percent(interval=1, percpu=True),
            'cpu_freq': psutil.cpu_freq().current if hasattr(psutil, 'cpu_freq') else 'N/A'
        }
        return cpu_info

    @staticmethod
    def get_memory_info():
        """获取内存信息"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        mem_info = {
            'total_memory': f"{mem.total / (1024 ** 3):.2f} GB",
            'available_memory': f"{mem.available / (1024 ** 3):.2f} GB",
            'used_memory': f"{mem.used / (1024 ** 3):.2f} GB",
            'memory_percent': mem.percent,
            'total_swap': f"{swap.total / (1024 ** 3):.2f} GB",
            'used_swap': f"{swap.used / (1024 ** 3):.2f} GB",
            'swap_percent': swap.percent
        }
        return mem_info

    @staticmethod
    def get_disk_info():
        """获取磁盘信息"""
        disks = []
        for part in psutil.disk_partitions(all=False):
            usage = psutil.disk_usage(part.mountpoint)
            disk_info = {
                'device': part.device,
                'mountpoint': part.mountpoint,
                'fstype': part.fstype,
                'total': f"{usage.total / (1024 ** 3):.2f} GB",
                'used': f"{usage.used / (1024 ** 3):.2f} GB",
                'free': f"{usage.free / (1024 ** 3):.2f} GB",
                'percent': usage.percent
            }
            disks.append(disk_info)

        io_counters = psutil.disk_io_counters()
        disk_io = {
            'read_count': io_counters.read_count,
            'write_count': io_counters.write_count,
            'read_bytes': f"{io_counters.read_bytes / (1024 ** 2):.2f} MB",
            'write_bytes': f"{io_counters.write_bytes / (1024 ** 2):.2f} MB"
        }

        return {'partitions': disks, 'io_counters': disk_io}


class NetworkInspector:
    """网络状态检查"""

    @staticmethod
    def get_network_info():
        """获取网络接口信息"""
        net_info = []
        for name, stats in psutil.net_io_counters(pernic=True).items():
            interface = {
                'interface': name,
                'bytes_sent': f"{stats.bytes_sent / (1024 ** 2):.2f} MB",
                'bytes_recv': f"{stats.bytes_recv / (1024 ** 2):.2f} MB",
                'packets_sent': stats.packets_sent,
                'packets_recv': stats.packets_recv,
                'errin': stats.errin,
                'errout': stats.errout,
                'dropin': stats.dropin,
                'dropout': stats.dropout
            }
            net_info.append(interface)
        return net_info

    @staticmethod
    def check_connectivity(host='8.8.8.8', port=53, timeout=3):
        """检查网络连通性"""
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except Exception:
            return False

    @staticmethod
    def check_ports(host='localhost', ports=[22, 80, 443]):
        """检查端口是否开放"""
        results = {}
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            results[port] = 'open' if result == 0 else 'closed'
            sock.close()
        return results

    @staticmethod
    def get_connections():
        """获取网络连接信息"""
        connections = []
        for conn in psutil.net_connections(kind='inet'):
            conn_info = {
                'fd': conn.fd,
                'family': conn.family,
                'type': conn.type,
                'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                'status': conn.status,
                'pid': conn.pid
            }
            connections.append(conn_info)
        return connections


class ServiceInspector:
    """服务检查"""

    @staticmethod
    def check_service(service_name):
        """检查服务状态"""
        try:
            if platform.system() == 'Linux':
                output = subprocess.check_output(['systemctl', 'status', service_name], stderr=subprocess.STDOUT)
                output = output.decode('utf-8')
                if 'active (running)' in output:
                    return 'running'
                elif 'inactive (dead)' in output:
                    return 'stopped'
                else:
                    return 'unknown'
            elif platform.system() == 'Windows':
                output = subprocess.check_output(['sc', 'query', service_name], stderr=subprocess.STDOUT)
                output = output.decode('utf-8')
                if 'RUNNING' in output:
                    return 'running'
                elif 'STOPPED' in output:
                    return 'stopped'
                else:
                    return 'unknown'
            else:
                return 'unsupported'
        except subprocess.CalledProcessError:
            return 'not_found'

    @staticmethod
    def check_process(process_name):
        """检查进程是否存在"""
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == process_name:
                return True
        return False

    @staticmethod
    def check_cron_jobs():
        """检查计划任务"""
        jobs = []
        try:
            if platform.system() == 'Linux':
                with open('/etc/crontab', 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if not line.startswith('#') and line.strip():
                            jobs.append(line.strip())
            elif platform.system() == 'Windows':
                output = subprocess.check_output(['schtasks', '/query', '/fo', 'LIST'], stderr=subprocess.STDOUT)
                # 尝试使用gbk编码解码，如果失败再使用utf-8
                try:
                    output = output.decode('gbk')
                except UnicodeDecodeError:
                    output = output.decode('utf-8', errors='ignore')
                jobs = output.split('\n')
        except Exception as e:
            logger.warning(f"Failed to check cron jobs: {str(e)}")
        return jobs


class LogInspector:
    """日志检查"""

    @staticmethod
    def analyze_log_file(log_file, pattern=None, last_n_lines=100):
        """分析日志文件"""
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()[-last_n_lines:]

            if pattern:
                matches = [line for line in lines if re.search(pattern, line)]
                return matches
            return lines
        except Exception as e:
            logger.error(f"Error analyzing log file {log_file}: {str(e)}")
            return []

    @staticmethod
    def check_error_logs(log_file, error_keywords=['error', 'fail', 'exception', 'critical'], last_n_lines=500):
        """检查错误日志"""
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()[-last_n_lines:]

            errors = []
            for line in lines:
                for keyword in error_keywords:
                    if keyword.lower() in line.lower():
                        errors.append(line.strip())
                        break
            return errors
        except Exception as e:
            logger.error(f"Error checking error logs in {log_file}: {str(e)}")
            return []

    @staticmethod
    def count_log_entries(log_file, pattern, time_range='1d'):
        """统计日志条目"""
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()

            count = 0
            for line in lines:
                if re.search(pattern, line):
                    # 这里可以添加时间范围过滤逻辑
                    count += 1
            return count
        except Exception as e:
            logger.error(f"Error counting log entries in {log_file}: {str(e)}")
            return 0


class PerformanceMonitor:
    """性能监控"""

    def __init__(self, duration=60, interval=5):
        self.duration = duration
        self.interval = interval
        self.data = {
            'timestamp': [],
            'cpu_usage': [],
            'memory_usage': [],
            'disk_io_read': [],
            'disk_io_write': []
        }

    def start_monitoring(self):
        """开始监控"""
        logger.info(
            f"Starting performance monitoring for {self.duration} seconds with {self.interval} second intervals")
        end_time = time.time() + self.duration

        while time.time() < end_time:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            disk_io = psutil.disk_io_counters()

            self.data['timestamp'].append(timestamp)
            self.data['cpu_usage'].append(cpu)
            self.data['memory_usage'].append(mem)
            self.data['disk_io_read'].append(disk_io.read_bytes / (1024 ** 2))
            self.data['disk_io_write'].append(disk_io.write_bytes / (1024 ** 2))

            time.sleep(self.interval)

        logger.info("Performance monitoring completed")

    def generate_report(self, output_file='performance_report.html'):
        """生成性能报告"""
        df = pd.DataFrame(self.data)

        # 创建图表
        plt.figure(figsize=(12, 8))

        # CPU使用率图表
        plt.subplot(2, 2, 1)
        plt.plot(df['timestamp'], df['cpu_usage'], 'r-')
        plt.title('CPU Usage (%)')
        plt.xticks(rotation=45)

        # 内存使用率图表
        plt.subplot(2, 2, 2)
        plt.plot(df['timestamp'], df['memory_usage'], 'b-')
        plt.title('Memory Usage (%)')
        plt.xticks(rotation=45)

        # 磁盘IO读取图表
        plt.subplot(2, 2, 3)
        plt.plot(df['timestamp'], df['disk_io_read'], 'g-')
        plt.title('Disk IO Read (MB)')
        plt.xticks(rotation=45)

        # 磁盘IO写入图表
        plt.subplot(2, 2, 4)
        plt.plot(df['timestamp'], df['disk_io_write'], 'y-')
        plt.title('Disk IO Write (MB)')
        plt.xticks(rotation=45)

        plt.tight_layout()

        # 保存图表
        plot_file = 'performance_plot.png'
        plt.savefig(plot_file)

        # 生成HTML报告
        html = f"""
        <html>
        <head>
            <title>Performance Monitoring Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                img {{ max-width: 100%; height: auto; }}
            </style>
        </head>
        <body>
            <h1>Performance Monitoring Report</h1>
            <p>Generated at: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

            <h2>Statistics</h2>
            {df.describe().to_html()}

            <h2>Charts</h2>
            <img src="{plot_file}" alt="Performance Charts">

            <h2>Raw Data</h2>
            {df.to_html(index=False)}
        </body>
        </html>
        """

        with open(output_file, 'w') as f:
            f.write(html)

        logger.info(f"Performance report generated: {output_file}")


class SecurityInspector:
    """安全检查"""

    @staticmethod
    def check_sudoers():
        """检查sudoers文件"""
        try:
            if platform.system() == 'Linux':
                with open('/etc/sudoers', 'r') as f:
                    content = f.read()
                return content
            return "Not a Linux system"
        except Exception as e:
            return f"Error reading sudoers file: {str(e)}"

    @staticmethod
    def check_ssh_config():
        """检查SSH配置"""
        try:
            if platform.system() == 'Linux':
                with open('/etc/ssh/sshd_config', 'r') as f:
                    content = f.read()
                return content
            return "Not a Linux system"
        except Exception as e:
            return f"Error reading SSH config: {str(e)}"

    @staticmethod
    def check_firewall():
        """检查防火墙状态"""
        try:
            if platform.system() == 'Linux':
                output = subprocess.check_output(['iptables', '-L'], stderr=subprocess.STDOUT)
                return output.decode('utf-8')
            elif platform.system() == 'Windows':
                output = subprocess.check_output(['netsh', 'advfirewall', 'show', 'allprofiles'],
                                                 stderr=subprocess.STDOUT)
                return output.decode('utf-8')
            else:
                return "Unsupported system"
        except Exception as e:
            return f"Error checking firewall: {str(e)}"


class ReportGenerator:
    """报告生成"""

    @staticmethod
    def generate_html_report(data, output_file='inspection_report.html'):
        """生成HTML报告"""
        html = f"""
        <html>
        <head>
            <title>System Inspection Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #444; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .warning {{ background-color: #fff3cd; }}
                .error {{ background-color: #f8d7da; }}
                .success {{ background-color: #d4edda; }}
            </style>
        </head>
        <body>
            <h1>System Inspection Report</h1>
            <p>Generated at: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

            <h2>System Information</h2>
            {ReportGenerator._dict_to_html(data.get('system_info', {}))}

            <h2>CPU Information</h2>
            {ReportGenerator._dict_to_html(data.get('cpu_info', {}))}

            <h2>Memory Information</h2>
            {ReportGenerator._dict_to_html(data.get('memory_info', {}))}

            <h2>Disk Information</h2>
            {ReportGenerator._list_of_dicts_to_html(data.get('disk_info', {}).get('partitions', []))}

            <h2>Network Information</h2>
            {ReportGenerator._list_of_dicts_to_html(data.get('network_info', []))}

            <h2>Port Status</h2>
            {ReportGenerator._dict_to_html(data.get('port_status', {}))}

            <h2>Service Status</h2>
            {ReportGenerator._dict_to_html(data.get('service_status', {}))}

            <h2>Error Logs</h2>
            {ReportGenerator._list_to_html(data.get('error_logs', []))}

            <h2>Security Checks</h2>
            <h3>Sudoers File</h3>
            <pre>{data.get('sudoers', '')}</pre>
            <h3>SSH Config</h3>
            <pre>{data.get('ssh_config', '')}</pre>
            <h3>Firewall Status</h3>
            <pre>{data.get('firewall_status', '')}</pre>
        </body>
        </html>
        """

        with open(output_file, 'w') as f:
            f.write(html)

        logger.info(f"HTML report generated: {output_file}")

    @staticmethod
    def _dict_to_html(data):
        """将字典转换为HTML表格"""
        if not data:
            return "<p>No data available</p>"

        html = "<table><tr><th>Key</th><th>Value</th></tr>"
        for key, value in data.items():
            html += f"<tr><td>{key}</td><td>{value}</td></tr>"
        html += "</table>"
        return html

    @staticmethod
    def _list_of_dicts_to_html(data):
        """将字典列表转换为HTML表格"""
        if not data:
            return "<p>No data available</p>"

        # 获取所有可能的键作为表头
        headers = set()
        for item in data:
            headers.update(item.keys())
        headers = sorted(headers)

        html = "<table><tr>"
        for header in headers:
            html += f"<th>{header}</th>"
        html += "</tr>"

        for item in data:
            html += "<tr>"
            for header in headers:
                value = item.get(header, '')
                # 根据值添加CSS类
                if isinstance(value, str) and ('error' in value.lower() or 'fail' in value.lower()):
                    html += f"<td class='error'>{value}</td>"
                elif isinstance(value, str) and ('warn' in value.lower()):
                    html += f"<td class='warning'>{value}</td>"
                elif isinstance(value, str) and ('ok' in value.lower() or 'success' in value.lower()):
                    html += f"<td class='success'>{value}</td>"
                else:
                    html += f"<td>{value}</td>"
            html += "</tr>"
        html += "</table>"
        return html

    @staticmethod
    def _list_to_html(data):
        """将列表转换为HTML"""
        if not data:
            return "<p>No data available</p>"

        html = "<ul>"
        for item in data:
            html += f"<li>{item}</li>"
        html += "</ul>"
        return html

    @staticmethod
    def generate_json_report(data, output_file='inspection_report.json'):
        """生成JSON报告"""
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info(f"JSON report generated: {output_file}")


class Notification:
    """通知功能"""

    @staticmethod
    def send_email(subject, body, to_addr, from_addr, smtp_server, smtp_port, smtp_user=None, smtp_pass=None):
        """发送电子邮件"""
        try:
            msg = MIMEMultipart()
            msg['From'] = from_addr
            msg['To'] = to_addr
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if smtp_user and smtp_pass:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)

            logger.info(f"Email sent to {to_addr}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    @staticmethod
    def send_slack_notification(webhook_url, message):
        """发送Slack通知"""
        try:
            payload = {'text': message}
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            logger.info("Slack notification sent")
            return True
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {str(e)}")
            return False


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='System Inspection Tool')
    parser.add_argument('--mode', choices=['full', 'quick', 'performance'], default='quick',
                        help='Inspection mode (full, quick, performance)')
    parser.add_argument('--output', default='report',
                        help='Output file prefix (without extension)')
    parser.add_argument('--email', help='Email address to send report to')
    parser.add_argument('--slack', help='Slack webhook URL for notifications')
    parser.add_argument('--duration', type=int, default=60,
                        help='Duration for performance monitoring (seconds)')
    parser.add_argument('--interval', type=int, default=5,
                        help='Interval for performance monitoring (seconds)')
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    logger.info("Starting system inspection")

    # 收集数据
    data = {}

    # 系统信息
    data['system_info'] = SystemInspector.get_system_info()
    data['cpu_info'] = SystemInspector.get_cpu_info()
    data['memory_info'] = SystemInspector.get_memory_info()
    data['disk_info'] = SystemInspector.get_disk_info()

    # 网络信息
    data['network_info'] = NetworkInspector.get_network_info()
    data['connectivity'] = NetworkInspector.check_connectivity()
    data['port_status'] = NetworkInspector.check_ports(ports=[22, 80, 443, 3306, 5432, 6379])
    data['connections'] = NetworkInspector.get_connections()

    # 服务检查
    services = ['sshd', 'nginx', 'mysql', 'postgresql', 'redis'] if platform.system() == 'Linux' else ['MySQL',
                                                                                                       'MSSQLSERVER']
    data['service_status'] = {service: ServiceInspector.check_service(service) for service in services}
    data['process_status'] = {
        'python': ServiceInspector.check_process('python'),
        'java': ServiceInspector.check_process('java')
    }
    data['cron_jobs'] = ServiceInspector.check_cron_jobs()

    # 日志检查
    if platform.system() == 'Linux':
        data['error_logs'] = LogInspector.check_error_logs('/var/log/syslog')
    elif platform.system() == 'Windows':
        log_path = 'C:\\Windows\\System32\\LogFiles\\AppEvent.evt'
        if os.path.exists(log_path):
            data['error_logs'] = LogInspector.check_error_logs(log_path)
        else:
            logger.warning(f"Log file not found: {log_path}")
            data['error_logs'] = []

    # 安全检查
    data['sudoers'] = SecurityInspector.check_sudoers()
    data['ssh_config'] = SecurityInspector.check_ssh_config()
    data['firewall_status'] = SecurityInspector.check_firewall()

    # 性能监控
    if args.mode == 'performance':
        monitor = PerformanceMonitor(duration=args.duration, interval=args.interval)
        monitor.start_monitoring()
        monitor.generate_report(f"{args.output}_performance.html")

    # 生成报告
    ReportGenerator.generate_html_report(data, f"{args.output}.html")
    ReportGenerator.generate_json_report(data, f"{args.output}.json")

    # 发送通知
    if args.email:
        with open(f"{args.output}.html", 'r') as f:
            report_html = f.read()
        Notification.send_email(
            subject="System Inspection Report",
            body=report_html,
            to_addr=args.email,
            from_addr="inspection@example.com",
            smtp_server="smtp.example.com",
            smtp_port=587,
            smtp_user="user@example.com",
            smtp_pass="password"
        )

    if args.slack:
        Notification.send_slack_notification(
            webhook_url=args.slack,
            message=f"System inspection completed. Report generated: {args.output}.html"
        )

    logger.info("System inspection completed")


if __name__ == "__main__":
    main()
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from config import TEMPLATE_DIR, REPORT_DIR, JINJA_FILTERS
import json
import pandas as pd
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    def __init__(self):
        # 初始化Jinja2环境
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # 注册自定义过滤器
        for name, filter_func in JINJA_FILTERS.items():
            self.env.filters[name] = filter_func

    def render_template(self, template_name, context, output_path=None):
        """渲染模板"""
        try:
            template = self.env.get_template(template_name)
            rendered = template.render(**context)

            if output_path:
                with open(output_path, 'w') as f:
                    f.write(rendered)
                logger.info(f"Report generated: {output_path}")

            return rendered
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            raise

    def generate_html_report(self, inspection_data, output_file='report.html'):
        """生成主HTML报告"""
        output_path = REPORT_DIR / output_file
        context = {
            'title': 'System Inspection Report',
            'generated_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': inspection_data
        }
        return self.render_template('report.html', context, output_path)

    def generate_performance_report(self, performance_data, output_file='performance.html'):
        """生成性能报告"""
        # 生成图表
        plot_file = REPORT_DIR / 'performance_plot.png'
        self._generate_performance_plots(performance_data, plot_file)

        # 准备上下文
        context = {
            'title': 'Performance Monitoring Report',
            'generated_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': performance_data,
            'plot_file': plot_file.name
        }

        # 渲染模板
        output_path = REPORT_DIR / output_file
        return self.render_template('performance.html', context, output_path)

    def _generate_performance_plots(self, data, output_file):
        """生成性能图表"""
        df = pd.DataFrame(data)

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
        plt.savefig(output_file)
        plt.close()

    def generate_json_report(self, data, output_file='report.json'):
        """生成JSON报告"""
        output_path = REPORT_DIR / output_file
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info(f"JSON report generated: {output_path}")
        return output_path

    def generate_email_content(self, report_data, report_url=None):
        """生成邮件内容"""
        context = {
            'title': 'System Inspection Report Summary',
            'generated_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': self._create_summary(report_data),
            'report_url': report_url
        }
        return self.render_template('email.html', context)

    def _create_summary(self, data):
        """创建报告摘要"""
        summary = {
            'system': f"{data['system_info']['system']} {data['system_info']['release']}",
            'cpu': f"{data['cpu_info']['total_cores']} cores, {data['cpu_info']['cpu_usage'][0]}% usage",
            'memory': f"{data['memory_info']['memory_percent']}% used",
            'disk': f"{data['disk_info']['partitions'][0]['percent']}% used on {data['disk_info']['partitions'][0]['mountpoint']}",
            'services': {
                            service: status for service, status in data['service_status'].items()
                            if status != 'running'
                        } or 'All services running normally',
            'errors': len(data.get('error_logs', []))
        }
        return summary
import psutil
import smtplib
from email.mime.text import MIMEText
import time
import configparser
import sys
from encrypt_decrypt import decrypt_password
import os

# 密钥和初始化向量
key = b'ThisIsASecretKey12345'
iv = b'ThisIsAnIV123456'

def send_email(subject, message, config):
    sender = config['EMAIL']['sender']
    receivers = config['EMAIL']['receivers'].split(',')
    encrypted_password = config['EMAIL']['encrypted_password']
    password = decrypt_password(encrypted_password)
    smtp_server = config['EMAIL']['smtp_server']
    smtp_port = int(config['EMAIL']['smtp_port'])

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ','.join(receivers)

    try:
        smtpObj = smtplib.SMTP(smtp_server, smtp_port)
        smtpObj.starttls()
        smtpObj.login(sender, password)
        smtpObj.sendmail(sender, receivers, msg.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print("邮件发送失败", e)

def check_system_status(config):
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')
    network_usage = psutil.net_io_counters()
    threshold_cpu = int(config['MONITOR']['threshold_cpu'])
    threshold_memory = int(config['MONITOR']['threshold_memory'])
    threshold_disk = int(config['MONITOR']['threshold_disk'])
    threshold_network = int(config['MONITOR']['threshold_network'])
    log_directory = config['MONITOR']['log_directory']
    process_name = config['MONITOR']['process_name']

    message = f"""
    系统状态报告:
    - CPU 使用率: {cpu_usage}%
    - 内存使用情况: {memory.percent}%, 已使用 {memory.used / (1024 ** 3):.2f} GB, 总共 {memory.total / (1024 ** 3):.2f} GB
    - 磁盘使用情况: {disk_usage.percent}%, 已使用 {disk_usage.used / (1024 ** 3):.2f} GB, 总共 {disk_usage.total / (1024 ** 3):.2f} GB
    - 网络流量: 发送 {network_usage.bytes_sent / 1024:.2f} KB, 接收 {network_usage.bytes_recv / 1024:.2f} KB
    - 进程 {process_name} 状态: {'正在运行' if is_process_running(process_name) else '未运行'}
    """

    if cpu_usage > threshold_cpu:
        message += f"\n警告: CPU 使用率超过阈值 {threshold_cpu}%"
    if memory.percent > threshold_memory:
        message += f"\n警告: 内存使用率超过阈值 {threshold_memory}%"
    if disk_usage.percent > threshold_disk:
        message += f"\n警告: 磁盘使用率超过阈值 {threshold_disk}%"
    if network_usage.bytes_sent > threshold_network or network_usage.bytes_recv > threshold_network:
        message += f"\n警告: 网络流量超过阈值 {threshold_network / 1024:.2f} KB"

    # 检查日志文件中的错误信息
    log_files = [os.path.join(log_directory, file) for file in os.listdir(log_directory) if file.endswith('.log')]
    for log_file in log_files:
        with open(log_file, 'r') as file:
            log_content = file.read()
            if "ERROR" in log_content:
                message += f"\n警告: 日志文件 {log_file} 中包含错误信息"

    return message

def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return True
    return False

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    interval = int(config['MONITOR']['interval'])
    while True:
        system_status = check_system_status(config)
        print(system_status)

        # 发送邮件
        send_email("系统状态报告", system_status, config)

        # 写入日志文件
        with open("system_status.log", "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {system_status}\n")

        time.sleep(interval)

if __name__ == "__main__":
    main()

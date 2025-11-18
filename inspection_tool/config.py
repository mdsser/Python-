import os
from pathlib import Path
from datetime import datetime

# 基础配置
BASE_DIR = Path(__file__).parent.absolute()
TEMPLATE_DIR = BASE_DIR / 'templates'
REPORT_DIR = BASE_DIR / 'reports'

# 确保报告目录存在
REPORT_DIR.mkdir(exist_ok=True)

# 邮件配置
EMAIL_CONFIG = {
    'smtp_server': 'smtp.example.com',
    'smtp_port': 587,
    'smtp_user': 'user@example.com',
    'smtp_pass': 'password',
    'from_addr': 'inspection@example.com',
    'admin_email': 'admin@example.com'
}

# 检查项配置
INSPECTION_CONFIG = {
    'services_to_check': ['sshd', 'nginx', 'mysql', 'postgresql', 'redis'],
    'ports_to_check': [22, 80, 443, 3306, 5432, 6379],
    'processes_to_check': ['python', 'java'],
    'log_files': {
        'linux': '/var/log/syslog',
        'windows': 'C:\\Windows\\System32\\LogFiles\\AppEvent.evt'
    },
    'performance': {
        'default_duration': 60,
        'default_interval': 5
    }
}

# Jinja2 过滤器
def format_bytes(size):
    """格式化字节大小为人类可读格式"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

JINJA_FILTERS = {
    'format_bytes': format_bytes,
    'format_timestamp': lambda ts: datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') if ts else 'N/A'
}
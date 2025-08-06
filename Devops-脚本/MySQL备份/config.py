# config.py
MYSQL_CONFIG = {
    'host': '192.168.1.10',
    'database': 'test',
    'user': 'root',
    'password': '123456'
}

# 定义备份文件的保留天数
FULL_BACKUP_DAYS_TO_KEEP = 7
INCREMENTAL_BACKUP_DAYS_TO_KEEP = 15

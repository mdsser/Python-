# 每天凌晨3点自动备份指定目录到 /backup
#
# 备份文件按日期命名（如 backup_20230715.tar.gz）
#
# 记录备份日志到 /var/log/backup.log
import os
import schedule
import time
import shutil
from datetime import datetime

def backup_directory(source_dir, backup_dir = "/backup"):
    "执行目录备份"
    if not os.path.exists(source_dir):
        log_message(f"错误: 源目录不存在 {source_dir}")
        return

    os.makedir(backup_dir,exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H")
    backup_name = f"backup_{timestamp}.tar.gz"
    backup_path = os.path.join(source_dir, backup_name)


    try:
        shutil.make_archive(
            backup_path.replace('.tar.gz', ''),
            'gztar',
            source_dir
        )
    except Exception as e:
        log_message(f"备份失败: {str(e)}")

def log_message(message):
    timestamp = datetime.now().strftime("%Y%m%d-%H")
    log_entry = f"[{timestamp} {message}\n]"
    with open("/var/log/backup.log","a") as f:
        f.write(log_entry)
    print(log_entry.strip())

schedule.every().day.at("03:00").do(
    backup_directory,
    source_dir="/var/www/html"
)

if __name__ == "__main__":
    print("备份服务启动，等待执行")
    while True:
        schedule.run_pending()
        time.sleep(60)
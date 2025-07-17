import time
import logging
import schedule
import shutil
from datetime import datetime
import os

logging.basicConfig(
    filename = '/var/log/backup_system.log',
    level = logging.INFO,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def backup_directory(source, dest):
    # 创建带有时间戳的备份目录

    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{os.path.basename(source)}_{timestamp}"
        dest_path = os.path.join(dest,backup_name)

        # 执行备份
        shutil.copytree(source, dest_path)
        logging.info(f"备份成功: {source} => {dest_path}")
        return True
    except Exception as e:
        logging.error(f"备份失败：{str(e)}")
        return False


def daily_backup_job():
    # 每日备份任务
    print(f"{time.ctime()} - 开始每日备份...")
    backup_directory("/var/www/html", "/backups/web")
    backup_directory("/etc/nginx", "/backups/config")

if __name__ == '__main__':
    # 每日凌晨2点
    schedule.every().day.at("02.00").do(daily_backup_job)

    print("备份服务已启动, 等待执行定时任务...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("服务已停止")

import os
import shutil
from datetime import datetime

def backup_txt_file(source_dir):
    # 创建备份目录
    backup_dir = os.path.join(source_dir, 'backup')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    today = datetime.now().strftime('%Y%m')


if __name__ == 'main':
    backup_txt_file('/path/to/your/backup.txt')

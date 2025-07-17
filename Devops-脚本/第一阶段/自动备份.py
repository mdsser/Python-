import os
import shutil
import datetime

def create_backup(source_dir, dest_dir):
    if not os.path.exists(source_dir):
        print(f"错误: 源目录不存在 {source_dir}")
        return False

    # 生成备份文件名
    os.makedirs(dest_dir, exist_ok=True)

    # 生成带时间戳的备份文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H")
    backup_name = f"backup_{os.path.basename(source_dir)}_{timestamp}.tar.gz"
    backup_path = os.path.join(dest_dir,backup_name)

    # 创建压缩包
    shutil.make_archive(backup_path.replace('.tar.gz', ''), 'gztar', source_dir)
    print(f"备份创建成功: {backup_path}")
    return backup_path

if __name__ == '__main__':
    # 备份目录
    create_backup("/var/www/html","/backups/web")
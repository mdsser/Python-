import subprocess
import datetime
import os

def mysql_backup(backup_dirs = "/backups/mysql"):
    # 执行MySQL备份策略
    today = datetime.date.today()

    # 每周六执行全量备份
    if today.weekday() == 5: # 星期六
        backup_type = "full"
        backup_file = f"{backup_dirs}/full_{today.strftime('%Y%m%d')}.sql"
        cmd = f"mysqldump -uroot -p123456 --all-databases --single-transaction > {backup_dirs}"
    else:
        # 增量备份(基于binlog)
        backup_type = "incremental"
        last_backup = max([f for f in os.listdir(backup_dirs) if f.startswith("full")], default=None)

        if not last_backup:
            return mysql_backup()

        last_backup_date = datetime.datetime.strptime(last_backup[5:13], "%Y%m%d")
        backup_file = f"{backup_dirs}/inc_{today.strftime('%Y%m%d')}.sql"
        cmd = f"mysqlbinlog --start-datetime='{last_backup_date} --stop-datetime='{today}' > {backup_file}"

    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"备份成功: {backup_type} -> {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"备份失败: {str(e)}")

    for file in os.listdir(backup_dirs):
        file_path = os.path.join(backup_dirs, file)
        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        if (today - file_time).days > 30:
            os.remove(file_path)
            print(f"清理旧备份: {file}")


if __name__ == '__main__':
    directory = os.makedirs("/backups/mysql",exist_ok = True)
    mysql_backup(directory)
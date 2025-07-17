import subprocess
from datetime import datetime

def mysql_backup():
    today = datetime.now().strftime('%Y%m%d')
    backup_type = 'full' if datetime.now().weekday() == 5 else 'incr'
    backup_file = f"/backups/mysql_{today}_{backup_type}.sql"

    if backup_type == 'full':
        cmd = f"mysqldump -uroot -p123456 --all-databases > {backup_file}"
    else:
        cmd = f"mysqldump -uroot -p123456 --no-create-info --insert-ignore mydb > {backup_file}"

    subprocess.run(cmd, shell=True, check=True)
    print(f"备份完成: {backup_file}")


if __name__ == '__main__':
    mysql_backup()
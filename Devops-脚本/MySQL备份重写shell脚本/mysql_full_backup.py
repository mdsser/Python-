import sys
import configparser
import subprocess
from datetime import datetime
from pathlib import Path


def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


def setup_directories(config):
    try:
        Path(config['backup']['full_backup_dir']).mkdir(parents=True, exist_ok=True)
        Path(config['backup']['log_dir']).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error creating directories: {e}")
        sys.exit(1)


def log_message(message, log_file):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    with open(log_file, 'a') as f:
        f.write(log_entry)
    print(log_entry.strip())


def perform_full_backup(config, log_file):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    backup_file = f"{config['backup']['full_backup_dir']}/full_backup_{timestamp}.sql"

    cmd = [
        'mysqldump',
        f"--user={config['mysql']['user']}",
        f"--password={config['mysql']['password']}",
        f"--host={config['mysql']['host']}",
        f"--port={config['mysql']['port']}",
        "--all-databases",
        "--single-transaction",
        "--flush-logs",
        "--master-data=2"
    ]

    try:
        with open(backup_file, 'w') as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, check=True)

        # Compress the backup file
        subprocess.run(['gzip', backup_file], check=True)
        log_message(f"备份完成: {backup_file}.gz", log_file)
        return True
    except subprocess.CalledProcessError as e:
        log_message(f"错误：备份失败 - {e.stderr.decode().strip()}", log_file)
        return False


def cleanup_old_backups(config, log_file):
    backup_dir = config['backup']['full_backup_dir']
    retention_days = config['backup']['full_backup_retention_days']

    find_cmd = [
        'find',
        backup_dir,
        '-name',
        'full_backup_*.sql.gz',
        '-mtime',
        f"+{retention_days}",
        '-exec',
        'rm',
        '{}',
        ';'
    ]

    try:
        subprocess.run(find_cmd, stderr=subprocess.PIPE, check=True)
        log_message(f"已清理超过{retention_days}天的旧完全备份", log_file)
    except subprocess.CalledProcessError as e:
        log_message(f"清理旧备份时出错: {e.stderr.decode().strip()}", log_file)


def main():
    config = load_config()
    log_file = f"{config['backup']['log_dir']}/mysql_fullbackup.log"

    setup_directories(config)
    log_message("开始完全备份", log_file)

    if perform_full_backup(config, log_file):
        cleanup_old_backups(config, log_file)

    log_message("完全备份脚本执行完毕", log_file)


if __name__ == "__main__":
    main()
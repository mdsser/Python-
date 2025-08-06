#!/usr/bin/env python3
import os
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
        Path(config['backup']['incremental_backup_dir']).mkdir(parents=True, exist_ok=True)
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


def execute_mysql_command(config, query, log_file):
    cmd = [
        'mysql',
        f"--user={config['mysql']['user']}",
        f"--password={config['mysql']['password']}",
        f"--host={config['mysql']['host']}",
        f"--port={config['mysql']['port']}",
        '-e',
        query
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        log_message(f"MySQL命令执行失败: {e.stderr.strip()}", log_file)
        return None


def get_binary_logs(config, log_file):
    # Flush logs first
    if not execute_mysql_command(config, "FLUSH LOGS;", log_file):
        return None

    # Get binary logs list
    output = execute_mysql_command(config, "SHOW BINARY LOGS;", log_file)
    if not output:
        return None

    # Skip header line and extract log names
    return [line.split('\t')[0] for line in output[1:]]


def get_current_log(config, log_file):
    output = execute_mysql_command(config, "SHOW MASTER STATUS;", log_file)
    if not output or len(output) < 2:
        return None
    return output[1].split('\t')[0]


def backup_binary_logs(config, log_file):
    binary_logs = get_binary_logs(config, log_file)
    if not binary_logs:
        log_message("错误：无法获取二进制日志列表", log_file)
        return 0

    current_log = get_current_log(config, log_file)
    if not current_log:
        log_message("错误：无法获取当前日志文件", log_file)
        return 0

    backup_count = 0
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    for binlog in binary_logs:
        if binlog != current_log:
            backup_file = f"{config['backup']['incremental_backup_dir']}/incremental_{timestamp}_{binlog}"

            # Backup binary log
            try:
                with open(backup_file, 'w') as f:
                    subprocess.run(
                        ['mysqlbinlog', f"{config['backup']['binlog_dir']}/{binlog}"],
                        stdout=f,
                        stderr=subprocess.PIPE,
                        check=True
                    )

                # Compress the backup
                subprocess.run(['gzip', backup_file], check=True)
                backup_count += 1
                log_message(f"已备份: {binlog}", log_file)
            except subprocess.CalledProcessError as e:
                log_message(f"警告：备份 {binlog} 失败 - {e.stderr.decode().strip()}", log_file)

    return backup_count


def cleanup_old_incremental_backups(config, log_file):
    backup_dir = config['backup']['incremental_backup_dir']
    retention_days = config['backup']['incremental_backup_retention_days']

    find_cmd = [
        'find',
        backup_dir,
        '-name',
        'incremental_*.gz',
        '-mtime',
        f"+{retention_days}",
        '-exec',
        'rm',
        '{}',
        ';'
    ]

    try:
        result = subprocess.run(find_cmd, capture_output=True, text=True)
        deleted_count = len(result.stdout.splitlines())
        log_message(f"已清理 {deleted_count} 个过期增量备份", log_file)
    except subprocess.CalledProcessError as e:
        log_message(f"清理旧增量备份时出错: {e.stderr.strip()}", log_file)


def main():
    config = load_config()
    log_file = f"{config['backup']['log_dir']}/mysql_incrbackup.log"

    setup_directories(config)
    log_message("开始增量备份", log_file)

    backup_count = backup_binary_logs(config, log_file)
    log_message(f"增量备份完成，共备份 {backup_count} 个日志文件", log_file)

    cleanup_old_incremental_backups(config, log_file)
    log_message("增量备份脚本执行完毕", log_file)


if __name__ == "__main__":
    main()
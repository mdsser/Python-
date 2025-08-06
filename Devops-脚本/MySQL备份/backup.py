import os
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import config  # 导入配置文件


def full_backup():
    # 获取当前时间，用于备份文件命名
    date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = f"full_backup_{date}.sql"

    # 使用mysqldump命令进行完全备份
    command = f"mysqldump -h {config.MYSQL_CONFIG['host']} -u {config.MYSQL_CONFIG['user']} -p'{config.MYSQL_CONFIG['password']}' {config.MYSQL_CONFIG['database']} > {backup_file}"
    os.system(command)

    print(f"完全备份完成，备份文件为: {backup_file}")
    return backup_file


def incremental_backup(last_position):
    # 获取当前时间，用于备份文件命名
    date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = f"incremental_backup_{date}.sql"

    # 使用mysqldump命令进行增量备份
    command = f"mysqldump -h {config.MYSQL_CONFIG['host']} -u {config.MYSQL_CONFIG['user']} -p'{config.MYSQL_CONFIG['password']}' --single-transaction --master-data=2 --flush-logs {config.MYSQL_CONFIG['database']} > {backup_file}"
    if last_position is not None:
        command += f" --log-pos={last_position}"
    os.system(command)

    # 获取新的二进制日志位置
    new_position = get_current_binlog_position()

    print(f"增量备份完成，备份文件为: {backup_file}")
    print(f"新的二进制日志位置为: {new_position}")
    return backup_file, new_position


def get_current_binlog_position():
    try:
        connection = mysql.connector.connect(**config.MYSQL_CONFIG)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SHOW MASTER STATUS")
            result = cursor.fetchone()
            if result:
                return result[1]
            else:
                return None
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return None


def cleanup_backups():
    # 定义备份文件存储路径，这里假设与脚本在同一目录下
    backup_dir = os.getcwd()
    # 计算完全备份和增量备份的时间界限
    full_cutoff_time = datetime.now() - timedelta(days=config.FULL_BACKUP_DAYS_TO_KEEP)
    incremental_cutoff_time = datetime.now() - timedelta(days=config.INCREMENTAL_BACKUP_DAYS_TO_KEEP)

    for filename in os.listdir(backup_dir):
        file_path = os.path.join(backup_dir, filename)
        try:
            file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
        except OSError as e:
            print(f"无法获取文件 {filename} 的创建时间: {e}")
            continue

        # 检查是否为完全备份文件并清理
        if filename.startswith("full_backup_"):
            if file_creation_time < full_cutoff_time:
                os.remove(file_path)
                print(f"已删除过期完全备份文件: {filename}")

        # 检查是否为增量备份文件并清理
        elif filename.startswith("incremental_backup_"):
            if file_creation_time < incremental_cutoff_time:
                os.remove(file_path)
                print(f"已删除过期增量备份文件: {filename}")


def main():
    # 执行完全备份
    full_backup_file = full_backup()

    # 假设这是上次增量备份的位置
    last_position = get_current_binlog_position()

    # 执行增量备份
    incremental_backup_file, last_position = incremental_backup(last_position)

    # 清理过期备份文件
    cleanup_backups()

    # 你可以在这里添加更多的逻辑，比如定期备份、发送备份文件到远程存储等


if __name__ == "__main__":
    main()

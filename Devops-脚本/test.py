import os
import subprocess
import logging
from datetime import datetime, timedelta
import configparser
import argparse
import gzip
import shutil
import pymysql


# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mysql_backup.log'),
        logging.StreamHandler()
    ]
)
# 记录来自该模板的记录
logger = logging.getLogger(__name__)


class MySQLNativeBackup:
    def __init__(self, config_file='mysql_backup.ini'):
        # 读取配置文件
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        # MySQL连接信息
        self.mysql_host = self.config.get('mysql', 'host', fallback='localhost')
        self.mysql_port = self.config.get('mysql', 'port', fallback='3306')
        self.mysql_user = self.config.get('mysql', 'user', fallback='root')
        self.mysql_password = self.config.get('mysql', 'password', fallback='123456')
        self.database = self.config.get('mysql', 'database', fallback='')

        # 备份配置
        self.backup_dir = self.config.get('backup', 'backup_dir', fallback='./backups')
        self.full_backup_retention = self.config.getint('backup', 'full_backup_retention', fallback=7)
        self.inc_backup_retention = self.config.getint('backup', 'inc_backup_retention', fallback=15)
        self.compress_backup = self.config.getboolean('backup', 'compress_backup', fallback=True)

        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(os.path.join(self.backup_dir, 'full'), exist_ok=True)
        os.makedirs(os.path.join(self.backup_dir, 'inc'), exist_ok=True)

        # 检查数据库是否存在
        if not self.database:
            raise ValueError("Database name must be specified in config file")

    def _execute_command(self, command):
        """执行命令并记录日志"""
        logger.info(f"Executing command: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            logger.debug(f"Command output: {result.stdout.decode('utf-8')}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.stderr.decode('utf-8')}")
            return False

    def _get_backup_filename(self, backup_type):
        """生成备份文件名"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if backup_type == 'full':
            base_name = f"{self.database}_full_{timestamp}.sql"
        elif backup_type == 'inc':
            base_name = f"{self.database}_inc_{timestamp}.sql"
        else:
            raise ValueError("Invalid backup type")

        if self.compress_backup:
            return base_name + '.gz'
        return base_name

    def _compress_file(self, filepath):
        """压缩文件"""
        if not self.compress_backup:
            return filepath

        compressed_path = filepath + '.gz'
        try:
            with open(filepath, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(filepath)
            logger.info(f"Compressed backup file: {compressed_path}")
            return compressed_path
        except Exception as e:
            logger.error(f"Failed to compress file {filepath}: {str(e)}")
            return filepath

    def full_backup(self):
        """执行完全备份"""
        logger.info(f"Starting full backup for database: {self.database}")

        filename = self._get_backup_filename('full')
        backup_path = os.path.join(self.backup_dir, 'full', filename)

        # 如果是压缩备份，先备份到临时文件再压缩
        if self.compress_backup:
            temp_path = backup_path.replace('.gz', '')
        else:
            temp_path = backup_path

        command = [
            'mysqldump',
            f'--host={self.mysql_host}',
            f'--port={self.mysql_port}',
            f'--user={self.mysql_user}',
            f'--password={self.mysql_password}',
            '--single-transaction',
            '--master-data=2',
            '--flush-logs',
            '--routines',
            '--triggers',
            '--events',
            self.database
        ]

        # 重定向输出到文件
        with open(temp_path, 'w') as f:
            process = subprocess.Popen(
                command,
                stdout=f,
                stderr=subprocess.PIPE
            )
            _, stderr = process.communicate()

            if process.returncode != 0:
                logger.error(f"Full backup failed: {stderr.decode('utf-8')}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return False

        # 如果需要压缩
        if self.compress_backup:
            self._compress_file(temp_path)

        logger.info(f"Full backup completed successfully: {backup_path}")
        return True

    def incremental_backup(self):
        """执行增量备份"""
        logger.info(f"Starting incremental backup for database: {self.database}")

        # 获取当前二进制日志位置
        try:
            connection = pymysql.connect(
                host=self.mysql_host,
                port=int(self.mysql_port),
                user=self.mysql_user,
                password=self.mysql_password,
                database=self.database
            )
            with connection.cursor() as cursor:
                cursor.execute("SHOW MASTER STATUS")
                result = cursor.fetchone()
                if not result:
                    logger.error("Cannot get binary log position - maybe binary logging is not enabled")
                    return False

                log_file, log_pos = result[0], result[1]
                logger.info(f"Current binary log position: {log_file} {log_pos}")

                # 刷新日志以创建新的二进制日志文件
                cursor.execute("FLUSH BINARY LOGS")

                # 获取之前的日志文件列表
                cursor.execute("SHOW BINARY LOGS")
                log_files = [row[0] for row in cursor.fetchall()]

                # 找到上一个日志文件（当前是新的，我们需要备份之前的）
                if len(log_files) < 2:
                    logger.error("Not enough binary logs for incremental backup")
                    return False

                prev_log_file = log_files[-2]

        except Exception as e:
            logger.error(f"Failed to get binary log position: {str(e)}")
            return False
        finally:
            if 'connection' in locals():
                connection.close()

        # 执行增量备份
        filename = self._get_backup_filename('inc')
        backup_path = os.path.join(self.backup_dir, 'inc', filename)

        # 如果是压缩备份，先备份到临时文件再压缩
        if self.compress_backup:
            temp_path = backup_path.replace('.gz', '')
        else:
            temp_path = backup_path

        command = [
            'mysqlbinlog',
            f'--host={self.mysql_host}',
            f'--port={self.mysql_port}',
            f'--user={self.mysql_user}',
            f'--password={self.mysql_password}',
            '--read-from-remote-server',
            '--result-file=' + temp_path,
            prev_log_file
        ]

        if not self._execute_command(command):
            return False

        # 如果需要压缩
        if self.compress_backup:
            self._compress_file(temp_path)

        logger.info(f"Incremental backup completed successfully: {backup_path}")
        return True

    def cleanup_old_backups(self):
        """清理旧的备份文件"""
        logger.info("Starting cleanup of old backups")

        # 清理完全备份
        full_backup_dir = os.path.join(self.backup_dir, 'full')
        cutoff_date = datetime.now() - timedelta(days=self.full_backup_retention)
        self._delete_old_files(full_backup_dir, cutoff_date)

        # 清理增量备份
        inc_backup_dir = os.path.join(self.backup_dir, 'inc')
        cutoff_date = datetime.now() - timedelta(days=self.inc_backup_retention)
        self._delete_old_files(inc_backup_dir, cutoff_date)

        logger.info("Cleanup completed")

    def _delete_old_files(self, directory, cutoff_date):
        """删除指定目录中早于cutoff_date的文件"""
        if not os.path.exists(directory):
            return

        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_time < cutoff_date:
                    try:
                        os.remove(filepath)
                        logger.info(f"Deleted old backup: {filepath}")
                    except Exception as e:
                        logger.error(f"Failed to delete {filepath}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='MySQL Database Backup Tool')
    parser.add_argument('--full', action='store_true', help='Perform a full backup')
    parser.add_argument('--inc', action='store_true', help='Perform an incremental backup')
    parser.add_argument('--cleanup', action='store_true', help='Clean up old backups')
    parser.add_argument('--config', default='mysql_backup.ini', help='Path to config file')

    args = parser.parse_args()

    try:
        backup = MySQLNativeBackup(args.config)

        if args.full:
            backup.full_backup()
        elif args.inc:
            backup.incremental_backup()
        elif args.cleanup:
            backup.cleanup_old_backups()
        else:
            # 默认执行完全备份
            backup.full_backup()
            backup.cleanup_old_backups()

    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
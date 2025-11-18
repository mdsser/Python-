#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库备份脚本
支持MySQL数据库的完全备份和增量备份
功能特性：
- 完全备份和增量备份
- 自动压缩备份文件
- 时间戳命名
- 自动清理7天前的备份文件
- 详细的日志记录
"""

import os
import sys
import subprocess
import gzip
import shutil
import logging
from datetime import datetime, timedelta
import argparse
import json
import time

class DatabaseBackup:
    def __init__(self, config_file='backup_config.json'):
        """
        初始化备份类
        :param config_file: 配置文件路径
        """
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.backup_dir = self.config.get('backup_dir', './backups')
        self.ensure_backup_dir()
        
    def load_config(self, config_file):
        """
        加载配置文件
        :param config_file: 配置文件路径
        :return: 配置字典
        """
        default_config = {
            'mysql': {
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': '',
                'database': 'test_db'
            },
            'backup_dir': './backups',
            'retention_days': 7,
            'compress': True,
            'log_level': 'INFO'
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                        elif isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if sub_key not in config[key]:
                                    config[key][sub_key] = sub_value
                    return config
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return default_config
        else:
            # 创建默认配置文件
            self.create_default_config(config_file, default_config)
            return default_config
    
    def create_default_config(self, config_file, config):
        """
        创建默认配置文件
        :param config_file: 配置文件路径
        :param config: 配置字典
        """
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f"已创建默认配置文件: {config_file}")
            print("请根据您的数据库配置修改该文件")
        except Exception as e:
            print(f"创建配置文件失败: {e}")
    
    def setup_logging(self):
        """
        设置日志记录
        """
        log_level = getattr(logging, self.config.get('log_level', 'INFO'))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('backup.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def ensure_backup_dir(self):
        """
        确保备份目录存在
        """
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            self.logger.info(f"创建备份目录: {self.backup_dir}")
    
    def get_timestamp(self):
        """
        获取当前时间戳
        :return: 时间戳字符串
        """
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def build_mysql_command(self, backup_type='full'):
        """
        构建MySQL备份命令
        :param backup_type: 备份类型 ('full' 或 'incremental')
        :return: 命令列表
        """
        mysql_config = self.config['mysql']
        
        # 基础命令
        cmd = ['mysqldump']
        
        # 添加连接参数
        if mysql_config.get('host'):
            cmd.extend(['-h', mysql_config['host']])
        if mysql_config.get('port'):
            cmd.extend(['-P', str(mysql_config['port'])])
        if mysql_config.get('user'):
            cmd.extend(['-u', mysql_config['user']])
        if mysql_config.get('password'):
            cmd.extend(['-p' + mysql_config['password']])
        
        # 添加备份选项
        cmd.extend([
            '--single-transaction',  # 保证数据一致性
            '--routines',           # 包含存储过程和函数
            '--triggers',           # 包含触发器
            '--events',             # 包含事件
            '--set-gtid-purged=OFF' # 避免GTID相关问题
        ])
        
        # 如果是增量备份，添加增量备份选项
        if backup_type == 'incremental':
            cmd.extend([
                '--master-data=2',  # 记录主从复制信息
                '--flush-logs'      # 刷新日志
            ])
        
        # 指定数据库
        cmd.append(mysql_config['database'])
        
        return cmd
    
    def compress_file(self, source_file, target_file=None):
        """
        压缩文件
        :param source_file: 源文件路径
        :param target_file: 目标文件路径（可选）
        :return: 压缩后的文件路径
        """
        if target_file is None:
            target_file = source_file + '.gz'
        
        try:
            with open(source_file, 'rb') as f_in:
                with gzip.open(target_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 删除原文件
            os.remove(source_file)
            self.logger.info(f"文件已压缩: {target_file}")
            return target_file
        except Exception as e:
            self.logger.error(f"压缩文件失败: {e}")
            return source_file
    
    def full_backup(self):
        """
        执行完全备份
        :return: 备份文件路径
        """
        timestamp = self.get_timestamp()
        backup_file = os.path.join(self.backup_dir, f"full_backup_{timestamp}.sql")
        
        self.logger.info("开始完全备份...")
        
        try:
            # 构建备份命令
            cmd = self.build_mysql_command('full')
            
            # 执行备份
            with open(backup_file, 'w', encoding='utf-8') as f:
                process = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.logger.info(f"完全备份成功: {backup_file}")
                
                # 压缩备份文件
                if self.config.get('compress', True):
                    backup_file = self.compress_file(backup_file)
                
                return backup_file
            else:
                self.logger.error(f"完全备份失败: {stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"完全备份异常: {e}")
            return None
    
    def incremental_backup(self):
        """
        执行增量备份
        :return: 备份文件路径
        """
        timestamp = self.get_timestamp()
        backup_file = os.path.join(self.backup_dir, f"incremental_backup_{timestamp}.sql")
        
        self.logger.info("开始增量备份...")
        
        try:
            # 构建备份命令
            cmd = self.build_mysql_command('incremental')
            
            # 执行备份
            with open(backup_file, 'w', encoding='utf-8') as f:
                process = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.logger.info(f"增量备份成功: {backup_file}")
                
                # 压缩备份文件
                if self.config.get('compress', True):
                    backup_file = self.compress_file(backup_file)
                
                return backup_file
            else:
                self.logger.error(f"增量备份失败: {stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"增量备份异常: {e}")
            return None
    
    def cleanup_old_backups(self):
        """
        清理过期的备份文件
        """
        retention_days = self.config.get('retention_days', 7)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        self.logger.info(f"清理 {retention_days} 天前的备份文件...")
        
        deleted_count = 0
        for filename in os.listdir(self.backup_dir):
            file_path = os.path.join(self.backup_dir, filename)
            
            # 检查文件修改时间
            if os.path.isfile(file_path):
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_mtime < cutoff_date:
                    try:
                        os.remove(file_path)
                        self.logger.info(f"删除过期备份文件: {filename}")
                        deleted_count += 1
                    except Exception as e:
                        self.logger.error(f"删除文件失败 {filename}: {e}")
        
        self.logger.info(f"清理完成，共删除 {deleted_count} 个文件")
    
    def list_backups(self):
        """
        列出所有备份文件
        """
        self.logger.info("当前备份文件列表:")
        
        if not os.path.exists(self.backup_dir):
            self.logger.info("备份目录不存在")
            return
        
        files = []
        for filename in os.listdir(self.backup_dir):
            file_path = os.path.join(self.backup_dir, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                files.append({
                    'name': filename,
                    'size': file_size,
                    'mtime': file_mtime
                })
        
        # 按修改时间排序
        files.sort(key=lambda x: x['mtime'], reverse=True)
        
        for file_info in files:
            size_mb = file_info['size'] / (1024 * 1024)
            self.logger.info(f"  {file_info['name']} - {size_mb:.2f}MB - {file_info['mtime']}")
    
    def run_backup(self, backup_type='full'):
        """
        运行备份
        :param backup_type: 备份类型 ('full' 或 'incremental')
        :return: 是否成功
        """
        start_time = time.time()
        
        try:
            if backup_type == 'full':
                backup_file = self.full_backup()
            elif backup_type == 'incremental':
                backup_file = self.incremental_backup()
            else:
                self.logger.error(f"不支持的备份类型: {backup_type}")
                return False
            
            if backup_file:
                # 清理过期备份
                self.cleanup_old_backups()
                
                # 计算备份时间
                elapsed_time = time.time() - start_time
                self.logger.info(f"备份完成，耗时: {elapsed_time:.2f} 秒")
                
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"备份过程异常: {e}")
            return False

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='数据库备份脚本')
    parser.add_argument('--type', choices=['full', 'incremental'], default='full',
                       help='备份类型 (full: 完全备份, incremental: 增量备份)')
    parser.add_argument('--config', default='backup_config.json',
                       help='配置文件路径')
    parser.add_argument('--list', action='store_true',
                       help='列出所有备份文件')
    parser.add_argument('--cleanup', action='store_true',
                       help='仅执行清理操作')
    
    args = parser.parse_args()
    
    # 创建备份实例
    backup = DatabaseBackup(args.config)
    
    if args.list:
        backup.list_backups()
    elif args.cleanup:
        backup.cleanup_old_backups()
    else:
        success = backup.run_backup(args.type)
        if success:
            print("备份操作完成")
            sys.exit(0)
        else:
            print("备份操作失败")
            sys.exit(1)

if __name__ == '__main__':
    main()
    
    def build_mysql_command(self, backup_type='full'):
        """
        构建MySQL备份命令
        :param backup_type: 备份类型 ('full' 或 'incremental')
        :return: 命令列表
        """
        mysql_config = self.config['mysql']
        
        # 基础命令
        cmd = ['mysqldump']
        
        # 添加连接参数
        if mysql_config.get('host'):
            cmd.extend(['-h', mysql_config['host']])
        if mysql_config.get('port'):
            cmd.extend(['-P', str(mysql_config['port'])])
        if mysql_config.get('user'):
            cmd.extend(['-u', mysql_config['user']])
        if mysql_config.get('password'):
            cmd.extend(['-p' + mysql_config['password']])
        
        # 添加备份选项
        cmd.extend([
            '--single-transaction',  # 保证数据一致性
            '--routines',           # 包含存储过程和函数
            '--triggers',           # 包含触发器
            '--events',             # 包含事件
            '--set-gtid-purged=OFF' # 避免GTID相关问题
        ])
        
        # 如果是增量备份，添加增量备份选项
        if backup_type == 'incremental':
            cmd.extend([
                '--master-data=2',  # 记录主从复制信息
                '--flush-logs'      # 刷新日志
            ])
        
        # 指定数据库
        cmd.append(mysql_config['database'])
        
        return cmd
    
    def compress_file(self, source_file, target_file=None):
        """
        压缩文件
        :param source_file: 源文件路径
        :param target_file: 目标文件路径（可选）
        :return: 压缩后的文件路径
        """
        if target_file is None:
            target_file = source_file + '.gz'
        
        try:
            with open(source_file, 'rb') as f_in:
                with gzip.open(target_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 删除原文件
            os.remove(source_file)
            self.logger.info(f"文件已压缩: {target_file}")
            return target_file
        except Exception as e:
            self.logger.error(f"压缩文件失败: {e}")
            return source_file
    
    def full_backup(self):
        """
        执行完全备份
        :return: 备份文件路径
        """
        timestamp = self.get_timestamp()
        backup_file = os.path.join(self.backup_dir, f"full_backup_{timestamp}.sql")
        
        self.logger.info("开始完全备份...")
        
        try:
            # 构建备份命令
            cmd = self.build_mysql_command('full')
            
            # 执行备份
            with open(backup_file, 'w', encoding='utf-8') as f:
                process = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.logger.info(f"完全备份成功: {backup_file}")
                
                # 压缩备份文件
                if self.config.get('compress', True):
                    backup_file = self.compress_file(backup_file)
                
                return backup_file
            else:
                self.logger.error(f"完全备份失败: {stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"完全备份异常: {e}")
            return None
    
    def incremental_backup(self):
        """
        执行增量备份
        :return: 备份文件路径
        """
        timestamp = self.get_timestamp()
        backup_file = os.path.join(self.backup_dir, f"incremental_backup_{timestamp}.sql")
        
        self.logger.info("开始增量备份...")
        
        try:
            # 构建备份命令
            cmd = self.build_mysql_command('incremental')
            
            # 执行备份
            with open(backup_file, 'w', encoding='utf-8') as f:
                process = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.logger.info(f"增量备份成功: {backup_file}")
                
                # 压缩备份文件
                if self.config.get('compress', True):
                    backup_file = self.compress_file(backup_file)
                
                return backup_file
            else:
                self.logger.error(f"增量备份失败: {stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"增量备份异常: {e}")
            return None
    
    def cleanup_old_backups(self):
        """
        清理过期的备份文件
        """
        retention_days = self.config.get('retention_days', 7)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        self.logger.info(f"清理 {retention_days} 天前的备份文件...")
        
        deleted_count = 0
        for filename in os.listdir(self.backup_dir):
            file_path = os.path.join(self.backup_dir, filename)
            
            # 检查文件修改时间
            if os.path.isfile(file_path):
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_mtime < cutoff_date:
                    try:
                        os.remove(file_path)
                        self.logger.info(f"删除过期备份文件: {filename}")
                        deleted_count += 1
                    except Exception as e:
                        self.logger.error(f"删除文件失败 {filename}: {e}")
        
        self.logger.info(f"清理完成，共删除 {deleted_count} 个文件")
    
    def list_backups(self):
        """
        列出所有备份文件
        """
        self.logger.info("当前备份文件列表:")
        
        if not os.path.exists(self.backup_dir):
            self.logger.info("备份目录不存在")
            return
        
        files = []
        for filename in os.listdir(self.backup_dir):
            file_path = os.path.join(self.backup_dir, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                files.append({
                    'name': filename,
                    'size': file_size,
                    'mtime': file_mtime
                })
        
        # 按修改时间排序
        files.sort(key=lambda x: x['mtime'], reverse=True)
        
        for file_info in files:
            size_mb = file_info['size'] / (1024 * 1024)
            self.logger.info(f"  {file_info['name']} - {size_mb:.2f}MB - {file_info['mtime']}")
    
    def run_backup(self, backup_type='full'):
        """
        运行备份
        :param backup_type: 备份类型 ('full' 或 'incremental')
        :return: 是否成功
        """
        start_time = time.time()
        
        try:
            if backup_type == 'full':
                backup_file = self.full_backup()
            elif backup_type == 'incremental':
                backup_file = self.incremental_backup()
            else:
                self.logger.error(f"不支持的备份类型: {backup_type}")
                return False
            
            if backup_file:
                # 清理过期备份
                self.cleanup_old_backups()
                
                # 计算备份时间
                elapsed_time = time.time() - start_time
                self.logger.info(f"备份完成，耗时: {elapsed_time:.2f} 秒")
                
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"备份过程异常: {e}")
            return False

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='数据库备份脚本')
    parser.add_argument('--type', choices=['full', 'incremental'], default='full',
                       help='备份类型 (full: 完全备份, incremental: 增量备份)')
    parser.add_argument('--config', default='backup_config.json',
                       help='配置文件路径')
    parser.add_argument('--list', action='store_true',
                       help='列出所有备份文件')
    parser.add_argument('--cleanup', action='store_true',
                       help='仅执行清理操作')
    
    args = parser.parse_args()
    
    # 创建备份实例
    backup = DatabaseBackup(args.config)
    
    if args.list:
        backup.list_backups()
    elif args.cleanup:
        backup.cleanup_old_backups()
    else:
        success = backup.run_backup(args.type)
        if success:
            print("备份操作完成")
            sys.exit(0)
        else:
            print("备份操作失败")
            sys.exit(1)

if __name__ == '__main__':
    main() 
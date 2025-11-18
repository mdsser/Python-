# 多服务器配置文件对比
"""
1、配置收集与备份（从多台服务器自动收集配置文件，将配置文件备份到本地）
2、配置差异比较
3、批量配置部署
4、配置验证
"""
import argparse
import difflib
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from jinja2 import Template

import yaml
import paramiko

class ConfigManager:
    # 初始化加载服务器的配置文件
    def __init__(self, config_file='servers.yaml'):
        self.servers = self.load_config(config_file)
        self.backup_dir = 'config_backups'
        os.makedirs(self.backup_dir, exist_ok=True)

    # 读取并加载yaml格式的配置文件
    def load_config(self, config_file):
        with open(config_file) as f:
            # 安全加载safe_load的内容
            return yaml.safe_load(f)

    # 与远程主机建立连接
    def get_ssh_client(self, server):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=server['192.168.1.11'],
            port=server.get('port', 22),
            username=server['root'],
            password=server.get('1'),
            # 如果使用秘钥登录，则不需要使用密码
            key_filename=server.get('key_file')
        )
        return client

    def get_file_content(self, server, remote_path):
        ssh = self.get_ssh_client(server)
        sftp = ssh.open_sftp()

        try:
            with sftp.file(remote_path, 'r') as f:
                content = f.read().decode('utf-8')
                return content
        except:
            sftp.close()
            ssh.close()

    def backup_config(self, server, remote_path):
        # 备份远程服务器上的配置文件
        content = self.get_file_content(server, remote_path)

        # 创建备份文件名
        timestamp = datetime.now().strftime('%Y%m%d - %H:%M:%S')
        hostname = server['host'].replace('.', '_') # 将主机名中的点替换为下划线
        filename = f"{hostname}_{os.path.basename(remote_path)}_{timestamp}.bak"
        backup_path = os.path.join(self.backup_dir, filename)

        # 保存备份文件
        with open(backup_path, 'w') as f:
            f.write(content)

        print(f"Backup created: {backup_path}")
        return backup_path

    def compare_config(self, config1, config2):
        # 比较两个配置文件的差异
        diff = difflib.context_diff(
            config1.splitlines(keepends=True),
            config2.splitlines(keepends=True),
            fromfile='config1',
            tofile='config2'
        )
        # 将difflib.context_diff产生的差异，合并为一整个字符串
        return ''.join(diff)

    def generate_config(self, template_file, context_file):
        # 模板文件是具有占位符的文件，上下文是给定具体的key和value的文件
        # 根据模板文件和上下文文件生成配置文件内容
        with open(template_file, 'r') as f:
            template = Template(f.read())

        with open(context_file) as f:
            context = yaml.safe_load(f.read())

        return template.render(**context)

    def deploy_config(self, server, remote_path, content):
        ssh = self.get_ssh_client(server)
        sftp = ssh.open_sftp()

        # 备份当前配置文件
        self.backup_config(server, remote_path)

        # 上传新配置文件到远程服务器的临时目录
        temp_path = f"/tmp/{os.path.basename(remote_path)}.{datetime.now().timestamp()}"
        with sftp.file(temp_path, 'w') as f:
            f.write(content)

        commands = [
            f"sudo cp {temp_path} {remote_path}",   # 复制文件
            f"sudo rm -f {temp_path}",              # 删除临时文件
            f"sudo chmod 644 {remote_path}",        # 设置文件权限为644
            f"sudo chown root:root {remote_path}"   # 设置文件所有者为root
        ]

        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            # 检查命令执行结果
            if stdout.channel.recv_exit_status() !=0:
                print(f"错误执行 {cmd} on {server['host']}: {stderr.read().decode()}")
                sftp.close()
                ssh.close()
                return False

        print(f"Config deployed successfully to {server['host']}:{remote_path}")  # 输出部署成功信息
        sftp.close()
        ssh.close()
        return True

    def check_configs(self):
        # 检查所有服务器的配置文件与最新备份文件的差异
        results = {}

        for server in self.servers:
            host = server['host']
            results[host] = {}

            for config_file in server['config_files']:
                remote_path = config_file['path']  # 远程配置文件路径
                current_content = self.get_file_content(server, remote_path)  # 获取当前配置文件内容
                # 获取与当前配置文件相关的备份文件列表，并按时间降序排序
                backup_files = sorted(
                    [f for f in os.listdir(self.backup_dir) if host in f and os.path.basename(remote_path) in f],
                    reverse=True
                )

                if backup_files:
                    # 获取最新的备份文件内容
                    latest_backup = os.path.join(self.backup_dir, backup_files[0])
                    with open(latest_backup) as f:
                        backup_content = f.read()

                    # 比较当前配置文件与最新备份文件的差异
                    if current_content != backup_content:
                        diff = self.compare_configs(backup_content, current_content)  # 计算差异
                        results[host][remote_path] = {
                            'status': 'changed',  # 状态为'changed'
                            'diff': diff  # 差异内容
                        }
                    else:
                        results[host][remote_path] = {
                            'status': 'unchanged'  # 状态为'unchanged'
                        }
                else:
                    results[host][remote_path] = {
                        'status': 'no_backup'  # 状态为'no_backup'
                    }

        return results

    def bulk_deploy(self, template_file, context_file):
        # 批量部署配置文件到所有服务器
        content = self.generate_config(template_file, context_file)  # 生成配置文件内容

        with ThreadPoolExecutor(max_workers=5) as executor:  # 创建线程池，最大工作线程数为5
            futures = []
            for server in self.servers:
                for config_file in server['config_files']:
                    # 如果配置文件需要部署（默认为True）
                    if config_file.get('deploy', True):
                        # 提交部署任务到线程池
                        futures.append(
                            executor.submit(
                                self.deploy_config,
                                server,
                                config_file['path'],
                                content
                            )
                        )

            results = [f.result() for f in futures]  # 获取所有任务的结果

        return all(results)  # 如果所有任务都成功返回True，否则返回False

def main():
    parser = argparse.ArgumentParser(description='Configuration Management Tool')
    # 目标存储空间是在command下面
    subparsers = parser.add_subparsers(dest='command', required=True)

    # 检查子命令
    check_parser = subparsers.add_parser('check', help='检查配置差异')

    # 备份子命令
    backup_parser = subparsers.add_parser('backup', help='备份文件配置')

    # 部署命令
    deploy_parser = subparsers.add_parser('deploy', help='部署配置')

    # 添加位置参数
    deploy_parser.add_argument('template', help='模板文件')
    deploy_parser.add_argument('context', help='文本文件')

    # 检测输入参数
    args = parser.parse_args()

    # 生成实例
    manager = ConfigManager()

    if args.command == 'check':
        results = manager.check_configs()
        print()

    elif args.command == 'backup':
        if args.all:
            # 备份所有配置文件
            for server in manager.servers:
                for config_file in server['config_files']:
                    manager.backup_config(server, config_file['path'])

    elif args.command == 'deploy':
        success = manager.bulk_deploy(args.template, args.context)  # 批量部署配置文件
        if success:
            print("All configs deployed successfully")  # 输出部署成功信息
        else:
            print("Some configs failed to deploy")  # 输出部署失败信息

if __name__ == '__main__':
    main()
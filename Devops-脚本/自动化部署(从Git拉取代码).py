import argparse
import configparser
import logging
import subprocess
import sys
import json
from logging.handlers import RotatingFileHandler
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class DeploymentTool:
    # 初始化类的初始值
    def __init__(self,config_file='deploy_config.json'):
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.current_version = None
        self.previous_version = None
        self.deploy_dir = Path(self.config.get('deploy_dir', '/var/www/app'))
        self.backup_dir = Path(self.config.get('backup_dir', '/var/www/backups'))
        self.env = Environment(loader=FileSystemLoader('templates'))

        # 确保目录存在
        self.deploy_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)


    def load_config(self, config_file):
        try:
            with open(config_file) as f:
                return json.load(f)
        except FileNotFoundError as e :
            return {
                'deploy_dir': '/var/www/app',
                'backup_dir': '/var/www/backups',
                'git_repo': 'https://github.com/example/repo.git',
                'branch': 'main',
                'service_name': 'myapp',
                'templates': {
                    'config.ini': 'config.ini.j2'
                },
                'pre_deploy_checks': [
                    'git --version',
                    'python --version'
                ],
                'post_deploy_tasks': [
                    'python manage.py migrate',
                    'python manage.py collectstatic --noinput'
                ]
            }

    def setup_logging(self):
        log_file = self.config.get('log_file', 'deploy.log')
        max_size = self.config.get('log_max_size', 5 * 1024 * 1024)
        backup_count = self.config.get('log_backup_count', 3)

        logging.basicConfig(
            level = logging.INFO,
            format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                RotatingFileHandler(
                    log_file, maxBytes = max_size, backupCount =backup_count),
                # 会将日志信息输出到标准输出流,即控制台
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('deploy')

    def run_command(self, command, cwd=None):
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.logger.info(f"command succeded: {command}")
            self.logger.debug(f"Output: {result.stdout}")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error()



def main():
    parser = argparse.ArgumentParser(description='Deployment Tool')
    parser.add_argument('--config', default='deploy_config.json', help='Path to config file')
    parser.add_argument('--rollback', action='store_true', help='Rollback to previous version')

    args = parser.parse_args()
    deployer = DeploymentTool(args.config)
    if args.rollback:
        if deployer.rollback():
            print('Rollback completed successfully!')
            sys.exit(0)
        else:
            print('Rollback failed')
            sys.exit(1)
    else:
        if deployer.deploy():
            print("Deployment completed successfully!")
            sys.exit(0)
        else:
            print("Deployment failed")
            sys.exit(1)

if __name__ == '__main__':
    main()
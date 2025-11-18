"""
自动化部署工具
功能要求：
1. 从Git仓库拉取指定分支/标签的代码
2. 安装Python依赖（requirements.txt）
3. 支持配置文件模板替换（使用Jinja2）
4. 支持服务重启（通过systemd或supervisor）
5. 支持回滚到上一个版本
6. 记录部署日志
7. 支持预部署检查和后置任务
"""

import os
import shutil
import subprocess
from datetime import datetime
import argparse
import json
from pathlib import Path
import sys
import tempfile
from jinja2 import Environment, FileSystemLoader
import logging
from logging.handlers import RotatingFileHandler

class DeploymentTool:
    def __init__(self, config_file='deploy_config.json'):
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
        except FileNotFoundError:
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
        max_size = self.config.get('log_max_size', 5 * 1024 * 1024)  # 5MB
        backup_count = self.config.get('log_backup_count', 3)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                RotatingFileHandler(
                    log_file, maxBytes=max_size, backupCount=backup_count),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('deploy')

    def run_command(self, command, cwd=None):
        """运行shell命令并返回输出"""
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
            self.logger.info(f"Command succeeded: {command}")
            self.logger.debug(f"Output: {result.stdout}")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {command}")
            self.logger.error(f"Error: {e.stderr}")
            return False, e.stderr

    def git_clone(self):
        """克隆或更新Git仓库"""
        repo_url = self.config['git_repo']
        branch = self.config.get('branch', 'main')

        if (self.deploy_dir / '.git').exists():
            # 已有仓库，执行pull
            self.logger.info("Updating existing repository...")
            success, output = self.run_command(
                f"git pull origin {branch}",
                cwd=self.deploy_dir
            )
            if not success:
                return False

            # 获取当前commit hash作为版本号
            success, output = self.run_command(
                "git rev-parse --short HEAD",
                cwd=self.deploy_dir
            )
            if success:
                self.current_version = output.strip()
            return success
        else:
            # 新克隆仓库
            self.logger.info("Cloning new repository...")
            success, output = self.run_command(
                f"git clone -b {branch} {repo_url} {self.deploy_dir}"
            )
            if success:
                # 获取当前commit hash作为版本号
                success, output = self.run_command(
                    "git rev-parse --short HEAD",
                    cwd=self.deploy_dir
                )
                if success:
                    self.current_version = output.strip()
            return success

    def install_dependencies(self):
        """安装Python依赖"""
        requirements = self.deploy_dir / 'requirements.txt'
        if requirements.exists():
            self.logger.info("Installing Python dependencies...")
            return self.run_command(
                f"pip install -r {requirements}"
            )[0]
        else:
            self.logger.warning("No requirements.txt found, skipping dependency installation")
            return True

    def render_templates(self):
        """渲染配置文件模板"""
        templates = self.config.get('templates', {})
        if not templates:
            self.logger.info("No templates to render")
            return True

        context = self.config.get('template_context', {})

        for dest, template in templates.items():
            self.logger.info(f"Rendering template {template} to {dest}")
            try:
                template_obj = self.env.get_template(template)
                rendered = template_obj.render(**context)

                dest_path = self.deploy_dir / dest
                with open(dest_path, 'w') as f:
                    f.write(rendered)
            except Exception as e:
                self.logger.error(f"Failed to render template {template}: {e}")
                return False

        return True

    def run_pre_deploy_checks(self):
        """运行预部署检查"""
        checks = self.config.get('pre_deploy_checks', [])
        if not checks:
            self.logger.info("No pre-deploy checks configured")
            return True

        self.logger.info("Running pre-deploy checks...")
        for check in checks:
            success, output = self.run_command(check)
            if not success:
                self.logger.error(f"Pre-deploy check failed: {check}")
                return False

        return True

    def run_post_deploy_tasks(self):
        """运行后置任务"""
        tasks = self.config.get('post_deploy_tasks', [])
        if not tasks:
            self.logger.info("No post-deploy tasks configured")
            return True

        self.logger.info("Running post-deploy tasks...")
        for task in tasks:
            success, output = self.run_command(task, cwd=self.deploy_dir)
            if not success:
                self.logger.error(f"Post-deploy task failed: {task}")
                return False

        return True

    def backup_current_version(self):
        """备份当前版本"""
        if not (self.deploy_dir / '.git').exists():
            self.logger.warning("No existing deployment to backup")
            return True

        # 获取当前版本
        success, output = self.run_command(
            "git rev-parse --short HEAD",
            cwd=self.deploy_dir
        )
        if not success:
            return False

        version = output.strip()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{timestamp}_{version}.tar.gz"
        backup_path = self.backup_dir / backup_name

        self.logger.info(f"Creating backup: {backup_path}")
        try:
            # 使用tar创建压缩备份
            success, output = self.run_command(
                f"tar -czf {backup_path} -C {self.deploy_dir.parent} {self.deploy_dir.name}"
            )
            if success:
                self.previous_version = version
            return success
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False

    def restart_service(self):
        """重启服务"""
        service = self.config.get('service_name')
        if not service:
            self.logger.info("No service name configured, skipping restart")
            return True

        self.logger.info(f"Restarting service: {service}")
        return self.run_command(f"systemctl restart {service}")[0]

    def rollback(self):
        """回滚到上一个版本"""
        if not self.previous_version:
            self.logger.error("No previous version available for rollback")
            return False

        # 查找最近的备份文件
        backups = sorted(self.backup_dir.glob(f"*_{self.previous_version}.tar.gz"))
        if not backups:
            self.logger.error(f"No backup found for version {self.previous_version}")
            return False

        latest_backup = backups[-1]
        self.logger.info(f"Rolling back to version {self.previous_version} using {latest_backup}")

        # 删除当前部署
        try:
            shutil.rmtree(self.deploy_dir)
        except Exception as e:
            self.logger.error(f"Failed to remove current deployment: {e}")
            return False

        # 从备份恢复
        try:
            success, output = self.run_command(
                f"tar -xzf {latest_backup} -C {self.deploy_dir.parent}"
            )
            if success:
                self.current_version = self.previous_version
                self.previous_version = None
                return self.restart_service()
            return False
        except Exception as e:
            self.logger.error(f"Restore from backup failed: {e}")
            return False

    def deploy(self):
        """执行完整部署流程"""
        self.logger.info("Starting deployment process")

        # 1. 运行预部署检查
        if not self.run_pre_deploy_checks():
            self.logger.error("Pre-deploy checks failed, aborting")
            return False

        # 2. 备份当前版本
        if not self.backup_current_version():
            self.logger.error("Backup failed, aborting")
            return False

        # 3. 克隆/更新代码
        if not self.git_clone():
            self.logger.error("Git clone/update failed, attempting rollback")
            self.rollback()
            return False

        # 4. 安装依赖
        if not self.install_dependencies():
            self.logger.error("Dependency installation failed, attempting rollback")
            self.rollback()
            return False

        # 5. 渲染模板
        if not self.render_templates():
            self.logger.error("Template rendering failed, attempting rollback")
            self.rollback()
            return False

        # 6. 运行后置任务
        if not self.run_post_deploy_tasks():
            self.logger.error("Post-deploy tasks failed, attempting rollback")
            self.rollback()
            return False

        # 7. 重启服务
        if not self.restart_service():
            self.logger.error("Service restart failed, attempting rollback")
            self.rollback()
            return False

        self.logger.info(f"Deployment completed successfully. Current version: {self.current_version}")
        return True

def main():
    parser = argparse.ArgumentParser(description='Deployment Tool')
    parser.add_argument('--config', default='deploy_config.json',
                      help='Path to config file')
    parser.add_argument('--rollback', action='store_true',
                      help='Rollback to previous version')

    args = parser.parse_args()

    deployer = DeploymentTool(args.config)

    if args.rollback:
        if deployer.rollback():
            print("Rollback completed successfully")
            sys.exit(0)
        else:
            print("Rollback failed")
            sys.exit(1)
    else:
        if deployer.deploy():
            print("Deployment completed successfully")
            sys.exit(0)
        else:
            print("Deployment failed")
            sys.exit(1)

if __name__ == '__main__':
    main()
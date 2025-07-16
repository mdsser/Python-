import filecmp
import os
import shutil
import paramiko
from scp import SCPClient
import time
import logging

logging.basicConfig(filename = 'log_collector.log', level=logging.INFO)
def collect_logs(local_log_dir, backup_log_dir):
    if not os.path.exists(backup_log_dir):
        os.makedirs(backup_log_dir)

    for root,_ , files in os.walk(local_log_dir):
        for file in files:
            local_path = os.path.join(root,file)
            backup_path = os.path.join(backup_log_dir,file)

            if os.path.exists(backup_path) and filecmp.cmp(local_path, backup_path, shallow=False):
                logging.info(f"文件：{local_path} 已存在且相同，跳过")
                continue

            # 复制文件到备份目录
            shutil.copy2(local_path, backup_path)
            logging.info(f"收集日志: {local_path} => {backup_path}")
    return backup_log_dir

def upload_logs(backup_log_dir, remote_host, remote_dir, username, password=None, key_filename=None):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(remote_host, username=username, password=password, key_filename=key_filename)

    with SCPClient(ssh.get_transport()) as scp:
        for root,_ , files in os.walk(backup_log_dir):
            for file in files:
                local_path = os.path.join(root,file)
                remote_path = os.path.join(remote_dir, os.path.relpath(local_path, backup_log_dir))

                # 上传文件到远程服务器
                scp.put(local_path, remote_path)
                logging.info(f"上传日志: {local_path} => {remote_path}")

    ssh.close()
    logging.info(f"日志上传完成")

if __name__ == '__main__':
    local_log_dir = "/var/log"
    backup_log_dir = "/tmp/logs"
    remote_host = "log.server.com"
    remote_dir = "/logs"
    username = "ops"
    password = "123456"

    while True:
        collect_logs(local_log_dir, backup_log_dir)
        upload_logs(backup_log_dir, remote_host, remote_dir, username, password)
        time.sleep(3600)
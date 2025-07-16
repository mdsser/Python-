import paramiko
from scp import SCPClient
import shutil

def upload_log(local_path, remote_host, remote_path, user, pwd):
    ssh =paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(remote_host, username=user, password=pwd)

    with SCPClient(ssh.get_transport()) as scp:
        scp.put(local_path, remote_path)
        print(f"已上传 {local_path} 到 {remote_path}")

if __name__ == '__main__':
    shutil.make_archive('nginx_logs','gztar', '/var/log/nginx')
    upload_log('nginx_logs.tar.gz', 'backup.server.com', '/backups', 'ops', 'Ops!2023')
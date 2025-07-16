import paramiko
from scp import SCPClient
import os
import filecmp

def sync_files(local_dir, remote_host, remote_dir, username):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(remote_host, username=username)

    with SCPClient(ssh.get_transport()) as scp:
        for root,_, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                remote_path = os.path.join(remote_dir, os.path.relpath(local_path, local_dir))

                # 检查远程文件是否存在及是否相同
                stdin, stdout, stderr = ssh.exec_command(f"test -f {remote_path} && echo 'exists")
                if 'exists' in stdout.read().decode('utf-8'):
                    if filecmp.cmp(local_path,remote_path):
                        continue
                print(f"同步: {local_path} => {remote_host}:{remote_path}")
                scp.put(local_path,remote_path)

    ssh.close()


if __name__ == '__main__':
    sync_files("/data/configs", "backup.server.com", "/backup/configs", "ops")
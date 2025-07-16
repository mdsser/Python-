import paramiko
from pathlib import Path

def deploy_ssh_key(hosts, username, password, pub_key_path="~/.ssh/id_rsa"):
    pub_key = Path(pub_key_path).expanduser().readtext()
    for host in hosts:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, username=username, password=password)

            stdin, stdout, stderr = ssh.exec_command(
                'mkdir -p ~/.ssh && grep -q "{}" ~/.ssh/authorized_keys || echo "{}" >> ~/.ssh/authorized_keys'.format(
                    pub_key.strip(), pub_key))

            if stderr.read():
                print(f"[{host}] 公钥部署失败")
            else:
                print(f"[{host}] 公钥部署成功")

        except Exception as e:
            print(f"[{host}] 连接异常: {str(e)}")
        finally:
            ssh.close()


if __name__ == '__main__':
    deploy_ssh_key(
        hosts=["192.168.1.11", "192.168.1.12", "192.168.1.13"],
        username = "root",
        password = "123456"
    )
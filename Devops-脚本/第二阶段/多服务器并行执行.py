import paramiko
from concurrent.futures import ThreadPoolExecutor

def run_remote_command(host, command, username, key_filename="~/.ssh/id_rsa"):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host,username=username, key_filename=key_filename)
        stdin, stdout, stderr = ssh.exec_command(command)
        return f"{host}: {stdout.read().decode().strip()}"
    except Exception as e:
        return f"{host}: ERROR - {str(e)}"
    finally:
        ssh.close()


hosts= [f"192.168.1.{i}" for i in range(101, 111)]
with ThreadPoolExecutor(max_workers=5 ) as executor:
    results = list(executor.map(
        lambda h: run_remote_command(h, "uptime," "root"),
        hosts
    ))

for result in results:
    print(result)
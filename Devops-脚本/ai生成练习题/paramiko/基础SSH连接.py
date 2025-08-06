import paramiko

def ssh_command(host, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password)
    stdin, stdout, stderr = client.exec_command(command)
    print(stdout.read().decode('utf-8'))
    client.close()

ssh_command("192.168.1.100", "root", "your_password", "df -h")
import paramiko

def ssh_key_auth(host, username, key_auth):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    private_key = paramiko.RSAKey.from_private_key_file(key_auth)

    client.connect(host, username=username, pkey=private_key)
    stdin, stdout, stderr = client.exec_command("uptime")
    print(stdout.read().decode('utf-8'))
    client.close()

ssh_key_auth("192.168.1.100", "root", "~/.ssh/id_rsa")
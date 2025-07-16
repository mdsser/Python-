import csv
import paramiko

servers = [
    {"host": "192.168.1.101","user": "root", "pwd": "123456"},
    {"host": "192.168.1.102","user": "admin", "pwd": "Admin@123"}
]

def ssh_exec(host,user,pwd,command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=pwd, timeout=5)
        stdin, stdout, stderr= client.exec_command(command)
        return stdout.read().decode('utf-8')
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        client.close()

with open('disk_usage.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Server', 'Disk Usage'])
    for server in servers:
        output = ssh_exec(server['host'],server['user'],server['pwd'],'df -h')
        writer.writerow([server['host'], output])

print("数据已保存到 disk_usage.csv")
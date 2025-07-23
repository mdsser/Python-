import paramiko
import csv


def get_server_health(host, username, password):
    """获取服务器健康信息"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=username, password=password, timeout=10)
        # 获取负载和内存信息
        stdin, stdout, stderr = client.exec_command('top -bn1 | head -5')
        output = stdout.read().decode()

        # 解析关键指标
        load_avg = output.split('load average:')[1].split(',')[0].strip()
        mem_line = [line for line in output.split('\n') if 'Mem' in line][0]
        mem_used = mem_line.split()[3]

        return {
            'host': host,
            'load_avg': load_avg,
            'mem_used': mem_used
        }
    finally:
        client.close()


# 服务器列表
servers = [
    {'host': '192.168.1.101', 'user': 'admin', 'pwd': 'Admin@123'},
    {'host': '192.168.1.102', 'user': 'root', 'pwd': 'Root#2023'}
]

# 收集数据并保存到CSV
with open('server_health.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['host', 'load_avg', 'mem_used'])
    writer.writeheader()

    for server in servers:
        health = get_server_health(server['host'], server['user'], server['pwd'])
        writer.writerow(health)
        print(f"已收集 {server['host']} 的健康数据")

print("数据已保存到 server_health.csv")
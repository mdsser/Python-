import smtplib
import sys
from email.mime.text import MIMEText
import paramiko
import time
import psutil

def run_ssh_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()

    return output, error

def configure_server(ssh_client):
    config_commands = (
        "sudo yum update",
        "sudo yum -y install psutil",
        "sudo yum -y install python3",
        "sudo yum -y install python3-pip",
        "sudo yum -y install paramiko"
    )

    for command in config_commands:
        output, error =  run_ssh_command(ssh_client, command)
        if error:
            print(f"配置失败: {command}\n错误: {error}")
            return False
        print(f"配置成功: {command}\n输出: {output}")

    return True

def send_alert_email(recipient, cpu_usage, memory_used, disk_used, cpu_threshold, memory_threshold,
                     disk_threshold):
    sender_email = "your_email@example.com"
    sender_password = "your_email_password"

    message = f"""
    系统资源警报！
    时间戳: {time.strftime('%Y-%m-%d %H:%M:%S')}
    CPU 使用率: {cpu_usage}%
    内存使用量: {memory_used:.2f} GB
    磁盘使用量: {disk_used:.2f} GB

    阈值:
    CPU 阈值: {cpu_threshold}%
    内存阈值: {memory_threshold} GB
    磁盘阈值: {disk_threshold} GB
    """

    msg = MIMEText(message)
    msg['Subject'] = '系统资源警报'
    msg['From'] = sender_email
    msg['To'] = recipient_email

    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
    print("警报邮件已发送")


def get_system_resources():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_info = psutil.disk_usage('/')

    return{
        'cpu_usage': cpu_usage,
        'memory_info': memory_info.used / (1024 ** 3),
        'disk_info': disk_info.used / (1024 ** 3)
    }

def monitor_and_alert(server_ip, port, username, password,
                      cpu_threshold, memory_threshold,
                      disk_threshold, recipient_email):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 第一个参数默认位置参数，后面都是关键字参数
        ssh_client.connect(server_ip, port=port, username=username, password=password)

        print(f"已经连接到 {server_ip}:{port}")

        if not configure_server(ssh_client):
            print("服务器配置失败")
            ssh_client.close()
            return False

        ssh_client.close()

        while True:
            resources = get_system_resources()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            print(f"时间戳: {timestamp}")
            print(f"CPU 使用率: {resources['cpu_usage']}%")
            print(f"内存使用量: {resources['memory_used']:.2f} GB")
            print(f"磁盘使用量: {resources['disk_used']:.2f} GB")

            if (resources['cpu_usage'] > cpu_threshold or
                    resources['memory_used'] > memory_threshold or
                    resources['disk_used'] > disk_threshold):
                print("资源使用率超过阈值，发送警报邮件...")
                send_alert_email(recipient_email, resources['cpu_usage'],
                                 resources['memory_used'], resources['disk_used'],
                                 cpu_threshold, memory_threshold, disk_threshold)
            else:
                print("资源使用率在阈值以下")

                time.sleep(60)
    except paramiko.AuthenticationException:
        print("认证失败，请检查用户名和密码")
    except paramiko.SSHException as e:
        print(f"无法建立 SSH 连接: {e}")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == '__main__':
    if len(sys.argv) !=9:
        print(
            "用法：python script.py <服务器IP> <端口号> <用户名> <密码> <CPU阈值> <内存阈值> <磁盘阈值> <收件人邮箱地址>"
        )
        sys.exit(1)

    server_ip = sys.argv[1]
    port = int(sys.argv[2])
    username = sys.argv[3]
    password = sys.argv[4]
    cpu_threshold = float(sys.argv[5])
    memory_threshold = float(sys.argv[6])
    disk_threshold = float(sys.argv[7])
    recipient_email = sys.argv[8]

    monitor_and_alert(server_ip, port, username, password,
                      cpu_threshold, memory_threshold,
                      disk_threshold, recipient_email)
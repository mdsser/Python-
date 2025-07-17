# 当内存使用超过80%时发送邮件告警，每2分钟检查一次
from email.mime.multipart import MIMEMultipart

import psutil
import time
import smtplib
from email.mime.text import MIMEText

def send_alert(usage):
    msg = MIMEText(f"内存使用率已达 {usage}%, 请及时处理! ")
    msg['Subject'] = '内存告警'
    msg['From'] = '2271623969@qq.com'
    msg['To'] = '13277681859@163.com'

    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.login('user', 'password')
        server.send_message(msg)

def memory_monitor():
    while True:
        mem = psutil.virtual_memory()
        if mem.percent > 80:
            print(f"告警：内存使用率 {mem.percent}%")
            send_alert(mem.percent)
        time.sleep(120)

if __name__ == '__main__':
    memory_monitor()
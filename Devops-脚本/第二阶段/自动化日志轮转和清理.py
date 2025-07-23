import shutil
import smtplib
from email.mime.text import MIMEText
import schedule
import time
import logging
import os
from datetime import datetime, timedelta

logging.basicConfig(filename='log_cleanup_log.txt',
                    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def rotate_and_cleanup_logs(log_dir, days_to_keep=7):
    try:
        for root, dirs , files in os.walk(log_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith('.log'):
                    file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if datetime.now() - file_mod_time >= timedelta(days=days_to_keep):
                        os.remove(file_path)
                        logging.info(f"成功删除旧日志文件 {file_path}")
                    else:
                        new_log_file = f"{file_path}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        shutil.move(file_path, new_log_file)
                        logging.info(f"成功轮转日志文件: {file_path} -> {new_log_file}")
    except Exception as e:
        logging.info(f"日志轮转和清理失败: {e}")
        send_email(e)

def send_email(error):
    sender = 'your_email@example.com'
    receiver = ['admin_email@example.com']
    subject = '日志轮转和清理失败通知'
    body = f"日志轮转和清理过程中发生错误:\n{error}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(receiver)

    try:
        with smtplib.SMTP('stmp.example.com', 587) as server:
            server.starttls()
            server.login(sender,'your_password')
            server.sendmail(sender, receiver, msg.as_string())
        logging.info("邮件发送成功")
    except Exception as e:
        logging.error(f"邮件发送失败: {e}")


def cleanup_and_send_report():
    rotate_and_cleanup_logs(log_directory, days_to_keep_logs)

if __name__ == '__main__':
    log_directory = '/path/to/logs'
    days_to_keep_logs = 7

    # 每天运行一次日志清理任务
    schedule.every().day.at("03:00").do(cleanup_and_send_report)

    while True:
        schedule.run_pending()
        time.sleep(60)
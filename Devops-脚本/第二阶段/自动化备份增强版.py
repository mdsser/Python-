import logging
from datetime import datetime
import shutil
import paramiko
import smtplib
from email.mime.text import MIMEText
import os

logging.basicConfig(filename = 'backup_log.txt', level = logging.INFO,
                    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def backup_directory(local_dir, remote_dir, hostname, port, username, password):
    try:
        backup_file = f"{local_dir}_{datetime.now().strftime('%Y%m%d%H%M%S')}.tar.gz"
        shutil.make_archive(backup_file.replace('.tar.gz', ''), 'gztar', local_dir)
        logging.info(f"成功创建备份文件: {backup_file}")

        # 通过SSH上传备份文件到远程服务器
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port, username, password)

        # sftp用于文件的传输操作，如上传sftp.put和下载sftp.get
        sftp = ssh.open_sftp()
        sftp.put(backup_file, os.path.join(remote_dir, os.path.basename(backup_file)))
        sftp.close()
        ssh.close()
        logging.info(f"成功上传备份文件到  {hostname}:{remote_dir}")

        # 删除本地备份文件
        os.remove(backup_file)
        logging.info(f"成功删除本地备份文件: {backup_file}")
    except Exception as e:
        logging.info(f"备份失败 {e}")
        send_mail(e)

def send_mail(error):
    sender = 'your_email@example.com'
    receiver = ['admin_email@example.com']
    subject = '备份失败通知'
    body = f"备份过程中发生错误:\n{error}"

    msg = MIMEText(body)
    msg['From'] = sender
    msg['Subject'] = subject
    msg['To'] = ', '.join(receiver)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, 'your_password')
            server.sendmail(sender, receiver, msg.as_string())
        logging.info(f"邮件发送成功")
    except Exception as e:
        logging.info(f"邮件发送失败: {e}")


if __name__ == '__main__':
    local_directory = '/path/to/local/dir'
    remote_directory = '/path/to/remote/dir'
    remote_hostname = 'example.com'
    remote_port = 22
    remote_username = 'your_username'
    remote_password = 'your_password'
    backup_directory(local_directory,
                     remote_directory,
                     remote_hostname,
                     remote_port,
                     remote_username,
                     remote_password)
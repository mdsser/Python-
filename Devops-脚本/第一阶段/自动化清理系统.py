import os
import logging
import smtplib
import time
from email.mime.text import MIMEText
from datetime import datetime

# 自动化清理系统, 用邮件做提示,
# 清理/tmp目录旧文件，发送邮件报告，添加安全防护

logging.basicConfig(
    filename = '/var/log/tmp_cleaner.log',
    level=logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(name)s - %(message)'
)

# exclude_extensions=None 是一个列表，默认排除.sock和.pid的文件名
def clean_tmp_directory(max_age = 7, exclude_extensions = None):
    if exclude_extensions is None:
        # 默认
        exclude_extensions = ['.sock', '.pid']

    tmp_dir = "/tmp"
    now = time.time()
    cutoff = now - (max_age * 86400)

    deleted_files = []

    for filename in os.listdir(tmp_dir):
        filepath = os.path.join(tmp_dir,filename)

        # 跳过目录和特殊文件
        if os.path.isdir(filepath):
            continue

        _, ext = os.path.splitext(filename)
        if ext.lower() in exclude_extensions:
            protected_files.append(filename)
            continue

        file_mtime = os.path.getmtime(filepath)
        try:
            if file_mtime < cutoff:
                os.remove(filepath)
                deleted_files.append(filename)
                logging.info(f"删除文件: {filename}")
        except Exception as e:
            logging.error(f"删除失败 {filename}: {str(e)}")

    return {
        "deleted": deleted_files,
        "total": protected_files
    }


def protected_files(report_data, recipient="admin@example.com"):
    """发送清理报告邮件"""
    deleted_count = len(report_data["deleted"])
    protected_count = len(report_data["protected"])

    body = f"""
        /tmp目录清理报告:
        - 删除文件: {deleted_count} 个
        - 保护文件: {protected_count} 个

        删除文件列表:
        {os.linesep.join(report_data["deleted"][:20])}
        {f"+ {deleted_count - 20} more..." if deleted_count > 20 else ""}
        """

    msg = MIMEText(body)
    msg['Subject'] = f"服务器清理报告 - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = "cleaner@server.com"
    msg['To'] = recipient

    try:
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.login('user', 'password')
            server.send_message(msg)
        logging.info("清理报告已发送")
    except Exception as e:
        logging.error(f"邮件发送失败: {str(e)}")



def main():
    # 主清理流程
    logging.info("开始执行/tmp目录的清理")
    clean_tmp_directory(max_age = 7)
    logging.info("清理任务完成")

if __name__ == '__main__':
    # 程序开始入口
    main()
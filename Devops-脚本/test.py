import os
import time
import smtplib
from email.mime.text import MIMEText
import logging
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    filename='/var/log/tmp_cleaner.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def clean_tmp_directory(max_age=7, exclude_extensions=None):
    """清理/tmp目录旧文件"""
    if exclude_extensions is None:
        exclude_extensions = ['.sock', '.pid']  # 默认排除的扩展名

    tmp_dir = "/tmp"
    now = time.time()
    cutoff = now - (max_age * 86400)  # 转换为秒

    deleted_files = []
    protected_files = []

    for filename in os.listdir(tmp_dir):
        filepath = os.path.join(tmp_dir, filename)

        # 跳过目录和特殊文件
        if os.path.isdir(filepath):
            continue

        # 检查文件扩展名是否在排除列表
        _, ext = os.path.splitext(filename)
        if ext.lower() in exclude_extensions:
            protected_files.append(filename)
            continue

        # 检查文件修改时间
        file_mtime = os.path.getmtime(filepath)
        if file_mtime < cutoff:
            try:
                os.remove(filepath)
                deleted_files.append(filename)
                logging.info(f"删除文件: {filename}")
            except Exception as e:
                logging.error(f"删除失败 {filename}: {str(e)}")

    return {
        "deleted": deleted_files,
        "protected": protected_files
    }


def send_clean_report(report_data, recipient="admin@example.com"):
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
    """主清理流程"""
    logging.info("开始执行/tmp目录清理")
    report = clean_tmp_directory(max_age=7)
    if report["deleted"]:
        send_clean_report(report)
    logging.info("清理任务完成")


if __name__ == "__main__":
    main()
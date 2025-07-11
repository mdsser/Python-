import os
import shutil
import time


def clean_old_files(directory, days=7, max_usage=85):
    """
    自动清理旧文件并确保磁盘空间充足
    :param directory: 监控目录
    :param days: 清理超过X天的文件
    :param max_usage: 磁盘使用率告警阈值
    """
    # 获取磁盘使用率
    disk_usage = shutil.disk_usage(directory)
    usage_percent = disk_usage.used / disk_usage.total * 100

    # 磁盘空间告警
    if usage_percent > max_usage:
        print(f"⚠️ 磁盘告警: {usage_percent:.1f}% > {max_usage}%")

    # 清理过期文件
    deleted_count = 0
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            # 检查文件修改时间
            file_age = time.time() - os.path.getmtime(filepath)
            if file_age > days * 86400:  # 86400秒=1天
                try:
                    os.remove(filepath)
                    print(f"🗑️ 已删除: {filename} (修改于{int(file_age / 86400)}天前)")
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ 删除失败 {filename}: {str(e)}")

    print(f"清理完成: 删除 {deleted_count} 个文件")
    return deleted_count


# 清理/tmp目录下超过7天的文件
clean_old_files("/tmp", days=7, max_usage=90)
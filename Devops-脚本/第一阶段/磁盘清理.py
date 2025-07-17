import os
import shutil
import time


def clean_old_files(directory, days=7, max_usage=90):
    # 获取磁盘使用率
    disk_usage = shutil.disk_usage(directory)
    usage_percent = disk_usage.used / disk_usage.total * 100

    # 磁盘空间告警
    if usage_percent > max_usage:
        print(f"⚠️ 磁盘告警: {usage_percent:.1f}% > {max_usage}%")

    # 清理过期文件
    delete_count = 0
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            # 检查文件修改时间
            file_age = time.time() - os.stat(file_path).st_mtime
            if file_age > days & 86400:
                try:
                    os.remove(file_path)
                    print(f"🗑️ 已删除: {file_name} (修改于{int(file_age / 86400)}天前)")
                    delete_count += 1
                except Exception as e:
                    print(f"❌ 删除失败 {file_name}: {str(e)}")
    print(f"🧹 已清理 {delete_count} 个文件")
    return delete_count

if __name__ == '__main__':
    clean_old_files("/tmp", days=7, max_usage=90)
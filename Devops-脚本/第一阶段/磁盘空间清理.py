import shutil


def check_disk_clean(threshold=80):
    disk_usage = shutil.disk_usage('/')
    pecent_used = (disk_usage.used / disk_usage.total) * 100

    if pecent_used > threshold:
        print(f"警告：磁盘使用率 {pecent_used: .1f}% 超过 {threshold}%, 开始清理...")
    else:
        print(f"磁盘使用率 {pecent_used: .1f}% 正常")


if __name__ == '__main__':
    check_disk_clean()
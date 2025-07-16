import os
import time

def clean_old_file(directory, days):
    # 删除超过指定天数的文件
    now = time.time()
    cutoff = now - (days * 86400)
    deleted = 0

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isdir(filepath):
            file_time = os.path.getmtime(filepath)
            if file_time < cutoff:
                os.remove(filepath)
                print(f"删除: {filename} (修改于 {time.ctime(file_time)})")
                deleted += 1
    print(f"清理完成! 删除 {deleted} 个文件")

if __name__ == '__main__':
    clean_old_file("/tmp", days=7)
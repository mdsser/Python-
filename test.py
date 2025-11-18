import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
from datetime import datetime



class DistWatcher(FileSystemEventHandler):
    def __init__(self, watch_dir, backup_dir):
        self.watch_dir = watch_dir  # 要监控的父目录（如/deploy）
        self.backup_dir = backup_dir  # 备份目录路径
        self.dist_path = os.path.join(watch_dir, "dist")  # 完整的dist路径
        os.makedirs(self.backup_dir, exist_ok=True)

    def on_created(self, event):
        # 只处理dist目录创建事件
        if event.is_directory and os.path.basename(event.src_path) == "dist":
            self.handle_new_dist()

    def handle_new_dist(self):
        print(f"检测到新的 dist 文件夹出现在 {self.watch_dir}")

        # 检查是否已存在旧的dist
        if os.path.exists(self.dist_path):
            # 备份旧的dist
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"dist_bak_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_name)

            try:
                shutil.move(self.dist_path, backup_path)
                print(f"已备份旧版本到: {backup_path}")
            except Exception as e:
                print(f"备份失败: {e}")
        else:
            print("没有找到旧的dist文件夹，无需备份")


def start_monitoring(watch_dir, backup_dir):
    event_handler = DistWatcher(watch_dir, backup_dir)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()

    print(f"开始监控目录: {watch_dir}")
    print(f"备份将保存到: {backup_dir}")
    print("按 Ctrl+C 停止监控...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    # 配置要监控的目录和备份目录
    WATCH_DIR = "/path/to/deploy"  # 替换为你的部署目录（dist的父目录）
    BACKUP_DIR = "/path/to/backups"  # 替换为你想要保存备份的目录

    # 初始检查（如果dist已存在）
    initial_dist = os.path.join(WATCH_DIR, "dist")
    if os.path.exists(initial_dist):
        print("初始检测到已存在的dist文件夹，准备备份...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"dist_bak_{timestamp}"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        shutil.move(initial_dist, backup_path)
        print(f"已备份初始版本到: {backup_path}")

    start_monitoring(WATCH_DIR, BACKUP_DIR)
import platform
import os
import socket

# 代码解析
# platform.system()：返回操作系统名称（如 Linux、Windows）
#
# platform.release()：返回操作系统版本号
#
# socket.gethostname()：获取当前主机名
#
# os.partitions()：列出所有磁盘分区
#
# os.disk_usage(path)：返回指定路径的磁盘使用情况（总空间、已用空间、剩余空间）
#
# 适用场景
# 快速检查服务器基本信息
#
# 监控磁盘空间是否充足


def get_system_info():
    print("=== 系统信息 ===")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"主机名: {socket.gethostname()}")
    print(f"CPU架构: {platform.machine()}")
    print(f"Python版本: {platform.python_version()}")

def get_disk_usage():
    print("\n=== 磁盘使用情况 ===")
    partitions = os.partitions()
    for part in partitions:
        try:
            usage = os.disk_usage(part.mountpoint)
            print(f"挂载点: {part.mountpoint}")
            print(f"  总空间: {usage.total / (1024**3):.2f} GB")
            print(f"  已用空间: {usage.used / (1024**3):.2f} GB")
            print(f"  可用空间: {usage.free / (1024**3):.2f} GB")
        except:
            continue

if __name__ == "__main__":
    get_system_info()
    get_disk_usage()

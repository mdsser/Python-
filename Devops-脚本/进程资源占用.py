import time
import psutil


def monitor_process(resource_type='memory', threshold=500, interval=3):
    print(f'开始监控{resource_type.upper()} 占用... (ctrl + c 退出)')

    try:
        while True:
            found = False
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                try:
                    # 内存监控模式
                    if resource_type == 'memory':
                        mem_mb = proc.info['memory_info'].rss / 1024 / 1024
                        if mem_mb > threshold:
                            print(f"🚨 内存超标 [{proc.info['name']}]: "
                                  f"{mem_mb:.1f}MB > {threshold}MB (PID:{proc.info['pid']})")
                            found = True

                    # CPU监控模式
                    elif resource_type == 'cpu':
                        # 获取1秒内的CPU使用率
                        proc.info['cpu_percent'] = proc.cpu_percent(interval=1)
                        if proc.info['cpu_percent'] > threshold:
                            print(f"🚨 CPU超标 [{proc.info['name']}]: "
                                  f"{proc.info['cpu_percent']:.1f}% > {threshold}% (PID:{proc.info['pid']})")
                            found = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

                if not found:
                    print(f"🆗 CPU正常 [{proc.info['name']}]: ")
                    time.sleep(interval)

    except KeyboardInterrupt:
        print("\n监控已停止")

if __name__ == '__main__':
    monitor_process('memory', threshold=500)
import psutil
import sys
import time


def monitor_network(interface_name, interval):
    log_file_path = f"{interface_name}_traffice.log"
    with open(log_file_path, 'a') as log_file:
        while True:
            try:
                net_io = psutil.net_io_counters(pernic=True)
                if interface_name in net_io:
                    interface = net_io[interface_name]
                    log_entry = f"{time.strtime('%Y-%m-%d %H:%M:%S')} -  Bytes Sent: {interface.bytes_sent}, Bytes Received: {interface.bytes_recv}\n"
                    log_file.write(log_entry)
                    log_file.flush()
                else:
                    print(f"网络接口 {interface_name} 未找到")
                    break
            except Exception as e:
                print(f"发生错误 {e}")
                break
        time.sleep(interval)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("用法: python script.py <网络接口名称> <监控间隔时间 (秒) >")
        sys.exit(1)

    interface_name = sys.argv[1]
    try:
        interval = int(sys.argv[2])
        if interval <= 0:
            raise ValueError("监控间隔时间必须为正整数! ")
    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)

    monitor_network(interface_name, interval)




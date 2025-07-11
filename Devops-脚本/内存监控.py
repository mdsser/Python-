import psutil
import time

def memory_monitor(thereshold=85,interval=5):
    while True:
        mem_usage = psutil.virtual_memory().percent
        if mem_usage > thereshold:
            print(f"Memory usage is {mem_usage}%")
        else:
            print(f"内存正常：{mem_usage}%")
        time.sleep(interval)

if __name__ == '__main__':
    memory_monitor(thereshold=85)
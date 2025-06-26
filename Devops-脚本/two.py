import re
from collections import defaultdict



def analyze_log(log_file):
    error_counts = defaultdict(int)
    ip_counts = defaultdict(int)

    with open(log_file, 'r') as f:
        for line in f:
            # 统计错误类型
            error_match = re.search(r'ERROR|WARNING|CRITICAL', line)
            if error_match:
                error_type = error_match.group()
                error_counts[error_type] += 1

            # 统计IP访问
            ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', line)
            if ip_match:
                ip = ip_match.group()
                ip_counts[ip] += 1

    print("=== 错误统计 ===")
    for error, count in error_counts.items():
        print(f"{error}: {count}次")

    print("\n=== 访问IP统计 ===")
    for ip, count in sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"{ip}: {count}次")


if __name__ == "__main__":
    log_file = input("请输入日志文件路径: ")
    analyze_log(log_file)
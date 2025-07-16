# 统计各类错误码出现次数


import re
from collections import defaultdict

def analyze_nginx_errors(log_file):
    error_counts = defaultdict(int)

    with open(log_file) as f:
        for line in f:
            match = re.search(r'HTTP/1.\d" (\d{3})', line)
            if match:
                status = match.group(1)
                if status.startswith(('4', '5')):
                    error_counts[status] += 1

    print("Nginx错误统计:")
    for code,count in sorted(error_counts.items()):
        print(f" HTTP {code}: {count}次")



if __name__ == '__main__':
    analyze_nginx_errors("/var/log/nginx/error.log")
import re


def validate_ip(ip):
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    match = re.match(pattern, ip)
    if not match:
        return False

    # 检查每个数字段是否在0-255之间
    for group in match.groups():
        if not 0 <= int(group) <= 255:
            return False
    return True


# 测试用例
test_ips = ["192.168.1.1", "256.0.0.1", "10.10.10.10"]
for ip in test_ips:
    print(f"{ip}: {'Valid' if validate_ip(ip) else 'Invalid'}")

# 输出：
# 192.168.1.1: Valid
# 256.0.0.1: Invalid
# 10.10.10.10: Valid
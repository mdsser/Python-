import socket
import concurrent.futures


def check_port(host, port, timeout=2):
    """检查指定端口是否开放"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False


def port_scanner(host, ports):
    """
    批量扫描主机端口
    :param host: 目标主机
    :param ports: 端口列表
    """
    print(f"扫描 {host} 的端口状态...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(check_port, host, port): port for port in ports}

        for future in concurrent.futures.as_completed(futures):
            port = futures[future]
            try:
                if future.result():
                    print(f"🟢 端口 {port} 开放")
            except Exception as e:
                print(f"❌ 扫描 {port} 出错: {str(e)}")


# 扫描常见服务端口
common_ports = [21, 22, 80, 443, 3306, 6379, 8080]
port_scanner("192.168.1.100", common_ports)
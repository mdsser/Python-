import ssl
import socket
import datetime
import argparse


def check_ssl_expiry(hostname, port=443):
    """检查SSL证书过期时间"""
    context = ssl.create_default_context()

    try:
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        # 解析证书有效期
        expire_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        days_left = (expire_date - datetime.datetime.utcnow()).days

        print(f"域名: {hostname}")
        print(f"颁发给: {cert['subject'][0][0][1]}")
        print(f"颁发者: {cert['issuer'][0][0][1]}")
        print(f"过期时间: {expire_date.strftime('%Y-%m-%d')}")
        print(f"剩余天数: {days_left} 天")

        # 证书过期预警
        if days_left < 30:
            print(f"⚠️ 警告: 证书将在 {days_left} 天后过期!")
            return False
        return True

    except ssl.SSLError as e:
        print(f"❌ SSL错误: {str(e)}")
        return False
    except socket.gaierror:
        print(f"❌ 域名解析失败: {hostname}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SSL证书检查工具")
    parser.add_argument("domain", help="要检查的域名")
    parser.add_argument("--port", type=int, default=443, help="HTTPS端口")
    args = parser.parse_args()

    check_ssl_expiry(args.domain, args.port)
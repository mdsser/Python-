# 使用 Python 编写脚本。
# 使用 subprocess 模块来执行系统命令。
# 输入参数：服务器的 IP 地址和端口号。
# 输出：每一步操作的结果。
'''
检查服务器上是否已安装 nginx。
如果未安装 nginx，则安装。
下载并配置一个简单的 Web 应用静态文件。
启动 nginx 服务。
'''


import subprocess
import sys

def run_cmd(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        print(f"成功: {result.stdout.decode()}")
        return result.stdout.decode()
    except subprocess.CalledProcessError as e:
        print(f"错误: {e.stderr.decode()}")
        return e.stderr.decode()

def is_nginx_installed():
    output = run_cmd("which nginx")
    # 返回相关nginx字段在which nginx中
    return 'nginx' in output

def install_nginx():
    run_cmd("sudo yum update")
    run_cmd("sudo yum -y install nginx")

def download_web_app():
    run_cmd("sudo mkdir -p /var/www/html/myapp")
    run_cmd("sudo wget -O /var/www/html/myapp/index.html http://example.com/index.html")

def configure_nginx():
    config = """
    server {
        listen 80;
        server_name localhost;
        root /var/www/html/myapp;
        index index.html;
    }
    """
    with open("/etc/nginx/sites-available/myapp", "w") as config_file:
        config_file.write(config)
        run_cmd("sudo ln -s /etc/nginx/site-available/myapp /etc/nginx/sites-enabled/")
        run_cmd("sudo nginx -t")
        run_cmd("sudo systemctl restart nginx")


def main():
    print(f"正在检查 {server_ip}:{port} 上的nginx 安装情况...")
    if not is_nginx_installed():
        print("nginx 未安装, 正在安装...")
        install_nginx()

    print(f"正在下载并配置 Web应用到 {server_ip}:{port}...")
    download_web_app()
    configure_nginx()
    print("部署完成")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("用法: python script.py <服务器IP> <端口号>")
        sys.exit(1)

    server_ip = sys.argv[1]
    port = sys.argv[2]
    main(server_ip, port)
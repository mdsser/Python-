import os
import subprocess
from typing import List


def batch_deploy_redis(
        local_tar: str,
        server_list: List[str],
        repo_name: str = "redis",
        tag: str = "7.4.6",
        target_image_id: str = "bdb47db47a6a",
        log_file: str = "redis_deploy_log.txt"
) -> None:
    """
    批量传输redis镜像并执行部署流程：
    1. 传输tar包到远程服务器
    2. 加载镜像
    3. 为指定镜像ID打标签
    4. 删除远程tar包
    """
    # 检查本地tar包是否存在
    if not os.path.isfile(local_tar):
        print(f"错误：本地文件 {local_tar} 不存在！")
        return

    # 初始化日志
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("Redis镜像批量部署日志\n")
        f.write("=" * 60 + "\n")

    # 遍历服务器列表
    for server in server_list:
        if not server.strip():
            continue

        print(f"\n===== 开始处理服务器：{server} =====")
        log_msg = f"服务器: {server}\n"
        success = True

        # 1. SCP传输文件
        try:
            scp_cmd = ["scp", local_tar, f"{server}:/root/"]
            subprocess.run(
                scp_cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"1. 文件传输成功")
            log_msg += "1. 文件传输: 成功\n"
        except Exception as e:
            print(f"1. 文件传输失败: {str(e)}")
            log_msg += f"1. 文件传输: 失败\n错误: {str(e)}\n"
            success = False

        # 2. 加载镜像（仅当传输成功）
        if success:
            try:
                # 构建SSH命令：加载镜像
                load_cmd = f"ssh {server} 'docker load -i /root/redis7.tar.gz'"
                subprocess.run(
                    load_cmd,
                    shell=True,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print(f"2. 镜像加载成功")
                log_msg += "2. 镜像加载: 成功\n"
            except Exception as e:
                print(f"2. 镜像加载失败: {str(e)}")
                log_msg += f"2. 镜像加载: 失败\n错误: {str(e)}\n"
                success = False

        # 3. 修改标签（仅当加载成功）
        if success:
            try:
                # 构建SSH命令：打标签
                tag_cmd = f"ssh {server} 'docker tag {target_image_id} {repo_name}:{tag}'"
                subprocess.run(
                    tag_cmd,
                    shell=True,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print(f"3. 镜像标签修改成功（{repo_name}:{tag}）")
                log_msg += f"3. 标签修改: 成功（{repo_name}:{tag}）\n"
            except Exception as e:
                print(f"3. 标签修改失败: {str(e)}")
                log_msg += f"3. 标签修改: 失败\n错误: {str(e)}\n"
                success = False

        # 4. 删除远程tar包（无论前面是否成功，尽量清理）
        try:
            rm_cmd = f"ssh {server} 'rm -f /root/redis7.tar.gz'"
            subprocess.run(
                rm_cmd,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"4. 远程tar包已删除")
            log_msg += "4. 清理文件: 成功\n"
        except Exception as e:
            print(f"4. 删除远程tar包失败: {str(e)}")
            log_msg += f"4. 清理文件: 失败\n错误: {str(e)}\n"

        # 记录最终状态
        final_status = "成功" if success else "失败"
        print(f"===== 服务器 {server} 处理{final_status} =====")
        log_msg += f"最终状态: {final_status}\n"
        log_msg += "-" * 60 + "\n"

        # 写入日志
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_msg)

    print(f"\n所有服务器处理完毕，详细日志见 {log_file}")


if __name__ == "__main__":
    # 配置参数（根据实际情况修改服务器列表）
    LOCAL_TAR_PATH = "/root/redis7.tar.gz"  # 本地镜像tar包路径
    SERVER_LIST = [
        "192.168.1.101",  # 示例服务器1（默认用户）
        "admin@192.168.1.102",  # 示例服务器2（指定用户）
        "user@192.168.1.103:2222"  # 示例服务器3（指定用户和端口）
    ]
    TARGET_IMAGE_ID = "bdb47db47a6a"  # 原始镜像ID
    REPOSITORY = "redis"  # 目标仓库名
    TAG = "7.4.6"  # 目标标签

    # 执行批量部署
    batch_deploy_redis(
        local_tar=LOCAL_TAR_PATH,
        server_list=SERVER_LIST,
        repo_name=REPOSITORY,
        tag=TAG,
        target_image_id=TARGET_IMAGE_ID
    )
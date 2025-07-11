#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shutil
import sys


def check_disk_usage(partition="/", threshold=80):
    """
    检查磁盘空间使用情况
    :param partition: 要检查的分区，默认为根分区
    :param threshold: 警告阈值百分比，默认为80%
    :return: 无返回值，直接打印警告信息
    """
    # 获取磁盘使用情况
    usage = shutil.disk_usage(partition)

    # 计算使用百分比
    percent_used = (usage.used / usage.total) * 100

    # 打印当前使用情况
    print(f"分区 {partition} 使用情况:")
    print(f"总空间: {usage.total / (1024 ** 3):.2f} GB")
    print(f"已使用: {usage.used / (1024 ** 3):.2f} GB")
    print(f"剩余空间: {usage.free / (1024 ** 3):.2f} GB")
    print(f"使用率: {percent_used:.2f}%")

    # 检查是否超过阈值
    if percent_used > threshold:
        print(f"警告: {partition} 分区使用率超过 {threshold}%!")
        sys.exit(1)  # 返回非0状态码，可用于监控系统告警
    else:
        print("磁盘空间正常")
        sys.exit(0)


if __name__ == "__main__":
    # 可以传入参数来检查不同分区或设置不同阈值
    # 例如: python script.py / 90
    partition = sys.argv[1] if len(sys.argv) > 1 else "/"
    threshold = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    check_disk_usage(partition, threshold)
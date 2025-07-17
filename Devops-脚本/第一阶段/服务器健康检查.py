import psutil
import platform
import datetime


def server_health_check():
    """综合服务器健康检查"""
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "hostname": platform.node(),
        "status": "OK",
        "checks": []
    }

    # 1. CPU检查
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_status = "OK" if cpu_usage < 80 else "WARNING"
    report["checks"].append({
        "name": "CPU使用率",
        "value": f"{cpu_usage}%",
        "status": cpu_status
    })

    # 2. 内存检查
    mem = psutil.virtual_memory()
    mem_status = "OK" if mem.percent < 85 else "WARNING"
    report["checks"].append({
        "name": "内存使用率",
        "value": f"{mem.percent}%",
        "status": mem_status
    })

    # 3. 磁盘检查
    for part in psutil.disk_partitions():
        if part.mountpoint == "/":  # 只检查根分区
            usage = psutil.disk_usage(part.mountpoint)
            disk_status = "OK" if usage.percent < 90 else "WARNING"
            report["checks"].append({
                "name": f"磁盘使用率 ({part.mountpoint})",
                "value": f"{usage.percent}%",
                "status": disk_status
            })

    # 4. 进程检查
    critical_processes = ["nginx", "mysql", "sshd"]
    for proc in critical_processes:
        running = any(proc in p.name() for p in psutil.process_iter(['name']))
        status = "OK" if running else "CRITICAL"
        report["checks"].append({
            "name": f"进程运行: {proc}",
            "value": "运行中" if running else "未运行",
            "status": status
        })

    # 总体状态评估
    if any(check["status"] == "CRITICAL" for check in report["checks"]):
        report["status"] = "CRITICAL"
    elif any(check["status"] == "WARNING" for check in report["checks"]):
        report["status"] = "WARNING"

    # 打印报告
    print("\n===== 服务器健康检查报告 =====")
    print(f"服务器: {report['hostname']}")
    print(f"时间: {report['timestamp']}")
    print(f"总体状态: {report['status']}")

    for check in report["checks"]:
        status_icon = "✅" if check["status"] == "OK" else "⚠️" if check["status"] == "WARNING" else "❌"
        print(f"{status_icon} {check['name']}: {check['value']}")

    return report


if __name__ == "__main__":
# 执行全面检查
    server_health_check()
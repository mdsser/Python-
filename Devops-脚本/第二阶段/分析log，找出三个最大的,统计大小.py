import os

def analyze_logs(directory="/var/log"):
    log_files = []
    total_size = 0

    # 遍历目录收集日志文件
    for root,dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".log"):
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                log_files.append((file_path, size))
                total_size += size

    log_files.sort(key=lambda x: x[1], reverse=True)
    top_files = log_files[:3]

    # 转换大小为MB
    total_size_mb = total_size / (1024*1024)

    print(f"日志目录分析结果: {directory}")
    print(f"发现 {len(log_files)} 个日志文件,总大小：{total_size_mb:.2f} MB\n")

    print("最大的3个日志文件")
    for i, (file, size) in enumerate(top_files, 1):
        size_mb = size / (1024*1024)
        print(f"{i}. {file} - {size_mb:.2f} MB")

    return {
        "total_files": len(log_files),
        "total_size": total_size,
        "top_files": top_files
    }

if __name__ == '__main__':
    analyze_logs()
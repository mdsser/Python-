import difflib
import os

def compare_configs(file1,file2):
    with open(file1, 'r') as f1,open(file2, 'r') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    diff = difflib.unified_diff(
        lines1,lines2,
        fromfile=os.path.basename(file1),
        tofile=os.path.basename(file2),
        lineterm=''
    )

    diff_lines = list(diff)
    if not diff_lines:
        print("配置文件相同")
        return 0

    print(f"配置文件不同，以下是{len(diff_lines) - 2}差异：")
    for line in diff_lines:
        if line.startswith('+'):
            print(f"\033[92m{line}\033[0m")  # 绿色显示新增
        elif line.startswith('-'):
            print(f"\033[91m{line}\033[0m")  # 红色显示删除
        else:
            print(line)

    return len(diff_lines) - 2  # 减去头部的3行说明


if __name__ == '__main__':
    print("请输入两个配置文件的路径：")
    file1 = input()
    file2 = input()
    compare_configs(file1,file2)
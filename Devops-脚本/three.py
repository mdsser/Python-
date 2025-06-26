import os

def get_dir_size(path):
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_dir_size(entry.path)
    return total

if __name__ == '__main__':
    path = input("请输入目录路径: ")
    size = get_dir_size(path)
    print(f"目录大小: {size/1024:.2f} KB")
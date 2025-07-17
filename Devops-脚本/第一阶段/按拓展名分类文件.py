import os
import shutil

def organize_files(directory):
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            # 获取文件扩展名
            ext = os.path.splitext(filename)[1]
            # 根据扩展名分类文件
            if not ext:
                ext = "no_extention"

            # 创建分类目录
            target_dir = os.path.join(directory, filename)
            os.makedirs(target_dir, exist_ok=True)

            # 移动文件
            src = os.path.join(directory, filename)
            dst = os.path.join(target_dir, filename)
            shutil.move(src, dst)
            print(f"移动: {filename} => {target_dir}")

if __name__ == '__main__':
    organize_files("/home/user/Downloads/")
    print("文件分类完成! ")
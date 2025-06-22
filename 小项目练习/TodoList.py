import os

# 文件路径
TODO_FILE = "todo_list.txt"


# 显示菜单
def show_menu():
    print("\n=== Todo List ===")
    print("1. 查看任务")
    print("2. 添加任务")
    print("3. 删除任务")
    print("4. 退出")
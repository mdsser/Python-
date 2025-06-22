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


# 读取任务
def read_tasks():
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, 'r') as file:
        tasks = file.readlines()
    return [task.strip() for task in tasks]


# 保存任务
def save_tasks(tasks):
    with open(TODO_FILE, 'w') as file:
        for task in tasks:
            file.write(f"{task}\n")


# 添加任务
def add_task():
    task = input("请输入新任务： ")
    tasks = read_tasks()
    tasks.append(task)
    save_tasks(tasks)
    print(f"任务 '{task}' 已添加。")


# 查看任务
def view_tasks():
    tasks = read_tasks()
    if not tasks:
        print("当前没有任务。")
    else:
        print("\n=== 当前任务 ===")
        for i, task in enumerate(tasks, start=1):
            print(f"{i}. {task}")


# 删除任务
def delete_task():
    tasks = read_tasks()
    if not tasks:
        print("当前没有任务可删除。")
        return

    view_tasks()
    try:
        task_num = int(input("请输入要删除的任务编号： "))
        if 1 <= task_num <= len(tasks):
            removed_task = tasks.pop(task_num - 1)
            save_tasks(tasks)
            print(f"任务 '{removed_task}' 已删除。")
        else:
            print("无效的任务编号。")
    except ValueError:
        print("请输入有效的数字。")


# 主程序
def main():
    while True:
        show_menu()
        choice = input("请选择操作（1-4）： ")

        if choice == '1':
            view_tasks()
        elif choice == '2':
            add_task()
        elif choice == '3':
            delete_task()
        elif choice == '4':
            print("退出程序。")
            break
        else:
            print("无效选择，请重试。")


if __name__ == "__main__":
    main()

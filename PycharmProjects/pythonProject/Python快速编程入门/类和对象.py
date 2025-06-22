class Car:
    #移动
    def move(self):
        print("车在奔跑...")
    def toot(self):
        print("车在鸣笛...嘟嘟...")

#创建一个对象，并用变量jeep保存它的引用
jeep = Car()

#添加表示颜色的属性
jeep.color = "黑色"

#调用方法
jeep.move()
jeep.toot()

#访问属性
print(jeep.color)
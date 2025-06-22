#定义表示战士、敌人的类
class Person:
    def __init__(self, name):
        # 姓名
        self.name = name
        # 血量
        self.blood = 100

# 给弹夹安装子弹
def install_bullet(self, clip , bullet):
    # 弹夹放置子弹
    clip.save_bullets(bullet)

#定义表示弹夹的类
class Clip:
    def __init__(self,capacity):
        # 最大容量
        self.capacity = capacity
        # 当前子弹数
        self.bullets = []

    # 安装子弹
    def save_bullets(self, bullet) :
        # 当前子弹数量小于最大容量
        if len(self.bullets) < self.capacity :
            self.bullets.append(bullet)

    def __str__(self):
        return "弹夹当前的子弹数量为： " + str(len(self.current_list)) + "/" + str(self.capacity)

# 定义子弹类型
class Bullet:
    pass

# 验证安装子弹的功能
# 创建一个战士
soldier = Person("老王")

# 创建一个弹夹
clip = Clip(20)
print(clip)

# 添加5颗子弹
i = 0
while i < 5:
    # 创建一个子弹
    bullet = Bullet()
    # 战士安装子弹到弹夹
    soldier.install_bullet(clip,bullet)
    i += 1

# 输出当前弹夹中子弹的数量
print(clip)
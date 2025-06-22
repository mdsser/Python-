# 请利用@property给一个Screen对象加上
# width和height属性，以及一个只读属性
# resolution：
class Screen(object):
    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, w):
        self._width = w

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, w):
        self._height = w

    @property
    def resolution(self):
        return self._width * self._height



# 测试:
s = Screen()
s.width = 1024
s.height = 768
print('resolution =', s.resolution)
if s.resolution == 786432:
    print('测试通过!')
else:
    print('测试失败!')
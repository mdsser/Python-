# # 迭代器版
# cars = iter(['奥迪', '宝马', '奔驰'])
# print(next(cars))
# print(next(cars))
# print(next(cars))
# print(next(cars))

# 生成器版
def 造车():
    yield '特斯拉'
    yield '比亚迪'
car_gen = 造车()
print(next(car_gen))
print(next(car_gen))
print(next(car_gen))
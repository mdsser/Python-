#编写一个生成器函数 square_generator，
# 生成从 1 到 10 的数字的平方值。
# 每次调用 next()，生成下一个平方。
#例子：1, 4, 9, 16, ..., 100。
def square_generator():
    for i in range(1,11):
        yield i * i

for square in square_generator():
    print(square)
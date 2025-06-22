fruits = ["苹果", "香蕉", "橙子"]
fruit_iter = iter(fruits)  # 通过 iter() 把列表变成迭代器

print(next(fruit_iter))  # 输出 "苹果"
print(next(fruit_iter))  # 输出 "香蕉"
print(next(fruit_iter))  # 输出 "橙子"
print(next(fruit_iter))
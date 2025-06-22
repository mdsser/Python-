# 创建一个迭代器类 InfiniteNumbers，
# 可以无限生成自然数序列（1, 2, 3, 4...）。
# 这个迭代器应该在调用 next() 时生成下一个数字，
# 而不会有停止点。
#提示：这是一个无穷迭代器，所以不会有 StopIteration。
class InfiniteNumbers:
    def __init__(self):
        self.num = 1
    def __iter__(self):
        return self

    def __next__(self):
        current = self.num
        self.num += 1
        return current

infinite_iter = InfiniteNumbers()
for num in infinite_iter:
    print(num)
    if num > 10:
        break
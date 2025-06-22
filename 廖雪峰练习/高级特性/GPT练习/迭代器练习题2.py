# 自定义迭代器 - 倒序输出
#
# 创建一个迭代器类 ReverseIterator，
# 这个迭代器可以从一个列表的最后一个元素开始，
# 依次返回前面的元素，直到第一个元素。
# 例子：[1, 2, 3] 会依次返回 3, 2, 1

class ReverseIterator:
    def __init__(self, lst):
        self.lst = lst
        self.index = len(lst)
    
    def __iter__(self):
        return self

    def __next__(self):
        if self.index > 0:
            self.index -= 1
            return self.lst[self.index]
        else:
            raise StopIteration

nums = [1, 2, 3]
reverse_iter = ReverseIterator(nums)
for num in reverse_iter:
    print(num)
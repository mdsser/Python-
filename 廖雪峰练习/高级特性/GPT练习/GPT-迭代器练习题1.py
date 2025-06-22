class Counter():
    def __init__(self):
        self.num = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.num <= 10:
            current = self.num
            self.num += 1
            return current
        else:
            raise StopIteration

Counter = Counter()
for num in Counter:
    print(num)
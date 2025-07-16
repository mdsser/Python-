class NaturalNumber:
    def __init__(self,n):
        self.n = n
        self.current = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.n:
            raise StopIteration
        value = self.current
        self.current += 1
        return value


natural_iter = NaturalNumber(5)
for num in natural_iter:
    print(num,end=' ')
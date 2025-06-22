import operator

s1 = 72
s2 = 85
r = ((s2-s1)/s1) *100
print(f'小明的成绩相比去年提升了{r:.2f}%')

s1 = 122
s2 = 100
s3 = s2 - s1
print(s3)

tuple1 = (50,)
type(tuple1)
print(type(tuple1))

# tinydict = {['Name']: 'Runoob', 'Age': 7}

# print("tinydict['Name']: ", tinydict['Name'])

'''
这个是一段注释，你可以在这里写任何你想说的话。
'''

name = 'Runoob'
print(f'Hello, {name}!')


a = [1, 2]
b = [2, 3]
c = [3, 4]
print("operate.eq(a,b): ",operator.eq(a,b))
print("operate.eq(c,b): ",operator.eq(c,b))

#
# thisset = set(("Google", "Runoob", "Taobao"))
# thisset.add("Facebook")
# print(thisset)
# {'Taobao', 'Facebook', 'Google', 'Runoob'}

def test(a , b, *args):
    print(a)
    print(b)
    print(args)

test(11,22)

# def print_log(func):
#     print('函数正在运行中')
#     func ()
# def test():
#     print('test')
# print_log(test)

def wrap(func):
    print('正在装饰')
    def inner():
        print('正在验证权限')
        func()
    return inner
@wrap
def test():
    print('test')
test()

# list = [1,2,3,4]
# it = iter(list)
# print(next(it))

# index_error = IndexError()
# raise index_error

# raise IndexError("索引下表超出范围")

for i in range(1,10):
    for j in range(1, i+1):
        print('{}*{}={}\t'.format(j,i,i*j),end='')
    print()

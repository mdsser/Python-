# def wrap_one(func):
#     print('--正在装饰1--')
#     def inner():
#         print('--正在验证权限1--')
#         func()
#     return inner
#
# def wrap_two(func):
#     print('--正在装饰2--')
#     def inner():
#         print('--正在验证权限2--')
#         func()      # =test
#     return inner
#
# @wrap_one       #test = wrap_one(test)
# @wrap_two       #test = wrap_two(test)
# def test():
#     print('---test---')
#
# test()

def wrap(func):
    def inner(a, b):
        print('开始验证权限')
        func(a,b)
    return inner

@wrap       #test = wrap(test)
def test(a,b):
    print('a=%d,b=%d'%(a,b))

test(1,2)

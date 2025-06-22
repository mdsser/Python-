import time, functools

def metric(fn):
    def wrapper(* args, **kargs):
        start_time = time.time()
        result = fn(*args, **kargs)
        end_time = time.time()
        executed_time = end_time - start_time
        print(f'程序{fn.__name__}的执行时间为: {executed_time}')
        return result
    return wrapper

# 测试
@metric
def fast(x, y):
    time.sleep(0.0012)
    return x + y;

@metric
def slow(x, y, z):
    time.sleep(0.1234)
    return x * y * z;

f = fast(11, 22)
s = slow(11, 22, 33)
if f != 33:
    print('测试失败!')
elif s != 7986:
    print('测试失败!')
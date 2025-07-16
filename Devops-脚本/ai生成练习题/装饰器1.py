# 练习题代码
def log_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling function {func.__name__} with arguments {args} and {kwargs}")
        result = func(*args, **kwargs)
        print(f"Function {func.__name__} returned {result}")
        return result
    return wrapper

@log_decorator
def add(x, y):
    return x + y

# 使用示例
add(3, 5)
# 输出:
# Calling function add with arguments (3, 5) and {}
# Function add returned 8

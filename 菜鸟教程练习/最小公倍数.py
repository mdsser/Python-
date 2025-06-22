print("请输入两个正整数")
m = int(input())
n = int(input())
x = m * n
print(f'{m}和{n}的最小公倍数是：',end='')
r = m % n
while r != 0:
    m = n
    n = r
    r = m % n
print(x // n)
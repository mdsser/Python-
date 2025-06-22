print("请输入两个正整数")
m = int(input())
n = int(input())
x = m * n
print(f"{m}和{n}的最小公倍数是: ", end='')
while m != n:
    if m > n:
        m = m - n
    else:
        n = n - m
print(x // m)
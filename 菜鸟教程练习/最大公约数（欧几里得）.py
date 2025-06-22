n, m = map(int, input().split(" "))
a = max(m, n)
b = min(m, n)
t = a % b
while t !=0:
    a = b
    b = t
print(f'最大公约数是:{b}')
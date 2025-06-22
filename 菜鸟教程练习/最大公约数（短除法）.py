n, m = map(int, input().split(" "))
t = 1
for i in range(2, min(n, m)):
    while n % i == 0 and m % i == 0:
        t = t * i
        n = n / i
        m = m / i
print(f"最大公约数为：{t}")
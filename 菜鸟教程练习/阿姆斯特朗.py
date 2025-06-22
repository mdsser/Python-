#153 = 1^3 + 5^3 + 3^3
num = int(input("请输入一个数字"))

sum = 0

n = len(str(num))

temp = num

while temp > 0:
    digit = temp % 10
    sum += digit ** n
    temp = temp // 10

if num == sum:
    print(num, "是阿姆斯特朗数")

else:
    print(num, "不是阿姆斯特朗数")


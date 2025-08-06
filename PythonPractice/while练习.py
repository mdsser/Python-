# i = 0
# while i<100:
#     print("向小美表白的第i次",i)
#     i += 1
import turtle

# 通过while循环，计算从1累加到100的和
# i=1
# num=0
# while i<=100:
#
#     num=i+num
#     i+=1
# print("从1累加到100的和为:num",num)



# 1-100猜数字，无限次机会，每次提示猜大或猜小，并在结束之后提示一共多少次
import random
num=random.randint(1,100)
count = 0
flag = True
while flag:
    guess_num = int(input("请输入你要猜测的数字:"))
    count += 1
    if guess_num == num:
        print("猜中了")
        flag = False
    else:
        if guess_num > num:
            print("你猜的大了")
        else:
            print("你猜的小了")

print(f"你总共猜测了{count}次")


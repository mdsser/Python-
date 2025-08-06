import random
num = random.randint(1,10)

guess_num = int(input("请输入你想要猜的数字:"))

if guess_num == num:
    print("恭喜你,你第一次就猜中了")
else:
    if guess_num > num:
        print("你猜测的数字大了")
    else:
        print("你猜测的数字小了")

    guess_num = int(input("第二次输入你要猜测的数字:"))

    if guess_num == num:
        print("恭喜你,你第二次就猜中了")
    else:
        if guess_num > num:
            print("你猜测的数字大了")
        else:
            print("你猜测的数字小了")

        guess_num = int(input("第三次输入你要猜测的数字:"))

        if guess_num == num:
            print("恭喜你,你第三次就猜中了")
        else:
            print("抱歉，您已经没有机会了")
# int shuzi = int(input(请输入你想猜的数字):)

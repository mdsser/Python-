
num = 5


if int(input("请猜一个数字: ")) == num:
    print("恭喜第一次就猜对了吧")
elif int(input("猜错了，再猜一次")) == num:
    print("猜对了")
elif int(input("猜错了，再猜一次")) == num:
    print("恭喜，最后一次机会，你猜对了")
else:
    print("Sorry：猜错了")
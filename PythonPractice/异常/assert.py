while True:
    try:
        x = int(input('请输入第一个数：'))
        y = int(input('请输入第二个数：'))
        assert x > 1 and y > 1, "a和b的值必须大于1"
        a = x
        b = y
        if a < b:
            a, b = b, a   # a = 55 b = 15
        while b!=0:
            temp = a % b #temp = 10 a = 15 b = 10 temp = 5 a = 10 b = 5 temp = 0 a = 5 b = 0
            a = b
            b = temp
        else:
            print('%s和%s的最大公约数为： %s'%(x, y, a))
            break
    except Exception as result:
        print('捕捉到异常：%s \n', result)
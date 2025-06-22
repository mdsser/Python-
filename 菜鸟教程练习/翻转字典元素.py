def dictionairy():
    key_value={}

    # 初始化
    key_value[2] = 56
    key_value[1] = 2
    key_value[5] = 12
    key_value[4] = 24
    key_value[6] = 18
    key_value[3] = 323

    print("按键(key)排序:")

    for i in sorted (key_value):
        print((i, key_value[i]), end = " ")


def main():
    dictionairy()


if __name__ == '__main__':
    main()
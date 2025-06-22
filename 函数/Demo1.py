# name = "zhoule"
# length = len(name)
# print(length)

# None用于if判断
def check_age(age):

    if age>18:
        return "SUCCESS"
    else:
        return None

result = check_age(17)
if not result:
    print("未成年，不许进入")
name = None


""
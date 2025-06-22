import random

offices = [[],[],[]]

names = ['A','B','C','D','E','F','G','H']

for name in names:
    index = random.randint(0,2)
    offices[index].append(name)

i = 1
for temp in offices:
    print('办公室%d的人数为：%d'%(i, len(temp)))
    i += 1
    for name in temp:
        print("%s"%name,end='')
    print("-"*20)
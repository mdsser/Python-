def search(arr, n, x):
    for i in range(0, n):
        if(arr[i] == x):
            return True
    return -1




arr = ['A', 'B', 'C', 'D', 'E']
x = 'D'
n = len(arr)
result = search(arr, n, x)
if(result == -1):
    print('Not Found')
else:
    print("元素在数组中的索引为",result)

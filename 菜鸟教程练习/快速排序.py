def partition(arr, low, high):
    # pivot = arr[low]
    # while low <= high:
    #     while arr[high] >= pivot:
    #         high -= 1
    #         arr[low] = arr[high]
    #     while arr[low] <= pivot:
    #         low += 1
    #         arr[high] = arr[low]
    # arr[low] = pivot
    # return low

    i = (low - 1)
    pivot = arr[high]
    for j in range(low, high):
        if arr[j] <= pivot:
            i = i+ 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i+1], arr[high] = arr[high],arr[i+1]
    return (i + 1)

def quickSort(arr,low,high):
    if low < high:
        pi = partition(arr, low, high)
        quickSort(arr, low, pi-1)
        quickSort(arr, pi+1, high)


arr = [10, 7, 8, 9, 1, 5]
n =len(arr)
quickSort(arr, 0, n-1)
print("排序后的数组：")
for i in range(n):
    print("%d"%arr[i], end=" ")

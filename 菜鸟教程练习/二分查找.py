def binary_search(alist, data):
    n = len(alist)
    first = 0
    last = n - 1
    while first <= last:
        mid = (first + last) // 2
        if alist[mid] > data:
            last = mid - 1
        elif alist[mid] < data:
            first = mid + 1
        else:
            return True
    return False

list = [2, 4, 5, 12, 16, 23]
if binary_search(list, 16):
    print("OK")
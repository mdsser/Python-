import sys
A = [64, 25, 12, 22, 11]

for i in range(len(A)):

    mid_idx = i
    for j in range(i+1, len(A)):
        if A[mid_idx] > A[j]:
            mid_idx = j

    A[i], A[mid_idx] = A[mid_idx], A[i]


print("排序后的数组：")
for i in range(len(A)):
    print("%d"%A[i], end=" ")
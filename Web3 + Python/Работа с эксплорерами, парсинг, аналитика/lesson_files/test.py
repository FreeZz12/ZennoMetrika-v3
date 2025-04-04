my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10]

for i in range(len(my_list) - 1, -1, -1):
    if my_list[i] == 9:
        my_list = my_list[:i]
        break

print(my_list)

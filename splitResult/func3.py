import math

def func3(lst):
    for i in range(len(lst)-1, -1, -1):
        if lst[i]<0 or lst[i]%3==0:
            lst.remove(lst[i])
    lst.sort(reverse=True)
    return lst


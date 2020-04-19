import math

def func2(a,b):
    if a<=0 or b<=0:
        return
    if a>b:
        t=a
        a=b
        b=t
    s = 0
    for i in range(a,b+1):
        n = i
        x = int(math.log10(i))+1
        h = 0
        for j in range(x):
            h = h * 10 + n%10
            n = n // 10
        if h == i:
            s = s + 1
    return s
            


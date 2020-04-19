import math

def func1(a,b):
    if a<=0 or b<=0:
        return
    if a>b:
        t=a
        a=b
        b=t
    p=1
    for i in range(a,b+1):
        p = p * i
    s=0
    while p%10==0:
        s = s + 1
        p = p // 10    
    return s


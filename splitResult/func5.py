import math

def func5(inputName,outputName):
    fp=open(inputName,"r")
    lines=fp.readlines()
    fp.close()
    data=[int(item[:-1]) for item in lines]
    data.sort(reverse=True)
    fp=open(outputName,"w")
    for item in data:
        fp.write(str(item)+"\n")
    fp.close()


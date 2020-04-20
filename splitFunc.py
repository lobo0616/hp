from utils import *
import re

""" 
#获取目录下所有py文件
prog_dir = "test"
py_list = get_student_py_list(prog_dir) 

#获取一个学生文件的相对路径
stu_py_name = prog_dir + "/" + py_list[3] + ".py" 
print("学生文件：",stu_py_name)
"""

def splitFunc(stu_py_file):
    f = open(stu_py_file,"r")    
    lines = f.readlines() 
    #正则表达式匹配学生写的所有的函数名
    stu_func_names = [] #存放学生的所有函数名
    for line in lines:
        pattern = '(?<=def )[a-zA-Z_]\w*(?=\()'
        s = re.compile(pattern=pattern).findall(line)
        if s:
            stu_func_names.append(s[0])

    #所有题目要求写的函数
    func_names = [] #存放题目要求写的函数
    all_func_info = get_func_info("func_info_list.txt")
    for (func_name, score, time_ratio, test_case_file_name,isFile) in all_func_info: #获取要批阅的函数名、得到多余的函数名
        func_names.append(func_name)

    #获取学生额外写的函数名
    stu_extra_func_names = []
    for i in stu_func_names:
        if i not in func_names:
            stu_extra_func_names.append(i)

    all_func_name = stu_extra_func_names + func_names

    #记录每个函数的开始行和结束行
    func_lineNum = {} #字典存储，'函数名':开始行数，结束行数
    for name in all_func_name:
        func_lineNum[name] = [0,0]

    # 逐行读取，记录函数起始行号
    count=0
    count_index = []
    for line in lines:
        count=count+1
        # 判断字符串是否包含def，作为函数分割的依据
        if "def" in line:
            for name in stu_func_names:
                if name in line and func_lineNum[name]:
                    func_lineNum[name][0]=count
                    count_index.append(count)
                else:
                    continue
        pattern = '^if .*[\'|\"]__main__[\'|\"]:$'
        s = re.compile(pattern=pattern).findall(line)
        if s:
            break

    count_index.append(count)

    for i in range(len(count_index)):
        for name in stu_func_names:
            if func_lineNum[name][0] == count_index[i]:
                func_lineNum[name][1]=count_index[i+1] - 1
            else:
                continue

    pos = dict()


    for fncname in all_func_name:
        pos.setdefault(fncname,{})['pos']=0
        pos.setdefault(fncname,{})['father']=""
        pos.setdefault(fncname,{})['content']=""

    publicStr = ""
    #函数引用和内容整理出来
    for fncname in all_func_name:
        cntWrite = 0
        publicStr = ""
        for line in lines:
            cntWrite = cntWrite + 1
            if cntWrite <  count_index[0] and fncname in func_names:
                publicStr += line
            elif cntWrite >= func_lineNum[fncname][0] and cntWrite <= func_lineNum[fncname][1]:
                pos[fncname]['content'] += line
            elif stu_extra_func_names:
                for i in stu_extra_func_names:
                    if i+"(" in line and "def" not in line:
                        pos[i]['pos']=cntWrite
                    else:
                        continue


    for fncname in stu_func_names:
        if pos[fncname]['pos']>0:
            for x in stu_func_names:
                if pos[fncname]['pos']>= func_lineNum[x][0] and pos[fncname]['pos'] <= func_lineNum[x][1]:
                    pos[fncname]['father']=x
        elif fncname in func_names:
            pos[fncname]['father']=""

    #找到最根部的引用
    def findFather(x):
        for i in stu_func_names:
            if pos[x]['father'] == i:
                if pos[i]['father'] != "" and pos[i]['content'] != "":
                    pos[x]['father'] = pos [i]['father']
                    findFather(x)


    for i in stu_func_names:
        findFather(i)

    #分割写入文件中
    for fn in func_names:
        dirf = "splitResult/" + fn + ".py"
        f = open( dirf,"w")
        f.write(publicStr)
        f.write(pos[fn]['content'])
        print("函数内容:",pos[fn]['content'])
        for extra_fn in stu_extra_func_names:
            if pos[extra_fn]['father'] == fn:
                f.write(pos[extra_fn]['content'])
                
            else:
                continue

# if __name__ == "__main__":
#     splitFunc("stuFile/1627402030.py")
    
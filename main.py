import sys   #sys.argv 是一个包含命令行参数的列表 sys.path 包含了一个 Python 解释器自动查找所需模块的路径的列表
import argparse #argparse 是python自带的命令行参数解析包，可以用来方便地读取命令行参数
import time 
import hashlib
import os

from utils import *
from my_timer import MyTimer
from splitFunc import *

max_time_for_import_one_py = 3.0  # seconds
min_time_for_run_one_func = 0.1  # seconds, sometimes time_gap_sec*time_ratio (for gold.py) is too small


def evaluate_one_py(file_path, py_name, all_func_info, stu_name, gold_funcs, verbose):
    if verbose > 0: 
        print('\nStart evaluating %s %s'%( py_name,stu_name), flush=True, file=sys.stderr)

    #打开学生文件,将每个题目分割写到不同文件夹中
    splitFunc(file_path)

    sys.path.insert(0, "splitResult/")
    prob_list = get_student_py_list("splitResult/") 

    func_scores = [] #学生每个函数得分列表
    stu_total_score = 0. #学生总得分
    func_names = []
    for one_prob in prob_list: #一个函数
        correct_case_cnt = 0.  #正确的测试用例个数
        try:
            with MyTimer(max_time_for_import_one_py): 
                this_func = get_funcs_in_one_module(one_prob, verbose) #将一个函数提取出来
        except Exception as e:
            print_a_thing_verbose_1('import module %s timeout: %s %s' % (one_prob, type(e).__name__, e), verbose)
        
        #prob_score = 0. 
       
        for (func_name, score, time_ratio, test_case_file_name ,isFile) in all_func_info: #批阅的函数名 分数  时间 测试用例文件
            if func_name == one_prob: 
                func_names.append(func_name)
                if this_func is None: #判断是否有函数
                    func_scores.append(0.)
                    print_a_thing_verbose_1('module %s does not contain func: %s' % (py_name, func_name), verbose)
                    continue
                case_lines = get_all_lines(test_case_file_name) #测试用例列表
                all_case_cnt = len(case_lines) #测试用例总个数
                gold_func = gold_funcs.get(func_name) #获取标准答案
                assert gold_func is not None
                if this_func.get(func_name) is None: 
                    case_lines = [] #如果没有相符合的函数名 测试用例文件为空
                if isFile == 0:
                    for i_input, one_input in enumerate(case_lines):#enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标 i是下标，one是数据
                        one_input_line = one_input.strip() #移除空格换行符
                        assert len(one_input_line) > 0 #检查长度
                        one_input = eval(one_input_line) #eval() 函数用来执行一个字符串表达式，并返回表达式的值（字符串转为列表）
                        one_input_for_sys = eval(one_input_line) 
                        start_time = time.time() 
                        gold_result = gold_func(*one_input) #将测试用例放入函数里执行？（数组第一个元素？）
                        end_time = time.time() 
                        time_gap_sec = end_time - start_time #执行时间
                        try:
                            with MyTimer(max(time_gap_sec * time_ratio, min_time_for_run_one_func)):
                                stu_result = this_func[func_name](*one_input_for_sys) #将测试用例放到学生函数里执行
                        except Exception as e:  #发生异常执行这一块
                            print_msg_verbose_2(py_name, func_name, i_input, '%s : %s' % (type(e).__name__, e), verbose)
                            continue
                        if gold_result is None: 
                            print(*one_input, gold_result)
                        if stu_result == gold_result: #判断学生结果和答案结果是否相等
                            correct_case_cnt += 1 #通过的正确的测试用例个数+1
                            print_msg_verbose_2(py_name, func_name, i_input, 'passed', verbose) 
                        else:
                            print_msg_verbose_2(py_name, func_name, i_input, 'failed', verbose)
                else:
                    for i_input, one_input in enumerate(case_lines):#enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标 i是下标，one是数据
                        one_input_line = one_input.strip() #移除空格换行符
                        assert len(one_input_line) > 0 #检查长度
                        start_time = time.time() 
                        one_input_line = one_input_line.split(",")
                        gold_result = gold_func(*one_input_line) #将测试用例放入函数里执行？（数组第一个元素？）
                        ll = get_all_lines(one_input_line[0])
                        gold_result = get_all_lines(one_input_line[-1])
                        #清空文件
                        empty_file_info(one_input_line[-1])
                        end_time = time.time() 
                        time_gap_sec = end_time - start_time #执行时间
                        md5_before = hashlib.md5((open(one_input_line[0]).read()).encode("utf-8")).hexdigest()
                        try:
                            with MyTimer(max(time_gap_sec * time_ratio, min_time_for_run_one_func)):
                                result = this_funcs[func_name](*one_input_line) #将测试用例放到学生函数里执行？
                                result = get_all_lines(one_input_line[-1])
                        except Exception as e:  #发生异常执行这一块
                            print_msg_verbose_2(py_name, func_name, i_input, '%s : %s' % (type(e).__name__, e), verbose)
                            continue
                        #判断是否内容有改动
                        if(hashlib.md5((open(one_input_line[0]).read()).encode("utf-8")).hexdigest() == md5_before) == False:
                            f22 = open(one_input_line[0],"w")
                            for i in ll:
                                f22.write(i)
                            f22.close()
                            result = ""
                        if gold_result is None: 
                            print(*one_input, gold_result)
                        if result == gold_result: #判断学生结果和答案结果是否相等
                            correct_case_cnt += 1 #通过的正确的测试用例个数+1
                            print_msg_verbose_2(py_name, func_name, i_input, 'passed', verbose) 
                        else:
                            print_msg_verbose_2(py_name, func_name, i_input, 'failed', verbose)
                this_func_score = score * correct_case_cnt / all_case_cnt #分数就是通过的用例/总用例
                func_scores.append(this_func_score) #函数的得分列表
                stu_total_score += this_func_score
                print_func_score_verbose_1(py_name, stu_name, func_name, score, correct_case_cnt, all_case_cnt, verbose)
            else:
                continue
    print_score_summary(py_name,stu_name, stu_total_score, func_names, func_scores)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser() #创建解析器
    argparser.add_argument('--prog_dir', default='examples/') #添加参数，学生代码文件敬爱
    argparser.add_argument('--gold_py', default='gold.py') #标准答案文件
    argparser.add_argument('--func_info_list', default='func_info_list.txt') #函数名对应的详情
    argparser.add_argument('--verbose', type=int, default=0) #输出形式
    argparser.add_argument('--student',default='student.csv')  #学生学号和姓名文件
    args, extra_args = argparser.parse_known_args() #解析参数
	#当仅获取到基本设置时，如果运行命令中传入了之后才会获取到的其他配置，不会报错；而是将多出来的部分保存起来，留到后面使用
    sys.path.insert(0, args.prog_dir) #新添加的目录会优先于其他目录被import检查
    all_func_info = get_func_info(args.func_info_list) #该函数在utils.py中，获取要评阅的函数名及分数、时间和各自的测试用例
    py_list = get_student_py_list(args.prog_dir) #该函数在utils.py中，返回没有.py后缀的学生文件列表
    gold_py = remove_py_suffix(args.gold_py.lower()) #该函数在utils.py中，lower()大写转成小写,去掉参考答案文件后缀
    gold_funcs = get_funcs_in_one_module(gold_py, args.verbose) #该函数在utils.py中，返回gold_py的函数
    assert gold_funcs is not None #assert（断言）用于判断一个表达式，在表达式条件为 false 的时候触发异常。
    with open('log.stdout-outputs', 'w') as f:
        sys.stdout = f #输出重定向
        for one_py in py_list: #学生代码文件夹
            print("学号：", one_py)
            stu_name = get_name_info(one_py,args.student) #获取相应学号的学生姓名
            print("姓名：", stu_name)
            file_path = args.prog_dir + "/" + one_py + ".py" #获取学生文件的相对路径
            evaluate_one_py(file_path, one_py, all_func_info, stu_name, gold_funcs, args.verbose) 
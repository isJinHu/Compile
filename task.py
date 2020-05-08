# -*- coding:UTF-8 -*-

code = ''
code_after_analysis = []

reserved_words = ['const', 'var', 'procedure', 'begin', 'end', 'odd', 'if',
                  'then', 'call', 'while', 'do', 'read', 'write']
bounds_or_operator = ['.', ',', ';', '(', ')',
                      '+', '-', '*', '/',
                      '=', '#', '<', '<=', '>', '>=', ':=']

class_id = 29  # id表
class_int = 30  # int表
class_float = 31  # float表
id_table = []
int_table = []
float_table = []
enter = 32  # \n 对比输出


class ID:
    def __init__(self, id, classs=''):
        self.id = id
        self.classs = classs

    # def __gt__(self, other):  # 大于
    #     return self.id > other.id

    # def __lt__(self, other):  # 小于
    #     return self.id < other.id

    def __eq__(self, other):  # 等于
        return self.id == other.id

    def __str__(self):
        return str((self.id, self.classs))


# TODO: 出错处理
def judge_num(index, num, float_flag=0, e_flag=0):
    global int_table, float_table, code_after_analysis
    num += code[index]
    index += 1
    while index < len(code) and code[index].isdigit():  # 读数字
        num += code[index]
        index += 1
    if index < len(code) and code[index] == '.' and float_flag == 0:  # 小数点
        num += code[index]
        index += 1
        # 调用本函数继续读，因为小数部分还是整数，防止再次出现小数点：float_flag
        index = judge_num(index, num, 1, e_flag)
    elif index < len(code) and (code[index] == 'e' or code[index] == 'E') and e_flag == 0:  # E
        num += code[index]
        index += 1
        # 调用本函数继续读，e后可以出现整数，防止再次出现e：e_flag
        index = judge_num(index, num, float_flag, 1)
    # 数字读完了
    else:
        if float_flag == 0 and e_flag == 0:
            if int(num) not in int_table:  # 未出现过
                int_table.append(int(num))
            code_after_analysis.append(
                (class_int, int_table.index(int(num))))  # 储存在整型常数表中序号
        else:
            if float(num) not in float_table:  # 未出现过
                float_table.append(float(num))
            code_after_analysis.append(
                (class_float, float_table.index(float(num))))  # 储存在实型常数表中序号
    return index


# 构造识别符号串的自动机
def automata():
    global code_after_analysis, id_table
    index = 0
    class_flag = 0
    while index < len(code):
        if code[index] == '{':  # 注释
            while code[index] != '}':
                index += 1
            index += 1

        elif code[index] == '\n':  # 换行 为了对比输出做特殊处理
            index += 1
            code_after_analysis.append(enter)

        elif code[index] in bounds_or_operator or code[index] == ':':  # 在界符、运算符中 或者:=特殊处理
            if code[index] == '+' or code[index] == '-':  # + -可能是数字 可能是运算符
                if index != len(code) - 1 and code[index + 1].isdigit() and code_after_analysis[-1][0] != class_int and \
                        code_after_analysis[-1][0] != class_float:  # 如果前一个不是数字且下一个是数字
                    index = judge_num(index, '')  # 识别数字
                else:  # 不是数字
                    code_after_analysis.append((bounds_or_operator.index(
                        code[index])+len(reserved_words), code[index]))
                    index += 1
            else:  # 除了+ -外的
                # >= <= := 2个字符
                if index != len(code) - 1 and code[index + 1] == '=':
                    code_after_analysis.append(
                        (bounds_or_operator.index(code[index] + '=') + len(reserved_words), code[index] + '='))
                    index += 2
                else:  # 单个字符
                    code_after_analysis.append(
                        (bounds_or_operator.index(code[index]) + len(reserved_words), code[index]))
                    index += 1

        elif code[index].isalpha():  # 标识符 字母开头 接数字、字母
            label = code[index]
            index += 1
            while index < len(code) and code[index].isalnum():
                label += code[index]
                index += 1
            if label in reserved_words:  # 是保留字
                if label == 'var':
                    class_flag = 1
                code_after_analysis.append(
                    (reserved_words.index(label), label))
            else:  # 是标识符
                if ID(label) not in id_table:  # 未出现过
                    id_table.append(ID(label, reserved_words[class_flag]))
                code_after_analysis.append(
                    (class_id, id_table.index(ID(label))))  # 储存在标识符表中的序号及类型

        elif code[index].isdigit():  # 数字
            index = judge_num(index, '')

        else:  # 其他
            index += 1


def show_result():
    lines = code.split('\n')
    index = 0
    with open(r'result.txt','a',encoding='utf-8') as f:
        for line in lines:
            print('{:<30}'.format(line), end='')
            while index < len(code_after_analysis) and code_after_analysis[index] != enter:
                print(code_after_analysis[index], end='')
                f.write(str(code_after_analysis[index]))
                index += 1
            index += 1
            print()


def show(name, content, lis):
    string=name+'如下：\n'
    print(name + '如下：')
    count = 0
    print('-----' * 25)
    string+='-----' * 25+'\n'
    for _ in range(5):
        print('{:<7}'.format(content[0])+'{:<18}'.format(content[1]), end='')
        string+=str('{:<7}'.format(content[0])+'{:<18}'.format(content[1]))
    print('\n' + '-----' * 25)
    string+='\n'+ '-----' * 25+'\n'
    for item in lis:
        print('{:<7}'.format(count)+'{:<18}'.format(str(item)), end='')
        string+=str('{:<7}'.format(count)+'{:<18}'.format(str(item)))
        count += 1
        if count % 5 == 0:
            string+='\n'
            print()
    if count % 5 != 0:
        print()
        string+='\n'
    print('-----' * 25+'\n')
    string+='-----' * 25+'\n'+'\n'
    with open(r'result.txt','a',encoding='utf-8') as f:
        f.write(string)


def main():
    global code
    path = input('请输入需要进行词法分析的程序地址：')
    # path = r'E:\Experiment\Compile\task1_test.pl0'
    with open(path, 'r', encoding='UTF-8') as f:
        code = f.read()
    automata()

    show('单词符号表', ('class', 'value'), reserved_words +
         bounds_or_operator + ['id', 'int', 'float'])
    show('标识符表', ('No', 'id'), id_table)
    show('整型常数表', ('No', 'value'), int_table)
    show('实型常数表', ('No', 'value'), float_table)
    show_result()


if __name__ == "__main__":
    main()

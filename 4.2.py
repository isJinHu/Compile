from prettytable import PrettyTable
from tkinter import _flatten
import os
import numpy as np

"""数据及其格式"""
grammar = {}
VN = []
VT = []
V = {}
sentence = ''  # i+i*i#
firstvt = {}
lastvt = {}
PM = []


# 求first follow select 构造预测分析表
def init():
    # global PM
    # ------------初始化
    for v in VN:
        firstvt[v] = None
        lastvt[v] = None
    # 求每一个非终结符的First集
    for v in VN:
        if not firstvt[v]:
            FIRSTVT(v)
        if not lastvt[v]:
            LASTVT(v)
    PM = np.empty((len(VT), len(VT)), dtype=str)
    PM.fill('')
    PM = PM.tolist()
    for key in grammar.keys():
        for lis in grammar[key]:
            if len(lis) > 1:
                for i in range(len(lis) - 1):
                    if lis[i] in VT and lis[i + 1] in VT:
                        PM[V[lis[i]]][V[lis[i + 1]]] = '='
                    if i < len(lis) - 2 and lis[i] in VT and lis[i + 2] in VT and lis[i + 1] in VN:
                        PM[V[lis[i]]][V[lis[i + 2]]] = '='
                    if lis[i] in VT and lis[i + 1] in VN:
                        for item in firstvt[lis[i + 1]]:
                            PM[V[lis[i]]][V[item]] = '<'
                    if lis[i] in VN and lis[i + 1] in VT:
                        for item in lastvt[lis[i]]:
                            PM[V[item]][V[lis[i + 1]]] = '>'

    return PM


# 求n的First集
def LASTVT(n):
    if lastvt[n]:  # 如果已经求出来了 不是None
        return lastvt[n]
    lastvt[n] = []
    # [].reverse()
    for lis in grammar[n]:  # 对于n的每一条产生式
        tmp = lis.copy()
        tmp.reverse()
        for item in tmp:
            if item in VT:
                lastvt[n].append(item)
                break
            if item in VN and item is not n:
                lastvt[n].append(LASTVT(item))
    lastvt[n] = list(set(_flatten(lastvt[n])))  # 求每条产生式First集的交集
    return lastvt[n]  # 返回First集


# 求n的First集
def FIRSTVT(n):
    global firstvt
    if firstvt[n]:  # 如果已经求出来了 不是None
        return firstvt[n]
    firstvt[n] = []
    for lis in grammar[n]:  # 对于n的每一条产生式
        for item in lis:
            if item in VT:
                firstvt[n].append(item)
                break
            if item in VN and item is not n:
                firstvt[n].append(FIRSTVT(item))
    firstvt[n] = list(set(_flatten(firstvt[n])))  # 求每条产生式First集的交集
    return firstvt[n]  # 返回First集


# 显示grammer
def show_grammar():
    strings = []
    for key in grammar.keys():
        strings.append([key + '->'])
        for lis in grammar[key]:
            strings[-1].append(''.join(lis) + '|')
        strings[-1][-1] = strings[-1][-1].replace('|', '\n')
    strings = ''.join(list(_flatten(strings)))
    return strings


def show_matrix():
    table = PrettyTable(border=False)
    table.field_names = ['VT'] + VT
    for i, lis in enumerate(PM):
        table.align = 'l'
        table.padding_width = 1
        table.add_row([VT[i]] + lis)
    return '优先矩阵:\n' + table.get_string()


# 读入语法
def main():
    """读入语法"""
    path = r'grammar2.txt'
    with open(path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    """字符串处理"""
    for line in lines:
        if line.isspace():  # 全是空白字符
            continue
        line = "".join(line.split())  # 去除空白字符
        print(line)
        l, r = line.split('->', 1)
        lis = []
        if l not in grammar:
            grammar[l] = []
        if l not in VN:
            VN.append(l)
        r = r.split('|')
        for i in r:
            for c in i:
                if not c.isupper() and c not in VT:
                    VT.append(c)
            lis.append(list(i))
        grammar[l] = grammar[l] + lis
    if 'ε' in VT:
        VT.remove('ε')


def analysis(sentence):
    stack = ['#']
    num = []
    count = 1
    idx = 0
    table = PrettyTable(border=False)
    table.field_names = ['步骤', '分析栈', '关系', '符号串', '下步动作']
    while stack:
        for i in stack[::-1]:
           if i in VT:
               break
        if PM[V[i]][V[sentence[0]]] == '<' or PM[V[i]][V[sentence[0]]] == '=':
            table.align='l'
            table.add_row([count, ''.join(stack), '<', sentence, '移进'])
            if PM[V[i]][V[sentence[0]]] == '<':
                num.append(stack.index(i)+1)
            stack.append(sentence[0])
            count += 1
            sentence = sentence[1:]
        elif PM[V[i]][V[sentence[0]]] == '>':
            row=[count, ''.join(stack), '>', sentence, '归约(']
            string = ''.join(stack[num[-1]:])
            stack=stack[:num[-1]]
            num.pop()
            flag=False
            for key in grammar:
                for lis in grammar[key]:
                    if ''.join(lis) == string:
                        stack.append(key)
                        row[-1]=row[-1]+key+'->'+string+')'
                        flag=True
                        break
                if flag:
                    break
            table.align = 'l'
            table.add_row(row)
        else:
            raise Exception('分析出错')
        if sentence=='#' and len(stack) == 2 and stack[1]==VN[0]:
            table.align='l'

            table.add_row([count, ''.join(stack), '', sentence, '成功'])
            break
    print(table)


if __name__ == '__main__':
    main()
    grammar['Z'] = [['#', 'S', '#']]
    VT.append('#')
    VN.append('Z')
    V = VT + VN
    num = list(range(len(V)))
    V = dict(zip(V, num))

    PM = init()
    print(show_matrix())
    path = r'BU1.txt'
    if os.path.exists(path):
        os.remove(path)
    with open(path, 'w', encoding='UTF-8') as f:
        f.write(show_grammar())  # 语法
        f.write(show_matrix())  # 优先矩阵
    sentence = input('请输入要语法分析的句子:')
    if sentence[-1] != '#':
        sentence += '#'
    analysis(sentence)
    print('分析成功')

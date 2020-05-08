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
SPM = []


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
    keys = list(V.keys())
    table.field_names = ['V'] + keys
    for i, lis in enumerate(SPM):
        table.align = 'l'
        table.padding_width = 1
        table.add_row([keys[i]] + lis)
    return '优先矩阵:\n' + table.get_string() + '\n\n'


def WARSHALL(matrix):
    beforePaths = matrix.copy()
    newPaths = matrix.copy()
    for k in range(matrix.shape[0]):
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[0]):
                newPaths[i][j] = beforePaths[i][j] or beforePaths[i][k] and beforePaths[k][j]
                beforePaths = newPaths.copy()
    return newPaths


def simple_precedence_matrix():
    first = np.zeros((len(V), len(V)))
    last = np.zeros((len(V), len(V)))
    equal = np.zeros_like(first)
    for key in grammar.keys():
        for lis in grammar[key]:
            first[V[key]][V[lis[0]]] = 1
            last[V[key]][V[lis[-1]]] = 1
            if len(lis) > 1:
                for i in range(len(lis) - 1):
                    equal[V[lis[i]]][V[lis[i + 1]]] = 1
    first_plus = WARSHALL(first)
    last_plus = WARSHALL(last)
    first_star = (np.eye(len(V)) + first_plus) > 0
    lt = equal.dot(first_plus)
    bt = (last_plus.T.dot(equal)).dot(first_star)
    for key in V:
        if key in VN:
            bt.T[V[key]] = 0
    equal = np.where(equal > 0, '=', 0)
    lt = np.where(lt > 0, '<', 0)
    bt = np.where(bt > 0, '>', 0)
    matrix = []
    for i in range(len(V)):
        matrix.append([])
        for j in range(len(V)):
            matrix[i].append((equal[i][j] + lt[i][j] + bt[i][j]).replace('0', ''))
            if len(matrix[i][-1]) > 1:
                return None
    return matrix


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


def analysis():
    for lis in SPM:
        lis.append('<')
    V.append('#')
    stack = ['#']
    count = 1
    idx = 0
    table = PrettyTable(border=False)
    table.field_names = ['步骤', '分析栈', '符号串', '下步动作']
    # while stack or idx < len(sentence):
    #     if idx >= len(sentence) or not stack:
    #         print(table)
    #         raise Exception("分析出错")
    #     if sentence[idx] not in VT and sentence[idx] != '#':
    #         print(table)
    #         raise Exception('字符不在终结符集中：', sentence[idx])
    #     while stack[-1] != sentence[idx] and stack[-1] in VN:
    #         production = prediction_analysis_table[stack[-1]][get_column(sentence[idx])]
    #         if not production:
    #             print(table)
    #             raise Exception("分析出错")
    #         table.align = 'l'
    #         table.add_row([count, ''.join(stack), sentence[idx:], stack[-1] + '->' + ''.join(production)])
    #         count = count + 1
    #         stack.pop()
    #         if production != ['ε']:
    #             pro = production.copy()
    #             pro.reverse()
    #             stack += pro
    #     if stack[-1] == sentence[idx]:
    #         table.align = 'l'
    #         table.add_row([count, ''.join(stack), sentence[idx:], ''])
    #         stack.pop()
    #         count += 1
    #         idx += 1
    #         continue
    #     print(table)
    #     raise Exception("分析出错")
    print(table)


if __name__ == '__main__':
    main()
    V = VN + VT
    num = list(range(len(V)))
    V = dict(zip(V, num))

    SPM = simple_precedence_matrix()

    if not SPM:
        print('不是简单优先文法')
    else:
        path = r'BU.txt'
        if os.path.exists(path):
            os.remove(path)
        with open(path, 'w', encoding='UTF-8') as f:
            f.write(show_grammar())  # 语法
            f.write(show_matrix())  # 优先矩阵
        sentence = input('请输入要语法分析的句子:')
        if sentence[-1] != '#':
            sentence += '#'
        analysis()
        print('分析成功')

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


# 求firstvt lastvt 构造优先分析表
def init():
    # ------------初始化
    for v in VN:
        firstvt[v] = None
        lastvt[v] = None

    # 求每一个非终结符的Firstvt集
    for v in VN:
        if not firstvt[v]:
            FIRSTVT(v)

    change = True  # 标记是否进行过替换
    while change:
        change = False
        for vn in VN:
            firstvt[vn] = list(set(firstvt[vn]))  # 对于每一个非终结符的firstvt集去重
            if vn in firstvt[vn]:  # 如果firstvt(A)含有firstvt(A) 直接去掉
                firstvt[vn].remove(vn)
            old = firstvt[vn].copy()  # 深复制当前非终结符的firstvt集
            for item in old:  # 对于其中每一项
                if item in VN:  # 如果是一个非终结符B，进行替换
                    change = True  # 标记替换了
                    firstvt[vn].remove(item)  # 去掉该非终结符B
                    firstvt[vn] += firstvt[item]  # 将该firstvt(B)加入当前firstvt集
                    if vn in firstvt[vn]:  # 如果添加的了本身，去掉
                        firstvt[vn].remove(vn)
            firstvt[vn] = list(set(firstvt[vn]))  # 去重

    # 求每一个非终结符的Lastvt集
    for v in VN:
        if not lastvt[v]:
            LASTVT(v)

    change = True  # 标记是否进行过替换
    while change:
        change = False
        for vn in VN:
            lastvt[vn] = list(set(lastvt[vn]))  # 对于每一个非终结符的lastvt集去重
            if vn in lastvt[vn]:  # 如果lastvt(A)含有lastvt(A) 直接去掉
                lastvt[vn].remove(vn)
            old = lastvt[vn].copy()  # 深复制当前非终结符的lastvt集
            for item in old:  # 对于其中每一项
                if item in VN:  # 如果是一个非终结符B，进行替换
                    change = True  # 标记替换了
                    lastvt[vn].remove(item)  # 去掉该非终结符B
                    lastvt[vn] += lastvt[item]  # 将该lastvt(B)加入当前lastvt集
                    if vn in lastvt[vn]:  # 如果添加的了本身，去掉
                        lastvt[vn].remove(vn)
            lastvt[vn] = list(set(lastvt[vn]))  # 去重
    # for key in firstvt.keys():
    #     print(key, firstvt[key])
    # print()
    # for key in lastvt.keys():
    #     print(key, lastvt[key])

    """
    • FOR 每条产生式P→X_1X_2 …X_n DO
    • {FOR (i=1,i<=n-1,i++)
    • {if X_i 和X_i+1 均为终结符 then 置X_i =X_i+1
    • if i<=n-2 and X_i 和X_i+2 均为终结符 and X_i+1 为非终结符 then 置X_i=X_i+1
    • if X_i 为终结符而X_i+1 为非终结符 then
    • for FIRSTVT(X_i+1)中的每个a DO
    • {置 X_i<a}
    • if X_i 为非终结符而X_i+1 为终结符 then
    • for LASTVT(X_i)中的每个a DO
    • {置 a>X_i }
    """
    PM = np.empty((len(VT), len(VT)), dtype=str)
    PM.fill('')
    PM = PM.tolist()
    for key in grammar.keys():
        for lis in grammar[key]:
            if len(lis) > 1:
                for i in range(len(lis) - 1):
                    if lis[i] in VT and lis[i + 1] in VT:
                        PM[V[lis[i]]][V[lis[i + 1]]] += '='
                    if i < len(lis) - 2 and lis[i] in VT and lis[i + 2] in VT and lis[i + 1] in VN:
                        PM[V[lis[i]]][V[lis[i + 2]]] += '='
                    if lis[i] in VT and lis[i + 1] in VN:
                        for item in firstvt[lis[i + 1]]:
                            PM[V[lis[i]]][V[item]] += '<'
                    if lis[i] in VN and lis[i + 1] in VT:
                        for item in lastvt[lis[i]]:
                            PM[V[item]][V[lis[i + 1]]] += '>'
    # print(PM)
    for lis in PM:
        for j in lis:
            if len(j)>1:
                print("不是算符优先文法")
    return PM


# 求n的Lastvt集
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
            if item in VN and item != n:
                # lastvt[n].append(LASTVT(item))
                lastvt[n].append(item)
    lastvt[n] = list(set(_flatten(lastvt[n])))  # 求每条产生式First集的交集
    return lastvt[n]  # 返回First集


"""
若有产生式P →a…或P →Qa… ，则a ∈FIRSTVT(P)
若a ∈FIRSTVT(Q)，且有产生式P →Q…，则
a ∈FIRSTVT(P)。
"""
# 求n的Firstvt集


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
            elif item in VN and item != n:
                firstvt[n].append(item)
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
            if PM[V[i]][V[sentence[0]]] == '<':
                table.add_row([count, ''.join(stack), '<', sentence, '移进'])
                num.append(stack.index(i) + 1)
            else:
                table.add_row([count, ''.join(stack), '=', sentence, '移进'])
            stack.append(sentence[0])
            count += 1
            sentence = sentence[1:]
        elif PM[V[i]][V[sentence[0]]] == '>':
            row = [count, ''.join(stack), '>', sentence, '归约(']
            string = ''.join(stack[num[-1]:])
            stack = stack[:num[-1]]
            num.pop()
            flag = False
            for key in grammar:
                for lis in grammar[key]:
                    if ''.join(lis) == string:
                        stack.append(key)
                        row[-1] = row[-1] + key + '->' + string + ')'
                        flag = True
                        break
                if flag:
                    break
            table.align = 'l'
            table.add_row(row)
        else:
            raise Exception('分析出错')
        if sentence == '#' and len(stack) == 2 and stack[1] == VN[0]:
            table.add_row([count, ''.join(stack), '', sentence, '成功'])
            break
    # table.align='l'
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

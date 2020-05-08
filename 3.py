from prettytable import PrettyTable
from tkinter import _flatten
import os

"""数据及其格式"""
grammar = {}  # 语法 默认第一个是开始符号 {'E': [['T', 'A']], 'A': [['+', 'T', 'A'], ['ε']], 'T': [['F', 'B']], 'B': [['*', 'F', 'B'], ['ε']], 'F': [['i'], ['(', 'E', ')']]}
VN = []  # 非终结符 ['E', 'A', 'T', 'B', 'F']
VT = []  # 终结符 ['+', '*', 'i', '(', ')']
first = {}  # {'E': ['(', 'i'], 'A': ['+', 'ε'], 'T': ['(', 'i'], 'B': ['ε', '*'], 'F': ['(', 'i'], '+': ['+'], '*': ['*'], 'i': ['i'], '(': ['('], ')': [')'], 'ε': ['ε']}
first_candidate = {}  # 每一个产生式的First集 {'E': [['(', 'i']], 'A': [['+'], ['ε']], 'T': [['(', 'i']], 'B': [['*'], ['ε']], 'F': [['i'], ['(']]}
follow = {}  # {'E': [')', '#'], 'A': [')', '#'], 'T': ['+', ')', '#'], 'B': ['+', ')', '#'], 'F': ['+', ')', '#', '*']}
select = {}  # {'E->TA': ['(', 'i'], 'A->+TA': ['+'], 'A->ε': [')', '#'], 'T->FB': ['(', 'i'], 'B->*FB': ['*'], 'B->ε': ['+', ')', '#'], 'F->i': ['i'], 'F->(E)': ['(']}
prediction_analysis_table = {}  # {'E': [None, None, ['T', 'A'], ['T', 'A'], None, None], 'A': [['+', 'T', 'A'], None, None, None, ['ε'], ['ε']], 'T': [None, None, ['F', 'B'], ['F', 'B'], None, None], 'B': [['ε'], ['*', 'F', 'B'], None, None, ['ε'], ['ε']], 'F': [None, None, ['i'], ['(', 'E', ')'], None, None]}
sentence = ''  # i+i*i#


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


# 显示预测分析表
def show_table():
    table = PrettyTable(border=False)
    table.field_names = ['VT'] + VT + ['#']
    for key in prediction_analysis_table.keys():
        table.align = 'l'
        table.padding_width = 1
        data = [key]
        for lis in prediction_analysis_table[key]:
            if lis:
                data.append(''.join(lis))
            else:
                data.append('')
        table.add_row(data)
    return '预测分析表\n' + table.get_string() + '\n\n'


# 显示first follow select
def show_dic(name, dic):
    table = PrettyTable(border=False, header=False)
    for key in dic.keys():
        table.align = 'l'
        table.left_padding_width = 3
        table.add_row([name + '(' + key + '):', '{' + ','.join(dic[key]) + '}'])
    return name + '集：\n' + table.get_string() + '\n\n'


# 求first follow select 构造预测分析表
def init():
    # ------------初始化
    for v in VN:
        '''非终结符first初始化为None：未知'''
        first[v] = None
        '''非终结符对应的产生式的first列表'''
        first_candidate[v] = []
        '''非终结符follow初始化为空列表'''
        follow[v] = []
        '''预测分析表对于每个非终结符添加行'''
        prediction_analysis_table[v] = []

    '''预测分析表对于每行，添加列——VT个数+1（#）'''
    for vn in prediction_analysis_table.keys():
        for _ in range(len(VT) + 1):
            prediction_analysis_table[vn].append(None)

    # ------------first
    # 非终结符 first为其本身
    for v in VT:
        first[v] = [v]
    first['ε'] = ['ε']
    # 求每一个非终结符的First集
    for v in VN:
        if not first[v]:
            FIRST(v)

    # ------------follow
    FOLLOW()

    # ------------select
    SELECT()

    # ------------预测分析表
    PREDICTION()

    #  是不是LL1文法
    return judge()


"""First集算法
α=X1X2...Xn，Xi∈VN∪VT,
i=0; FIRST(α)={}; 
REPEAT i=i+1;
FIRST(α)=FIRST(α)∪(FIRST(X i )-{ε})
UNTIL ε∉ FIRST(X i ) 或i=n
IF (i=n 且ε∈ FIRST(X n ))THEN FIRST(α)=FIRST(α)∪{ε}
"""


# 求n的First集
def FIRST(n):
    if first[n]:  # 如果已经求出来了 不是None
        return first[n]
    for lis in grammar[n]:  # 对于n的每一条产生式
        first_candidate[n].append(FIRST_CANDIDATE(lis))  # 求这条产生式右端符号串的First集
    first[n] = list(set(_flatten(first_candidate[n])))  # 求每条产生式First集的交集
    return first[n]  # 返回First集


# 求符号串production的First集
def FIRST_CANDIDATE(production):
    if production[0] in VT or production[0] == 'ε':  # VT或空串
        return first[production[0]]
    first_production = []
    for item in production:  # 对于产生式中的每一项
        first_item = FIRST(item)  # 求first
        first_production += first_item  # 并
        if 'ε' not in first_item:  # 如果不含空串 退出
            break
        else:
            first_production.remove('ε')  # 含有去除
    if 'ε' in first_item:  # 如果最后一个符号的first含有空串（非最后一个符号退出都没有空串）
        first_production.append('ε')  # 添加空串
    first_production = list(set(first_production))  # 去重
    return first_production


"""Follow集算法
1)对文法开始符号S，将‘#’加入到Follow(S)中；
2)若B →αAβ是文法G的一个产生式，则将First(β)-ε加入到Follow(A)中;
3)若B →αA是文法G的一个产生式,或B →αAβ是文法G的一个产生式,且β →ε，则将Follow(B)加入到Follow(A)中。
"""


# 求Follow集
def FOLLOW():
    follow[VN[0]].append('#')  # 开始符号Follow集添加#
    # 遍历全部产生式
    for rule in grammar.keys():  # 对于每一个非终结符
        for lis in grammar[rule]:  # 对于该终结符的每一个产生式
            for idx, item in enumerate(lis):  # 对于产生式中每一个符号
                if item in VN:  # 如果是非终结符
                    if idx == len(lis) - 1:  # B →αA
                        follow[item].append(rule)  # 标记follow(A)中含有follow(B)
                    if idx < len(lis) - 1:  # B →αAβ
                        first_production = FIRST_CANDIDATE(lis[idx + 1:])  # 求符号串β的First集
                        follow[item] += first_production  # First(β)加入到Follow(A)中
                        if lis[idx + 1] in VN and 'ε' in first_production:  # β能推导出空串
                            follow[item].append(rule)  # 标记follow(A)中含有follow(B)
                            follow[item].remove('ε')  # 将First(β)添加进来的空串删除

    # print(follow) # 显示当前的Follow集
    # 迭代消除follow(A)中follow(B)的情况
    change = True  # 标记是否进行过替换
    while change:
        change = False
        for vn in VN:
            follow[vn] = list(set(follow[vn]))  # 对于每一个非终结符的Follow集去重
            if vn in follow[vn]:  # 如果follow(A)含有follow(A) 直接去掉
                follow[vn].remove(vn)
            old = follow[vn].copy()  # 深复制当前非终结符的Follow集
            for item in old:  # 对于其中每一项
                if item in VN:  # 如果是一个非终结符B，进行替换
                    change = True  # 标记替换了
                    follow[vn].remove(item)  # 去掉该非终结符B
                    follow[vn] += follow[item]  # 将该follow(B)加入当前Follow集
                    if vn in follow[vn]:  # 如果添加的了本身，去掉
                        follow[vn].remove(vn)
            follow[vn] = list(set(follow[vn]))  # 去重
        # print(follow) # 显示每一步迭代结果


"""Select集算法
1.SELECT(A->α)=FIRST(α)，
2.若α=>ε，SELECT(A->α)=(FIRST(α)-{ε})∪FOLLOW(A)。
"""


# 求Sellect集
def SELECT():
    for rule in grammar.keys():  # 对于每一个非终结符
        for idx, lis in enumerate(grammar[rule]):  # 对于其每一条产生式
            production = rule + '->' + ''.join(lis)  # key:production
            select[production] = first_candidate[rule][idx].copy()  # SELECT(A->α)=深复制FIRST(α)
            if 'ε' in first_candidate[rule][idx]:  # 如果产生式能推出空串
                select[production].remove('ε')  # 消除空串
                select[production] += follow[rule]  # 并上Follow(A)
            select[production] = list(set(select[production]))  # 去重


"""判断是不是LL1文法
对每个非终结符A的两个不同产生式Α→α,Α→β
满足(SELECT(Α→α)∩SELECT(Α→β)=Φ
"""


# 判断是不是LL1文法
def judge():
    idx = 0
    flag = True
    keys = list(select.keys())
    while idx < len(select) and flag:
        idx_p = idx + 1
        sets = [set(select[keys[idx]])]
        while idx_p < len(select) and keys[idx_p][0] == keys[idx][0]:
            sets.append(set(select[keys[idx_p]]))
            idx_p = idx_p + 1
        idx = idx_p
        if len(sets) == 1:
            continue
        for i in range(len(sets)):
            for j in range(i + 1, len(sets)):
                if sets[i] & sets[j] == set():
                    continue
                flag = False
                break
    return flag


# 获取终结符在预测分析表中列号
def get_column(c):
    if c == '#':
        return len(VT)
    return VT.index(c)


"""构造预测分析表算法
1）假定A →α是一个产生式，a∈ First(α),那么当A是栈顶符号且将读入a时， A →α就应作为选用的侯选式，A →α应填入 M[A,a]中。
2）若A →α，而 ε ∈ First(α) ,对每个a∈ Follow(A),在M[A,a]元素中应填A →α(一般填A → ε)。
"""


# 构造预测分析表
def PREDICTION():
    for key in first_candidate.keys():
        for idx, lis in enumerate(first_candidate[key]):  # 对于每个非终结符的每一条产生式的First集
            for item in lis:  # 对于其中每个终结符
                if item == 'ε':  # 空
                    for i in follow[key]:  # 对于改非终结符的Follow集中的每一个终结符
                        prediction_analysis_table[key][get_column(i)] = grammar[key][idx]  # A →α
                else:  # 非空
                    prediction_analysis_table[key][get_column(item)] = grammar[key][idx]  # A →α


def analysis():
    stack = ['#', VN[0]]
    count = 1
    idx = 0
    table = PrettyTable(border=False)
    table.field_names = ['步骤', '分析栈', '预留输入串', '所用产生式']
    while stack or idx < len(sentence):
        if idx >= len(sentence) or not stack:
            print(table)
            raise Exception("分析出错")
        if sentence[idx] not in VT and sentence[idx] != '#':
            print(table)
            raise Exception('字符不在终结符集中：', sentence[idx])
        while stack[-1] != sentence[idx] and stack[-1] in VN:
            production = prediction_analysis_table[stack[-1]][get_column(sentence[idx])]
            if not production:
                print(table)
                raise Exception("分析出错")
            table.align = 'l'
            table.add_row([count, ''.join(stack), sentence[idx:], stack[-1] + '->' + ''.join(production)])
            count = count + 1
            stack.pop()
            if production != ['ε']:
                pro = production.copy()
                pro.reverse()
                stack += pro
        if stack[-1] == sentence[idx]:
            table.align = 'l'
            table.add_row([count, ''.join(stack), sentence[idx:], ''])
            stack.pop()
            count += 1
            idx += 1
            continue
        print(table)
        raise Exception("分析出错")
    print(table)


# 读入语法
def main():
    """读入语法"""
    path = r'grammar.txt'
    with open(path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    """字符串处理"""
    for line in lines:
        if line.isspace():  # 全是空白字符
            continue
        line = "".join(line.split())  # 去除空白字符
        print(line)
        l, r = line.split('->', 1)
        grammar[l] = []
        VN.append(l)
        r = r.split('|')
        for i in r:
            for c in i:
                if not c.isupper() and c not in VT:
                    VT.append(c)
            grammar[l].append(list(i))
    if 'ε' in VT:
        VT.remove('ε')


if __name__ == '__main__':
    main()
    ll1 = init()
    if ll1:
        print('是LL1文法')
    else:
        print('不是LL1文法')
    print()

    path = r'GrammarAnalysis.txt'
    if os.path.exists(path):
        os.remove(path)

    with open(path, 'w', encoding='UTF-8') as f:
        f.write(show_grammar())  # 语法
        f.write('非终结符集:{' + ','.join(VN) + '}\n')  # VN
        f.write('终结符集:{' + ','.join(VT) + '}\n')  # VT
        f.write(show_dic('FIRST', first))  # FIRST
        f.write(show_dic('FOLLOW', follow))  # FOLLOW
        f.write(show_dic('SELECT', select))  # SELECT
        f.write(show_table())  # 预测分析表
    sentence = input('请输入要语法分析的句子:')
    if sentence[-1] != '#':
        sentence += '#'
    analysis()
    print('分析成功')

# def FIRST(n):
#     if first[n]:
#         return first[n]
#     first[n] = []
#     for lis in grammar[n]:
#         first_candidate[n].append([])
#         for item in lis:
#             first_item = FIRST(item)
#             # first[n] = first[n] + first_item
#             first_candidate[n][-1] += first_item
#             if 'ε' not in first_item:
#                 break
#             else:
#                 # first[n].remove('ε')
#                 first_candidate[n][-1].remove('ε')
#         if 'ε' in first_item:
#             # first[n].append('ε')
#             first_candidate[n][-1].append('ε')
#         first_candidate[n][-1] = list(set(first_candidate[n][-1]))
#     # first[n] = list(set(first[n]))
#     first[n] = list(set(_flatten(first_candidate[n])))
#     return first[n]


# def FOLLOW():
#     follow[VN[0]].append('#')
#     for rule in grammar.keys():
#         for lis in grammar[rule]:
#             for idx, item in enumerate(lis):
#                 if item in VN:
#                     if idx == len(lis) - 1:
#                         follow[item].append(rule)
#                     if idx < len(lis) - 1:
#                         follow[item] += first[lis[idx + 1]]
#                         if lis[idx + 1] in VN and ['ε'] in grammar[lis[idx + 1]]:
#                             follow[item].append(rule)
#                             follow[item].remove('ε')
#
#     print(follow)
#     change = True
#     while change:
#         change = False
#         for vn in VN:
#             follow[vn] = list(set(follow[vn]))
#             if vn in follow[vn]:
#                 follow[vn].remove(vn)
#             old = follow[vn].copy()
#             for item in old:
#                 if item.isupper():
#                     change = True
#                     follow[vn].remove(item)
#                     follow[vn] += follow[item]
#                     if vn in follow[vn]:
#                         follow[vn].remove(vn)
#             follow[vn] = list(set(follow[vn]))
#         print(follow)

# def SELECT():
#     for rule in grammar.keys():
#         for lis in grammar[rule]:
#             production = rule + '->' + ''.join(lis)
#             select[production] = []
#             first_production = []
#             for item in lis:
#                 first_item = FIRST(item)
#                 first_production = first_production + first_item
#                 if 'ε' not in first_item:
#                     break
#                 else:
#                     first_production.remove('ε')
#             if 'ε' in first_item:
#                 first_production.append('ε')
#
#             select[production] += first_production
#             if 'ε' in first_production:
#                 select[production].remove('ε')
#                 select[production] += follow[rule]
#             select[production] = list(set(select[production]))

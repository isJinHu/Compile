test = {'1': None}
# print(''.join(test['1']))
print(test)
lis = [1, 2]
if 1 in lis:
    print(lis.index(1))

a = [1, 1, 2, 3, 4]
print(list(set(a)))
# a.remove(5)
for item in a:
    if item == 2:
        a.remove(item)
    print(item, a)
print(a)
# a+=[1111]
# print(a)

# a=[[1],['ε']]
# print(['ε'] in a)


# E->TA
# A->+TA|ε
# T->FB
# B->*FB|ε
# F->i|(E)

# A->BC
# C->aDA
# D->bC|a
# B->EaA|ε
# E->aBd

lis = []
for i in range(5):
    lis.append([])
for i in lis:
    for _ in range(2):
        i.append(None)
print(lis)

li=[1,3,4,5,6]
print(li[2:])

s='   \t\n'
print(s.isspace())
s='111'
print(s[1])

x=set([1,2])
y=set([1,3,4])
z=set([5])
print(x &y)
print((x &z)==set())
print(y &z)

print([])
a=[]
if a:
    print('22')
else:
    print('00')
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 10:42:42 2022
heirarchal clustering
@author: p0ne
"""
import matplotlib.pyplot as plt
from math import sqrt as st
import string as s
import random
chars = s.ascii_uppercase

def func1(nlist,indlist, indnum):
    nlist[indlist]+=nlist[indnum]
    nlist.pop(indnum)
    return nlist

func2 = lambda x,num: len(x)==num

def evklid(a,b):
    sum_p = []
    for i,j in zip(a,b):
        sum_p.append((i-j)**2)
    res = st(sum(sum_p))
    return res

def points_generator(nlist,intervs,qwerty={}):
    for i in nlist:
        klist = []
        for j in intervs:
            klist.append(( random.randint(j[0],j[1])))
        qwerty[i] = tuple(klist)
    return qwerty

points = points_generator(range(10),[(0,10),(0,10)])
points = points_generator(range(10,20),[(15,30),(0,10)],points)
print(points)
points_list=[[i] for i in points]
iteration=len(points_list)
for it in range(iteration):
    list_a = []
    for k,i in enumerate(points_list):
        for j in i:
            for l in points_list[:k]+points_list[k+1:]:
                for kl in l:
                    list_a.append((evklid(points[j],points[kl]),k,points_list.index(l),j,kl))
    try:
        op = min(list_a,key=lambda x:x[0])
    except ValueError:
        break 
    points_list = func1(points_list,op[1],op[2])
    print("Iteration "+str(it))
    print(points_list)
    print(op[:1]+op[3:])
    print("-------------------------")
    if func2(points_list,1):
        break
print("-------------------------")

print("-------------------------")
points_w = {}
for i,j in enumerate(points_list):
    points_w[chars[i]]=j
print(points_w)
print("-------------------------")
print(points)
print("-------------------------")
plt.plot(points,range(i, j, int()))
print("ONEIL")

# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 11:12:12 2020

@author: ydeng
"""

def print_list(lst, title):
    print("\n%s:\n--------------" % title)
    for e in lst:
        print(e)
        
def print_dict(dic, title):
    for k,v in dic.items():
        print("\n生产 %s" % k) 
        print_list(v, title)
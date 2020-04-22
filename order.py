# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 12:14:08 2020

@author: ydeng
"""

from item import *

class Order:
    def __init__(self, oid, demander, supplier):
        print("创建新订单")
        self.oid = oid
        self.goods = []
        self.demander = demander  # 需求方
        self.supplier = supplier  # 供给方
    
    def __str__(self):
        s = "订单号：%d\n" % self.oid
        s += "订购货物：\n"
        for i in self.goods:
            s += "  %s\n" % i
        s += "订货方：%s\n" % self.demander
        s += "供货方：%s" % self.supplier
        return s
        
    def add(self, r):
        self.goods.append(r)
        
    def display(self):
        print("%s\n" % self)
        
    #def analyze(self):
    #    print("分析订单...")
            
        
    # 拆分订单算法
    #def get_split():
        
        

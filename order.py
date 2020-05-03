# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 12:14:08 2020

@author: ydeng
"""

from item import *
from constant import OStatus
#import tools

class Order:
    _oid = 0  # order id
    def __init__(self, s_name):
        #print(">> 创建新订单")
        Order._oid += 1
        self.oid = Order._oid
        self.goods = []
        # default from Engine instead of any factory
        self.set_demander("Engine(System)", -1) # 需求方
        self.supplier_name = s_name
        self.status = OStatus.ongoing
    
    def __str__(self):
        s = "订单号：%d (Status: %s)\n" % (self.oid, self.status)
        s += "订购货物：\n"
        for i in self.goods:
            s += "  %s\n" % i
        s += "订货方：%s(id=%d)\n" % (self.demander_name, self.demander_id)
        s += "供货方：%s" % self.supplier_name
        return s
      
    def set_demander(self, name, d_id):
      self.demander_name = name
      self.demander_id = d_id
      
    def add(self, r):
        self.goods.append(r)
        
    def display(self):
        print("%s\n" % self)
        
    def finished(self):
        return self.status == OStatus.finished
    
    # get qty of ordered item
    def get_qty(self, iname):
        for i in self.goods:
          if i.name == iname:
            return i.qty
        return 0
      
    #def analyze(self):
    #    print("分析订单...")
    
    # 拆分订单算法
    #def get_split():

#def _get_supplier_name(d_name):
  
# split demands
# m4order is a list
def get_demand(m4order, names):
    demand = []
    for n in names:
      for r in m4order:
        if r.name == n:
          demand.append(r)
    return demand
"""
def get_demand(m4order, names):
    #tools.print_list(m4order.keys(), "demands")
    demand = []
    for n in names:
      for l in m4order.values():
        for r in l:
          if r.name == n:
            demand.append(r)
    return demand
"""    

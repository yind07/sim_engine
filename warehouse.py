# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 13:10:37 2020

@author: ydeng
"""

import random

from constant import WType
from item import ItemRecord

class Warehouse:
    # rate_mul: 消耗/生产速度的倍数
    # 单个物品消耗/生产速度 = rate_mul * itemRecord.rate_base
    def __init__(self, wtype, stocks, rm):
        self.type = wtype
        self.stocks = stocks
        self.rate_mul = rm
        
    def __str__(self):
        s = "库存 %s(%d类):" % (self.type, len(self.stocks))
        for i in self.stocks:
            s += "\n    %s" % i
        return s

class PWarehouse(Warehouse):
    ## rate_base: 消耗/生产速度的基数，
    ## 原料 – 消耗速度；成品 – 生产速度
    def __init__(self, stocks, rm, rb):
        self.type = WType.products
        self.stocks = stocks
        self.rate_mul = rm
        self.rate_base = rb
    
    # remove half of current stocks
    # return the halved stocks as dict (iname: qty)    
    def halve_stocks(self):
      stocks = {}
      for i in self.stocks:
        stocks[i.name] = i.halve()
      return stocks

    # used to close the last order
    def dec_stocks(self, goods):
      for i in self.stocks:
        for g in goods:
          if i.name == g.name:
            i.dec(g.qty)

    # return true if 停产上限 is met
    # 实际算法：当所有的成品均超出相应停产上限时才确认为仓库已满      
    # 这和如果成品严格按比例增加/减少情况下只判断其中一种是否已达上限是一致的
    def is_full(self, cfg_pw):
      for i in self.stocks:
        limit = cfg_pw[i.name]["pause_limit"]
        if i.qty < limit:
          return False
      return True

class MWarehouse(Warehouse):
    def __init__(self, stocks, rm, rb):
        self.type = WType.materials
        self.stocks = stocks
        self.rate_mul = rm
        self.rate_base = rb
        
    def inc_stocks(self, goods, cfg):
        for i in self.stocks:
          if i.is_raw():
            print(">>> 港口进货 %s，增加3倍进货下限" % i.name)
            i.inc(3*cfg[i.name]["restock_limit"])
          elif i.name in goods: # ensure item key exists!
            i.inc(goods[i.name])
            #print(">> inc_stocks(): 库存 %s 增加 %.2f，现有 %.2f" % (i.name, goods[i.name], i.qty))
    
    # Return: 当前库存原料可以生产的最大成品数
    # mcfgs: dict - 生产一个成品的原料数量配比，例如BOM表
    def maxProductQty(self, mcfgs):
        min_qty = float("inf")  # 正无穷
        for m in self.stocks:
            mp = m.maxProductQty(mcfgs[m.name])
            if mp < min_qty:
                min_qty = mp
        return min_qty

    # 按当前原料库存和消耗率，当天最多消耗多少份原料(一份配比为ratebase)
    # 如果原料不够一天生产，则按比例生产成品！
    def maxDailyConsumption(self):
        min_qty = float("inf")  # 正无穷
        for m in self.stocks:
          if not m.hasEnough(1):
            return 0
          mc = m.qty/self.rate_base[m.name]
          if mc < min_qty:
            min_qty = mc
        if mc > self.rate_mul:
          return self.rate_mul
        return mc
      
# helper functions

# assumption: fname + wtype => goods on stock
#def _init_stocks(cfg, fname, names, wtype):
def init_stocks(cfg, fname, wtype):
  # calculate the minimal multiple (ul/base) of goods
  min_multiple = float("inf") 
  for i,v in cfg.f_stocks[fname][wtype].items():
    m = v["ul"]/v["base"]
    if m < min_multiple:
      min_multiple = m
  rand_multiple = random.randrange(min_multiple)+1
  #print("rand_multiple: %d" % rand_multiple)
  
  stocks = []
  for i,v in cfg.f_stocks[fname][wtype].items():
    r = ItemRecord(i, v["base"]*rand_multiple)
    stocks.append(r)
  return stocks 

# return initial stocks by configuration, factory name and warehouse type
#def default_stocks(cfg, fname, wtype):
#  return _init_stocks(cfg, fname, wtype)

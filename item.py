# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 16:59:15 2020

@author: ydeng
"""

# 是否无限供应？
# 可由工厂类型 + 物品类型判断，基础工厂的原料由港口无限供应，目前有五种：
# 原油、氢气、催化剂（氧化铝）、铁矿石、铝矿石

# Background
# A commodity is a raw material used to manufacture finished goods.
# A product, on the other hand, is the finished goods sold to consumers.
#

import math
from constant import IName

# item + quantity
class ItemRecord:
    def __init__(self, iname, qty):
        self.name = iname
        self.qty = qty
        # save periodic produce/consume rate, for daily log
        # it's actual value (including random deviation)
        self.reset_dr()
        
    def __str__(self):
        return "%s (qty=%d)" % (self.name, self.qty)
    
    def inc(self, qty):
        self.qty += qty
        
    def dec(self, qty):
        self.qty -= qty
    
    def is_part(self):
        return self.name in [IName.plastic_gear,
                             IName.plastic_lever,
                             IName.plastic_enclosure,
                             IName.iron_gear,
                             IName.iron_lever,
                             IName.iron_enclosure,
                             IName.alum_gear,
                             IName.alum_lever,
                             IName.alum_enclosure]
    def is_raw(self):
        return self.name in [IName.crudeoil,
                             IName.hydrogen,
                             IName.alumina,
                             IName.ironstone,
                             IName.bauxite]
    # decrease 50% qty of current item record,
    # return decreased quantity
    def halve(self):
        qty = self.qty/2
        if self.is_part():
          qty = math.floor(qty)
        self.dec(qty)
        #print(">> halve(): %s库存 减少 %.2f，现有 %.2f" % (self.name, qty, self.qty))
        return qty
      
    def hasEnough(self, qty):
        return self.qty >= qty
    
    def mul(self, multiple):
        self.qty *= multiple
        return self
    # reset daily rate  
    def reset_dr(self):
        self.daily_rate = 0
    def set_dr(self, dr):
        self.daily_rate = dr
    
    # unit_num: 生产一个成品的需求量, constraint: >0
    def maxProductQty(self, unit_num):
        return math.floor(self.qty/unit_num)

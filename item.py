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

from enum import Enum

# 物品(Item)名称
class IName(Enum):
    def __str__(self):
        if self.name == "aircraft":
            return "飞机"
        elif self.name == "automobile":
            return "汽车"
        elif self.name == "crudeoil":
            return "原油" 
        elif self.name == "hydrogen":
            return "氢气"
        elif self.name == "alumina":
            return "氧化铝（催化剂）"
        elif self.name == "benzene":
            return "苯"
        elif self.name == "toluene":
            return "甲苯" 
        elif self.name == "ironstone":
            return "铁矿石"
        elif self.name == "steel":
            return "钢锭"
        elif self.name == "bauxite":
            return "铝矿石"
        elif self.name == "aluminium":
            return "铝锭"
        elif self.name == "pvc":
            return "聚氯乙烯"
        elif self.name == "pvc_hb":
            return "高苯聚氯乙烯"
        elif self.name == "iron_shcc":
            return "热轧钢板"
        elif self.name == "iron_spcc":
            return "冷轧钢板"
        elif self.name == "alum_shcc":
            return "热轧铝板"
        elif self.name == "alum_spcc":
            return "冷轧铝板"
        elif self.name == "plastic_gear":
            return "塑料齿轮"
        elif self.name == "plastic_lever":
            return "塑料连杆"
        elif self.name == "plastic_enclosure":
            return "塑料外壳"
        elif self.name == "iron_gear":
            return "铁质齿轮"
        elif self.name == "iron_lever":
            return "铁质连杆"
        elif self.name == "iron_enclosure":
            return "铁质外壳"
        elif self.name == "alum_gear":
            return "铝质齿轮"
        elif self.name == "alum_lever":
            return "铝质连杆"
        elif self.name == "alum_enclosure":
            return "铝质外壳"
        return "IName.NEW"
    
    aircraft          = 1  # 飞机
    automobile        = 2  # 汽车
    crudeoil          = 3  # 原油
    hydrogen          = 4  # 氢气
    alumina           = 5  # 氧化铝（催化剂）
    benzene           = 6  # 苯
    toluene           = 7  # 甲苯
    ironstone         = 8  # 铁矿石
    steel             = 9  # 钢锭
    bauxite           = 10 # 铝矿石
    aluminium         = 11 # 铝锭
    pvc               = 12 # 聚氯乙烯
    pvc_hb            = 13 # 高苯聚氯乙烯
    iron_shcc         = 14 # 热轧钢板
    iron_spcc         = 15 # 冷轧钢板
    plastic_gear      = 16 # 塑料齿轮
    plastic_lever     = 17 # 塑料连杆
    plastic_enclosure = 18 # 塑料外壳
    iron_gear         = 19 # 铁质齿轮
    iron_lever        = 20 # 铁质连杆
    iron_enclosure    = 21 # 铁质外壳
    alum_gear         = 22 # 铝质齿轮
    alum_lever        = 23 # 铝质连杆
    alum_enclosure    = 24 # 铝质外壳
    alum_shcc         = 25 # 热轧铝板
    alum_spcc         = 26 # 冷轧铝板

# item + quantity
class ItemRecord:
    # rate_base: 消耗/生产速度的基数，
    # 原料 – 消耗速度；成品 – 生产速度
    def __init__(self, iname, qty, cfg):
        self.name = iname
        self.qty = qty
        self.rate_base = cfg.ratebase[iname]
        
    def __str__(self):
        return "%s (qty=%d)" % (self.name, self.qty)
    
    def inc(self, qty):
        self.qty += qty
        
    def dec(self, qty):
        self.qty -= qty
        
    def hasEnough(self, qty):
        return self.qty >= qty
    
    def mul(self, multiple):
        self.qty *= multiple
        return self
    
    # unit_num: 生产一个成品的需求量, constraint: >0
    def maxProductQty(self, unit_num):
        return math.floor(self.qty/unit_num)
        
"""
# a collection of item records
class ItemRecords:
    def __init__(self):
        self.records = []
    
    def __str__(self, ident="    "):
        s = ""
        first = True
        for r in self.records:
            if first:
                first = False
            else:
                s += "\n"
            s += "%s%s" % (ident, r)
        return s
    
    def size(self):
        return len(self.records)
    
    def add(self, record):
        self.records.append(record)
"""
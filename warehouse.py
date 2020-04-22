# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 13:10:37 2020

@author: ydeng
"""
import constant
from enum import Enum
from item import IName, ItemRecord

# 仓库种类
class WType(Enum):
    def __str__(self):
        if self.name == "materials":
            return "原料库"
        elif self.name == "products":
            return "成品库"
        return "WType.NEW"
        
    materials = 1 # 工厂生产的输入
    products  = 2 # 工厂生产的输出

class Warehouse:
    # rate_mul: 消耗/生产速度的倍数
    # 单个物品消耗/生产速度 = rate_mul * itemRecord.rate_base
    def __init__(self, wtype, stocks, rm):
        self.type = wtype
        self.stocks = stocks
        self.rate_mul = rm
        
    def __str__(self):
        s = "库存 %s(%d):" % (self.type, len(self.stocks))
        for i in self.stocks:
            s += "\n    %s" % i
        return s
    
class PWarehouse(Warehouse):
    def __init__(self, stocks, rm):
        self.type = WType.products
        self.stocks = stocks
        self.rate_mul = rm

class MWarehouse(Warehouse):
    def __init__(self, stocks, rm):
        self.type = WType.materials
        self.stocks = stocks
        self.rate_mul = rm
    
    # Return: 当前库存原料可以生产的最大成品数
    # mcfgs: dict - 生产一个成品的原料数量配比，例如BOM表
    def maxProductQty(self, mcfgs):
        max_qty = float("inf")  # 正无穷
        for m in self.stocks:
            mp = m.maxProductQty(mcfgs[m.name])
            if mp < max_qty:
                max_qty = mp
        return max_qty
        
# helper functions
def _init_stocks(cfg, fname, names, wtype):
    stocks = []
    for n in names:
        r = ItemRecord(n, cfg.get_init_qty(fname, wtype, n), cfg)
        stocks.append(r)
    return stocks    

def init_stocks_p(cfg, fname, names):
    return _init_stocks(cfg, fname, names, WType.products)

def init_stocks_m(cfg, lst_names, fname):
    return _init_stocks(cfg, lst_names, fname, WType.materials)            


# return initial stocks by configuration, factory name and warehouse type
def default_stocks(cfg, fname, wtype):
    if fname == constant.FName.aircraft_assembly:
        if wtype == WType.products:
            return init_stocks_p(cfg, fname, [IName.aircraft])
        elif wtype == WType.materials:
            return init_stocks_m(cfg, fname,\
                                 [IName.plastic_gear,\
                                  IName.plastic_lever,\
                                  IName.plastic_enclosure,\
                                  IName.iron_gear,\
                                  IName.iron_lever,\
                                  IName.iron_enclosure,\
                                  IName.alum_gear,\
                                  IName.alum_lever,\
                                  IName.alum_enclosure])
    
    elif fname == constant.FName.automobile_assembly:
        if wtype == WType.products:
            return init_stocks_p(cfg, fname, [IName.automobile])
        elif wtype == WType.materials:
            return init_stocks_m(cfg, fname,\
                                 [IName.plastic_gear,\
                                  IName.plastic_lever,\
                                  IName.plastic_enclosure,\
                                  IName.iron_gear,\
                                  IName.iron_lever,\
                                  IName.iron_enclosure,\
                                  IName.alum_gear,\
                                  IName.alum_lever,\
                                  IName.alum_enclosure])
    else:
        pass
    return []

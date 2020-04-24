# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 13:10:37 2020

@author: ydeng
"""

from constant import WType, IName, FName
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
        min_qty = float("inf")  # 正无穷
        for m in self.stocks:
            mp = m.maxProductQty(mcfgs[m.name])
            if mp < min_qty:
                min_qty = mp
        return min_qty
        
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
    if fname == FName.aircraft_assembly:
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
    
    elif fname == FName.automobile_assembly:
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
    elif fname == FName.plastic_parts:
        if wtype == WType.products:
            return init_stocks_p(cfg, fname,\
                                 [IName.plastic_gear,\
                                  IName.plastic_lever,\
                                  IName.plastic_enclosure])
        elif wtype == WType.materials:
            return init_stocks_m(cfg, fname,\
                                 [IName.pvc,\
                                  IName.pvc_hb])
    elif fname == FName.iron_parts:
        if wtype == WType.products:
            return init_stocks_p(cfg, fname,\
                                 [IName.iron_gear,\
                                  IName.iron_lever,\
                                  IName.iron_enclosure])
        elif wtype == WType.materials:
            return init_stocks_m(cfg, fname,\
                                 [IName.iron_shcc,\
                                  IName.iron_spcc])
    elif fname == FName.alum_parts:
        if wtype == WType.products:
            return init_stocks_p(cfg, fname,\
                                 [IName.alum_gear,\
                                  IName.alum_lever,\
                                  IName.alum_enclosure])
        elif wtype == WType.materials:
            return init_stocks_m(cfg, fname,\
                                 [IName.alum_shcc,\
                                  IName.alum_spcc])
    else:
        print("Warning: Add new stocks!")
        pass
    return []

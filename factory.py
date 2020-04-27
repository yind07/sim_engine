# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 16:55:30 2020

@author: ydeng
"""

import math

from warehouse import *
from item import ItemRecord
from constant import IName, FName, WType, FStatus
import tools

class Factory:
    def __init__(self, fname, pwh, mwh, status, cfg):
        self.name = fname
        #self.type = ftype
        self.pwarehouse = pwh   # 成品库
        self.mwarehouse = mwh   # 原料库
        self.status = status
        self.power_consumption = cfg.f_pc[fname]
        self.maintenance_len = cfg.f_mlen[fname]
        
        
    def __str__(self):
        s = "%s: %s\n" % (self.name, self.status)
        s += "  耗电（1000Kwh/周期）： %d\n" % self.power_consumption
        s += "  维修时长（周期）： %d\n" % self.maintenance_len
        s += "  %s\n" % self.pwarehouse
        s += "  %s" % self.mwarehouse
        return s
    
    # calculate minimal multiple of required materials's formula unit, such as:
    # required materials formula unit {x: qty1, y: qty2}
    def calMaterials(self, order_goods, cfg):
        # match supplier's end_products with order commodities
        dict_materials = {}
        for g in self.pwarehouse.stocks:
            for og in order_goods:
                if og.name == g.name:
                    print("%s: 订购 %d, 库存 %d, 还需 %d" % (og.name, og.qty, g.qty, og.qty-g.qty))
                    #bom = cfg.bom[og.name]
                    bom = cfg.bom[self.name]
                    #print(bom)
                    
                    ratebase = cfg.ratebase[self.name][WType.products][g.name]
                    maxp = self.mwarehouse.maxProductQty(bom)*ratebase
                    rate = cfg.f_stocks[self.name][WType.products][g.name]["rate"]
                    #print("每天生产 %d" % rate)
                    tlen = math.ceil(maxp/rate)
                    print("目前库存原料最多可以生产%s：%d, 需要%d天（周期）" % (og.name, maxp, tlen))
                    dict_materials[og.name] = self.calM4Order(get_required_materials(bom, og.qty-g.qty, ratebase), cfg)
        return get_lst_materials(dict_materials)
                            
    def calM4Order(self, req_ms, cfg):
        materials = []
        for g in self.mwarehouse.stocks:
            qty = req_ms[g.name]-g.qty
            if qty <= 0:
                qty = 0
                #print("%s 库存够！" % m.name)
            materials.append(ItemRecord(g.name, qty))
        return materials

# get the most enough materials supply      
def get_lst_materials(dict_m):
  #tools.print_dict(dict_m, "require")
  qty = 0
  for k,v in dict_m.items():
    for i in v:
      if qty < i.qty:
        qty = i.qty
        key = k
        break
  return dict_m[key]

# return a new factory by fname and initial configuration(static)
def get_newf(cfg, fname):
    return Factory(fname,\
                   PWarehouse(default_stocks(cfg, fname, WType.products),
                              cfg.ratemul[fname][WType.products]),\
                   MWarehouse(default_stocks(cfg, fname, WType.materials),
                              cfg.ratemul[fname][WType.materials]),\
                   FStatus.normal, cfg)
    
# return list of total required materials by BOM table and qty    
def get_required_materials(bom, qty, rb):
    return {x: y*qty/rb for (x, y) in list(bom.items())}

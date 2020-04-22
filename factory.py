# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 16:55:30 2020

@author: ydeng
"""

import math
import constant

from warehouse import *
from item import IName, ItemRecord
#import tools

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
    
    # calculate required raw materials's qtys
    def calMaterials(self, order_goods, cfg):
        # match supplier's end_products with order commodities
        for g in self.pwarehouse.stocks:
            for og in order_goods:
                if og.name == g.name:
                    print("%s: 订购 %d, 库存 %d, 还需 %d" % (og.name, og.qty, g.qty, og.qty-g.qty))
                    bom_ac = cfg.bom[IName.aircraft]
                    #tools.print_list(bom_ac, "飞机BOM表")
                    
                    maxp = self.mwarehouse.maxProductQty(bom_ac)
                    rate = g.rate_base * self.pwarehouse.rate_mul
                    tlen = math.ceil(maxp/rate)
                    print("目前库存原料最多可以生产%s：%d, 需要%d天（周期）" % (og.name, maxp, tlen))

                    return self.calM4Order(get_required_materials(bom_ac, og.qty-g.qty), cfg)
                            
    def calM4Order(self, req_ms, cfg):
        materials = []
        for g in self.mwarehouse.stocks:
            qty = req_ms[g.name]-g.qty
            if qty <= 0:
                qty = 0
                #print("%s 库存够！" % m.name)
            materials.append(ItemRecord(g.name, qty, cfg))
        return materials
        
# return a new factory by fname and initial configuration(static)
def get_newf(cfg, fname):
    if fname == constant.FName.aircraft_assembly:
        return Factory(fname,\
                       PWarehouse(default_stocks(cfg, fname, WType.products),\
                                  cfg.ratemul[fname][WType.products]),\
                       MWarehouse(default_stocks(cfg, fname, WType.materials),\
                                  cfg.ratemul[fname][WType.materials]),\
                       constant.FStatus.normal, cfg)
    elif fname == constant.FName.automobile_assembly:
        return Factory(fname,\
                       PWarehouse(default_stocks(cfg, fname, WType.products),\
                                  cfg.ratemul[fname][WType.products]),\
                       MWarehouse(default_stocks(cfg, fname, WType.materials),\
                                  cfg.ratemul[fname][WType.materials]),\
                       constant.FStatus.normal, cfg)
    else:
        return None
    
# return list of total required materials by BOM table and qty    
def get_required_materials(bom, qty):
    return {x: y*qty for (x, y) in list(bom.items())}
    
# return list of items for aircraft BOM        
def get_bom_ac(cfg):
    bom = []
    bom.append(ItemRecord(IName.plastic_gear, cfg, cfg))
    bom.append(ItemRecord(IName.plastic_lever, cfg.bom_ac_pl, cfg))
    bom.append(ItemRecord(IName.plastic_enclosure, cfg.bom_ac_pe, cfg))
    bom.append(ItemRecord(IName.iron_gear, cfg.bom_ac_ig, cfg))
    bom.append(ItemRecord(IName.iron_lever, cfg.bom_ac_il, cfg))
    bom.append(ItemRecord(IName.iron_enclosure, cfg.bom_ac_ie, cfg))
    bom.append(ItemRecord(IName.alum_gear, cfg.bom_ac_ag, cfg))
    bom.append(ItemRecord(IName.alum_lever, cfg.bom_ac_al, cfg))
    bom.append(ItemRecord(IName.alum_enclosure, cfg.bom_ac_ae, cfg))
    return bom

# return list of items for automobile BOM        
def get_bom_am(cfg):
    bom = []
    bom.append(ItemRecord(IName.plastic_gear, cfg.bom_am_pg))
    bom.append(ItemRecord(IName.plastic_lever, cfg.bom_am_pl))
    bom.append(ItemRecord(IName.plastic_enclosure, cfg.bom_am_pe))
    bom.append(ItemRecord(IName.iron_gear, cfg.bom_am_ig))
    bom.append(ItemRecord(IName.iron_lever, cfg.bom_am_il))
    bom.append(ItemRecord(IName.iron_enclosure, cfg.bom_am_ie))
    bom.append(ItemRecord(IName.alum_gear, cfg.bom_am_ag))
    bom.append(ItemRecord(IName.alum_lever, cfg.bom_am_al))
    bom.append(ItemRecord(IName.alum_enclosure, cfg.bom_am_ae))
    return bom

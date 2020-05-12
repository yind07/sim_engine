# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 16:55:30 2020

@author: ydeng
"""

import math

import order
import tools
from warehouse import PWarehouse, MWarehouse, init_stocks
from item import ItemRecord
from constant import FName, WType, FStatus, OStatus, IName

class Factory:
    def __init__(self, fname, fid, pwh, mwh, status, cfg):
        self.name = fname
        self.id = fid
        self.pwarehouse = pwh   # 成品库
        self.mwarehouse = mwh   # 原料库
        self.status = status
        self.maintenance_len = cfg.f_mlen[fname]
        self.cfg = cfg
        self.order = None
        # 能耗分为：计划用电和实际用电
        self.pc_plan = cfg.f_pc[fname]
        self.pc_actual = self.pc_plan

    def __str__(self):
        s = "%s(id=%d): %s\n" % (self.name, self.id+1, self.status)
        s += "  耗电（1000Kwh/周期）： 计划=%.2f，实际=%.2f\n" % (self.pc_plan, self.pc_actual)
        s += "  维修时长（周期）： %d\n" % self.maintenance_len
        if self.name not in [FName.community,
                             FName.harbor,
                             FName.power_station]:
          if self.order == None:
            s += "  当前订单：无\n"
          else:
            s += "  当前订单：%s\n" % self.order
          s += "  %s\n" % self.pwarehouse
          s += "  %s" % self.mwarehouse
        return s
    # return true for 总装厂， return false otherwise 
    def is_assembly(self):
      return self.name in [FName.aircraft_assembly,
                           FName.automobile_assembly]
      
    def set_order(self, order):
      self.order = order
      self.qty_sum = {} # 订单内已完成数量
      self.exp_tlen = {} # 多久完工？
      self.ideal_tlen = {} # 计划多久？
      self.actual_tlen = {} # 已经花费多久？
      # for ordered goods doesn't cover all products (like 热轧/冷轧厂)
      # for r in order.goods:
      for r in self.pwarehouse.stocks:
        self.reset_order_props(r.name)
        # set ideal_tlen
        total = self.get_ordered_qty(r.name)
        if total > r.qty:
          rate = self.cfg.f_stocks[self.name][WType.products][r.name]["rate"]
          self.ideal_tlen[r.name] = math.ceil((total-r.qty)/rate)
        
    def reset_order(self):
      if self.order != None:
        self.pwarehouse.dec_stocks(self.order.goods)
        self.order = None
        # for ordered goods doesn't cover all products (like 热轧/冷轧厂)
        # for r in order.goods:
        for r in self.pwarehouse.stocks:
          self.reset_order_props(r.name)

    # 订购总数
    def get_ordered_qty(self, iname):
      if self.order == None:
        return 0
      else:
        return self.order.get_qty(iname)
    
    # reset 订单内已完成数量 and 预期完工时间长度
    def reset_order_props(self, iname):
      self.qty_sum[iname] = 0
      self.exp_tlen[iname] = 0
      self.ideal_tlen[iname] = 0
      self.actual_tlen[iname] = 0
      
    # 订单内已完成数量 
    def get_qty_sum(self, iname):
      if self.order == None or iname not in self.qty_sum:
        return 0
      else:
        return self.qty_sum[iname]
      
    def add_qty_sum(self, iname, qty):
      if self.order != None:
        if iname in self.qty_sum: # make sure the key exists!
          self.qty_sum[iname] += qty
        else:
          print("!! %s doesn't have %s" % (self.name, iname))

    # 预计完工时间长度（还要多少周期）
    def get_expected_tlen(self, iname):
      if self.order == None or iname not in self.exp_tlen:
        return 0
      else:
        return self.exp_tlen[iname]
      
    def get_ideal_tlen(self, iname):
      #if self.order == None or iname not in self.exp_tlen:
      if self.order == None:
        return 0
      else:
        return self.ideal_tlen[iname]
    
    def get_actual_tlen(self, iname):
      #if self.order == None or iname not in self.exp_tlen:
      if self.order == None:
        return 0
      else:
        return self.actual_tlen[iname]
    
    def update_expected_tlen(self, iname, qty):
      if self.order != None and iname in self.qty_sum:
        total = self.get_ordered_qty(iname)
        if total > qty: # calculate only when stock is not enough
          rate = self.cfg.f_stocks[self.name][WType.products][iname]["rate"]
          self.exp_tlen[iname] = math.ceil((total-qty)/rate)
        else:
          self.exp_tlen[iname] = 0
    
    def update_actual_len(self):
      if self.order != None:
        for r in self.pwarehouse.stocks:
          self.actual_tlen[r.name] += 1

    def get_daily_pc(self):
      return self.pc_actual

    # daily planned power comsumption, mainly for community
    # 工厂的计划用电在初始化时设定，不变化
    def set_pc_plan(self):
      if self.name == FName.community:
        deviation = self.cfg.rand_deviation(self.name)
        rate = 1+deviation
        self.pc_plan = self.cfg.f_pc[self.name] * rate
        self.pc_actual = self.pc_plan

    def can_produce(self):
      # TODO: check if materials can keep manufacturing
      return self.status in [FStatus.normal, FStatus.recharge]

    # periodic manufacture if possible
    def run(self):
      if self.can_produce():
        self.produce()

    # 按消耗/生产比例周期生产（原料减少，成品增加）
    def produce(self):
      #print("生产前：\n%s" % self)
      deviation = self.cfg.rand_deviation(self.name)
      rate = 1+deviation
      #print("deviation: %.2f, rate: %.2f" % (deviation,rate))
      
      # 消耗原料
      mul = self.mwarehouse.maxDailyConsumption()
      #print("daily materials consumption multiple: %d" % mul)
      if mul > 0:
        # 成品
        for i in self.pwarehouse.stocks:
          qty_ideal = self.pwarehouse.rate_base[i.name]*mul*self.pwarehouse.rate_mul/self.mwarehouse.rate_mul
          qty = math.floor(qty_ideal*rate) # ensure integer qty
          rate = qty/qty_ideal # re-calculate rate!!
          i.inc(qty)
          i.set_dr(qty)
          self.add_qty_sum(i.name, qty) # 订单内已完成数量
          self.update_expected_tlen(i.name, i.qty)
          # check/update order status
          if self.is_assembly():
            ordered_qty = self.get_ordered_qty(i.name)
            if ordered_qty > 0 and i.qty >= ordered_qty:
              self.order.status = OStatus.finished
              #print("$$$ 完成订单 %d, ready for next Order!" % self.order.oid)

        # 原料
        for i in self.mwarehouse.stocks:
          qty = self.mwarehouse.rate_base[i.name]*mul*rate
          # just in case materials are all used up
          # which should be avoided by set proper logistics
          # and bottom limit constraints of materials
          if i.qty < qty:
            qty = i.qty
          i.dec(qty)
          i.set_dr(qty)

      #print("生产后：\n%s" % self)
      
    # 检查原料库存是否足够维持生产？
    # 如果原料库存 <= 进货下限，标记下游厂家
    # 返回需要供货的下游厂家名称集合
    def check(self):
      supplier_names = set()
      for i in self.mwarehouse.stocks:
        limit = self.cfg.f_stocks[self.name][WType.materials][i.name]["restock_limit"]
        if i.qty <= limit:
          #print("!! %s: %s 库存<=进货下限，库存 %d, 进货下限 %d" % (self.name, i.name, i.qty, limit))
          supplier_names.add(get_supplier_name(i.name))
      return supplier_names
    
    def is_pwarehouse_full(self):
      return self.pwarehouse.is_full(self.cfg.f_stocks[self.name][WType.products])
      
    # 计算需要订购的原料，返回给下游工厂的订单list
    def plan(self):
      m_orders = []
      m4order = self.calMaterials()
      tools.print_list(m4order, ("%s 需要订购的原料" % self.name))
      m_suppliers = self.get_suppliers_list() # 原料供应厂
      for fname in m_suppliers:
        inames = self.cfg.f_stocks[fname][WType.products].keys()
        demand = order.get_demand(m4order, inames)
        
        if len(demand) > 0:
          m_order = order.Order(fname)
          m_order.set_demander(self.name, 0) # TODO id
          m_order.goods = demand
          
          m_orders.append(m_order)
      return m_orders
      
    # calculate minimal multiple of required materials's formula unit, such as:
    # required materials formula unit {x: qty1, y: qty2}
    #def calMaterials(self, order_goods, cfg):
    def calMaterials(self):
        if self.order == None:
          return []
        # match supplier's end_products with order commodities
        dict_materials = {}
        for g in self.pwarehouse.stocks:
            for og in self.order.goods:
                if og.name == g.name:
                  if og.qty <= g.qty:
                    print("%s: 订购 %d, 库存 %d, 足够，无需订购" % (og.name, og.qty, g.qty))
                  else:  
                    #print("%s: 订购 %d, 库存 %d, 还需 %d" % (og.name, og.qty, g.qty, og.qty-g.qty))
                    bom = self.cfg.bom[self.name]
                    #print(bom)
                    
                    ratebase = self.cfg.ratebase[self.name][WType.products][g.name]
                    maxp = self.mwarehouse.maxProductQty(bom)*ratebase
                    rate = self.cfg.f_stocks[self.name][WType.products][g.name]["rate"]
                    #print("每天生产 %d" % rate)
                    tlen = math.ceil(maxp/rate)
                    #print("目前库存原料最多可以生产%s：%d, 需要%d天（周期）" % (og.name, maxp, tlen))
                    dict_materials[og.name] = self.calM4Order(get_required_materials(bom, og.qty-g.qty, ratebase))
        return get_lst_materials(dict_materials)
                            
    def calM4Order(self, req_ms):
        materials = []
        for g in self.mwarehouse.stocks:
            qty = req_ms[g.name]-g.qty
            if qty <= 0:
                qty = 0
                #print("%s 库存够！" % m.name)
            materials.append(ItemRecord(g.name, qty))
        return materials
    
    # return materials suppliers list
    def get_suppliers_list(self):
      if self.name in [FName.aircraft_assembly, FName.automobile_assembly]:
        return [FName.plastic_parts, FName.iron_parts, FName.alum_parts]
      elif self.name == FName.plastic_parts:
        return [FName.chemical]
      elif self.name in [FName.iron_parts, FName.alum_parts]:
        return [FName.hot_rolling, FName.cold_rolling]
      elif self.name in [FName.hot_rolling, FName.cold_rolling]:
        return [FName.iron_making, FName.alum_making]
      elif self.name == FName.chemical:
        return [FName.petrochemical]
      else:
        return []

def get_supplier_name(iname):
  if iname in [IName.aircraft]:
    return FName.aircraft_assembly
  elif iname in [IName.automobile]:
    return FName.automobile_assembly
  elif iname in [IName.alum_gear, IName.alum_lever, IName.alum_enclosure]:
    return FName.alum_parts
  elif iname in [IName.plastic_gear, IName.plastic_lever, IName.plastic_enclosure]:
    return FName.plastic_parts
  elif iname in [IName.iron_gear, IName.iron_lever, IName.iron_enclosure]:
    return FName.iron_parts
  elif iname in [IName.iron_spcc, IName.alum_spcc]:
    return FName.cold_rolling
  elif iname in [IName.iron_shcc, IName.alum_shcc]:
    return FName.hot_rolling
  elif iname in [IName.pvc, IName.pvc_hb]:
    return FName.chemical
  elif iname in [IName.aluminium]:
    return FName.alum_making
  elif iname in [IName.iron]:
    return FName.iron_making
  elif iname in [IName.benzene, IName.toluene]:
    return FName.petrochemical
  elif iname in [IName.crudeoil, IName.hydrogen, IName.alumina, IName.ironstone, IName.bauxite]:
    return FName.harbor

# get the most enough materials supply      
def get_lst_materials(dict_m):
  #tools.print_dict(dict_m, "require")
  qty = 0
  key = -1
  for k,v in dict_m.items():
    for i in v:
      if qty < i.qty:
        qty = i.qty
        key = k
        break
  if key != -1:
    return dict_m[key]
  else:
    return []

# return a new factory by fname and initial configuration(static)
def get_newf(cfg, fname, idx):
    # specific for community
    if fname == FName.community:
      return Factory(fname, idx, None, None, FStatus.normal, cfg)
    else:
      return Factory(fname, idx,\
                     PWarehouse(init_stocks(cfg, fname, WType.products),
                                cfg.ratemul[fname][WType.products],
                                cfg.ratebase[fname][WType.products]),\
                     MWarehouse(init_stocks(cfg, fname, WType.materials),
                                cfg.ratemul[fname][WType.materials],
                                cfg.ratebase[fname][WType.materials]),\
                     FStatus.normal, cfg)
    
# return list of total required materials by BOM table and qty    
def get_required_materials(bom, qty, rb):
    return {x: y*qty/rb for (x, y) in list(bom.items())}

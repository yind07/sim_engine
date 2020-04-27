# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 18:50:00 2020

@author: ydeng
"""

#from configuration import Config
from factory import get_newf
from order import Order, get_demand
from item import ItemRecord
import constant
import tools

import queue
import csv

class Simulation:
    def __init__(self, cfg, sec=1):
        self.config = cfg
        self.period_by_sec = sec
        self.orders = queue.Queue()
        
        # init static info
        self.f_aircraft = []
        self.f_automobile = []
        self.f_plastic_parts = []
        self.f_iron_parts = []
        self.f_alum_parts = []
        
        for i in range(cfg.f_num[constant.FName.aircraft_assembly]):
            self.f_aircraft.append(get_newf(cfg, constant.FName.aircraft_assembly))
        for i in range(cfg.f_num[constant.FName.automobile_assembly]):
            self.f_automobile.append(get_newf(cfg, constant.FName.automobile_assembly))
        for i in range(cfg.f_num[constant.FName.plastic_parts]):
            self.f_plastic_parts.append(get_newf(cfg, constant.FName.plastic_parts))
        for i in range(cfg.f_num[constant.FName.iron_parts]):
            self.f_iron_parts.append(get_newf(cfg, constant.FName.iron_parts))
        for i in range(cfg.f_num[constant.FName.alum_parts]):
            self.f_alum_parts.append(get_newf(cfg, constant.FName.alum_parts))
        
    def run(self):
        print("Start simulation...")
        
        self.config.init_db()
        
        oid = 1 # initial oid
        supplier = self.f_aircraft[0]
        r = ItemRecord(constant.IName.aircraft, 60)
        order = Order("Engine", supplier)
        oid += 1
        order.add(r)
        self.orders.put(order)
        
        self.save_log("logs\\test.csv")
        
        while not self.orders.empty():
            order = self.orders.get()
            order.display()
            m4order = order.supplier.calMaterials(order.goods, self.config)
            tools.print_list(m4order, "需要订购的原料")
            
            print("\n<TODO> 安排生产链")
            # 根据需求原料，生成订单到下游工厂
            demand_p = get_demand(m4order, [constant.IName.plastic_gear,
                                             constant.IName.plastic_lever,
                                             constant.IName.plastic_enclosure])
            if len(demand_p) > 0:
              demander = order.supplier.name
              supplier = self.f_plastic_parts[0]
              order_new = Order(demander, supplier)
              order_new.goods = demand_p
              self.orders.put(order_new)
              
            demand_i = get_demand(m4order, [constant.IName.iron_gear,
                                             constant.IName.iron_lever,
                                             constant.IName.iron_enclosure])
            if len(demand_i) > 0:
              demander = order.supplier.name
              supplier = self.f_iron_parts[0]
              order_new = Order(demander, supplier)
              order_new.goods = demand_i
              self.orders.put(order_new)
              
            demand_a = get_demand(m4order, [constant.IName.alum_gear,
                                             constant.IName.alum_lever,
                                             constant.IName.alum_enclosure])
            if len(demand_i) > 0:
              demander = order.supplier.name
              supplier = self.f_alum_parts[0]
              order_new = Order(demander, supplier)
              order_new.goods = demand_a
              self.orders.put(order_new)
              
            
            
            
            # arrange production
        # 
        # if getAttacked:
        #   process attack
        # else
        #   if time_length_sofar < self.period_by_sec:
        #       continue check attack
        #
        # 
     
    # write periodic log to DB and csv
    def save_log(self, csvfile):
      with open(csvfile, 'w', newline='') as h:
        w = csv.writer(h)
        w.writerow(["厂名","Id","仓库","品名","订购总数","当前库存","已完成数量","生产/消耗速度","预计完工时间"])
        _save_log_f(w, self.f_aircraft)
        _save_log_f(w, self.f_automobile)
        _save_log_f(w, self.f_plastic_parts)
        _save_log_f(w, self.f_iron_parts)
        _save_log_f(w, self.f_alum_parts)
     
      h.close()
        
# helper function for save_log
def _save_log_f(writer, lst_f):
  for i, f in enumerate(lst_f):
    # 成品库
    for item in f.pwarehouse.stocks:
      writer.writerow([f.name,i+1,constant.WType.products,item.name,"?",item.qty,"?","?","?"])
    # 原料库
    for item in f.mwarehouse.stocks:
      writer.writerow([f.name,i+1,constant.WType.materials,item.name,"?",item.qty,"?","?","?"])
            
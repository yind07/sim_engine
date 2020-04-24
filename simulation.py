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
        r = ItemRecord(constant.IName.aircraft, 100, self.config)
        order = Order("Engine", supplier)
        oid += 1
        order.add(r)
        self.orders.put(order)
        
        while not self.orders.empty():
            order = self.orders.get()
            order.display()
            m4order = order.supplier.calMaterials(order.goods, self.config)
            tools.print_list(m4order, "需要订购的原料")
            
            print("\n<TODO> 安排生产链")
            # 拆分需求原料，生成订单到下游工厂
            demand_new = get_demand(m4order, [constant.IName.plastic_gear,
                                             constant.IName.plastic_lever,
                                             constant.IName.plastic_enclosure])
            if len(demand_new) > 0:
              demander = order.supplier.name
              supplier = self.f_plastic_parts[0]
              order_new = Order(demander, supplier)
              order_new.goods = demand_new
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
        
        
        
        
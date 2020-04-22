# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 18:50:00 2020

@author: ydeng
"""

#from configuration import Config
from factory import get_newf
from order import Order
from item import ItemRecord, IName
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
        
        for i in range(cfg.f_num[constant.FName.aircraft_assembly]):
            self.f_aircraft.append(get_newf(cfg, constant.FName.aircraft_assembly))
        for i in range(cfg.f_num[constant.FName.automobile_assembly]):
            self.f_automobile.append(get_newf(cfg, constant.FName.automobile_assembly))
        
        # how many times does module ready return false? for demo purpose
        self.cnt_false = 1
        
    # return true if mod_name is ready, return false otherwise
    def is_module_ready(self, mod_name):
        print("Check if %s is ready" % mod_name)
        if self.cnt_false > 0:
            self.cnt_false -= 1
            return False
        else:
            self.cnt_false = 1
            return True
        
    def check_modules(self):
        mod_num = 2 # for demo
        for i in range(mod_num):
            name = "mod_" + str(i+1)
            while not self.is_module_ready(name):
                pass
            print("%s is ready" % name)
        
    def run(self):
        print("Start simulation...")
        
        self.config.init_db()
        
        self.check_modules()
        
        oid = 1 # initial oid
        supplier = self.f_aircraft[0]
        r = ItemRecord(IName.aircraft, 100, self.config)
        order = Order(oid, "Engine", supplier)
        order.add(r)
        self.orders.put(order)
        
        while not self.orders.empty():
            order = self.orders.get()
            order.display()
            m4order = order.supplier.calMaterials(order.goods, self.config)
            tools.print_list(m4order, "需要订购的原料")
            print("\n安排生产链：TODO")
            
            # arrange production
        # 
        # if getAttacked:
        #   process attack
        # else
        #   if time_length_sofar < self.period_by_sec:
        #       continue check attack
        #
        # 
        
        
        
        
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
        self.dict_f = {}
        skip_list = [constant.FName.power_station]
        for fname in constant.dict_fname.values():
          if fname not in skip_list:
            factories = []
            for i in range(cfg.f_num[fname]):
              factories.append(get_newf(cfg, fname))
            self.dict_f[fname] = factories
        
    def run(self):
        print("Start simulation...")
        self.config.init_db()
        
        t = 0 # start time - The beginning of Day One
        # test
        cnt = 5
        while cnt > 0:
          print("Manufacturing...")
          skip_list = [constant.FName.power_station]
          for fname in constant.dict_fname.values():
            if fname not in skip_list:
              for f in self.dict_f[fname]:
                f.run()
          cnt -= 1
          
        
        """
        oid = 1 # initial oid
        supplier = self.select_supplier(constant.FName.aircraft_assembly)
        r = ItemRecord(constant.IName.aircraft, 100)
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

            print("\n<TODO> 根据需求原料，生成订单到下游工厂")
            m_suppliers = order.supplier.get_suppliers_list()
            for fname in m_suppliers:
              inames = self.config.f_stocks[fname][constant.WType.products].keys()
              demand = get_demand(m4order, inames)
              
              if len(demand) > 0:
                demander = order.supplier.name
                supplier = self.select_supplier(fname)
                order_new = Order(demander, supplier)
                order_new.goods = demand
                self.orders.put(order_new)
        """
            
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
        
        skip_list = [constant.FName.power_station]
        for fname in constant.dict_fname.values():
          if fname not in skip_list:
            _save_log_f(w, self.dict_f[fname])
     
      h.close()
      
    def select_supplier(self, fname):
      # TODO
      return self.dict_f[fname][0]
      
        
# helper function for save_log
def _save_log_f(writer, lst_f):
  for i, f in enumerate(lst_f):
    # 成品库
    for item in f.pwarehouse.stocks:
      writer.writerow([f.name,i+1,constant.WType.products,item.name,"?",item.qty,"?","?","?"])
    # 原料库
    for item in f.mwarehouse.stocks:
      writer.writerow([f.name,i+1,constant.WType.materials,item.name,"?",item.qty,"?","?","?"])
            
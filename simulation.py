# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 18:50:00 2020

@author: ydeng
"""

#from configuration import Config
from factory import get_newf
from order import Order, get_demand
from item import ItemRecord
from event import Event
import constant
#import tools

import queue
import csv
import random
import datetime
import time

class Simulation:
    def __init__(self, cfg, db, sec=1):
        self.config = cfg
        self.db = db
        self.day_by_sec = sec
        self.orders_ac = queue.Queue() # 飞机订单
        self.orders_am = queue.Queue() # 汽车订单
        self.events = queue.PriorityQueue()
        
        # init static info
        self.dict_f = {}
        skip_list = [constant.FName.power_station,
                     constant.FName.harbor]
        for fname in constant.dict_fname.values():
          if fname not in skip_list:
            factories = []
            for i in range(cfg.f_num[fname]):
              factories.append(get_newf(cfg, fname, i))
            self.dict_f[fname] = factories
        
    def run(self):
        print("\nStart simulation...")
        self.config.init_db()
        
        # start time - Day 0 - to initiate the engine
        # why 0 instead of 1?
        # To avoid actions outside the loop!
        t = 0
        
        """
        Periodic manufacturing process:
        1.  物流处理、生产并记录（NOT for Day 0）
        2.  如果总订单数未达上限，产生新订单
        3.  检查订单（老订单未结束？/有新订单？），
            安排、预测下周期生产/物流
        4.  根据设定周期长短，调整时间(NOT for Day 0)
        """
        t1 = datetime.datetime.now()
        total_orders_ac = 0 # 飞机订单总数
        total_orders_am = 0 # 汽车订单总数
        while True:
          print("\n ===== Day %d =====" % t)

          if t > 0:
            start = datetime.datetime.now()
            #print("[Step 1]: 物流处理、生产并记录")
            # 物流处理
            self.handle_supplies(t)
            # 生产
            skip_list = [constant.FName.power_station,
                         constant.FName.harbor]
            for fname in constant.dict_fname.values():
              if fname not in skip_list:
                for f in self.dict_f[fname]:
                  f.run()
                  f.update_actual_len()
                  
            # 记录
            # format example: 200507102338
            timestamp = datetime.datetime.now().strftime("%y%m%d%H%M%S")
            logfname = "logs\\log-%s-%d.csv" % (timestamp, t)
            self.db.clear_table("daily_logs_new2")
            #self.db.clear_table("daily_logs")
            self.save_log(logfname)
          
          num_orders_ac = self.orders_ac.qsize()
          num_orders_am = self.orders_am.qsize()
          #print("[Step 2]: 按需产生新订单, 当前排队订单数 - 飞机(%d)，汽车(%d)" % (num_orders_ac, num_orders_am))
          if t <= self.config.ul_order_days:
            if num_orders_ac < self.config.max_orders:
              self.orders_ac.put(self.get_new_order(6,10,constant.FName.aircraft_assembly))
              total_orders_ac += 1
            if num_orders_am < self.config.max_orders:
              self.orders_am.put(self.get_new_order(8,12,constant.FName.automobile_assembly))
              total_orders_am += 1

          #print("[Step 3]: 检查订单状态，安排、预测下周期生产/物流")
          #print("a. 检查、物流安排；b. 成品库停产上限检查")
          skip_list = [constant.FName.power_station,
                       constant.FName.harbor]
          for fname in constant.dict_fname.values():
            if fname not in skip_list:
              for f in self.dict_f[fname]:
                self.arrange(f, t)
                
          if t == 0: # the very beginning
            current_order_ac = self.orders_ac.get()
            print(">> 新订单（飞机） %d - 开始处理" % current_order_ac.oid)
            #current_order_ac.display()
            current_order_am = self.orders_am.get()
            print(">> 新订单（汽车） %d - 开始处理" % current_order_am.oid)
            #current_order_am.display()

            # choose supplier
            supplier_ac = self.select_supplier(current_order_ac.supplier_name,0)
            supplier_ac.set_order(current_order_ac)
            supplier_am = self.select_supplier(current_order_am.supplier_name,0)
            supplier_am.set_order(current_order_am)
          else: # t > 0
            if current_order_ac.finished():
              supplier_ac.reset_order()
              if not self.orders_ac.empty():
                print("<< 完成订单（飞机） %d, ready for next Order!" % current_order_ac.oid)
                current_order_ac = self.orders_ac.get()
                print(">> 新订单（飞机） %d - 开始处理" % current_order_ac.oid)
                supplier_ac = self.select_supplier(current_order_ac.supplier_name,0)
                supplier_ac.set_order(current_order_ac)
              else:
                print("<<< 完成订单（飞机） %d, 已无后续飞机订单！" % current_order_ac.oid)
            if current_order_am.finished():
              supplier_am.reset_order()
              if not self.orders_am.empty():
                print("<< 完成订单（汽车） %d, ready for next Order!" % current_order_am.oid)
                current_order_am = self.orders_am.get()
                print(">> 新订单（汽车） %d - 开始处理" % current_order_am.oid)
                supplier_am = self.select_supplier(current_order_am.supplier_name,0)
                supplier_am.set_order(current_order_am)
              else:
                print("<<< 完成订单（汽车） %d, 已无后续汽车订单！" % current_order_am.oid)
                
            if current_order_ac.finished() and self.orders_ac.empty() and current_order_am.finished() and self.orders_am.empty():
              print("$$$ 无后续订单，退出了！")
              break

          if t > 0:
            #print("[Step 4]: 调整时间")
            if self.config.enable_delay:
              tdelta = datetime.datetime.now() - start
              while tdelta.seconds < self.day_by_sec:
                time.sleep(0.1) # 100ms
                tdelta = datetime.datetime.now() - start

          t += 1
            
        # TODO: Attacks
        # if getAttacked:
        #   process attack
        # else
        #   if time_length_sofar < self.day_by_sec:
        #       continue check attack
        #
        #
        tdlt = datetime.datetime.now() - t1
        print("\n>>> 本次演示 %d 天，实际花费 %.2f 分钟, 共产生/完成飞机订单 %d, 汽车订单 %d" % (t, tdlt.seconds/60,total_orders_ac,total_orders_am))

    # 物流处理 - 每天开始生产前
    def handle_supplies(self, t):
      #print(">>> handle_supplies: events size %d" % self.events.qsize())
      while not self.events.empty():
        e = self.events.get()
        if e.time > t:
          self.events.put(e) # put it back
          break
        # processing
        if e.type == constant.EventType.order:
          # a. 获取单次物流的原料补充量
          goods = self.get_m_supplies(e.dest, e.did)
          # b. 添加相应deliver event
          self.events.put(Event(e.time+1, constant.EventType.deliver,
                                e.src, e.sid, e.dest, e.did, goods))
        # 补充原料库
        elif e.type == constant.EventType.deliver:
          self.inc_stocks(e.dest, e.did, e.goods)
        else:
          print("!! New event: %s" % e)

    # 获取单次物流的原料补充量
    def get_m_supplies(self, fname, fid):
      # specific handling for 基础工厂原料
      if fname == constant.FName.harbor:
        goods = {} # 港口进货
      else:
        # 减少50%成品库存
        supplier = self.select_supplier(fname, fid)
        goods = supplier.pwarehouse.halve_stocks()
      return goods
    
    def inc_stocks(self, fname, idx, goods):
      f = self.dict_f[fname][idx]
      f.mwarehouse.inc_stocks(goods,
                              self.config.f_stocks[fname][constant.WType.materials])
      f.status = constant.FStatus.normal

    # 检查、安排物流(次日)
    # 成品停产上限检查
    def arrange(self, f, t):
      # Avoid double recharge!!
      if f.status in [constant.FStatus.normal]:
        suppliers = f.check()
        for name in suppliers:
          if name not in [constant.FName.harbor]:
            # send to each downstrean suppliers
            for did in range(self.config.f_num[name]):
              self.events.put(Event(t+1, constant.EventType.order,
                                    name, did, f.name, f.id, {}))
          else: # specific for 港口进货
            self.events.put(Event(t+1, constant.EventType.order,
                                  name, 0, f.name, f.id, {}))
        if len(suppliers) > 0:
          f.status = constant.FStatus.recharge

      # 成品停产上限检查
      # 如果成品库已达停产上限，但出于触发物流状态，则进入停产状态，后续物流照常
      if f.name not in [constant.FName.aircraft_assembly,
                        constant.FName.automobile_assembly]:
        if f.status in [constant.FStatus.normal,
                        constant.FStatus.recharge,
                        constant.FStatus.pause]:
          if f.is_pwarehouse_full():
            if f.status != constant.FStatus.pause:
              #print("$$$ %s：%s -> 停产" % (f.name, f.status))
              f.status = constant.FStatus.pause
          elif f.status == constant.FStatus.pause:
            #print("@@@ %s：停产 -> 正常" % f.name)
            f.status = constant.FStatus.normal
      
    # plan the production - recursive!
    def plan(self, f):
      m_orders = f.plan()
      for order in m_orders:
        m_supplier = self.select_supplier(order.supplier_name,0) # TODO
        m_supplier.set_order(order)
        self.plan(m_supplier)
                
    # write periodic log to DB and csv
    def save_log(self, csvfile):
      with open(csvfile, 'w', newline='') as h:
        w = csv.writer(h)
        w.writerow(["厂名","Id","状态","仓库","品名","订购总数","当前库存","已完成数量","生产/消耗速度","计划多久","已花多久","还需多久","能耗"])
        
        skip_list = [constant.FName.power_station,
                     constant.FName.harbor]
        for fname in constant.dict_fname.values():
          if fname not in skip_list:
            _save_log_f(w, self.dict_f[fname], self.db)
     
      h.close()
      
    def select_supplier(self, fname, fid):
      return self.dict_f[fname][fid]
      
    # return a new order:
    # random numbers (初始库存基数 * [lbm, ubm])
    def get_new_order(self, lbm, ubm, fname):
      # only one product!
      for i,v in self.config.f_stocks[fname][constant.WType.products].items():
        iname = i
        base = v["base"]
      qty = random.randint(lbm, ubm) * base
      
      #supplier = self.select_supplier(fname)
      r = ItemRecord(iname, qty)
      order = Order(fname)
      order.add(r)      
      order.display()
      return order

# helper function for save_log
def _save_log_f(writer, lst_f, db):
  for i, f in enumerate(lst_f):
    # 成品库
    for item in f.pwarehouse.stocks:
      writer.writerow([f.name,i+1,f.status,constant.WType.products,
                       item.name,
                       f.get_ordered_qty(item.name), # 订购总数
                       item.qty, # 当前库存
                       f.get_qty_sum(item.name), # 已完成数量
                       item.daily_rate, # 生产速度
                       f.get_ideal_tlen(item.name), #计划多久
                       f.get_actual_tlen(item.name), #已经多久
                       f.get_expected_tlen(item.name), # 还要多久完工
                       f.get_daily_pc()]) #能耗
      db.add_daily_log(f.name,i+1,f.status,constant.WType.products,
                       item.name, item.daily_rate,
                       f.get_ordered_qty(item.name),
                       item.qty,
                       f.get_qty_sum(item.name),
                       f.get_expected_tlen(item.name),
                       f.get_ideal_tlen(item.name),
                       f.get_actual_tlen(item.name),
                       f.get_daily_pc())
      item.reset_dr()
    # 原料库
    for item in f.mwarehouse.stocks:
      writer.writerow([f.name,i+1,f.status,constant.WType.materials,
                       item.name,"?",item.qty,"?",item.daily_rate,"?"])
      item.reset_dr()
            
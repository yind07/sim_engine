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
import keyboard

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
        skip_list = [constant.FName.harbor]
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
        1.  物流处理、能耗规划、生产并记录（NOT for Day 0）
        2.  如果总订单数未达上限，产生新订单
        3.  检查订单（老订单未结束？/有新订单？），
            安排、预测下周期生产/物流
        4.  根据设定周期长短，调整时间(NOT for Day 0)
        """
        t1 = datetime.datetime.now()
        total_orders_ac = 0 # 飞机订单总数
        total_orders_am = 0 # 汽车订单总数
        while True:
          # detect key pressing
          if keyboard.is_pressed('q'):
            #print('You Pressed a Key!')
            break # quit decently

          print("\n ===== Day %d =====" % t)
          
          if t > 0:
            start = datetime.datetime.now()
            #print("[Step 1]: 物流处理、能耗规划、生产并记录")
            
            # 事件处理 - 物流、维修
            self.handle_events(t)
            
            # 根据当日发电量规划参与生产的工厂，并记录实际用电量
            self.plan_pc()
            
            # 生产
            skip_list = [constant.FName.power_station,
                         constant.FName.harbor,
                         constant.FName.community]
            for fname in constant.dict_fname.values():
              if fname not in skip_list:
                for f in self.dict_f[fname]:
                  f.run()
                  f.update_actual_len()
                  
            # 记录
            # format example: 200507102338
            timestamp = datetime.datetime.now().strftime("%y%m%d%H%M%S")
            logfname = "logs\\log-%s-%d.csv" % (timestamp, t)
            self.db.clear_table("daily_logs")
            self.save_log(logfname)
          
          num_orders_ac = self.orders_ac.qsize()
          num_orders_am = self.orders_am.qsize()
          #print("[Step 2]: 按需产生新订单, 当前排队订单数 - 飞机(%d)，汽车(%d)" % (num_orders_ac, num_orders_am))
          #if t <= self.config.ul_order_days:
          if True:
            if num_orders_ac < self.config.max_orders:
              self.orders_ac.put(self.get_new_order(6,10,constant.FName.aircraft_assembly))
              total_orders_ac += 1
            if num_orders_am < self.config.max_orders:
              self.orders_am.put(self.get_new_order(8,12,constant.FName.automobile_assembly))
              total_orders_am += 1

          #print("[Step 3]: 能耗检查、预估；检查订单状态，安排、预测下周期生产/物流")
          # 能耗检查、预估
          self.check_pc(t)
          #print("a. 检查、物流安排；b. 成品库已满 - 停产检查")
          skip_list = [constant.FName.power_station,
                       constant.FName.harbor,
                       constant.FName.community]
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
            supplier_ac = self.get_factory(current_order_ac.supplier_name,0)
            supplier_ac.set_order(current_order_ac)
            supplier_am = self.get_factory(current_order_am.supplier_name,0)
            supplier_am.set_order(current_order_am)
            
            # 产生首次维修事件组
            skip_list = [constant.FName.harbor,
                         constant.FName.power_station,
                         constant.FName.community]
            for fname in constant.dict_fname.values():
              if fname not in skip_list:
                for i in range(self.config.f_num[fname]):
                  # 开始维修时间（随机）
                  mt = random.randint(self.config.f_mplb[fname],
                                      self.config.f_mpub[fname])
                  self.events.put(Event(t+mt, constant.EventType.maintain_begin,
                                fname, i, "NA", 0, {}))

          else: # t > 0
            if current_order_ac.finished():
              supplier_ac.reset_order()
              if not self.orders_ac.empty():
                print("<< 完成订单（飞机） %d, ready for next Order!" % current_order_ac.oid)
                current_order_ac = self.orders_ac.get()
                print(">> 新订单（飞机） %d - 开始处理" % current_order_ac.oid)
                supplier_ac = self.get_factory(current_order_ac.supplier_name,0)
                supplier_ac.set_order(current_order_ac)
              else:
                print("<<< 完成订单（飞机） %d, 已无后续飞机订单！" % current_order_ac.oid)
            if current_order_am.finished():
              supplier_am.reset_order()
              if not self.orders_am.empty():
                print("<< 完成订单（汽车） %d, ready for next Order!" % current_order_am.oid)
                current_order_am = self.orders_am.get()
                print(">> 新订单（汽车） %d - 开始处理" % current_order_am.oid)
                supplier_am = self.get_factory(current_order_am.supplier_name,0)
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
                
                # 攻击处理
                self.handle_attacks()
                time.sleep(0.1) # 100ms
                tdelta = datetime.datetime.now() - start
                # detect key pressing
                if keyboard.is_pressed('q'):
                  #print('You Pressed a Key!')
                  break

          t += 1
            
        tdlt = datetime.datetime.now() - t1
        print("\n>>> 本次演示 %d 天，实际花费 %.2f 分钟, 共产生/完成飞机订单 %d, 汽车订单 %d" % (t-1, tdlt.seconds/60,total_orders_ac,total_orders_am))

    # 攻击处理
    def handle_attacks(self):
      attack_info = self.db.get_attack()
      #print("factory types: %d" % len(attack_info))
      for fname, v in attack_info.items():
        #print("%s: cnt=%d" % (fname, len(v)))
        for fid in v.keys():
          f = self.get_factory(fname, fid)
          if f != None:
            if attack_info[fname][fid] == 1:
              if f.status != constant.FStatus.under_attack:
                f.status = constant.FStatus.under_attack
                f.pc_actual = 0
                print(">> %s(%d): 被攻击 -> 攻击处理" % (fname,fid+1))
            else: # 攻击取消 - attack_info[fname][fid] == 0
              if f.status == constant.FStatus.under_attack:
                # constraits: no backup of status before being attacked!
                f.status = constant.FStatus.normal
                f.pc_actual = f.pc_plan
                print(">> %s(%d): 攻击取消 -> 正常" % (fname,fid+1))

    # 物流处理 - 每天开始生产前
    def handle_events(self, t):
      #print(">>> handle_events: events size %d" % self.events.qsize())
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
          # 发货后检查是否可以继续生产？
          if e.dest not in [constant.FName.harbor]:
            f = self.get_factory(e.dest, e.did)
            if not f.is_mwarehouse_short() and not f.is_pwarehouse_full():
              if f.status == constant.FStatus.pause:
                print("### %s(%d)：%s -- 物流发货 --> 正常" % (f.name, f.id+1, f.status))
                f.status = constant.FStatus.normal
                f.pc_actual = f.pc_plan
        # 补充原料库
        elif e.type == constant.EventType.deliver:
          self.inc_stocks(e.dest, e.did, e.goods)
          
        elif e.type == constant.EventType.maintain_begin:
          if not self.is_underattack(e.dest, e.did):
            self.dict_f[e.dest][e.did].status = constant.FStatus.maintain
            #self.dict_f[e.dest][e.did].pc_actual = self.dict_f[e.dest][e.did].pc_plan
            mlen = self.config.f_mlen[e.dest]
            print("%s(%d)开始维修，需要 %d 天" % (e.dest,e.did+1,mlen))
            # 根据维修时长，产生维修结束event
            self.events.put(Event(t+mlen, constant.EventType.maintain_end,
                                  e.dest, e.did, e.src, e.sid, e.goods))
        elif e.type == constant.EventType.maintain_end:
          if not self.is_underattack(e.dest, e.did):
            # depends: if need restore last status before maintain?
            self.dict_f[e.dest][e.did].status = constant.FStatus.normal
            #self.dict_f[e.dest][e.did].pc_actual = self.dict_f[e.dest][e.did].pc_plan
            print("%s(%d)结束维修" % (e.dest,e.did+1))
            # 产生下次维修开始event
            mt = random.randint(self.config.f_mplb[e.dest],
                                self.config.f_mpub[e.dest])
            self.events.put(Event(t+mt, constant.EventType.maintain_begin,
                                  e.dest, e.did, e.src, e.sid, e.goods))
        else:
          print("!! New event: %s" % e)

    # 获取单次物流的原料补充量
    def get_m_supplies(self, fname, fid):
      # specific handling for 基础工厂原料
      if fname == constant.FName.harbor:
        goods = {} # 港口进货
      else:
        # 减少50%成品库存
        supplier = self.get_factory(fname, fid)
        goods = supplier.pwarehouse.halve_stocks()
      return goods
    
    def inc_stocks(self, fname, idx, goods):
      f = self.dict_f[fname][idx]
      f.mwarehouse.inc_stocks(goods,
                              self.config.f_stocks[fname][constant.WType.materials])

      # 并非成品库满导致的停产
      if f.status == constant.FStatus.pause and not f.is_pwarehouse_full():
        # check if the materials are enough to produce!!
        bom = f.cfg.bom[fname]
        if f.mwarehouse.maxProductQty(bom) > 0:
          f.status = constant.FStatus.normal
          f.pc_actual = f.pc_plan
          print("@@@ %s(%d): 补充原料后能够继续生产！" % (fname, idx+1))

    # 检查、安排物流(次日)
    # 成品停产上限检查
    def arrange(self, f, t):
      # Avoid double recharge!!
      if f.status == constant.FStatus.normal or (
          f.status == constant.FStatus.pause and
          f.is_mwarehouse_short()):
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
      # 如果成品库已达停产上限，但处于触发物流状态，则进入停产状态，后续物流照常
      if f.name not in [constant.FName.aircraft_assembly,
                        constant.FName.automobile_assembly]:
        if f.status in [constant.FStatus.normal,
                        constant.FStatus.recharge,
                        constant.FStatus.pause]:
          if f.is_pwarehouse_full():
            if f.status != constant.FStatus.pause:
              #print("$$$ %s：成品库满，%s -> 停产" % (f.name, f.status))
              f.status = constant.FStatus.pause
              f.pc_actual = 0 # update 实际用电
          elif not f.is_mwarehouse_short() and f.status == constant.FStatus.pause:
            #print("@@@ %s：停产 -> 正常" % f.name)
            f.status = constant.FStatus.normal
            f.pc_actual = f.pc_plan
      
    # plan the production - recursive!
    def plan(self, f):
      m_orders = f.plan()
      for order in m_orders:
        m_supplier = self.get_factory(order.supplier_name,0) # id - depends
        m_supplier.set_order(order)
        self.plan(m_supplier)
                
    # write periodic log to DB and csv
    def save_log(self, csvfile):
      with open(csvfile, 'w', newline='') as h:
        w = csv.writer(h)
        w.writerow(["厂名","Id","状态","仓库","品名","订购总数","当前库存","已完成数量","生产/消耗速度","计划多久","已花多久","还需多久","能耗"])
        
        skip_list = [constant.FName.power_station,
                     constant.FName.harbor,
                     constant.FName.community]
        for fname in constant.dict_fname.values():
          if fname not in skip_list:
            _save_log_f(w, self.dict_f[fname], self.db)
     
      h.close()
      
    def get_factory(self, fname, fid):
      if fname in self.dict_f:
        if fid < len(self.dict_f[fname]):
          return self.dict_f[fname][fid]
        else:
          print("!!! No such fid: %d, total # of %s: %d" % (fid,fname,len(self.dict_f[fname])))
      else:
        print("!!! No such fname: %s" % fname)
      return None
      
    # return a new order:
    # random numbers (初始库存基数 * [lbm, ubm])
    def get_new_order(self, lbm, ubm, fname):
      # only one product!
      for i,v in self.config.f_stocks[fname][constant.WType.products].items():
        iname = i
        base = v["base"]
      qty = random.randint(lbm, ubm) * base
      
      #supplier = self.get_factory(fname)
      r = ItemRecord(iname, qty)
      order = Order(fname)
      order.add(r)      
      order.display()
      return order
    
    # 日发电量 * 可用发电厂数
    def get_total_power(self):
      # check if power stations are under attack first!
      self.handle_attacks()
      power = 0
      for f in self.dict_f[constant.FName.power_station]:
        if f.status != constant.FStatus.under_attack:
          power += self.config.f_pc[f.name]
      return power
    
    
    # 根据当日发电量规划参与生产的工厂，并记录实际用电量
    # Add attack handling for power station! - 5/15/2020
    def plan_pc(self):
      # 实际发电能力（电厂可能遭攻击！）
      power_supply = self.get_total_power()
      print("计划用电：%.2f， 实际能提供：%.2f" % (self.power_estimation, power_supply))
      if power_supply <= 0:
        self.blackout_all()
      elif self.power_estimation > power_supply:
        self.blackout_factories(self.power_estimation - power_supply)
      else:
        print("实际发电能力足够!")
    
    # 能耗检查、预估次日用电量
    def check_pc(self, t):
      if t == 0:
        self.power_estimation = self.get_total_power()
        #print("首日发电预测：%.2f" % self.power_estimation)
      else:
        pc_actual = 0 # 当日实际能耗
        for fname in constant.dict_fname.values():
          if fname in self.dict_f and fname != constant.FName.power_station:
            for f in self.dict_f[fname]:
              #print("%s(id=%d, %s), pc_actual=%.2f" % (f.name, f.id+1, f.status, f.pc_actual))
              # !! Important: 先恢复停电的工厂能耗，再预估！
              if f.status == constant.FStatus.blackout:
                # !! Important: 停电工厂状态 -> 正常
                f.status = constant.FStatus.normal
                f.pc_actual = f.pc_plan # 停电结束后，能耗恢复!
              pc_actual += f.pc_actual
        #print("本日实际能耗：%.2f" % pc_actual)
        # 次日预测能耗
        self.power_estimation = pc_actual*(1+self.config.f_deviation[constant.FName.power_station])
        #print("发电预测：%.2f" % self.power_estimation)
    
    # shutdown all factories
    def blackout_all(self):
      print("没有电力，全部停产！")
      skip_list = [constant.FName.harbor]
      for fname in constant.dict_fname.values():
        if fname not in skip_list:
          for f in self.dict_f[fname]:
            if f.status != constant.FStatus.blackout:
              f.status = constant.FStatus.blackout
              f.pc_actual = 0 # update 实际用电
      
    # select factories to shutdown
    # To make sure:
    #   1. 被选工厂原来可以正常生产
    #   2. 被选工厂总耗电量 >= delta
    def blackout_factories(self, delta):
      print("实际发电总量不足，需要关闭若干工厂! delta = %.2f" % delta)
      saved_power = 0
      skip_list = [constant.FName.power_station,
                   constant.FName.harbor,
                   constant.FName.community]
      for fname in constant.dict_fname.values():
        if fname not in skip_list:
          if self.is_ok4blackout(fname):
            for f in self.dict_f[fname]:
              if f.status == constant.FStatus.normal:
                f.status = constant.FStatus.blackout
                print("%s(id=%d): %s, saved %.2f" % (f.name, f.id+1, f.status, f.pc_plan))
                saved_power += f.pc_plan
                f.pc_actual = 0 # update 实际用电
                break
            if saved_power >= delta:
              print("发电总量够了！")
              break

      if saved_power < delta:
        print("saved_power = %.2f, 发电总量还是不够！" % saved_power)
        self.blackout_by_order(delta - saved_power)

    def blackout_by_order(self, delta):
      print("开始从最下游关闭/停电工厂！")
      saved_power = 0
      fname_list = [constant.FName.petrochemical,
                    constant.FName.iron_making, constant.FName.alum_making,
                    constant.FName.chemical,
                    constant.FName.cold_rolling, constant.FName.hot_rolling,
                    constant.FName.plastic_parts,
                    constant.FName.iron_parts, constant.FName.alum_parts,
                    constant.FName.automobile_assembly,
                    constant.FName.aircraft_assembly]
      for fname in fname_list:
        for f in self.dict_f[fname]:
          if f.status in [constant.FStatus.normal,
                          constant.FStatus.recharge,
                          constant.FStatus.maintain]: # 维护要耗电！
            f.status = constant.FStatus.blackout
            print("%s(id=%d): %s, saved %.2f" % (f.name, f.id+1, f.status, f.pc_plan))
            saved_power += f.pc_plan
            f.pc_actual = 0 # update 实际用电
            if saved_power >= delta:
              break
        if saved_power >= delta:
          print("发电总量够了！")
          break
      print("Will save power %.2f" % saved_power)
      
    # 对于生产链中多于1家可以正常生产的厂, 返回True
    def is_ok4blackout(self, fname):
      if self.config.f_num[fname] == 1:
        return False
      else:
        cnt = 0
        for f in self.dict_f[fname]:
          if f.can_produce():
            cnt += 1
        return cnt > 1

    def is_underattack(self, fname, fid):
      f = self.get_factory(fname, fid)
      if f != None:
        return f.status == constant.FStatus.under_attack
      return False
      
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

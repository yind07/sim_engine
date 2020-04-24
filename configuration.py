# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 11:22:20 2020

@author: ydeng
"""
import math
import random
import pandas # get info from excel file

from constant import IName, FName, WType

class Config:
    def __init__(self, filename):
        print("Get static configuration info from %s" % filename)
        xls = pandas.ExcelFile(filename)
        
        self.__cfg_db(xls)
        #print("%s %s %s" % (self.ip, self.username, self.password))
        self.__cfg_factory(xls)
        self.__cfg_stocks(xls)
        
        #  TODO
        # 生产/消耗速度
        # 基数
        self.ratebase = {
            IName.aircraft: 1,
            IName.automobile: 1,
            IName.plastic_gear: 4,
            IName.plastic_lever: 2,
            IName.plastic_enclosure: 1,
            IName.iron_gear: 4,
            IName.iron_lever: 2,
            IName.iron_enclosure: 1,
            IName.alum_gear: 4,
            IName.alum_lever: 2,
            IName.alum_enclosure: 1,
            IName.pvc: 2,
            IName.pvc_hb: 1,
            IName.iron_shcc: 2,
            IName.iron_spcc: 1,
            IName.alum_shcc: 2,
            IName.alum_spcc: 1,
        }
        # 倍数
        self.ratemul = {
            FName.aircraft_assembly: {
                WType.products: 2,
                WType.materials: 500,
            },
            FName.automobile_assembly: {
                WType.products: 100,
                WType.materials: 500,
            },
            FName.plastic_parts: {
                WType.products: 500,
                WType.materials: 50,
            },
            FName.iron_parts: {
                WType.products: 500,
                WType.materials: 50,
            },
            FName.alum_parts: {
                WType.products: 500,
                WType.materials: 50,
            },
        }
        
        
        """self.crudeoil          
        self.hydrogen          
        self.alumina           
        self.benzene           
        self.toluene           
        self.ironstone         
        self.steel             
        self.bauxite           
        self.aluminium         
        self.pvc               
        self.pvc_hb            
        self.shcc              
        self.spcc              
        self.plastic_gear      
        self.plastic_lever     
        self.plastic_enclosure 
        self.iron_gear         
        self.iron_lever        
        self.iron_enclosure    
        self.alum_gear         
        self.alum_lever        
        self.alum_enclosure"""    
        
        
    def init_db(self):
        print("<TODO> Init DB tables")
        
    def get_init_qty(self, fname, wtype, iname):
        return rand_qty(self.f_stocks[fname][wtype][iname]["base"],
                      self.f_stocks[fname][wtype][iname]["ul"])
      
    def __cfg_db(self, h_xls):
        db = pandas.read_excel(h_xls, "database")
        self.ip = db.loc[0, "ip"]
        self.username = db.loc[0, "username"]
        self.password = db.loc[0, "password"]
        
    def __cfg_factory(self, h_xls):
        cfg_col_name = "名称"
        cfg_col_num = "初始化数量（<=10）"
        cfg_col_pc = "能耗（单位：千度/天）"
        cfg_col_mlen = "维修恢复时长（单位：时间周期）"

        self.f_num = {}   # 各厂数量
        self.f_pc = {}    # 各厂能耗（单位：1000 Kwh/周期）
        self.f_mlen = {}  # 各厂维修恢复时长（单位：时间周期）

        df = pandas.read_excel(h_xls, "factory")
        for i in range(len(df)):
          row = df.loc[i]
          key = FName.get(row[cfg_col_name])
          self.f_num[key] = row[cfg_col_num]
          self.f_pc[key] = row[cfg_col_pc]
          self.f_mlen[key] = row[cfg_col_mlen]
          
    def __cfg_stocks(self, h_xls):
        cfg_col_fname = "名称"
        cfg_col_wtype = "仓库"
        cfg_col_iname = "品名"
        cfg_col_rate = "生产/消耗速度"
        cfg_col_pauselimit = "停产上/下限" # 原料下限，成品上限
        cfg_col_restocklimit = "进货下限" # 仅对原料有效
        cfg_col_qtybase = "初始库存基数"
        cfg_col_qtyul = "初始库存上限"
        
        self.f_stocks = {}   # 各厂库存
        d = pandas.read_excel(h_xls, "stocks")
        for i in range(len(d)):
          row = d.loc[i]
          fname = row[cfg_col_fname]
          wtype = row[cfg_col_wtype]
          if not pandas.isna(fname):
            key_f = FName.get(fname) # key of factory name
            warehouses = {}
          if not pandas.isna(wtype):
            key_w = WType.get(wtype) # key of warehouse type
            items = {}
          items[IName.get(row[cfg_col_iname])] = {
            "rate": row[cfg_col_rate],
            "pause_limit": row[cfg_col_pauselimit],
            "restock_limit": row[cfg_col_restocklimit],
            "base": row[cfg_col_qtybase],
            "ul": row[cfg_col_qtyul],
          }
          warehouses[key_w] = items
          self.f_stocks[key_f] = warehouses
        self.__cal_bom()
          
    def __cal_bom(self):
      self.bom = {}
      for k_f,v_f in self.f_stocks.items():
        min_qty = get_min_qty(v_f[WType.products])
        materials = {}
        for k_m,v_m in v_f[WType.materials].items():
          materials[k_m] = v_m["rate"]/min_qty
        self.bom[k_f] = materials
      #print(self.bom)

def get_min_qty(dict_prod):
  min_qty = float("inf")  # 正无穷
  for k,v in dict_prod.items():
    if v["rate"] < min_qty:
      min_qty = v["rate"]
  return min_qty
          
def rand_qty(base, upperlimit):
    # ensure base, upperlimit > 0 and base < upperlimit
    if base <= 0 or upperlimit <= 0 or base >= upperlimit:
        print("Warning: Please use valid base and upperlimit. Current base = %d, ul = %d" % (base, upperlimit))
        return 1
    else: # 0 < base < upperlimit
        multiple = math.floor(upperlimit/base)
        return (random.randrange(multiple)+1) * base

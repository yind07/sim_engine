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
        self.deviation = 0.05  # 5%浮动，消耗/生产速度偏差(+/-)
        
        # TODO
        #   电厂
        #   居民区
        
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
    # TODO: init by warehouse goods ratebase ratio!!!   
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
        self.__fac_rate()
          
    def __cal_bom(self):
      self.bom = {}
      for k_f,v_f in self.f_stocks.items():
        min_qty = get_min_qty(v_f[WType.products])
        materials = {}
        for k_m,v_m in v_f[WType.materials].items():
          materials[k_m] = v_m["rate"]/min_qty
        self.bom[k_f] = materials
      #print(self.bom)
    
    # calculate ratebase and ratemul so that: rate = ratebase*ratemul
    def __fac_rate(self):
      self.ratebase = {} # for each factory+warehouse+item
      self.ratemul = {}  # 倍数：for each factory+warehouse
      
      for k_f,v_f in self.f_stocks.items():
        rb = {}
        rm = {}
        # 成品库
        rb_prod = {}
        min_qty = get_min_qty(v_f[WType.products])
        for k,v in v_f[WType.products].items():
          rb_prod[k] = v["rate"]/min_qty
          if rb_prod[k] == 1:
            rm[WType.products] = v["rate"]
        rb[WType.products] = rb_prod
        # 原料库
        rb_matr = {}
        min_qty = get_min_qty(v_f[WType.materials])
        for k,v in v_f[WType.materials].items():
          rb_matr[k] = v["rate"]/min_qty
          if rb_matr[k] == 1:
            rm[WType.materials] = v["rate"]
        rb[WType.materials] = rb_matr
        
        self.ratebase[k_f] = rb
        self.ratemul[k_f] = rm
      #print(self._ratebase)
      #print(self.ratemul)

    # return randome deviation within [-self.deviation, +self.deviation]
    def rand_deviation(self):
      multiple = 100 # precision == 2, ~0.01
      return random.randrange(multiple*self.deviation*2+1)/multiple - self.deviation

def get_min_qty(dic):
  min_qty = float("inf")  # 正无穷
  for k,v in dic.items():
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

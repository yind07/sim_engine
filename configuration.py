# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 11:22:20 2020

@author: ydeng
"""
import math
import random
import pandas # get info from excel file

from constant import FName
from warehouse import WType
from item import IName

# mapping for config file
cfg_fname_dict = {
  "飞机总装厂": FName.aircraft_assembly,
  "汽车总装厂": FName.automobile_assembly,
  "炼化厂":     FName.petrochemical,      
  "冶铁厂":     FName.iron_making,        
  "冶铝厂":     FName.alum_making,        
  "化工厂":     FName.chemical,           
  "热轧厂":     FName.hot_rolling,        
  "冷轧厂":     FName.cold_rolling,       
  "塑料零件厂": FName.plastic_parts,      
  "铁质零件厂": FName.iron_parts,         
  "铝质零件厂": FName.alum_parts,         
  "发电厂":     FName.power_station,      
}


class Config:
    def __init__(self, filename):
        print("Get static configuration info from %s" % filename)
        xls = pandas.ExcelFile(filename)
        
        self.__cfg_db(xls)
        #print("%s %s %s" % (self.ip, self.username, self.password))
        self.__cfg_factory(xls)
        self.__cfg_stocks(xls)
        
        # 初始库存(stock qty)Base及相应上限(upper limit)
        #   base: 库存Base
        #   ul:   库存上限（目前为库存Base的10倍）
        self.f = {
            FName.aircraft_assembly: {
                WType.products: {
                    IName.aircraft: {
                        "base": 5,
                        "ul": 50,
                    },
                },
                WType.materials: {
                    IName.plastic_gear: {
                        "base": 1000,
                        "ul": 10000,
                    },
                    IName.plastic_lever: {
                        "base": 500,
                        "ul": 5000,
                    },
                    IName.plastic_enclosure: {
                        "base": 600,
                        "ul": 6000,
                    },
                    IName.iron_gear: {
                        "base": 2000,
                        "ul": 20000,
                    },
                    IName.iron_lever: {
                        "base": 1000,
                        "ul": 10000,
                    },
                    IName.iron_enclosure: {
                        "base": 1000,
                        "ul": 10000,
                    },
                    IName.alum_gear: {
                        "base": 2000,
                        "ul": 20000,
                    },
                    IName.alum_lever: {
                        "base": 1200,
                        "ul": 12000,
                    },
                    IName.alum_enclosure: {
                        "base": 1500,
                        "ul": 15000,
                    },
                },
            },
            FName.automobile_assembly: {
                WType.products: {
                    IName.automobile: {
                        "base": 10,
                        "ul": 100,
                    },
                },
                WType.materials: {
                    IName.plastic_gear: {
                        "base": 500,
                        "ul": 5000,
                    },
                    IName.plastic_lever: {
                        "base": 300,
                        "ul": 3000,
                    },
                    IName.plastic_enclosure: {
                        "base": 300,
                        "ul": 3000,
                    },
                    IName.iron_gear: {
                        "base": 600,
                        "ul": 6000,
                    },
                    IName.iron_lever: {
                        "base": 800,
                        "ul": 8000,
                    },
                    IName.iron_enclosure: {
                        "base": 200,
                        "ul": 2000,
                    },
                    IName.alum_gear: {
                        "base": 800,
                        "ul": 8000,
                    },
                    IName.alum_lever: {
                        "base": 600,
                        "ul": 6000,
                    },
                    IName.alum_enclosure: {
                        "base": 500,
                        "ul": 5000,
                    },
                },
            },
        }

        # BOM表（目前和库存Base比例一致，各零件数量为Base的1/2）
        self.bom = {
            IName.aircraft: {
                IName.plastic_gear: 500,
                IName.plastic_lever: 250,
                IName.plastic_enclosure: 300,
                IName.iron_gear: 1000,
                IName.iron_lever: 500,
                IName.iron_enclosure: 500,
                IName.alum_gear: 1000,
                IName.alum_lever: 600,
                IName.alum_enclosure: 750,
            },
            IName.automobile: {
                IName.plastic_gear: 250,
                IName.plastic_lever: 150,
                IName.plastic_enclosure: 150,
                IName.iron_gear: 300,
                IName.iron_lever: 400,
                IName.iron_enclosure: 100,
                IName.alum_gear: 400,
                IName.alum_lever: 300,
                IName.alum_enclosure: 250,
            },
        }
        
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
        return rand_qty(self.f[fname][wtype][iname]["base"],
                      self.f[fname][wtype][iname]["ul"])
      
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
          key = cfg_fname_dict[row[cfg_col_name]]
          self.f_num[key] = row[cfg_col_num]
          self.f_pc[key] = row[cfg_col_pc]
          self.f_mlen[key] = row[cfg_col_mlen]
          
    def __cfg_stocks(self, h_xls):
        print("<TODO> __cfg_stocks")

def rand_qty(base, upperlimit):
    # ensure base, upperlimit > 0 and base < upperlimit
    if base <= 0 or upperlimit <= 0 or base >= upperlimit:
        print("Warning: Please use valid base and upperlimit. Current base = %d, ul = %d" % (base, upperlimit))
        return 1
    else: # 0 < base < upperlimit
        multiple = math.floor(upperlimit/base)
        return (random.randrange(multiple)+1) * base
        
        
    
       
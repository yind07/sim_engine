# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 11:22:20 2020

@author: ydeng
"""
import math
import random

from constant import FName
from warehouse import WType
from item import IName

class Config:
    def __init__(self, filename):
        print("Read %s: TODO" % filename)
        
        # DB info
        self.ip = "192.168.1.5"
        self.username = "test"
        self.password = "123456"
        
        # 各厂数量
        self.f_num = {
            FName.aircraft_assembly:    1,
            FName.automobile_assembly:  1,
            FName.petrochemical:        1,
            FName.iron_making:          1,
            FName.alum_making:          1,
            FName.chemical:             3,
            FName.hot_rolling:          2,
            FName.cold_rolling:         4,
            FName.plastic_parts:        6,
            FName.iron_parts:           10,
            FName.alum_parts:           8,
            FName.power_station:        2,
        }
        
        # 各厂能耗（单位：1000 Kwh/周期）
        self.f_pc = {
            FName.aircraft_assembly:    1.2,
            FName.automobile_assembly:  1.2,
            FName.petrochemical:        2.2,
            FName.iron_making:          2.5,
            FName.alum_making:          2.5,
            FName.chemical:             1.2,
            FName.hot_rolling:          1.6,
            FName.cold_rolling:         1.5,
            FName.plastic_parts:        1,
            FName.iron_parts:           1,
            FName.alum_parts:           1,
            FName.power_station:        0,
        }
        
        # 各厂维修恢复时间（单位：时间周期）
        self.f_mlen = {
            FName.aircraft_assembly:    2,
            FName.automobile_assembly:  1,
            FName.petrochemical:        3,
            FName.iron_making:          3,
            FName.alum_making:          3,
            FName.chemical:             5,
            FName.hot_rolling:          2,
            FName.cold_rolling:         2,
            FName.plastic_parts:        1,
            FName.iron_parts:           1,
            FName.alum_parts:           1,
            FName.power_station:        1,
        }
        
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
        print("Init DB tables: TODO")
        
    def get_init_qty(self, fname, wtype, iname):
      return rand_qty(self.f[fname][wtype][iname]["base"],
                      self.f[fname][wtype][iname]["ul"])

def rand_qty(base, upperlimit):
    # ensure base, upperlimit > 0 and base < upperlimit
    if base <= 0 or upperlimit <= 0 or base >= upperlimit:
        print("Warning: Please use valid base and upperlimit. Current base = %d, ul = %d" % (base, upperlimit))
        return 1
    else: # 0 < base < upperlimit
        multiple = math.floor(upperlimit/base)
        return (random.randrange(multiple)+1) * base
        
        
    
       
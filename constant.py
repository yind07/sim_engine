# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 13:04:25 2020

@author: ydeng
"""

from enum import Enum

# 物品(Item)名称
class IName(Enum):
    aircraft          = 1  # 飞机
    automobile        = 2  # 汽车
    crudeoil          = 3  # 原油
    hydrogen          = 4  # 氢气
    alumina           = 5  # 氧化铝（催化剂）
    benzene           = 6  # 苯
    toluene           = 7  # 甲苯
    ironstone         = 8  # 铁矿石
    iron              = 9  # 钢锭
    bauxite           = 10 # 铝矿石
    aluminium         = 11 # 铝锭
    pvc               = 12 # 聚氯乙烯
    pvc_hb            = 13 # 高苯聚氯乙烯
    iron_shcc         = 14 # 热轧钢板
    iron_spcc         = 15 # 冷轧钢板
    plastic_gear      = 16 # 塑料齿轮
    plastic_lever     = 17 # 塑料连杆
    plastic_enclosure = 18 # 塑料外壳
    iron_gear         = 19 # 铁质齿轮
    iron_lever        = 20 # 铁质连杆
    iron_enclosure    = 21 # 铁质外壳
    alum_gear         = 22 # 铝质齿轮
    alum_lever        = 23 # 铝质连杆
    alum_enclosure    = 24 # 铝质外壳
    alum_shcc         = 25 # 热轧铝板
    alum_spcc         = 26 # 冷轧铝板
    
    def __str__(self):
      for k,v in dict_iname.items():
        if v == self:
          return k
      return ">>> New IName: %s" % self.name
    
    def get(name_str): # return the enum value by name_str
      return dict_iname[name_str]
    
# 工厂名称
class FName(Enum):
    petrochemical       = 1  # 炼化厂
    iron_making         = 2  # 冶铁厂
    alum_making         = 3  # 冶铝厂
    chemical            = 4  # 化工厂
    hot_rolling         = 5  # 热轧厂
    cold_rolling        = 6  # 冷轧厂
    plastic_parts       = 7  # 塑料零件厂（注塑厂, injection_molding）
    iron_parts          = 8  # 铁质零件厂
    alum_parts          = 9  # 铝质零件厂
    automobile_assembly = 10 # 汽车总装厂
    aircraft_assembly   = 11 # 飞机总装厂
    power_station       = 12 # 发电厂
    
    def __str__(self):
      for k,v in dict_fname.items():
        if v == self:
          return k
      return ">>> New FName: %s" % self.name
    
    def get(name_str): # return the enum value by name_str
      return dict_fname[name_str]
    
# 仓库种类
class WType(Enum):
    materials = 1 # 工厂生产的输入
    products  = 2 # 工厂生产的输出
    
    def __str__(self):
      for k,v in dict_wtype.items():
        if v == self:
          return k
      return ">>> New WType: %s" % self.name
    
    def get(name_str): # return the enum value by name_str
      return dict_wtype[name_str]

# 工厂类型
class FType(Enum):
    def __str__(self):
        if self.name == "energy":
            return "能源工厂"
        elif self.name == "base":
            return "基础工厂"
        elif self.name == "materials":
            return "原料厂"
        elif self.name == "parts":
            return "零部件厂"
        elif self.name == "assembly":
            return "总装厂"
        return "FType.NEW"
    
    energy    = 0 # 能源工厂（目前只有发电厂）
    base      = 1 # 基础工厂
    materials = 2 # 原料厂
    parts     = 3 # 零部件厂
    assembly  = 4 # 总装厂    

# 工厂状态    
class FStatus(Enum):
    def __str__(self):
        if self.name == "normal":
            return "正常"
        elif self.name == "pause":
            return "暂停"
        elif self.name == "stop":
            return "停产"
        return "FStatus.NEW"
    
    normal  = 1     # 正常（可运转、在运转）
    pause   = 2     # 暂停（原料不够、成品达上限、维修、可恢复攻击）
    stop    = 3     # 停产（不可恢复攻击、电量不够）

# 事件类型    
class EventType(Enum):
    attack  = 1     # 攻击
    maintain = 2    # 维修
    purchase = 3    # 进货（原料）/物流
    manufacture = 4 # 生产

# name_str-FName mapping
dict_fname = {
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

# name_str-WType mapping
dict_wtype = {
  "原料库": WType.materials,
  "成品库": WType.products,
}

# name_str-IName mapping
dict_iname = {
  "飞机": IName.aircraft,
  "汽车": IName.automobile,
  "原油": IName.crudeoil,
  "氢气": IName.hydrogen,
  "氧化铝（催化剂）": IName.alumina,
  "苯": IName.benzene,
  "甲苯": IName.toluene,
  "铁矿石": IName.ironstone,
  "钢锭": IName.iron,
  "铝矿石": IName.bauxite,
  "铝锭": IName.aluminium,
  "聚氯乙烯": IName.pvc,
  "高苯聚氯乙烯": IName.pvc_hb,
  "热轧钢板": IName.iron_shcc,
  "冷轧钢板": IName.iron_spcc,
  "热轧铝板": IName.alum_shcc,
  "冷轧铝板": IName.alum_spcc,
  "塑料齿轮": IName.plastic_gear,
  "塑料连杆": IName.plastic_lever,
  "塑料外壳": IName.plastic_enclosure,
  "铁质齿轮": IName.iron_gear,
  "铁质连杆": IName.iron_lever,
  "铁质外壳": IName.iron_enclosure,
  "铝质齿轮": IName.alum_gear,
  "铝质连杆": IName.alum_lever,
  "铝质外壳": IName.alum_enclosure,
}
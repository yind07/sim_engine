# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 13:04:25 2020

@author: ydeng
"""

from enum import Enum

# 工厂名称
class FName(Enum):
    def __str__(self):
        if self.name == "petrochemical":
            return "炼化厂"
        elif self.name == "iron_making":
            return "冶铁厂"
        elif self.name == "alum_making":
            return "冶铝厂"
        elif self.name == "chemical":
            return "化工厂"
        elif self.name == "hot_rolling":
            return "热轧厂"
        elif self.name == "cold_rolling":
            return "冷轧厂"
        elif self.name == "plastic_parts":
            return "塑料零件厂"
        elif self.name == "iron_parts":
            return "铁质零件厂"
        elif self.name == "alum_parts":
            return "铝质零件厂"
        elif self.name == "automobile_assembly":
            return "汽车总装厂"
        elif self.name == "aircraft_assembly":
            return "飞机总装厂"
        elif self.name == "power_station":
            return "发电厂"
        return "FName.NEW"
    
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

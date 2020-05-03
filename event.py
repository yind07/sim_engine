# -*- coding: utf-8 -*-
"""
Created on Sat May  2 17:10:18 2020

@author: ydeng
"""
# 物流事件
from constant import EventType

class Event:
  def __init__(self, t, etype, dest, src, idx, goods):
    self.time = t # 触发时间
    self.type = etype # EventType
    self.dest = dest # 接收方厂名
    self.src = src # 发送方厂名
    self.id = idx # order: 发送方 id; deliver: 接收方 id
    self.goods = goods # 相关货物 list
  
  def __str__(self):
    s = "%d(%s): %s, goods [\n" % (self.time, self.type, self.receiver_name)
    for i in self.goods:
      s += ("%s\n" % i)
    s += "]"
    return s
  
  def __lt__(self, other):
    return self.time < other.time
  
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 22:35:05 2020

@author: ydeng
"""

class Database:
  def __init__(self, dbtype):
    print("<TODO> %s: Set DB type" % self.__class__)
    self.type = dbtype
    
  def connect(self, ip, uname, password):
    print("<TODO> %s: Connect to DB, return boolean" % self.connect.__name__)
    return True
  
  def get_attack(self):
    print("<TODO> %s: return(fname, fid, tlen)" % __name__)
  
  # return true if mname is ready, return false otherwise
  def is_module_ready(self, mname):
    print("<TODO> %s: Check if %s is ready, return boolean" % (self.is_module_ready.__name__, mname))
    return True
  
  def add_daily_summary(fname, fid, wtype, cname, rate, order_qty, stock_qty, qty_sum, exp_tlen):
    print("<TODO> %s: return boolean" % (self.add_daily_summary.__name__))
    
  # many set functions - change DB dynamically
  
  
    
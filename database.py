# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 22:35:05 2020

@author: ydeng
"""
import sys
import MySQLdb

class Database:
  def __init__(self, cfg):
    dbname = 'sim'
    self.db = MySQLdb.connect(cfg.ip, cfg.username, cfg.password, dbname, charset='utf8')
    print("Connected to DB successfully.")
    self.db.autocommit(True)
    
  def get_attack(self):
    print("<TODO> %s: return(fname, fid, tlen)" % __name__)
  
  # return true if mname is ready, return false otherwise
  def is_module_ready(self, mname):
    print("<TODO> %s: Check if %s is ready, return boolean" % (self.is_module_ready.__name__, mname))
    return True
  
  def clear_table(self, tbl_name):
    c = self.db.cursor()
    c.execute("TRUNCATE %s" % tbl_name)
    c.close()

  def add_daily_log(self, fname, fid, fstatus, wtype, iname, rate, order_qty, stock_qty, qty_sum, exp_tlen, ideal_tlen, actual_tlen, energy):
    #print("<TODO> %s: return boolean" % (self.add_daily_summary.__name__))
    #tbl_name = "daily_logs"
    tbl_name = "daily_logs_new2"
    c = self.db.cursor()
    query = "INSERT INTO %s values ('%s',%d,'%s','%s','%s',%d,%.2f,%d,%.2f,%d,%d,%d,%.2f)" % (tbl_name, fname,fid,fstatus,wtype,iname,order_qty,stock_qty,qty_sum,rate,ideal_tlen,actual_tlen,exp_tlen,energy)
    #query = "INSERT INTO %s values ('%s',%s,'%s','%s','%s',%s,%s,%s,%s,%s)" % (tbl_name, fname,fid,fstatus,wtype,iname,order_qty,stock_qty,qty_sum,rate,exp_tlen)
    #print(query)
    c.execute(query) #c.execute(query.encode("cp936"))
    c.close()
    #quit()
    #sys.exit(0)

  # many set functions - change DB dynamically
  
  
    
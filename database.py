# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 22:35:05 2020

@author: ydeng
"""
import sys
import MySQLdb
from constant import FName, WType

class Database:
  def __init__(self, cfg):
    dbname = 'sim'
    self.db = MySQLdb.connect(cfg.ip, cfg.username, cfg.password, dbname, charset='utf8')
    print("Connected to DB successfully.")
    self.db.autocommit(True)
  
  # return dict: key=fname, val=dict_1 (key=fid(0-9), val=0/1)
  # 0为正常，1为攻击状态
  def get_attack(self):
    #print("%s" % __name__)
    tbl_name = "attacksignal"
    c = self.db.cursor()
    query = "SELECT * FROM %s" % tbl_name
    c.execute(query)
    
    attack_info = {}
    
    # meaning for column index
    i_id = 0
    i_type = 1
    i_count = 2
    i_status = 3
    result = c.fetchall()
    for row in result:
      fname = FName.get(row[i_type])
      if fname not in attack_info:
        attack_info[fname] = {}
      fid = (row[i_id]-1) % 10
      status = int.from_bytes(row[i_status], "little")
      attack_info[fname].update({fid: status})
    c.close()
    return attack_info
  
  # return true if mname is ready, return false otherwise
  def is_module_ready(self, mname):
    print("%s: Check if %s is ready, return boolean - <depends>" % (self.is_module_ready.__name__, mname))
    return True
  
  def clear_table(self, tbl_name):
    c = self.db.cursor()
    c.execute("TRUNCATE %s" % tbl_name)
    c.close()

  def add_daily_log(self, fname, fid, fstatus, wtype, iname, rate, order_qty, stock_qty, qty_sum, exp_tlen, ideal_tlen, actual_tlen, energy):
    tbl_name = "daily_logs"
    c = self.db.cursor()
    if wtype == WType.products:
      query = "INSERT INTO %s values ('%s',%d,'%s','%s','%s',%d,%.2f,%d,%.2f,%d,%d,%d,%.2f)" % (tbl_name, fname,fid,fstatus,wtype,iname,order_qty,stock_qty,qty_sum,rate,ideal_tlen,actual_tlen,exp_tlen,energy)
    #query = "INSERT INTO %s values ('%s',%s,'%s','%s','%s',%s,%s,%s,%s,%s)" % (tbl_name, fname,fid,fstatus,wtype,iname,order_qty,stock_qty,qty_sum,rate,exp_tlen)
    elif wtype == WType.materials:
      query = "INSERT INTO %s values ('%s',%d,'%s','%s','%s',NULL,%.2f,NULL,%d,NULL,NULL,NULL,%.2f)" % (tbl_name, fname,fid,fstatus,wtype,iname,stock_qty,rate,energy)
    else: # so far for power station ONLY!
      query = "INSERT INTO %s values ('%s',%d,'%s','N/A','N/A',NULL,0,NULL,0,NULL,NULL,NULL,0)" % (tbl_name, fname,fid,fstatus)      
    #print(query)
    c.execute(query) #c.execute(query.encode("cp936"))
    c.close()
    #quit()
    #sys.exit(0)

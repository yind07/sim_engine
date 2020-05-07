# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 18:46:53 2020

@author: ydeng
"""
import sys

from simulation import Simulation
from configuration import Config
from database import Database

day_by_sec = 1 # by default, one day as 1 second.
if len(sys.argv) > 2:
  print("Usage: python main.py <day_by_seconds>")
elif len(sys.argv) == 1:
  print("Default one day as 1 second. You can use python main.py <length_by_seconds> to specify.")
else:
  day_by_sec = int(sys.argv[1])
  print("Use %d seconds as one day" % day_by_sec)
    
cfg = Config("config.xlsx")
db = Database(cfg)

modules = ["m1", "m2"]
for m in modules:
  while not db.is_module_ready(m):
    pass
  print("%s is ready" % m)
    
s = Simulation(cfg, db, day_by_sec)
s.run()
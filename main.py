# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 18:46:53 2020

@author: ydeng
"""

from simulation import Simulation
from configuration import Config
from database import Database

cfg = Config("config.xlsx")

db = Database("mysql")
modules = ["m1", "m2"]
if db.connect(cfg.ip, cfg.username, cfg.password):
  for m in modules:
    while not db.is_module_ready(m):
      pass
    print("%s is ready" % m)
    
  s = Simulation(cfg, 5)
  s.run()
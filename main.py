# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 18:46:53 2020

@author: ydeng
"""

from simulation import Simulation
from configuration import Config

cfg = Config("static_configuration_file")
s = Simulation(cfg, 5)
s.run()
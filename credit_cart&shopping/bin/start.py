# -*- coding:utf-8 -*-
#Author:Kris
import sys,os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from core import main

main.run()


# -*- coding:utf-8 -*-
#Author:Kris

import os,sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

#print(sys.path)

from core import main
from conf import settings

if __name__ == '__main__':
    obj = main.Manage_center()
    obj.run()


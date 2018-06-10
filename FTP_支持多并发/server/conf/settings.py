# -*- coding:utf-8 -*-
#Author:Kris
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACCOUNTS_FILE = os.path.join(BASE_DIR, 'conf', 'accounts.ini')

HOST = '127.0.0.1'
PORT = 8080

MAX_CONCURRENT_COUNT = 10
# -*- coding:utf-8 -*-
#Author:Kris

import logging,sys,os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

def card_log(username,log):
#定义一个信用卡日志函数
    log_path = BASE_DIR+r'\log\card_log\%s_card.log'%username
    logger = logging.getLogger('Test_LOG')
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(log_path,encoding='utf-8') #将日志打印到log目录下的日志文件中
    fh.setLevel(logging.INFO)

    fh_format = logging.Formatter('%(asctime)s %(message)s',datefmt='%m/%d/%Y %H:%M:%S')
    fh.setFormatter(fh_format)

    logger.addHandler(fh)
    logger.info(log)

    logger.removeHandler(fh)  #避免打印重复日志

def shop_log(username,log):
#定义一个购物日志函数
    log_path = BASE_DIR + r'\log\shop_log\%s_shop.log' % username

    logger = logging.getLogger('Test_LOG')
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(log_path,encoding='utf-8')
    fh.setLevel(logging.INFO)

    fh_format = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    fh.setFormatter(fh_format)

    logger.addHandler(fh)
    logger.info(log)

    logger.removeHandler(fh)
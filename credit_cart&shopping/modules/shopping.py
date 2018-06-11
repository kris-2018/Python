# -*- coding:utf-8 -*-
#Author:Kris
import os,sys,logging
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
shop_path = BASE_DIR+r'\db\product_list'
shop_car_path = BASE_DIR+r'\db\shop_car'
#shop_car_paths = shop_car_path + '\%s_shopcar.txt %user_account["username"]'

db_path = BASE_DIR + r'\db\user_info'
log_path = BASE_DIR+r'\log\shop_log\%s_shop.log %user_account["username"]'
from core import main
from log import loggers

def shopping(user_account):
#定义一个购物商城函数
    shopcar_list,pro_list = [],[] #shopcar_list:购物车列表   pro_list:商品清单列表
    with open(shop_path,'r',encoding='utf-8') as fh:
        for item in fh:
            pro_list.append(item.strip('\n').split())
    def shop_info():
        print("\t编号\t\t\t商品\t\t\t价格")
        for index,item in enumerate(pro_list):
            print('\t %s\t\t\t%s\t\t%s'%(index,item[0],item[1]))
    while True:
        print(("\033[32;0m目前商城在售的商品信息\033[0m").center(40, "-"))
        shop_info()
        choice_id = input("\n\33[34;0m选择要购买的商品编号ID /【返回输入b】\33[0m：")
        if choice_id.isdigit():
            choice_id = int(choice_id)
            if choice_id < len(pro_list) and choice_id >= 0:    #判断用户选择商品编号是否大于商品清单列表最大值
                pro_item = pro_list[choice_id]      #定义一个 pro_item 变量存储 用户选择的商品 信息和价格
                num = input('\033[34;1m选择商品数量>>>\033[0m')
                if num.isdigit():
                    num = int(num)
                    if num > 0:
                        print("\33[31;0m商品 %s 加入购物车 价格%s 数量%s\33[0m" % (pro_item[0], pro_item[1],num))
                        shopcar_list.append(pro_item)
                        shop_car_paths = shop_car_path+'\%s_shopcar.txt'%user_account['username']
                        with open(shop_car_paths,'a',encoding='utf-8') as fc:
                            fc.write(str('%s\t%s\t%s')%(pro_item[0],pro_item[1],num) +'\n')
                    else:
                        print('\033[31;1m购买数量不得为0\033[0m')
                else:
                    print('\033[31;1m请输入有效购买数量\033[0m')
            else:
                print("\33[31;0m错误：没有相应的编号 请重新输入:\33[0m\n")
        elif choice_id == "b":
            main.shop_info()
        else:
            print("\33[31;0m错误：没有相应的编号 请重新输入:\33[0m\n")

def shop_car(user_account):
#定义一个购物车函数
    money_list,product_list= [],[]
    product_info = ''
    shop_car_paths = shop_car_path + '\%s_shopcar.txt' % user_account['username']
    if not os.path.isfile(shop_car_paths):
        print('\033[31;1m您还未有购物记录，请先进入商城购物\033[0m')
        shopping(user_account)
    else:
        with open(shop_car_paths,'r',encoding='utf-8')as fc:
            print(('\033[32;1m购物车清单\033[0m').center(32, '-'))
            print("编号\t\t商品\t\t价格\t\t数量")
            lock_list = fc.readlines()
            for index ,lock_info in enumerate(lock_list):
                lock = lock_info.split()
                product_name = lock[0]
                money = lock[1]
                num = lock[2]
                print('%s\t\t%s\t%s\t\t%s'%(index,product_name,money,num))
                moneys = int(money)*int(num) #定义moneys变量来计算 单个商品总金额 = 商品金额*数量
                product_info = '%s商品%s件'%(product_name,num)  #定义打印商品名称及数量 字符串
                money_list.append(moneys) #将单个商品总金额 添加至 金额列表中
                product_list.append(product_info) #将product_info添加至 购物信息列表中

        if sum(money_list) == 0 : # sum(money_list) = 购物车所有商品总金额
            print('\033[31;1m购物车空空如也\033[0m')
        else:
            db_path_user = db_path + '\%s.json' % user_account["username"]
            with open(db_path_user, 'r',encoding='utf-8') as fh:
                fr = fh.read()
                fd = eval(fr)
            print('\n\33[33;0m您当前余额为 %s 元，当前商品金额为 %s 元'%(fd['balance'],sum(money_list)))
            go_shop = input("\n\33[34;0m是否选择购买 "
                            "任意键：购买 /【返回输入b】\33[0m：")  #使用sum方法求出购物车商品总支付金额
            if go_shop == 'b':
                main.shop_info()
            else:
                if sum(money_list) < fd["balance"]:  #判断用户余额买得起购物商品
                    balance = fd["balance"] - sum(money_list)  # 当前余额 = 原余额-商品总额
                    log = ('\033[31;1m尊敬的用户您已成功购物 %s ，购物总额为 %s 元，您购物后余额: %s元!\033[0m'
                           %(str(product_list),sum(money_list),balance))
                    loggers.shop_log(user_account['username'],log)  # 调用购物日志打印函数
                    print("\033[33;1m购物成功！余额为: ￥%s\033[0m" % balance)
                    with open(db_path_user,'w',encoding='utf-8') as fh:
                        res = fr.replace(str(fd["balance"]), str(balance))  # 修改用户文件操作
                        fh.write(res)
                    shop_car_paths = shop_car_path + '\%s_shopcar.txt %user_account["username"]'
                    with open(shop_car_paths,'w',encoding='utf-8') as fc:
                        #fc.seek(0)
                        fc.truncate(0)   #购物支付完成后 购物车文件清空
                else:
                    print("\33[31;0m对不起您的余额不足无法购买:\33[0m\n")
    main.shop_info()

def center(user_account):
#定义一个查看购物记录的函数
    if not os.path.isfile(log_path % user_account["username"]):
        print('\033[31;1m当前用户无流水记录\033[0m')
    else:
        with open(log_path % user_account["username"], 'r', encoding='utf-8') as fh:
            for line in fh:
                print(line)
    main.shop_info()
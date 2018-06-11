# -*- coding:utf-8 -*-
#Author:Kris

import sys,os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from core import auth
from modules import creditcard
from modules import shopping
from modules import admincenter

#用户数据信息
user_data = {
    'account_id':None,          #帐号ID
    'is_authenticated':False,  #是否认证
    'account_data':None        #帐号数据
 }

def run():
#定义一个主界面函数
    while True:
        print('''\033[31;0m ----------欢迎来到ATM电子商务运行----------
                1.信用卡中心
                2.购物中心
                3.管理中心
                4.退出\033[0m''')
        inputs = input('\033[34;1m请选择操作方式>>>:\033[0m').strip()
        dict = {
            '1':card_info,
            '2':shop_info,
            '3':admin_info
        }
        if inputs in dict.keys():
            dict[inputs]()
        elif inputs == '4':
            exit('程序退出 欢迎下次使用')
        else:
            print('\033[31;1m请输入有效操作方式\033[0m')

def admin_info():
#定义一个管理员权限用户主函数
    auth_user()    #调用用户认证接口
    if user_data['account_data']['type'] == 1:
        while True:
            print('''\033[31;0m------------欢迎 %s 来到信用卡管理中心-----------
                        1.发行信用卡
                        2.冻结信用卡
                        3.解冻信用卡
                        4.提升信用卡额度
                        5.返回主菜单
                        6.退出\033[0m'''%user_data['account_data']["username"])
            inputs = input('\033[35;1m请选择操作方式>>>:\033[0m').strip()
            menu_dic = {
                "1": admincenter.banks,
                "2": admincenter.freezing,
                "3": admincenter.defrosting,
                "4": admincenter.limit,
            }
            if inputs in menu_dic.keys():
                menu_dic[inputs](user_data['account_data'])
            elif inputs == '5':
                break
            elif inputs == '6':
                exit('程序退出 欢迎下次使用')
            else:
                print('\033[31;1m请输入有效操作方式\033[0m')
    else:
        exit('对不起您的账号权限不足无法登录该模块')
def shop_info():
#定义一个用户购物的主函数
    auth_user() #调用用户认证接口
    while True:
        print('''\033[31;0m---------------欢迎来到购物中心---------------
                    1.购物商城
                    2.查看购物车
                    3.查看购物记录
                    4.返回主菜单
                    5.退出\033[0m''')
        menu_dic = {
            '1':shopping.shopping,
            '2':shopping.shop_car,
            '3':shopping.center
        }
        inputs = input('\033[35;1m请选择操作方式>>>:\033[0m').strip()
        if inputs in menu_dic.keys():
            menu_dic[inputs](user_data['account_data'])
        elif inputs == '4':
            break
        elif inputs == '5':
            exit('程序退出 欢迎下次使用')
        else:
            print('\033[31;1m请输入有效操作方式\033[0m')
def card_info():
#定义一个信用卡管理中心的主函数
    auth_user() #调用用户认证接口
    while True:
        print('''\033[31;0m ------------欢迎%s来到信用卡中心-----------
                    1.账户信息
                    2.存款
                    3.提现
                    4.转账
                    5.账单
                    6.返回主菜单
                    7.退出
        \033[0m'''%user_data['account_data']["username"])
        user_account = user_data['account_data']
        inputs =  input('\033[35;1m请选择操作方式>>>:\033[0m').strip()
        menu_dic = {
            "1": creditcard.account_info,
            "2": creditcard.repay,
            "3": creditcard.withdraw,
            "4": creditcard.transfer,
            "5": creditcard.paycheck,
            }
        if inputs in menu_dic.keys():
            menu_dic[inputs](user_account)
        elif inputs == '6':
            break
        elif inputs == '7':
            exit('程序退出,欢迎下次使用')
        else:
            print('\033[31;1m请输入有效操作方式\033[0m')

@auth.accse_login(user_data)   #装饰器认证
def auth_user():
#调用 auth模块中的accse_login装饰器对用户进行登录认证
    print('\033[32;1m用户 %s 登录认证成功\033[0m'% user_data['account_data']["username"])

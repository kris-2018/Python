# -*- coding:utf-8 -*-
#Author:Kris

import os,sys
import hashlib
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

def accse_login(user_data):
#定义一个用户登录装饰器
    def out_wrapper(func):  #func接收 admin_info,shop_info,admin_info函数的返回值
        def wrapper(*args,**kwargs):
            count = 0
            if not user_data['is_authenticated'] and count < 3:
                print("\33[32;0m用户登录认证\33[0m".center(40, "-"))
                while count < 3:
                    user = input('\033[32;1m请输入用户名>>>:\033[0m')
                    db_path = BASE_DIR + r'\db\user_info'
                    db_path_user = db_path + '\%s.json' % user
                    if os.path.isfile(db_path_user):    #判断用户文件是否存在
                        with open(db_path_user, 'r', encoding='utf-8') as fh:
                            user_datas = eval(fh.read())    #将用户文件中内容转换为字典形式
                        pwd = input('\033[32;1m请输入用户密码>>>:\033[0m')
                        m = hashlib.md5()
                        m.update(pwd.encode())
                        if m.hexdigest() == user_datas['password'] :
                        #if pwd == user_datas['password']:
                            user_data['account_id'] = user_datas["cardid"]
                            user_data['is_authenticated'] = True
                            user_data['account_data'] = user_datas

                            break
                        else:
                            print('\033[31;1m密码错误请重新输入\033[0m')
                    else:
                        count += 1
                        print('\033[31;1m该用户不存在,请重新输入还剩 %s 次机会\033[0m'% (3-count))
                func(*args,**kwargs)
            return func
        return wrapper
    return out_wrapper



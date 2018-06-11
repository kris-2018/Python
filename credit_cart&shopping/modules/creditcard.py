# -*- coding:utf-8 -*-
#Author:Kris
import os,sys,logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
db_path = BASE_DIR + r'\db\user_info'
log_path = BASE_DIR+r'\log\card_log\%s_card.log'

from log import loggers

def account_info(user_account):
#定义一个查看用户信息的函数 user_account = user_data['account_data'] 接收用户字典信息

    db_path_user = db_path + '\%s.json' % user_account["username"]
    with open(db_path_user, 'r',encoding='utf-8') as fh:
        fd = eval(fh.read())
    print("\033[33;1m我的账户信息："
          "\n持卡人: %s "
          "\n卡号: %s"
          "\n存款: ￥%s"
          "\n可提现额度: ￥%s \033[0m"
          %(user_account["username"],user_account["cardid"],fd["balance"],fd["credit"]))
    inputs = input('\033[33;1m按任意键返回上一级菜单>>>:\033[0m')

def repay(user_account):
#定义一个用户存款函数
    db_path_user = db_path + '\%s.json' % user_account["username"]
    with open(db_path_user, 'r',encoding='utf-8') as fh:
        fr = fh.read()
        fd = eval(fr)
    print("\033[33;1m您的当前存款为: ￥%s "% fd["balance"])
    while True:
        repays = input('\033[33;1m请输入存款金额并确认存款，按Q取消存款>>>\033[0m')
        if repays.capitalize() == 'Q' :
            exit()
        else:
            if repays.isdigit():
                repays = int(repays)
                user_balance = fd["balance"] + repays  #当前存款=原存款+存款金额
                with open(db_path_user,'w',encoding='utf-8') as fh:
                    res = fr.replace(str(fd["balance"]),str(user_balance)) #修改用户文件操作
                    fh.write(res)
                    print('\033[33;1m尊敬的用户已为您成功存入 %s 元，您当前存款金额为 %s 元!\033[0m'
                          %(repays,user_balance))
                break
            else:
                print('\033[31;1m请输入有效存款金额\033[0m')
    log = ('\033[31;1m尊敬的用户已为您成功存入: %s元，您当前存款金额: %s元!\033[0m'
           % (repays, user_balance))
    loggers.card_log(user_account["username"], log)

def withdraw(user_account):
#定义一个用户提现函数
    db_path_user = db_path + '\%s.json' % user_account["username"]
    with open(db_path_user, 'r',encoding='utf-8') as fh:
        fr = fh.read()
        fd = eval(fr)
    print("\033[33;1m您的当前存款为: ￥%s" % fd["balance"])
    print("\033[33;1m您可提现额度为: ￥%s" % fd["credit"])
    while True:
        repays = input('\033[33;1m请输入提现金额，按Q取消提现>>>\033[0m')
        if repays.capitalize() == 'Q': #判断用户输入
            break
        else:
            if repays.isdigit():
                repays = int(repays)
                if repays > fd["credit"]:  #判断用户输入的提现金额是否大于现有存款
                    print('\033[31;1m提现金额不得大于可提现额度\033[0m')
                else:
                    print('\033[31;1m提现金额: ￥%s 手续费:￥%s \033[0m'%(repays,repays*0.05))
                    user_balance = fd["balance"] - (repays + repays * 0.05)  #提现后的用户余额
                    inputs = input('\033[33;1m请确认提现金额，按任意键提现>>>\033[0m')
                    if user_balance <= 0:    #判断结算后存款是否为负数，如结算后存款为负给出提示不让提现
                        print('\033[31;1m当前存款不足以提现\033[0m')
                    else:
                        user_credit = user_account["credit"] - repays  #提现后的可提现额度
                        print('\033[31;1m尊敬的用户您已成功提现 %s 元!\033[0m'% repays)
                        print("\033[33;1m您的当前存款为: ￥%s" % user_balance)
                        print("\033[33;1m您可提现额度为: ￥%s" % user_credit)
                        with open(db_path_user, 'w',encoding='utf-8') as fh:
                            res1 = fr.replace(str(fd["balance"]), str(user_balance)) #先扣除用户的余额
                            res2 = res1.replace(str(fd["credit"]), str(user_credit)) #然后扣除用户的可提现额度
                            fh.write(res2)   #将变更后的余额和提现额度重新写入json文本中
                        break
            else:
                print('\033[31;1m请输入有效提现金额\033[0m')
    log = ("\033[31;1m尊敬的用户您已成功提现: %s元 所剩存款: %s元 可提现金额为: %s元!\033[0m"
           % (repays, user_balance, user_credit))           #打印日志内容
    loggers.card_log(user_account["username"], log)         #传递参数给card_log日志主函数


def transfer(user_account):
#定义一个用户转账的函数
    count = 0
    while count < 3:
        transfer = input('\033[33;1m请输入需转账人用户名>>>\033[0m')
        db_path_user1 = db_path + '\%s.json' % transfer   #需被转账用户
        db_path_user2 = db_path + '\%s.json' % user_account["username"] #当前用户
        if transfer == user_account["username"]:
            print('\033[31;1m转账人不能是自己\033[0m')
        else:
            if os.path.isfile(db_path_user1):  # 判断用户文件是否存在
                with open(db_path_user1, 'r',encoding='utf-8') as fh:
                    frh = fh.read()
                    fd = eval(frh) #需被转账用户
                with open(db_path_user2,'r',encoding='utf-8') as fw:
                    frw = fw.read()
                    fc = eval(frw)  #当前用户
                    print('\033[33;1m转账用户信用卡号为:\033[0m \033[32;1m %s \033[0m'%fd["cardid"])
                    while True:
                        money = input('\033[33;1m请输入需转账金额:\033[0m')
                        if money.isdigit():
                            money = int(money)
                            if money > fc["balance"]: #判断转账金额是否大于存款
                                print('\033[31;1m对不起您的存款不足,无法转账\033[0m')
                            else:
                                print('\033[31;1m转账用户卡号: %s 转账金额:￥%s\033[0m'
                                % (fd["cardid"],money))
                                inputs = input('\033[33;1m请再次确认转账信息数据:按Q|q取消>>>\033[0m')
                                if inputs.capitalize() == 'Q':
                                    break
                                else:
                                    user_balance1 = fc["balance"] - money   #当前用户转账后余额
                                    with open(db_path_user2,'w',encoding='utf-8') as fw:
                                        res1 = frw.replace(str(fc["balance"]),str(user_balance1))
                                        fw.write(res1)
                                        print('\033[33;1m您转账后存款为: ￥%s '%user_balance1)
                                    user_balance2 = fd["balance"] + money   #需被转账用户转账后余额
                                    with open(db_path_user1,'w',encoding='utf-8') as fh:
                                        res2 = frh.replace(str(fd["balance"]), str(user_balance2))
                                        fh.write(res2)
                                    log = ('\033[31;1m您为卡号:%s 用户转账: %s元 您当前存款金额: %s元!\033[0m'
                                           % (fd["cardid"], money, user_balance1))
                                    loggers.card_log(user_account["username"], log)
                            break
                        else:
                            print('\033[31;1m请输入有效转账金额\033[0m')
            else:
                count += 1
                print('\033[31;1m该用户不存在,请重新输入还剩 %s 次机会\033[0m' % (3 - count))

        break

def paycheck(user_account):
    if not os.path.isfile(log_path % user_account["username"]):
        print('\033[31;1m当前用户无流水记录\033[0m')
    else:
        with open(log_path % user_account["username"], 'r', encoding='utf-8') as fh:
            for line in fh:
                print(line)


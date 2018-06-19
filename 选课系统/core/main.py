# -*- coding:utf-8 -*-
#Author:Kris
import os,sys,shelve
from conf import settings
from modules.school import School

class Manage_center(object):
    # def __init__(self):
    #     pass
    def run(self):
        while True:
            print("\033[31;0m欢迎进入选课系统\033[0m\n"
                  "\033[34;0m1 学生视图\033[0m\n"
                  "\033[34;0m2 教师视图\033[0m\n"
                  "\033[34;0m3 管理视图\033[0m\n"
                  "\033[34;0m4 退出学员管理系统(请按q)\033[0m\n")
            user_choice = input("\033[35;0m请输入您要进入的视图序号:\033[0m")
            if user_choice == '1':
                Manage_student()
            elif user_choice == '2':
                Manage_teacher()
            elif user_choice == '3':
                Manage_school()
            elif user_choice == 'q':
                print("\033[31;0m感谢使用学员管理系统\033[0m")
                break
            else:
                print("请输入正确的选项")

class Manage_school(object):
    '''学校管理视图'''
    def __init__(self):  #为对象定制对象自己独有的特征
        if os.path.exists(settings.school_db_file+".dat"): #shelve会生成三个文件，其中有.dat结尾
            self.school_db = shelve.open(settings.school_db_file)  #打开学校数据库文件
            self.run_manage()   #运行管理视图
            self.school_db.close()  #关闭数据库文件
        else:
            print("系统信息：初始化数据库")
            self.initialize_school()  #初始化数据库
            self.run_manage()
            self.school_db.close()

    def initialize_school(self):  ##初始化两所学校
        self.school_db = shelve.open(settings.school_db_file)
        self.school_db['北京'] = School('北京', '中国.北京')
        self.school_db['上海'] = School('上海', '中国.上海')
    def run_manage(self):
        '''运行学校管理视图 '''
        while True:
            for key in self.school_db:
                print("\033[31;0m学校名称：\033[0m",key)
            choice_school = input("\033[31;0m输入要管理的学校名:\033[0m").strip()
            if choice_school in self.school_db:
                self.choice_school = choice_school
                self.school_obj = self.school_db[choice_school] #取出value值
                while True:
                    print("\n\033[31;0m欢迎来到老男孩%s校区\033[0m\n"
                          "\033[34;0m添加课程 add_course\033[0m\n"
                          "\033[34;0m增加班级 add_class\033[0m\n"
                          "\033[34;0m招聘讲师 add_teacher\033[0m\n"
                          "\033[34;0m查看课程 check_course\033[0m\n"
                          "\033[34;0m查看班级 check_class\033[0m\n"
                          "\033[34;0m查看讲师 check_teacher\033[0m\n"
                          "\033[34;0m退出程序 exit\033[0m\n"% self.choice_school) ##也有可以self.school_obj.school_name
                    user_func = input("\033[35;0m输入要操作的\033[34;0m英文指令:\033[0m").strip()
                    if hasattr(self,user_func):
                        getattr(self,user_func)()
            else:
                print("输入错误：请输入正确的学校名>>")

    def add_course(self):
        course_name = input("输入要添加课程的名称:").strip()
        course_price = input("输入要添加课程的价格:").strip()
        course_time = input("输入要添加课程的周期:").strip()
        if course_name in self.school_obj.school_course:  #判断课程是否已经添加过
            print("课程存在")
            self.school_obj.create_course(course_name, course_price, course_time)
            print("课程更新完成")
        else:
            self.school_obj.create_course(course_name,course_price,course_time)
            print("课程添加成功")
        self.school_db.update({self.choice_school: self.school_obj}) #更新数据库数据 k:v

    def add_class(self):
        class_name = input("输入要添加班级的名称：").strip()
        course_name = input("输入要关联的课程：").strip()
        if class_name not in self.school_obj.school_class:
            if course_name in self.school_obj.school_course:
                course_obj = self.school_obj.school_course[course_name]
                self.school_obj.create_class(class_name,course_obj)
                self.school_db.update({self.choice_school: self.school_obj})  # 更新数据库数据
                print("班级创建成功")
            else:
                print("\33[31;1m系统错误：关联的课程不存在\33[0m")
        else:
            print("\33[31;1m系统错误：班级已经存在\33[0m")

    def add_teacher(self):
        teacher_name = input("输入要招聘教师的名称：").strip()
        teacher_salary = input("输入教师的薪资：").strip()
        teacher_class = input("输入要关联的班级：").strip()
        if teacher_class in self.school_obj.school_class:  #判断班级是否存在
            class_obj = self.school_obj.school_class[teacher_class] #获取班级名对应的实例
            if teacher_name not in self.school_obj.school_teacher:#判断招聘教师是否存在，不存在创建，存在更新
                self.school_obj.create_teacher(teacher_name,teacher_salary,teacher_class,class_obj)
                print("新讲师招聘成功")
            else:
                self.school_obj.update_teacher(teacher_name, teacher_class, class_obj)
                print("讲师已经存在，信息更新完成")

            self.school_db.update({self.choice_school: self.school_obj})  # 更新数据库数据
        else:
            print("\33[31;1m系统错误：关联的班级不存在\33[0m")

    def check_course(self):
        self.school_obj.show_course()

    def check_class(self):
        self.school_obj.show_class()

    def check_teacher(self):
        self.school_obj.show_teacher()

    def exit(self):
        self.school_db.close()
        sys.exit("\033[32;1m欢迎下次使用学员管理系统\033[0m")

class Manage_student(object):
    '''学生视图'''
    def __init__(self):
        if os.path.exists(settings.school_db_file + ".dat"):  # shelve会生成三个文件，其中有.dat结尾
            self.school_db = shelve.open(settings.school_db_file)  # 打开学校数据库文件
            self.run_manage()  # 运行管理视图
            self.school_db.close()  # 关闭数据库文件
        else:
            print("数据库文件不存在，请先创建学校")
            exit()

    def run_manage(self):
        print("\n欢迎进入学员视图")
        for key in self.school_db:
            print("学校名称：", key)
        choice_school = input("输入选择注册的学校名:").strip()
        if choice_school in self.school_db:
            self.choice_school = choice_school
            self.school_obj = self.school_db[choice_school]
            student_name = input("输入学生的姓名：").strip()
            student_age = input("输入学生的年龄：").strip()
            self.school_obj.show_class_course()
            class_choice = input("输入上课的班级：").strip()
            if class_choice in self.school_obj.school_class:
                self.school_obj.create_student(student_name,student_age,class_choice)
                self.school_db.update({self.choice_school: self.school_obj})  # 更新数据库数据
                print("学生注册成功")
            else:
                print("\33[31;1m系统错误：输入的班级不存在\33[0m")
        else:
            print("\33[31;1m系统错误：输入的学校不存在\33[0m")


class Manage_teacher(object):
    '''教师视图'''
    def __init__(self):
        if os.path.exists(settings.school_db_file + ".dat"):  # shelve会生成三个文件，其中有.dat结尾
            self.school_db = shelve.open(settings.school_db_file)  # 打开学校数据库文件
            self.run_manage()  # 运行管理视图
            self.school_db.close()  # 关闭数据库文件
        else:
            print("数据库文件不存在，请先创建学校")
            exit()

    def run_manage(self):
        for key in self.school_db:
            print("学校名称：", key)
        choice_school = input("输入选择学校名:").strip()
        if choice_school in self.school_db:
            self.choice_school = choice_school
            self.school_obj = self.school_db[choice_school]
            teacher_name = input("输入登录讲师的姓名：").strip()
            while True:
                if teacher_name in self.school_obj.school_teacher:
                    print("\033[31;0m欢迎来到教师中心\033[0m\n"
                          "查看班级 check_class\n"
                          "退出程序 exit\n" )
                    user_func = input("输入要操作的命令：").strip()
                    if hasattr(self, user_func):
                        getattr(self, user_func)(teacher_name)
                else:
                    print("讲师不存在")

    def check_class(self,teacher_name):
        self.school_obj.show_teacher_classinfo(teacher_name)

    def exit(self,*args):
        self.school_db.close()
        sys.exit("欢迎下次使用学员管理系统")
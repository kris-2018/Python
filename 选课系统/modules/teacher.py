# -*- coding:utf-8 -*-
#Author:Kris

class Teacher(object):
    '''讲师类，定义teacher_name，teacher_salary，包含teacher_class'''
    def __init__(self, teacher_name, teacher_salary):
        self.teacher_name = teacher_name
        self.teacher_salary = teacher_salary
        self.teacher_calss = {}
    def teacher_add_class(self,class_name,class_obj):
        self.teacher_calss[class_name] = class_obj
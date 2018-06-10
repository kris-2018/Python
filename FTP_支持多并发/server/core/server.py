# -*- coding:utf-8 -*-
#Author:Kris

import os
import socket
import struct
import pickle
import hashlib
import subprocess
import queue
from conf import settings
from core.user_handle import UserHandle

#from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Lock

class FTPServer():
    MAX_SOCKET_LISTEN = 5
    MAX_RECV_SIZE = 8192

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((settings.HOST, settings.PORT))
        self.socket.listen(self.MAX_SOCKET_LISTEN)

        self.q = queue.Queue(settings.MAX_CONCURRENT_COUNT)  #可以配置最大并发数

    def server_accept(self):
        """等待client链接"""
        print('starting...')
        while True:
            self.conn,self.client_addr = self.socket.accept()
            print('客户端地址:', self.client_addr)

            #pool.submit(self.get_recv, self.conn)
        #self.server_accept.close()
            try:
                t = Thread(target=self.server_handle, args=(self.conn, ))
                self.q.put(t)
                t.start()
            except Exception as e:
                print(e)
                self.conn.close()
                self.q.get()

    def get_recv(self):
        """接收client发来的数据"""
        return pickle.loads(self.conn.recv(self.MAX_RECV_SIZE))

    def auth(self):
        """处理用户的认证请求
        1.根据username读取accounts.ini文件,password相比,判断用户是否存在
        2.将程序运行的目录从bin/ftp_server.py修改到用户home/alice,方便之后查询 ls
        3.给client返回用户的详细信息
        """
        while True:
            user_dic = self.get_recv()
            username = user_dic.get('username')
            user_handle = UserHandle(username)
            user_data = user_handle.judge_user()
            # 判断用户是否存在 返回列表
            #如[('password','202cb962ac59075b964b07152d234b70'),('homedir','home/alex'),('quota','100')]
            if user_data:
                if user_data[0][1] == hashlib.md5(user_dic.get('password').encode('utf-8')).hexdigest():  # 密码也相同
                    self.conn.send(struct.pack('i', 1)) #登录成功返回 1
                    self.username = username
                    self.homedir_path = '%s\%s\%s'%(settings.BASE_DIR, 'home', self.username)
                    os.chdir(self.homedir_path) #将程序运行的目录名修改到用户home目录下
                    self.quota_bytes = int(user_data[2][1]) * 1024 * 1024  #将用户配额的大小从M改到字节
                    user_info_dic = {
                        'username': username,
                        'homedir': user_data[1][1],
                        'quota': user_data[2][1]
                    }
                    self.conn.send(pickle.dumps(user_info_dic))  #用户的详细信息发送到客户端
                    return True
                else:
                    self.conn.send(struct.pack('i', 0))  #登录失败返回 0
            else:
                self.conn.send(struct.pack('i', 0))

    def readfile(self):
        """读取文件,得到文件内容的bytes型"""
        with open(self.filepath, 'rb') as f:
            filedata = f.read()
        return filedata

    def getfile_md5(self):
        """对文件内容md5"""
        return hashlib.md5(self.readfile()).hexdigest()

    def get(self):
        """从server下载文件到client
        """
        if len(self.cmds) > 1:
            filename = self.cmds[1]
            filepath = os.path.join(os.getcwd(), filename) #os.getcwd()得到当前工作目录
            if os.path.isfile(filepath): #判断文件是否存在
                exist_file_size = struct.unpack('i', self.conn.recv(4))[0]
                self.filepath = filepath
                header_dic = {
                    'filename': filename,
                    'file_md5': self.getfile_md5(),
                    'file_size': os.path.getsize(self.filepath)
                }
                header_bytes = pickle.dumps(header_dic)
                if exist_file_size:  #表示之前被下载过 一部分
                    self.conn.send(struct.pack('i', len(header_bytes)))
                    self.conn.send(header_bytes)
                    if exist_file_size != os.path.getsize(self.filepath):
                        with open(self.filepath, 'rb') as f:
                            f.seek(exist_file_size)
                            for line in f:
                                self.conn.send(line)
                    else:
                        print('断点和文件本身大小一样')
                else:  #文件第一次下载
                    self.conn.send(struct.pack('i', len(header_bytes)))
                    self.conn.send(header_bytes)
                    with open(self.filepath, 'rb') as f:
                        for line in f:
                            self.conn.send(line)
            else:
                print('当前目录下文件不存在')
                self.conn.send(struct.pack('i',0))
        else:
            print('用户没有输入文件名')

    def recursion_file(self,menu):
        """递归查询用户home/alice目录下的所有文件，算出文件的大小"""
        res = os.listdir(menu) #指定目录下所有的文件和和目录名
        for i in res:
            path = '%s\%s' % (menu, i)
            if os.path.isdir(path):#判断指定对象是否为目录
                self.recursion_file(path)
            elif os.path.isfile(path):
                self.home_bytes_size += os.path.getsize(path)

    def current_home_size(self):
        """得到当前用户home/alice目录的大小，字节/M"""
        self.home_bytes_size = 0
        self.recursion_file(self.homedir_path)
        print('字节：', self.home_bytes_size)  # 单位是字节
        home_m_size = round(self.home_bytes_size / 1024 / 1024, 1)
        print('单位M:', home_m_size)  # 单位时 M

    def put(self):
        """从client上传文件到server当前工作目录下"""
        if len(self.cmds) > 1:
            state_size = struct.unpack('i', self.conn.recv(4))[0]
            if state_size:
                self.current_home_size()  #算出了home下已被占用的大小self.home_bytes_size
                header_bytes = self.conn.recv(struct.unpack('i', self.conn.recv(4))[0])
                header_dic = pickle.loads(header_bytes)
                print(header_dic)
                filename = header_dic.get('filename')
                file_size = header_dic.get('file_size')
                file_md5 = header_dic.get('file_md5')

                upload_filepath = os.path.join(os.getcwd(), filename)
                self.filepath = upload_filepath  # 为了全局变量读取文件算md5时方便
                if os.path.exists(upload_filepath):  #文件已经存在
                    self.conn.send(struct.pack('i', 1))
                    has_size = os.path.getsize(upload_filepath)
                    if has_size == file_size:
                        print('文件已经存在')
                        self.conn.send(struct.pack('i', 0))
                    else:  #上次没有传完 接着继续传
                        self.conn.send(struct.pack('i', 1))
                        if self.home_bytes_size + int(file_size - has_size) > self.quota_bytes:
                            print('超出了用户的配额')
                            self.conn.send(struct.pack('i', 0))
                        else:
                            self.conn.send(struct.pack('i', 1))
                            self.conn.send(struct.pack('i', has_size))
                            with open(upload_filepath, 'ab') as f:
                                f.seek(has_size)
                                while has_size < file_size:
                                    recv_bytes = self.conn.recv(self.MAX_RECV_SIZE)
                                    f.write(recv_bytes)
                                    has_size += len(recv_bytes)
                                    self.conn.send(struct.pack('i', has_size))  # 为了显示 进度条

                            if self.getfile_md5() == file_md5: #判断下载下来的文件MD5值和server传过来的MD5值是否一致
                                print('\033[1;32m上传成功\033[0m')
                                self.conn.send(struct.pack('i', 1))
                            else:
                                print('\033[1;32m上传失败\033[0m')
                                self.conn.send(struct.pack('i', 0))
                else:  #第一次上传
                    self.conn.send(struct.pack('i', 0))
                    if self.home_bytes_size + int(file_size) > self.quota_bytes:
                        print('超出了用户的配额')
                        self.conn.send(struct.pack('i', 0))
                    else:
                        self.conn.send(struct.pack('i', 1))
                        with open(upload_filepath, 'wb') as f:
                            recv_size = 0
                            while recv_size < file_size:
                                file_bytes = self.conn.recv(self.MAX_RECV_SIZE)
                                f.write(file_bytes)
                                recv_size += len(file_bytes)
                                self.conn.send(struct.pack('i', recv_size)) #为了进度条的显示

                        if self.getfile_md5() == file_md5:  # 判断下载下来的文件MD5值和server传过来的MD5值是否一致
                            print('\033[1;32m上传成功\033[0m')
                            self.conn.send(struct.pack('i', 1))
                        else:
                            print('\033[1;32m上传失败\033[0m')
                            self.conn.send(struct.pack('i', 0))
            else:
                print('待传的文件不存在')
        else:
            print('用户没有输入文件名')

    def ls(self):
        """查询当前工作目录下,先返回文件列表的大小,在返回查询的结果"""
        subpro_obj = subprocess.Popen('dir', shell=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
        stdout = subpro_obj.stdout.read()
        stderr = subpro_obj.stderr.read()
        self.conn.send(struct.pack('i', len(stdout + stderr)))
        self.conn.send(stdout)
        self.conn.send(stderr)

    def mkdir(self):
        """在当前目录下,增加目录"""
        if len(self.cmds) > 1:
            mkdir_path = os.path.join(os.getcwd(),self.cmds[1])
            if not os.path.exists(mkdir_path): #查看目录名是否存在
                os.mkdir(mkdir_path)
                print('增加目录成功')
                self.conn.send(struct.pack('i', 1)) #增加目录成功，返回1
            else:
                print('目录名已存在')
                self.conn.send(struct.pack('i', 0)) #失败返回0
        else:
            print('用户没有输入目录名')

    def cd(self):
        """切换目录"""
        if len(self.cmds) > 1:
            dir_path = os.path.join(os.getcwd(), self.cmds[1])
            if os.path.isdir(dir_path): #查看是否是目录名
                previous_path = os.getcwd()  #拿到当前工作的目录
                os.chdir(dir_path) #改变工作目录到...
                target_dir = os.getcwd()
                if self.homedir_path in target_dir:  #判断homedir_path是否在目标目录
                    print('切换成功')
                    self.conn.send(struct.pack('i', 1)) #切换成功返回1
                else:
                    print('切换失败')  # 切换失败后,返回到之前的目录下
                    os.chdir(previous_path)
                    self.conn.send(struct.pack('i', 0))
            else:
                print('要切换的目录不在该目录下')
                self.conn.send(struct.pack('i', 0))
        else:
            print('没有传入切换的目录名')

    def remove(self):
        """删除指定的文件,或者空文件夹"""
        if len(self.cmds) > 1:
            file_name = self.cmds[1]
            file_path = '%s\%s'%(os.getcwd(), file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                self.conn.send(struct.pack('i', 1))
            elif os.path.isdir(file_path): #删除空目录
                if not len(os.listdir(file_path)):
                    os.removedirs(file_path)
                    print('删除成功')
                    self.conn.send(struct.pack('i', 1))
                else:
                    print('文件夹非空，不能删除')
                    self.conn.send(struct.pack('i', 0))
            else:
                print('不是文件也不是文件夹')
                self.conn.send(struct.pack('i', 0))
        else:
            print('没有输入要删除的文件')

    def server_handle(self, conn):
        """处理与用户的交互指令"""
        if self.auth():
            print('\033[1;32m用户登录成功\033[0m')
            while True:
                try:  #try ...except 适合windows  client 断开
                    user_input = self.conn.recv(self.MAX_RECV_SIZE).decode('utf-8')
                    #if not user_input: continue  # 这里适合 linux client 断开
                    self.cmds = user_input.split()
                    if hasattr(self,self.cmds[0]):
                        getattr(self,self.cmds[0])()
                    else:
                        print('\033[1;31m请用户重复输入\033[0m')
                except Exception:
                    break

    def run(self):
        self.server_accept()

    def close(self):
        self.socket.close()
#if __name__ == '__main__':
    #pool = ThreadPoolExecutor(10)
# -*- coding:utf-8 -*-
#Author:Kris

import os
import sys
import socket
import struct
import pickle
import hashlib

class FTPClient():
    HOST = '127.0.0.1'  # 服务端的IP
    PORT = 8080  # 服务端的端口
    MAX_RECV_SIZE = 8192
    DOWNLOAD_PATH =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'download')
    UPLOAD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload')

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def connect(self):
        """连接服务端server"""
        try:
            self.socket.connect((self.HOST, self.PORT))
        except Exception:
            exit('\033[1;31mserver还未启动\033[0m')

    def get_recv(self):
        """获取server返回的数据"""
        return pickle.loads(self.socket.recv(self.MAX_RECV_SIZE))

    def auth(self):
        """用户认证"""
        count = 0
        while count < 3:
            name = input('username>>>:').strip()
            if not name: continue
            password = input('password>>>:').strip()
            user_dic = {
                'username': name,
                'password': password
            }
            self.socket.send(pickle.dumps(user_dic)) #把用户名和密码发送给server
            res = struct.unpack('i',self.socket.recv(4))[0]
            if res:  #接收返回的信息，并判断
                print('welcome'.center(20,'-'))
                user_info_dic = self.get_recv()
                self.username = user_info_dic.get('username')
                print(user_info_dic)
                return True
            else:
                print('\033[1;31m用户名或密码不对!\033[0m')
            count += 1

    def readfile(self):
        """读取文件,得到文件内容的bytes型"""
        with open(self.filepath, 'rb') as f:
            filedata = f.read()
        return filedata

    def getfile_md5(self):
        """对文件内容md5"""
        return hashlib.md5(self.readfile()).hexdigest()

    def progress_bar(self, num, get_size, file_size):
        """进度条显示"""
        float_rate = get_size / file_size
        # rate = str(float_rate * 100)[:5]  # 95.85%
        rate = round(float_rate * 100,2)  # 95.85%

        if num == 1:  #1表示下载
            sys.stdout.write('\r已下载:\033[1;32m{0}%\033[0m'.format(rate))
        elif num == 2:  #2 表示上传
            sys.stdout.write('\r已上传:\033[1;32m{0}%\033[0m'.format(rate))
        sys.stdout.flush()

    def get(self):
        """从server下载文件到client"""
        if len(self.cmds) > 1:
            filename = self.cmds[1]
            self.filepath = os.path.join(self.DOWNLOAD_PATH, filename) #结合目录名和文件名
            if os.path.isfile(self.filepath): #如果文件存在 支持断点续传
                temp_file_size = os.path.getsize(self.filepath)
                self.socket.send(struct.pack('i', temp_file_size))
                header_size = struct.unpack('i', self.socket.recv(4))[0]
                if header_size: #如果存在
                    header_dic = pickle.loads(self.socket.recv(header_size))
                    print(header_dic)
                    filename = header_dic.get('filename')
                    file_size = header_dic.get('file_size')
                    file_md5 = header_dic.get('file_md5')

                    if temp_file_size == file_size:
                        print('\033[1;32m文件已存在\033[0m')
                    else:
                        print('\033[1;33m正在进行断点续传...\033[0m')
                        download_filepath = os.path.join(self.DOWNLOAD_PATH, filename)
                        with open(download_filepath, 'ab') as f:
                            f.seek(temp_file_size)
                            get_size = temp_file_size
                            while get_size < file_size:
                                file_bytes = self.socket.recv(self.MAX_RECV_SIZE)
                                f.write(file_bytes)
                                get_size += len(file_bytes)
                                self.progress_bar(1, get_size, file_size)  # 1表示下载

                        if self.getfile_md5() == file_md5:  #判断下载下来的文件MD5值和server传过来的MD5值是否一致
                            print('\n\033[1;32m下载成功\033[0m')
                        else:
                            print('\n\033[1;32m下载文件大小与源文件大小不一致，请重新下载，将会支持断点续传\033[0m')
                else:
                    print('\033[1;31m该文件,之前被下载了一部分,但是server端的该文件,已被删除,无法再次下载\033[0m')
            else:  #文件第一次下载
                self.socket.send(struct.pack('i', 0))  # 0表示之前没有下载过
                header_size = struct.unpack('i', self.socket.recv(4))[0]
                if header_size:
                    header_dic = pickle.loads(self.socket.recv(header_size))
                    print(header_dic)
                    filename = header_dic.get('filename')
                    file_size = header_dic.get('file_size')
                    file_md5 = header_dic.get('file_md5')

                    download_filepath = os.path.join(self.DOWNLOAD_PATH, filename)
                    with open(download_filepath, 'wb') as f:
                        get_size = 0
                        while get_size < file_size:
                            file_bytes = self.socket.recv(self.MAX_RECV_SIZE)
                            f.write(file_bytes)
                            get_size += len(file_bytes)
                            self.progress_bar(1, get_size, file_size)  #1表示下载
                            print('总大小:%s已下载:%s'% (file_size, get_size))
                    if self.getfile_md5() == file_md5:  #判断下载下来的文件MD5值和server传过来的MD5值是否一致
                        print('\n\033[1;32m恭喜您,下载成功\033[0m')
                    else:
                        print('\n\033[1;32m下载失败，再次下载支持断点续传\033[0m')
                else:
                    print('\033[1;31m当前目录下,文件不存在\033[0m')
        else:
            print('用户没有输入文件名')

    def put(self):
        """往server自己的home/alice目录下,当前工作的目录下上传文件"""
        if len(self.cmds) > 1:  #确保用户输入了文件名
            filename = self.cmds[1]
            filepath = os.path.join(self.UPLOAD_PATH, filename)
            if os.path.isfile(filepath):
                self.socket.send(struct.pack('i', 1))
                self.filepath = filepath
                filesize = os.path.getsize(self.filepath)
                header_dic = {
                    'filename': filename,
                    'file_md5': self.getfile_md5(),
                    'file_size': filesize
                }
                header_bytes = pickle.dumps(header_dic)
                self.socket.send(struct.pack('i', len(header_bytes)))
                self.socket.send(header_bytes)

                state = struct.unpack('i', self.socket.recv(4))[0]
                if state:  #已经存在了
                    has_state = struct.unpack('i', self.socket.recv(4))[0]
                    if has_state:
                        quota_state = struct.unpack('i', self.socket.recv(4))[0]
                        if quota_state:
                            has_size = struct.unpack('i', self.socket.recv(4))[0]
                            with open(self.filepath, 'rb') as f:
                                f.seek(has_size)
                                for line in f:
                                    self.socket.send(line)
                                    recv_size = struct.unpack('i', self.socket.recv(4))[0]
                                    self.progress_bar(2, recv_size, filesize)
                            success_state = struct.unpack('i', self.socket.recv(4))[0]
                            # 这里一定要判断，因为最后一次send(line)之后等待server返回，
                            # server返回，最后一次的recv_size==file_size,但client已经跳出了循环，
                            # 所以在for外面接收的success_state其实时file_size，这种情况只针对大文件
                            if success_state == filesize:
                                success_state = struct.unpack('i', self.socket.recv(4))[0]

                            if success_state:
                                print('\n\033[1;32m恭喜您，上传成功\033[0m')
                            else:
                                print('\n\033[1;32m上传失败\033[0m')
                        else: #超出了配额
                            print('\033[1;31m超出了用户的配额\033[0m')
                    else:  # 存在的大小 和文件大小一致 不必再传
                        print('\033[1;31m当前目录下，文件已经存在\033[0m')
                else:  #第一次传
                    quota_state = struct.unpack('i', self.socket.recv(4))[0]
                    if quota_state:
                        with open(self.filepath, 'rb') as f:
                            send_bytes = b''
                            for line in f:
                                self.socket.send(line)
                                send_bytes += line
                                print('总大小:%s 已上传:%s' % (filesize, len(send_bytes)))

                                recv_size = struct.unpack('i', self.socket.recv(4))[0]
                                self.progress_bar(2, recv_size, filesize)

                        success_state = struct.unpack('i', self.socket.recv(4))[0]

                        if success_state == filesize:
                            success_state = struct.unpack('i', self.socket.recv(4))[0]

                        if success_state:
                            print('\n\033[1;32m恭喜您，上传成功\033[0m')
                        else:
                            print('\n\033[1;32m上传失败\033[0m')
                    else:  # 超出了配额
                        print('\033[1;31m超出了用户的配额\033[0m')
            else:  #文件不存在
                print('\033[1;31m文件不存在\033[0m')
                self.socket.send(struct.pack('i', 0))
        else:
            print('用户没有输入文件名')

    def ls(self):
        """查询当前工作目录下,文件列表"""
        dir_size = struct.unpack('i', self.socket.recv(4))[0]
        recv_size = 0
        recv_bytes = b''
        while recv_size < dir_size:
            temp_bytes = self.socket.recv(self.MAX_RECV_SIZE)
            recv_bytes += temp_bytes
            recv_size += len(temp_bytes)
        print(recv_bytes.decode('gbk'))  # gbk适合windows utf-8 适合linux

    def mkdir(self):
        """增加目录"""
        if len(self.cmds) > 1:
            res = struct.unpack('i', self.socket.recv(4))[0]
            if res:
                print('\033[1;32m在当前目录下，增加目录: %s 成功\033[0m'%self.cmds[1])
            else:
                print('\033[1;31m增加目录失败\033[0m')
        else:
            print('没有输入要增加的目录名')

    def cd(self):
        """切换目录"""
        if len(self.cmds) > 1:
            res = struct.unpack('i', self.socket.recv(4))[0]
            if res:
                print('\033[1;32m切换成功\033[0m')
            else:
                print('\033[1;31m切换失败\033[0m')
        else:
            print('没有输入要切换的目录名')

    def remove(self):
        """删除指定的文件,或者文件夹"""
        if len(self.cmds) > 1:
            res = struct.unpack('i', self.socket.recv(4))[0]
            if res:
                print('\033[1;32m删除成功\033[0m')
            else:
                print('\033[1;31m删除失败\033[0m')
        else:
            print('没有输入要删除的文件')

    def interactive(self):
        """与server交互"""
        if self.auth():
            while True:
                try:
                    user_input = input('[%s]>>>:'%self.username)
                    if not user_input: continue
                    self.socket.send(user_input.encode('utf-8'))
                    self.cmds = user_input.split()
                    if hasattr(self, self.cmds[0]):
                        getattr(self, self.cmds[0])()
                    else:
                        print('请重新输入')
                except Exception as e:  # server关闭了
                    print(e)
                    break
    def close(self):
        self.socket.close()

if __name__ == '__main__':
    ftp_client = FTPClient()
    ftp_client.interactive()
    ftp_client.close()
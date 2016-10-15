# -*- coding: utf-8 -*-
import os
import sys
import ftplib
import threading
import socket
import traceback
import platform
import datetime
from queue import Queue
import shutil
import hashlib

ftp_user = 'anonymous'
ftp_pwd = ''


class Ftp_Down:
    def __init__(self, file_list, version_num, comp_name, result_q, needMD5):
        self._version_num = version_num
        self._file_list = file_list
        self._comp_name = comp_name
        self._result_q = result_q
        self._needMD5 = needMD5
        sys_type = platform.system()

        if sys_type == 'Windows':
            self._dir_separator = '\\'
            self._root_dir = '.\\data\\temp'
        else:
            self._dir_separator = '/'
            self._root_dir = './data/temp'

        dest_comp_dir = "{0}{1}{2}".format(self._root_dir, self._dir_separator, self._comp_name)
        if os.path.exists(dest_comp_dir) == True:
            shutil.rmtree(dest_comp_dir)

        #dest_dir = "{0}{1}{2}{3}{4}".format(self._root_dir,self._dir_separator,self._comp_name,self._dir_separator,str(self._version_num))
        dest_dir = "{0}{1}{2}".format(self._root_dir,self._dir_separator,self._comp_name)
        if os.path.exists(dest_dir) == False:
            os.makedirs(dest_dir)

    def run(self):
        pass

    def down_load(self):
        if os.path.exists(self._root_dir) == False:
            local_dir = "{0}".format(self._root_dir)
            os.makedirs(local_dir)
        threads = []
        for i in range(0, len(self._file_list)):
            source_name = self._file_list[i]
            dest_name = self._file_list[i]
            one_thread = threading.Thread(target = self.one_file_down_load, args=(source_name, dest_name))
            threads.append(one_thread)

        for i in range(0, len(threads)):
            threads[i].start()

        for i in range(0, len(threads)):
            threads[i].join()

        return self._result_q

    def one_file_down_load(self, s_name, d_name):
        str_list = s_name.split(',')
        if len(str_list) != 3:
            self._result_q.put([-1, str_list[0], 'param error'])
            return
        else:
            file_name = str_list[0]
            ftp_host   = str_list[1]
            dest_name = "{0}{1}{2}{3}{4}".format(self._root_dir,self._dir_separator,self._comp_name,
                                                       self._dir_separator,
                                                       os.path.basename(file_name))
            try:
                one_ftp = ftplib.FTP(ftp_host, ftp_user, ftp_pwd)
            except Exception as e:
                self._result_q.put([-1, str_list[0], 'ftp init failed'])
                return
            try:
                fp = open(dest_name, 'wb')
                one_ftp.retrbinary('RETR ' + file_name, fp.write, 8192)
                fp.close()
                one_ftp.close()
                #下载完成后进行MD5校验
                if self._needMD5 == True:
                    if isFileCorrect(file_name,str_list[2]):
                        self._result_q.put([0, str_list[0], dest_name])
                    else:
                        self._result_q.put([-1, str_list[0], "MD5校验失败"])
                else:
                    self._result_q.put([0, str_list[0], dest_name])

            except IOError as e:
                self._result_q.put([-1, str_list[0], e.message])
                return
            except Exception as e:
                self._result_q.put([-1, str_list[0], e.message])
                return

    def stop(self):
        return 0

def resource_download(f_list, v_num, c_name,needMD5):
    result_q = Queue()
    r_down = Ftp_Down(f_list, v_num, c_name, result_q,needMD5)
    queue = r_down.down_load()
    result = ''
    q_size = queue.qsize()
    for i in range(q_size):
        value = queue.get(i)
        result += str(value[0]) + ',' + value[1] + ',' + value[2] + ';'
    return  result

#对比下载文件的md5值是否相同
def isFileCorrect(file_name,md5):
    if md5sum(file_name) != md5:
            return -1
    return 0

'''
def md5sum1(filename):
    fd = open(filename,"rb")
    fcont = fd.read()
    fd.close()
    fmd5 = hashlib.md5(fcont)
    return fmd5.hexdigest()
'''

def md5sum(f_name):
    """ 计算文件的MD5值
    """
    def read_chunks(fh):
        fh.seek(0)
        chunk = fh.read(8096)
        while chunk:
            yield chunk
            chunk = fh.read(8096)
        else: #最后要将游标放回文件开头
            fh.seek(0)

    m = hashlib.md5()
    #if isinstance(f_name, basestring) \
            #and os.path.exists(f_name):
    if os.path.exists(f_name):
        with open(f_name, "rb") as fh:
            for chunk in read_chunks(fh):
                m.update(chunk)
    #上传的文件缓存 或 已打开的文件流
    elif f_name.__class__.__name__ in ["StringIO", "StringO"]: #\
     #       or isinstance(f_name, file):
        for chunk in read_chunks(f_name):
            m.update(chunk)
    else:
        return ""
    return m.hexdigest()

if __name__ == '__main__':
    #命令格式：down.py 项目名称 版本号 更新/回滚（0,1） 需不需要md5校验（0,1） 文件名，FTP地址，MD5值
    file_list=[]
    for i in range(5, len(sys.argv)):
        file_list.append(sys.argv[i])

    comp_name = sys.argv[1]
    version_num = sys.argv[2]
    updateOrBackup = sys.argv[3] #update:0 backup:1
    if sys.argv[4] == '0':
        needMD5 = False
    else:
        needMD5 = True

    sys_type = platform.system()

    if sys_type == 'Windows':
        dir_separator = '\\'
        workSpaceDir = 'd:\\msp\\platform\\data\\temp\\' + comp_name + '\\'
        backupDir = "d:\\msp\\platform\\data\\backup\\" + comp_name + "\\"
    else:
        dir_separator = '/'
        workSpaceDir = '/msp/platform/data/temp/' + comp_name + '/'
        backupDir = "/msp/platform/data/backup/" + comp_name + "/"

    #更新的情况下直接下载，下载前备份
    #判断工作目录有没有工作目录
    if updateOrBackup == '0':
        if os.path.exists(workSpaceDir):
            # 判断是否有备份目录
            if os.path.exists(backupDir):
                shutil.rmtree(backupDir)
            backupDir = backupDir + str(int(version_num) - 1)
            os.mkdir(backupDir)
            for i in range(0,len(file_list)):
                subFileInfo = file_list[i].split(",")
                fileDir = "{0}{1}{2}".format(workSpaceDir, dir_separator, subFileInfo[0])
                shutil.copy(fileDir,backupDir)

        #备份完成后先删除工作目录再进行下载
        resource_download(file_list, version_num, comp_name, needMD5)

    #回滚的情况看工作目录是否有文件，没有则直接下载，有则看备份文件中是否有文件，没有文件就直接下载，有文件则比较文件md5值，相同则拷贝，不同就直接下载
    #将需要下载的文件加入到needDownload数组中
    if updateOrBackup == '1':
        needDownloadFile = []
        if os.path.exists(workSpaceDir):
            backupDir = backupDir + version_num
            if os.path.exists(backupDir):
                for i in range(0,len(file_list)):
                    subFileInfo = file_list[i].split(",")
                    fileDir = "{0}{1}{2}".format(backupDir, dir_separator, subFileInfo[0])
                    if isFileCorrect(fileDir,subFileInfo[2]) == 0:
                        #先删掉工作目录中的文件，再从备份中拷贝过来
                        fileDir = "{0}{1}{2}".format(workSpaceDir, dir_separator, subFileInfo[0])
                        if os.path.exists(fileDir):
                            os.remove(fileDir)
                        shutil.copy(backupDir+dir_separator+subFileInfo[0], workSpaceDir)
                    else:
                        needDownloadFile.append(file_list[i])
            else:
                needDownloadFile = file_list
        else:
            needDownloadFile = file_list
        resource_download(needDownloadFile, version_num, comp_name, needMD5)

'''
    starttime = datetime.datetime.now()
    print (resource_download(file_list, version_num, comp_name))
    stoptime  = datetime.datetime.now()
    print (stoptime - starttime)
'''

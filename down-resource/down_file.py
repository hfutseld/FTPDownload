# -*- coding: utf-8-*-
import ftplib
import os
import socket
import datetime

ftp_server = ''
ftp_port   = 21
ftp_user   = 'anonymous'
ftp_pwd    = ''

def down_file(remote_file,local_file):
    ret = 0
    disp = ''
    try:
        client = ftplib.FTP()
    	print client.connect(ftp_server,ftp_port)
    	print client.login(ftp_user,ftp_pwd)

    	f = open(local_file,'wb')
    	client.retrbinary('RETR ' + remote_file, f.write , 1024)
    	f.close()
    	client.close()
    except ftplib.error_perm:
    	print 'error'
    	os.unlink(local_file)
	ret = -1
	disp = 'ftp down error'
    return ret,disp

if __name__ == '__main__':
    starttime = datetime.datetime.now()
    down_file('filename','/')
    stoptime  = datetime.datetime.now()
    print stoptime - starttime

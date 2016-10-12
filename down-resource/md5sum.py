# -*- coding: utf-8 -*-
import os
import sys
import platform
import hashlib

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

#计算文件的MD5值，并将该MD5值保存在“文件名+md5sum.txt”文件中
if __name__ == '__main__':
    fileName = sys.argv[1]

    sys_type = platform.system()

    if sys_type == 'Windows':
        dir_separator = '\\'
        workSpaceDir = '.\\' + fileName
    else:
        dir_separator = '/'
        workSpaceDir = './' + fileName

    md5 = md5sum(workSpaceDir)
    print(md5)
    fileinfo = fileName.split('.')
    md5File = fileinfo[0] + "md5sum.txt"
    currentConfig_file = '.' + dir_separator + md5File
    with open(currentConfig_file, 'w') as f:
        f.write(md5)

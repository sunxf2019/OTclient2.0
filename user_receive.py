# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 15:20:45 2020

@author: Sharksunxf
"""



import shutil
from user_send     import *


def user_receive_File(win, sk, header_dic):
    path = os.getcwd()
    BUF = 1024 * 100
    total_size = header_dic['file_size']
    file_name = header_dic['file_name']
    file_name_full = "{}{}{}".format(path, "\\TempFolderReceive\\", file_name)
    #print("received file is {}".format(file_name_full))
    win.do_message("正在接收文件{}......".format(file_name), "#ffffff")
    while True:
        with open(file_name_full, 'wb') as f:
            recv_size = 0
            while recv_size < total_size:
                res = sk.recv(BUF)
                f.write(res)
                recv_size += len(res)
            f.close()
            break
    if ".json" in file_name:
        win.userdatabase.do_addRecord(win, file_name) # 接收完后立即在数据库中添加记录
        orgfile = "{}{}{}".format(path, "\\TempFolderReceive\\", file_name)
        dstfile = "{}{}{}".format(path, "\\FolderReceive\\", file_name)
        shutil.copyfile(orgfile, dstfile)
        # os.remove(orgfile)
    win.do_message("接收完毕。", "#FFFFFF")
    sk.close()
   # orgfile = "{}{}{}".format(path, "\\TempFolderReceive\\", file_name)
   # dstfile = "{}{}{}".format(path, "\\FolderReceive\\", file_name)
    #shutil.copyfile(orgfile, dstfile)
   # os.remove(orgfile)





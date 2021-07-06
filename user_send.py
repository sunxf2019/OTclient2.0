# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 14:57:06 2020

@author: Sharksunxf
"""
import socket
import struct
import json
import os

def user_send(win, server_Address, cmd, filelist):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #print("send file:{}".format(f))
    try:
        sk.connect(server_Address)
    except Exception as e:
        print("user send  error:{}".format(e))
        return False
    else:
        with open('newNetInfo.json', 'r') as ff:  # 打开文件用于读
            data = json.load(ff)
            ff.close()
        if filelist != []:
            for f in filelist:
                data["file_name"] = f
                data["file_num"] = 1
                path = os.getcwd()
                file = "{}{}{}".format(path, "\\TempFolderSend\\", f)
                data["file_size"] = os.path.getsize(file)
                with open(file, 'rb') as ff:
                    filedata = ff.read()
                break
        else:
            data["file_name"] = ""
            data["file_num"] = 1
            data["file_size"] = 0
            #filedata = b""
        data["CMD"] = cmd
        header_json = json.dumps(data)
        header_bytes = header_json.encode('utf-8')
        win.do_message("发送指令{}........".format(data["CMD"]), "#FFFFFF")
            # 2 发送报头长度
        try:
            sk.send(struct.pack('i', len(header_bytes)))  # 将报头长度转化为int类型，而int类型为4个字节，所以发送固定长度4个字节
            # 3 发报头
            sk.send(header_bytes)
        except Exception as e:
            win.do_message("发送指令{}失败，原因：{}".format(e,data["CMD"]), "#FFFFFF")

            # 4 发真实数据
        else:
            if data["file_size"]:
                win.do_message( "发送查询文书{}........".format(data["file_name"]), "#FFFFFF")
                sk.sendall(filedata)
                os.remove(file)
                win.userdatabase.do_changeAndRecord(win,f)
        win.do_message("发送完毕。", "#FFFFFF")
        sk.close()

    return True




    


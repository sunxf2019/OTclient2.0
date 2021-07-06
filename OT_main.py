# -*- coding: utf-8 -*-
import sys
import threading
from threading       import Thread
from user_loginUI    import Ui_Dialog_Login
from user_receive    import *
from user_database   import *
from PyQt5 import QtCore, QtWidgets
from progressUI      import Ui_Dialog_Progress
from PyQt5.QtWidgets import QMainWindow, QAbstractItemView, QLineEdit,QApplication
from user_mainUI import Ui_MainWindow
from PyQt5.QtCore import pyqtSignal, Qt, QObject
from setUI             import   Ui_Dialog_Set


class MyProgress(QDialog, Ui_Dialog_Progress):
    progressBarValue = pyqtSignal(str, int, int)
    def __init__(self):
        super(MyProgress, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
    def do_myprocress_show(self, s, num_newfile, num_receive):
        self.progressBar.setRange(0, num_newfile)
        self.label_Progress.setText("正在{}文件......".format(s))
        self.progressBar.setValue(num_receive)




class MyDialog(QDialog, Ui_Dialog_Login):
    def __init__(self):
        super(MyDialog, self).__init__()
        self.setupUi(self)
       # self.setDialog = MySet()
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_QuitOnClose)
        self.LineEdit_Password.setEchoMode(QLineEdit.Password)
        self.pushButton_Login.clicked.connect(self.login)
       # self.pushButton_Set.clicked.connect(self.set)
        self.closesw = True
        with open('newNetInfo.json', 'r') as f1:
            self.data = json.load(f1)
            f1.close()
        self.LineEdit_ServerIP.setText(self.data["MainServerTrueAdd"][0])
        self.LineEdit_ServerPort.setText(str(self.data["MainServerTrueAdd"][1]))
        self.LineEdit_Password.setText(self.data["user_password"])

    def set(self):
        self.setDialog.show()

    def login(self):
       # self.lineEdit_Tip_login.setVisible(True)
        # 将login界面输入的服务器地址和端口号保存在netInfo.json中
        server_ip = self.LineEdit_ServerIP.text()
        server_port = int(self.LineEdit_ServerPort.text())
        # self.data是读取netInfo.json的数据
        self.data["MainServerTrueAdd"][0] = server_ip
        self.data["MainServerTrueAdd"][1] = server_port
        with open('userInfoSet.json', 'r', encoding='UTF-8') as f:
            dd = json.load(f)
            f.close()
        username = self.comboBox_Name.currentText()
        self.data["user_name"] = dd["client"][username][0]
        self.data["user_password"] = self.LineEdit_Password.text().strip(" ")
        # 如果本机有多个IP地址，则要根据服务器IP地址，将客户端程序的IP地址设置在与服务器同一个网址段内
        ll = server_ip.split(".")
        ipstr = "{}.{}.{}".format(ll[0], ll[1], ll[2]) # 提取服务器ip地址前3段
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if ip.startswith(ipstr):
                self.data["user_ip"] = ip
                break
        with open('newNetInfo.json', 'w') as f2:
            json.dump(self.data, f2)
            f2.close()
        if self.data["user_password"] == "":
            QMessageBox.critical(self, "错误", "请输入密码！")
        else:
            # 发送指令'$Login$'，请求登录
            server_Address = tuple(self.data["MainServerTrueAdd"])
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.connect(server_Address)
            except Exception as e:
                QMessageBox.critical(self, "错误", "服务器未启动,请稍后再试！")
            else:
                with open('newNetInfo.json', 'r') as f:
                    data = json.load(f)
                    f.close()
                data["CMD"] = '$Login$'
                header_json = json.dumps(data)
                header_bytes = header_json.encode('utf-8')
                sock.send(struct.pack('i', len(header_bytes)))
                sock.send(header_bytes)
                # 1接受报头长度
                obj = sock.recv(4)
                header_size = struct.unpack('i', obj)[0]
                # 2接收报头
                header_bytes = sock.recv(header_size)
                header_json = header_bytes.decode('utf-8')
                header_dic = json.loads(header_json)
                # 收到指令'$Allowed$'，登录
                # 在这里要记录服务器为用户开辟的新端口
                if "$Allowed$" in header_dic['CMD'] :
                    cmdlist = header_dic['CMD'].split("$")
                    # 保存与服务器会话地址
                    with open('newNetInfo.json', 'w') as f2:
                        self.data["MainServerTempAdd"][0] = cmdlist[2]
                        self.data["MainServerTempAdd"][1] = int(cmdlist[3])
                        json.dump(self.data,f2)
                        f2.close()
                    self.closesw = False
                    self.close()#此处登录对话框已经关闭，是否意味主动套接字结束
                    time.sleep(0.2)
                    win.show()
           #         win.do_inital()

                elif header_dic['CMD'] == "$Denied$":
                    QMessageBox.critical(self, "错误", "密码输入错误！")
        # 保存密码为否时，清空密码
        if not self.checkBox.isChecked():
            self.data["user_password"] = ""
        with open('newNetInfo.json', 'w') as f2:
            json.dump(self.data, f2)
            f2.close()
        self.pushButton_Login.setEnabled(True)
    def closeEvent(self, event):
        if self.closesw:
            os._exit(0)
class MainForm(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainForm, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint| Qt.WindowMinimizeButtonHint)
        self.desktop = QApplication.desktop()
        # 获取显示器分辨率大小
        self.screenRect = self.desktop.screenGeometry()
        height = self.screenRect.height()
        width = self.screenRect.width()
        self.setMaximumSize(QtCore.QSize(width, height))
        self.userdatabase = MySqlTableModel()
        self.tableView_Data.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView_Data.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView_Data.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pushButton_ReceiveFile.clicked.connect(self.do_receiveFile)
        self.pushButton_AddFeedback.clicked.connect(self.do_addFeedback)
        self.pushButton_AddFeedback_2.clicked.connect(self.do_addFeedback_2)
        self.pushButton_SendFile.clicked.connect(self.do_sendFile)
        self.pushButton_OpenFile.clicked.connect(self.do_openFile)
        self.pushButton_Modify.clicked.connect(self.do_modify)
        self.tableView_Data.clicked.connect(self.do_clicked)
        self.tableView_Data.doubleClicked.connect(self.do_doubleclicked)
        self.userdatabase.user_Database_init(self)
        self.userdatabase.selModel.currentRowChanged.connect(self.do_currentRowChanged)
        self.pushButton_Search.clicked.connect(self.do_search)
        self.pushButton_Find.clicked.connect(self.do_find)
        self.pushButton_Forward.clicked.connect(self.do_forward)
        self.pushButton_Backward.clicked.connect(self.do_backward)
        self.comboBox_area.currentIndexChanged.connect(self.do_combochange)
        self.lineEdit_keyword.textChanged.connect(self.do_keywordchange)

        self.num_left = 0
        self.num_newfile = 0
        self.num_add = 0
        self.num_addmore = 0
        self.num_send = 0
        self.curidx = 0
        self.searchshow = True
        self.forward = False
        self.backward = False
        self.tempidx = 0
        self.isfirst = True

    def do_combochange(self):
        # combobox中查询范围发生变化时，将curidx复位
        self.curidx = 0
        self.forward = False
        self.backward = False
        self.tableView_Data.clearSelection()
        self.pushButton_OpenFile.setEnabled(False)
        self.pushButton_AddFeedback.setEnabled(False)
        self.pushButton_AddFeedback_2.setEnabled(False)
        self.pushButton_Modify.setEnabled(False)

    def do_keywordchange(self):
        # keyword中查询范围发生变化时，将curidx复位
        self.curidx = 0
        self.forward = False
        self.backward = False
        self.tableView_Data.clearSelection()
        self.pushButton_OpenFile.setEnabled(False)
        self.pushButton_AddFeedback.setEnabled(False)
        self.pushButton_AddFeedback_2.setEnabled(False)
        self.pushButton_Modify.setEnabled(False)

    def do_find(self):
        self.curidx = 0
        area = self.comboBox_area.currentText()
        keyword = self.lineEdit_keyword.text()
        keyword = keyword.strip(" ")
        if keyword == "":
            QMessageBox.warning(self, "提示", "请输入关键字！")
            return
        thereis = False
      #  for self.curidx in range(self.tabModel.rowCount()):
        while self.curidx < self.userdatabase.tabModel.rowCount():
            rec = self.userdatabase.tabModel.record(self.curidx)
            if keyword in rec.value(area):
                self.tableView_Data.selectRow(self.curidx)
                thereis = True
                break
            self.curidx = self.curidx + 1
        if not thereis:
            QMessageBox.warning(self, "提示", "没有发现记录！")
            # 取消选中行的高亮状态
            self.tableView_Data.clearSelection()
            self.forward = False
            self.backward = False
        else:
            self.forward = True
            self.backward = True
    def do_backward(self):
        if self.forward:
            area = self.comboBox_area.currentText()
            keyword = self.lineEdit_keyword.text()
            thereis = False
            while self.curidx >= 0:
                if self.curidx >= 0:
                    self.curidx = self.curidx - 1
                    rec = self.userdatabase.tabModel.record(self.curidx)
                    if keyword in rec.value(area):
                        self.tableView_Data.selectRow(self.curidx)
                        thereis = True
                        self.tempidx = self.curidx
                        break
                else:
                    self.curidx = self.curidx + 1
                    break
            if not thereis:
                self.curidx = self.tempidx
                QMessageBox.warning(self, "提示", "查询完毕！")

    def do_forward(self):
        if self.forward:
            area = self.comboBox_area.currentText()
            keyword = self.lineEdit_keyword.text()
            thereis = False
            while self.curidx < self.userdatabase.tabModel.rowCount():
                self.curidx = self.curidx + 1
                if self.curidx < self.userdatabase.tabModel.rowCount():
                    rec = self.userdatabase.tabModel.record(self.curidx)
                    if keyword in rec.value(area):
                        self.tableView_Data.selectRow(self.curidx)
                        thereis = True
                        self.tempidx = self.curidx
                        break
                else:
                    self.curidx = self.curidx - 1
                    break
            if not thereis:
                self.curidx =self.tempidx
                QMessageBox.warning(self, "提示", "查询完毕！")
    def do_search(self):
        self.pushButton_OpenFile.setEnabled(False)
        self.pushButton_AddFeedback.setEnabled(False)
        self.pushButton_AddFeedback_2.setEnabled(False)
        self.pushButton_Modify.setEnabled(False)
        self.tableView_Data.clearSelection()
        rec = self.textBrowser_Info.geometry()
        x = rec.left()
        y = rec.height() + rec.top()
        self.Frame.setGeometry(x + 1, y - 39, rec.width() - 3, 36)
        if self.Frame.isHidden():
            self.Frame.show()
        else:
            self.Frame.hide()

    def resizeEvent(self, event):
        # 当窗体初始化后第一次显示时，会产生resizeEvent事件，会错误显示self.frame
        if self.isfirst:
            self.isfirst = False
        else:
            rec = self.textBrowser_Info.geometry()
            x = rec.left()
            y = rec.height() + rec.top()
            self.Frame.setGeometry(x + 1, y - 39, rec.width() - 3, 36)
            if not self.Frame.isHidden():
                self.Frame.show()
            self.do_showtip(self.pushButton_ReceiveFile)
            self.do_showtip(self.pushButton_SendFile)
            self.do_showtip(self.pushButton_AddFeedback)
            self.do_showtip(self.pushButton_AddFeedback_2)
    def do_showtip(self, btn):
        sw =False
        # tip for New

        if btn == self.pushButton_ReceiveFile:
            tip = self.Tip_Btn_Rec
            tipnum = self.num_newfile
            sw = True

        if btn == self.pushButton_SendFile:
            tip = self.Tip_Btn_Send
            path = os.getcwd()
            tipnum = len(os.listdir("{}{}".format(path, "\\TempFolderSend\\")))
            if tipnum :
                sw =True

        if btn == self.pushButton_AddFeedback:
            tip = self.Tip_Btn_Add
            tipnum = 0
            for i in range(self.userdatabase.tabModel.rowCount()):
                rec = self.userdatabase.tabModel.record(i)
                if rec.value("反馈状态") == "新的查询":
                    tipnum =tipnum +1
                    sw = True

        if btn == self.pushButton_AddFeedback_2:
            tip = self.Tip_Btn_Addmore
            tipnum = 0
            for i in range(self.userdatabase.tabModel.rowCount()):
                rec = self.userdatabase.tabModel.record(i)
                if rec.value("反馈状态") == "部分反馈":
                    tipnum = tipnum + 1
                    sw = True

        if sw and tipnum:
            x = btn.x()
            y = btn.y()
            tip.setGeometry(x - 8, y - 10, 20, 20)
            tip.setText(str(tipnum))
            tip.setVisible(True)
        else:
            tip.setVisible(False)


    def do_set(self):



        # 提示有几个查询需要发送
        self.do_showtip(self.pushButton_SendFile)
        self.do_showtip(self.pushButton_AddFeedback)
        self.do_showtip(self.pushButton_AddFeedback_2)
        num_send = len(os.listdir(".\\TempFolderSend\\"))
        if num_send:
            self.pushButton_SendFile.setEnabled(True)
        else:
            self.pushButton_SendFile.setEnabled(False)




    def do_openFile(self):
        if not self.Frame.isHidden():
            self.Frame.hide()

        curindex = self.tableView_Data.currentIndex()
        curRecNo = curindex.row()
        rec = self.userdatabase.tabModel.record(curRecNo)
        filename = rec.value("查询文件编号")
        if filename == "":
            QMessageBox.critical(self, "提示", "请选择需要查看的查询文书！")
        else:
            filelist = os.listdir(".\\FolderReceive\\")
            for f in filelist:
                if (filename in f) and (f != "{}.json".format(filename)):
                    os.startfile(".\\FolderReceive\\{}".format(f))
                    break
        self.pushButton_OpenFile.setEnabled(False)
        self.userdatabase.tabModel.setSort(12, Qt.AscendingOrder)
        self.userdatabase.tabModel.select()

    def do_sendFile(self):
        if not self.Frame.isHidden(): # 隐藏查询界面
            self.Frame.hide()
        self.pushButton_OpenFile.setEnabled(False)
        with open('newNetInfo.json', 'r') as f:
            data = json.load(f)
        server_Address = tuple(data["MainServerTempAdd"])
        user = data["user_name"]
        path = os.getcwd()
        filelist = os.listdir("{}{}".format(path, "\\TempFolderSend\\"))
        self.num_newfile = len(filelist)
        self.num_left = 1
        if filelist:
            self.do_message( "正在等待服务器响应！", "#FFFFFF")
            cmd = "${}$IsReadyToSendFile$".format(user)
            try:
                user_send(self, server_Address, cmd, filelist)
                time.sleep(0.1)
            except Exception as e:
                self.do_message("服务器未响应，原因：{}。".format(e), "#FFFFFF")
                time.sleep(0.1)
            else:
                self.do_message("服务器已启动！", "#FFFFFF")
                progress.do_myprocress_show("发送", self.num_newfile, self.num_left)
                progress.show()
                self.pushButton_SendFile.setEnabled(False)
                self.pushButton_Modify.setEnabled(False)


        else:
            self.do_message("没有需要发送的反馈文件！", "#FFFFFF")


        self.userdatabase.tabModel.setSort(12, Qt.AscendingOrder)
        self.userdatabase.tabModel.select()

    def do_receiveFile(self):
        if not self.Frame.isHidden():
            self.Frame.hide()
        self.pushButton_OpenFile.setEnabled(False)
        with open('newNetInfo.json', 'r') as f:  # 打开文件用于读
            data = json.load(f)
        serverAddr = tuple(data["MainServerTempAdd"])
        self.do_message("正在等待服务器响应！", "#FFFFFF")
        time.sleep(0.1)
        try:
            user_send(self, serverAddr, "$WeNeedFileFromJW$",[])
            time.sleep(0.1)
        except Exception as e:
            self.do_message("服务器未响应，原因：{}。".format(e), "#FFFFFF")
            self.pushButton_OpenFile.setEnabled(True)
        else:
            self.do_message("服务器已启动！", "#FFFFFF")
            progress.show()



        self.do_showtip(self.pushButton_AddFeedback)


        self.userdatabase.tabModel.setSort(12, Qt.AscendingOrder)
        self.userdatabase.tabModel.select()

    def do_message(self, message, fontcolor):
        timeStamp = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
        self.textBrowser_Info.append("<font color=\"{}\">".format(fontcolor)
                                     + "{}>>{}".format(timeStamp, message)
                                     + "</font> ")
        time.sleep(0.1)
        self.textBrowser_Info.moveCursor(self.textBrowser_Info.textCursor().End)

    def do_modify(self):
        if not self.Frame.isHidden():
            self.Frame.hide()
        curIndex = self.tableView_Data.currentIndex()
        currow = curIndex.row()
        curRec = self.userdatabase.tabModel.record(currow)
        filename = curRec.value("反馈文件编号")
        #flist = re.split('-', filename)
        # 如果是关联了反馈
        if curRec.value("sortrank") == 1:
            self.userdatabase.do_dealFeedbackFile(self, "modify")

        self.pushButton_Modify.setEnabled(False)
        self.pushButton_OpenFile.setEnabled(False)
        self.do_showtip(self.pushButton_SendFile)
        self.do_showtip(self.pushButton_AddFeedback)
        self.do_showtip(self.pushButton_AddFeedback_2)

        self.userdatabase.tabModel.setSort(12, Qt.AscendingOrder)
        self.userdatabase.tabModel.select()

    # 关联查询结果
    def do_addFeedback(self):
        if not self.Frame.isHidden():
            self.Frame.hide()
        self.pushButton_OpenFile.setEnabled(False)
        self.pushButton_AddFeedback.setEnabled(False)
        if self.userdatabase.do_dealFeedbackFile(self, "firstTime"):
            self.pushButton_SendFile.setEnabled(True)
            self.do_showtip(self.pushButton_SendFile)
            self.do_showtip(self.pushButton_AddFeedback)
            self.do_showtip(self.pushButton_AddFeedback_2)
            self.userdatabase.tabModel.setSort(12, Qt.AscendingOrder)
            self.userdatabase.tabModel.select()

    # 补充查询结果
    def do_addFeedback_2(self):
        if not self.Frame.isHidden():
            self.Frame.hide()
        self.pushButton_OpenFile.setEnabled(False)
        self.pushButton_AddFeedback_2.setEnabled(False)
        if self.userdatabase.do_dealFeedbackFile(self, "notFirstTime"):
            self.pushButton_SendFile.setEnabled(True)
            self.do_showtip(self.pushButton_SendFile)
            self.do_showtip(self.pushButton_AddFeedback)
            self.do_showtip(self.pushButton_AddFeedback_2)
            self.userdatabase.tabModel.setSort(12, Qt.AscendingOrder)
            self.userdatabase.tabModel.select()

    def do_doubleclicked(self):
        if not self.Frame.isHidden():
            self.Frame.hide()
        curRecNo = self.userdatabase.selModel.currentIndex().row()
        curRec = self.userdatabase.tabModel.record(curRecNo)
        path = os.getcwd()
        if curRec.value("反馈状态") == "新的查询":
            filelist = os.listdir("{}{}".format(path, "\\FolderReceive\\"))
            file = curRec.value("查询文件编号")
            #filepath = "{}{}{}".format(path, "\\FolderReceive\\", curRec.value("查询文件编号"))
            for f in filelist:
                if (file in f) and (".json" not in f):
                    os.startfile("{}\\FolderReceive\\{}".format(path,f))
        else:
            filepath = "{}{}".format(path, "\\FolderSend\\")
            os.startfile(filepath)
        self.pushButton_Modify.setEnabled(False)
        self.pushButton_AddFeedback_2.setEnabled(False)
        self.userdatabase.tabModel.setSort(12, Qt.AscendingOrder)
        self.userdatabase.tabModel.select()
    def do_clicked(self, current):
        if not self.Frame.isHidden():
            self.Frame.hide()
        self.userdatabase.mapper.setCurrentIndex(current.row())
        self.pushButton_OpenFile.setEnabled(True)
        self.pushButton_AddFeedback.setEnabled(False)
        self.pushButton_AddFeedback_2.setEnabled(False)
        self.pushButton_Modify.setEnabled(False)
        self.pushButton_SendFile.setEnabled(False)
        curRecNo = self.userdatabase.selModel.currentIndex().row()
        curRec = self.userdatabase.tabModel.record(curRecNo)
        status = curRec.value("反馈状态")
        if status == "新的查询":
            self.pushButton_AddFeedback.setEnabled(True)
            self.pushButton_AddFeedback_2.setEnabled(False)
        elif status == "部分反馈":
            if curRec.value("sortrank") == 1:
                self.pushButton_AddFeedback.setEnabled(False)
                self.pushButton_AddFeedback_2.setEnabled(False)

                self.pushButton_Modify.setEnabled(True)
            else:
                self.pushButton_AddFeedback.setEnabled(False)
                self.pushButton_AddFeedback_2.setEnabled(True)

                self.pushButton_Modify.setEnabled(False)
        elif status == "全部反馈":
            self.pushButton_AddFeedback.setEnabled(False)
            self.pushButton_AddFeedback_2.setEnabled(False)
            self.pushButton_Modify.setEnabled(True)

        elif status == "结束归档":
            self.pushButton_AddFeedback.setEnabled(False)
            self.pushButton_AddFeedback_2.setEnabled(False)
        filelist_send = os.listdir(".\\TempFolderSend\\")
        if filelist_send == []:
            self.pushButton_SendFile.setEnabled(False)
        else:
            self.pushButton_SendFile.setEnabled(True)

    def do_currentRowChanged(self, current):
        self.userdatabase.mapper.setCurrentIndex(current.row())
        self.pushButton_OpenFile.setEnabled(True)
        self.pushButton_AddFeedback.setEnabled(False)
        self.pushButton_AddFeedback_2.setEnabled(False)
        self.pushButton_Modify.setEnabled(False)
        self.pushButton_SendFile.setEnabled(False)
        curRecNo = self.userdatabase.selModel.currentIndex().row()
        curRec = self.userdatabase.tabModel.record(curRecNo)
        status = curRec.value("反馈状态")
        if status == "新的查询":
            self.pushButton_AddFeedback.setEnabled(True)
            self.pushButton_AddFeedback_2.setEnabled(False)

        elif status == "部分反馈":
            if curRec.value("sortrank") == 1:
                self.pushButton_AddFeedback.setEnabled(False)
                self.pushButton_AddFeedback_2.setEnabled(False)

                self.pushButton_Modify.setEnabled(True)
            else:
                self.pushButton_AddFeedback.setEnabled(False)
                self.pushButton_AddFeedback_2.setEnabled(True)

                self.pushButton_Modify.setEnabled(False)
        elif status == "全部反馈":
            self.pushButton_AddFeedback.setEnabled(False)
            self.pushButton_AddFeedback_2.setEnabled(False)
            self.pushButton_Modify.setEnabled(True)

        elif status == "结束归档":
            self.pushButton_AddFeedback.setEnabled(False)
            self.pushButton_AddFeedback_2.setEnabled(False)


        filelist_send = os.listdir(".\\TempFolderSend\\")
        if filelist_send == []:
            self.pushButton_SendFile.setEnabled(False)
        else:
            self.pushButton_SendFile.setEnabled(True)
        self.do_showInfo(curRec)
    def do_showInfo(self,curRec):
        banklist1 = curRec.value("查询银行")
        banklist2 = curRec.value("未反馈银行")
        bankinfoEx = curRec.value("短消息")
        b1num = len(banklist1.split("、"))
        b2num = len(banklist2.split("、"))
        # print(type(banklist2))
        if banklist1:
            if banklist1 == banklist2:
                bankinfo2 = "目前没有银行反馈信息。"
            else:
                if banklist2 == "":
                    bankinfo2 = "目前所有银行均已反馈。"
                else:
                    bankinfo2 = "目前有{}家银行未反馈：{}。".format(b2num, banklist2)

            if bankinfoEx == "":
                self.textBrowser_BankInfo.setText("此查询涉及{}家银行：{},{}".format(b1num, banklist1, bankinfo2))
            else:
                self.textBrowser_BankInfo.setText("此查询涉及{}家银行：{},{}附加信息:{}。".format(b1num, banklist1, bankinfo2, bankinfoEx))
        else:

            self.textBrowser_BankInfo.setText(bankinfoEx)



    def CMD_Process(self, header_bytes, sk):
        header_json = header_bytes.decode('utf-8')
        header_dic = json.loads(header_json)
        cmd = header_dic['CMD']
        with open('newNetInfo.json', 'r') as f:  # 打开文件用于读
            data = json.load(f)
        i = cmd.split('$')
        #print("CMD processing:{}".format(header_dic["CMD"]))
        self.do_message("--------------------------------------------------", "#FFFFFF")
        self.do_message("收到指令{}，正在处理......".format(header_dic["CMD"]), "#FFFFFF")
        # 服务器通知有新的查询需要接收
        if "$HereIsNewFile$" in cmd:
            i = cmd.split('$')
            self.do_message("你有新的查询，共计{}个文件，请查收！".format(i[2]), "#77FF00")
            self.num_newfile = int(i[2])
            self.do_showtip(self.pushButton_ReceiveFile)

        elif cmd == "$ServerIsReadyToSend$":
            self.num_left = self.num_left + 1
            progress.progressBarValue.emit("接收", self.num_newfile, self.num_left)
            #print("receive file:{}".format(header_dic["file_name"]))
            user_receive_File(self, sk, header_dic)
            time.sleep(0.1)
            user_send(self, tuple(header_dic["MainServerTempAdd"]), "$WeNeedFileFromJW$", [])

        elif cmd == "$NoNewFile$":#加入文件拼接
            time.sleep(0.5)
            self.do_message("没有新的查询！", "#FFFFFF")
            self.num_left = 0
            self.num_newfile = 0
            time.sleep(0.5)
            progress.hide()
            self.do_showtip(self.pushButton_ReceiveFile)
            self.do_showtip((self.pushButton_AddFeedback_2))
            self.do_showtip((self.pushButton_AddFeedback))
            self.do_showtip(self.pushButton_SendFile)
            # 拼接文件

            fileid = []
            filedic = {}
            filelist = os.listdir(".\\TempFolderReceive\\")
            for f in filelist:
                if ".json" in f:
                    (shotname, extension) = os.path.splitext(f)
                    fileid.append(shotname)
            for id in fileid:
                t=[]
                for f in filelist:
                    if (id in f ) and (".json" not in f):
                        t.append(f)
                filedic[id] = t

            for k in filedic.keys():
                (shotname, extension) = os.path.splitext(filedic[k][0])
                outfile = open((".\\FolderReceive\\{}{}".format(k, extension)), 'wb')
                for file in filedic[k]:
                    infile = open((".\\TempFolderReceive\\{}".format(file)), 'rb')
                    data = infile.read()
                    outfile.write(data)
                    infile.close()
                outfile.close()

            for f in filelist:
                os.remove(".\\TempFolderReceive\\{}".format(f))


        elif cmd == "$ServerIsReadyToAccept$":
            server_Address = tuple(header_dic["MainServerTempAdd"],)
            user = data["user_name"]
            filelist = os.listdir(".\\TempFolderSend\\")
            if filelist:
                cmd = "${}$IsReadyToSendFile$".format(user)
                try:
                    user_send(self, server_Address, cmd, filelist)
                    self.num_left = self.num_left + 1
                    progress.progressBarValue.emit("发送", self.num_newfile, self.num_left)
                except Exception as e:
                    self.do_message("发送失败，原因：{}。".format(e), "#FFFFFF")
            else:
                self.num_newfile = 0
                self.num_left = 0
                progress.hide()
                try:
                    user_send(self, server_Address, "$OtIsEnd$", [])
                except Exception as e:
                    self.do_message("发送失败，原因：{}。".format(e), "#FFFFFF")
                self.do_showtip(self.pushButton_SendFile)
        elif "$UserIsNotAlive$" in cmd:
            self.do_message("纪委当前不在线！", "#77FF00")

        self.do_message("处理完毕。", "#FFFFFF")

    def closeEvent(self, event):
        with open('newNetInfo.json', 'r') as f:  # 打开文件用于读
            data = json.load(f)
            f.close()
        data["file_name"] = "userdb.db3"
        data["file_num"] = 1
        path = os.getcwd()
        file = "{}\\{}".format(path, "userdb.db3")
        data["file_size"] = os.path.getsize(file)
        with open(file, 'rb') as ff:
            filedata = ff.read()
        data["CMD"] = "${}$down$".format(data["user_name"])
        header_json = json.dumps(data)
        header_bytes = header_json.encode('utf-8')
        # print(header_bytes)
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.do_message("正在备份数据库文件.......", "#FFFFFF")
        try:
            sk.connect(tuple(data["MainServerTempAdd"]))
            sk.send(struct.pack('i', len(header_bytes)))  # 将报头长度转化为int类型，而int类型为4个字节，所以发送固定长度4个字节
            sk.send(header_bytes)
            if data["file_size"]:
                sk.sendall(filedata)
            sk.close()
        except Exception as e:
            self.do_message("备份失败，原因：{}，请稍后再试。".format(e), "#FFFFFF")
        else:
            self.do_message("数据库文件备份成功！", "#FFFFFF")
        time.sleep(1)
        with open('info.log', 'a') as f:
            text = self.textBrowser_Info.toPlainText()
            f.write(text)
            f.close()
        time.sleep(1)
        os._exit(0)


def server_Process():
    with open('newNetInfo.json', 'r') as f:  # 打开文件用于读
        data = json.load(f)
        f.close()
    #userserver_Address = tuple(data["UserServer"])
    user_ip = data["user_ip"]
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((user_ip, 0))  # 绑定套接字到本机的网络地址,端口随机
    user_ip,port = sock.getsockname()
    data["user_port"] = port
    data["UserServer"][0] = user_ip
    data["UserServer"][1] = port
    with open('newNetInfo.json', 'w') as ff:
        json.dump(data, ff)
        ff.close()
    sock.listen(4)  # 10表示最大连接数
    while True:
        sk, sockname = sock.accept()
        # 1收报头长度
        obj = sk.recv(4)
        header_size = struct.unpack('i', obj)[0]
        # 2接收报头
        header_bytes = sk.recv(header_size)
        win.CMD_Process(header_bytes, sk)
        sk.close()


if __name__ == '__main__':

    folder = os.path.exists("TempFolderSend")
    if not folder:                               #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs("TempFolderSend")            #makedirs 创建文件时如果路径不存在会创建这个路径
    folder = os.path.exists("TempFolderReceive")
    if not folder:
        os.makedirs("TempFolderReceive")


    folder = os.path.exists("FolderSend")
    if not folder:                               #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs("FolderSend")
    folder = os.path.exists("FolderReceive")
    if not folder:                               #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs("FolderReceive")




    app = QtWidgets.QApplication(sys.argv)
    progress = MyProgress()
    progress.progressBarValue.connect(progress.do_myprocress_show)
    win = MainForm()
    dlg = MyDialog()
    dlg.exec_()
    serverStart = Thread(target=server_Process, args=())
    serverStart.start()
    win.do_set()
    time.sleep(0.2)
    with open('newNetInfo.json', 'r') as f:  # 打开文件用于读
        data = json.load(f)
        f.close()
    #print("server temp address is:{}".format(data["MainServerTempAdd"]))
    win.do_message("===================New Session====================", "#FFFFFF")
    win.do_message("正在获取新的查询........", "#FFFFFF")
    user_send(win, tuple(data["MainServerTempAdd"]), "$WeNeedFileFromJW$", [])
   # win.do_set()
    sys.exit(app.exec_())

# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 23:18:05 2020

@author: Sharksunxf
"""
import os
import re
import time
import shutil, json
from PyQt5           import QtWidgets,QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox, QDataWidgetMapper, QHeaderView
from PyQt5.QtCore    import Qt, QItemSelectionModel, QModelIndex, QStringListModel
from PyQt5.QtSql     import QSqlDatabase, QSqlTableModel
from PyQt5.QtGui     import QBrush, QColor
from user_statusUI   import Ui_Dialog_FeedbackStatusSelection
class StatusDialog(QDialog, Ui_Dialog_FeedbackStatusSelection):
    def __init__(self , feID):
        super(StatusDialog, self).__init__()
        self.setupUi(self)
        self.feid =feID
        #self.checkBox_all.setChecked(True) # 默认全反馈
        self.pushButton_SelAll.clicked.connect(self.selAll)
        self.pushButton_SelOne.clicked.connect(self.selOne)
        self.pushButton_DelAll.clicked.connect(self.delAll)
        self.pushButton_DelOne.clicked.connect(self.delOne)
        self.pushButton_FindBank.clicked.connect(self.findBank)
        self.listView_BankList.doubleClicked.connect(self.doubleclik)
        self.listView_BankList_Sel.doubleClicked.connect(self.doubleclik_sel)
        self.checkBox_part.clicked.connect(self.check_part)
        self.checkBox_all.clicked.connect(self.check_all)



        with open('newNetInfo.json', 'r') as f:  # 打开文件用于读
            data = json.load(f)
            f.close()
        self.user = data["user_name"]
        if self.user == "RH":
            self.checkBox_all.hide()
            self.checkBox_part.hide()
            with open(self.feid, 'r', encoding='UTF-8') as f:  # 打开文件用于读
                data = json.load(f)
                f.close()
            #print("data : {}".format(data))
            self.banklist = data["未反馈银行"].split("、")
            self.banklist_model = QStringListModel()
            self.banklist_model.setStringList(self.banklist)
            self.listView_BankList.setModel(self.banklist_model)

            self.banklist_sel = []
            self.banklist_sel_model = QStringListModel()
            self.banklist_sel_model.setStringList(self.banklist_sel)
            self.listView_BankList_Sel.setModel(self.banklist_sel_model)
        else:
            self.checkBox_all.show()
            self.checkBox_part.show()
            self.resize(745, 305)
            self.setMinimumSize(QtCore.QSize(745, 305))
            self.setMaximumSize(QtCore.QSize(745, 305))

    def check_part(self):
        self.checkBox_all.setChecked(False)
        self.checkBox_part.setChecked(True)
        self.feedbackstatus = "P" # 部分反馈

    def check_all(self):
        self.checkBox_all.setChecked(True)
        self.checkBox_part.setChecked(False)
        self.feedbackstatus = "F"  # 全部反馈

    def doubleclik(self):
        self.selOne()

    def doubleclik_sel(self):
        self.delOne()

    def selAll(self):
        with open(self.feid, 'r', encoding='UTF-8') as f:  # 打开文件用于读
            data = json.load(f)
            f.close()
        self.banklist = data["未反馈银行"].split("、")
        self.banklist_sel = self.banklist
        self.banklist_sel_model.setStringList(self.banklist_sel)

    def selOne(self):
        sw = True
        item = self.listView_BankList.currentIndex().row()  # item为当前选中行行号，默认未选中时，item =-1，是最后一项
        if item >= 0:
            # print("item {}".format(item))
            value = self.banklist_model.stringList()[item]
            if self.banklist_sel == []:
                self.banklist_sel.append(value)
            else:
                for i in range(len(self.banklist_sel)):
                    if value == self.banklist_sel[i]:
                        sw = False
                        break
                if sw:
                    self.banklist_sel.append(value)
            self.banklist_sel_model.setStringList(self.banklist_sel)


    def delAll(self):
        self.banklist_sel = []
        self.banklist_sel_model.setStringList(self.banklist_sel)


    def delOne(self):
        # print(self.banklist_sel)
        item = self.listView_BankList_Sel.currentIndex().row()
        # print("item{}".format(item))
        if item >= 0:
            item = self.listView_BankList_Sel.currentIndex().row()
            value = self.banklist_sel_model.stringList()[item]
            self.banklist_sel.remove(value)
        self.banklist_sel_model.setStringList(self.banklist_sel)


    def findBank(self):
        bank = self.lineEdit_FindBank.text()
        s = False
        for row in range(self.banklist_model.rowCount()):
            index = self.banklist_model.index(row, 0)
            item = self.banklist_model.data(index, Qt.DisplayRole)
            if bank in item:
                self.listView_BankList.setCurrentIndex(index)
                s = True
                # print(item)
                break
        if not s:
            QMessageBox.critical(self, "提示", "你要添加的银行不存在！")

    def setDatas(self, value):
        self.LineEdit_Dlg_Filename.setText(value)
    '''
    def closeEvent(self, event):
        if self.user =="RH":
            self.feedbackliststr = ""
            for row in range(self.banklist_sel_model.rowCount()):
                index = self.banklist_sel_model.index(row, 0)
                item = self.banklist_sel_model.data(index, Qt.DisplayRole)
                self.feedbackliststr = self.feedbackliststr + item +"、"
            if self.feedbackliststr =="":
                QMessageBox.critical(self, "提示", "请选择需要反馈的银行！")
                return False
            else:
                self.feedbackliststr = self.feedbackliststr.rstrip("、")
                return True
        else:
            return True
            
    def accept(self) -> None:
        if self.user =="RH":
            self.getFullStatus()
        else:
            self.inforeturn.append(self.feedbackstatus)
            self.inforeturn.append("")
        return self.inforeturn
        '''

    def getFullStatus(self):
        self.inforeturn =[]
        self.liststr= []
        self.liststrsel=[]
        str=""
        self.inforeturn.append(self.user)
        if self.user == "RH":
            for row in range(self.banklist_model.rowCount()):
                index1 = self.banklist_model.index(row, 0)
                item1 = self.banklist_model.data(index1, Qt.DisplayRole)
                str = str + item1 + "、"
            str = str.rstrip("、")
            self.liststr=str.split("、")
            str = ""
            for row in range(self.banklist_sel_model.rowCount()):
                index2 = self.banklist_sel_model.index(row, 0)
                item2 = self.banklist_sel_model.data(index2, Qt.DisplayRole)
                str = str + item2 + "、"
            str = str.rstrip("、")
            self.liststrsel=str.split("、")
            self.nofeekbacklist = list(set(self.liststr) - set(self.liststrsel))

            #print("self.liststr {}".format(self.liststr))
            #print(" self.liststrsel {}".format( self.liststrsel))
            #print("self.nofeekbacklist {}".format(self.nofeekbacklist))

            if self.liststrsel == ['']:
                self.feedbackstatus = "error"
            elif self.nofeekbacklist == []:
                self.feedbackstatus = "F"
            else:
                self.feedbackstatus = "P"
            self.noliststr  = ""
            for i in range(len(self.nofeekbacklist)):
                self.noliststr = self.noliststr + self.nofeekbacklist[i]+"、"
            self.noliststr = self.noliststr.rstrip("、")
            self.inforeturn.append(self.feedbackstatus)
            self.inforeturn.append(self.noliststr)
        else:
            if self.checkBox_part.isChecked():
                self.feedbackstatus = "P"
            elif self.checkBox_all.isChecked():
                self.feedbackstatus = "F"
            else:
                self.feedbackstatus = "error"
            self.inforeturn.append(self.feedbackstatus)
            self.inforeturn.append("")
        sms =self.textEdit_Dlg_Sms.toPlainText()
        self.inforeturn.append(sms)
        #print("self.inforeturn {}".format(self.inforeturn) )
        return self.inforeturn




class MySqlTableModel(QSqlTableModel, QSqlDatabase):

    def __init__(self, parent = QSqlTableModel, db = QSqlDatabase()):
        super(MySqlTableModel, self).__init__()
        self.num = 0
    def data(self, index, role):
        curRecNo = index.row()
        sortrank = QSqlTableModel.data(self,QSqlTableModel.index(self, curRecNo, 12))
        # 颜色等级分三级：
        # 1、红色：新的任务：      新查询和已关联未发送的新反馈
        # 2、黄色：等待反馈的任务：已发送的部分反馈
        # 3、灰色：结束归档的任务：已发送的全部反馈
        if role == Qt.BackgroundRole:
            if sortrank == 0:
                return QBrush(QColor(255, 255, 255))  # 等级0
            elif sortrank == 1:
                return QBrush(QColor(255, 80, 0))   # 等级1
            elif sortrank == 2:
                return QBrush(QColor(255, 215, 0))  # 等级2
            elif sortrank == 3:
                return QBrush(QColor(200, 200, 200))  # 等级3
                # 设置单元格居中显示
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        return QSqlTableModel.data(self, index, role)



    def user_Database_init(self,win):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("userdb.db3")
        self.db.close()
        if self.db.open():
            self.do_openTable(win)
        else:
            QMessageBox.warning(win, "错误", "打开userdb.db3文件失败！")

    def do_openTable(self,win):
        self.tabModel = MySqlTableModel(self, self.db)
        self.tabModel.setTable("UserData")
        self.tabModel.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.tabModel.setSort(self.tabModel.fieldIndex("序号"), Qt.DescendingOrder)
        self.selModel = QItemSelectionModel(self.tabModel)
        if(self.tabModel.select()==False):
            QMessageBox.critical(win, "错误", "打开数据表UserData失败！")
            self.db.close()
            return

        win.tableView_Data.setModel(self.tabModel)
        win.tableView_Data.setSelectionModel(self.selModel)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex("序号"), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex("查询内容"), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex("sortrank"), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex("反馈文件名称"), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex("查询银行"), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex("未反馈银行"), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex("短消息"), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex("templist"), True)
        #self.tableView_Data.setColumnHidden(self.tabModel.fieldIndex("人数（个）"), True)
        #self.tableView_Data.setColumnHidden(self.tabModel.fieldIndex("单位数（个）"), True)
        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(self.tabModel)
        self.mapper.setSubmitPolicy(QDataWidgetMapper.AutoSubmit)
        self.mapper.addMapping(win.lineEdit_AskTime,self.tabModel.fieldIndex("查询时间"))
        self.mapper.addMapping(win.lineEdit_AskFileName, self.tabModel.fieldIndex("查询文件编号"))
        self.mapper.addMapping(win.LineEdit_User,self.tabModel.fieldIndex("申请单位"))
        self.mapper.addMapping(win.LineEdit_FeedbackTime,self.tabModel.fieldIndex("反馈时间"))
        self.mapper.addMapping(win.LineEdit_FeedbackFile,self.tabModel.fieldIndex("反馈文件名称"))
        self.mapper.addMapping(win.LineEdit_FeedbackID,self.tabModel.fieldIndex("反馈文件编号"))
        self.mapper.addMapping(win.LineEdit_FeedbackStatus,self.tabModel.fieldIndex("反馈状态"))
        for i in range(1, 11):
            win.tableView_Data.resizeColumnToContents(i)
        # 设置第7、9、10列列宽为自适应
        win.tableView_Data.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)
        win.tableView_Data.horizontalHeader().setSectionResizeMode(9, QHeaderView.Stretch)
        win.tableView_Data.horizontalHeader().setSectionResizeMode(10, QHeaderView.Stretch)
        win.tableView_Data.horizontalHeader().setStyleSheet(
            "QHeaderView::section{ font-size : 10pt; height:26px;border-top:1px solid gray;border-bottom:1px solid gray;"
            "border-right:1px solid gray;background:#CFCFCF;}")
        win.tableView_Data.setStyleSheet("selection-background-color:#76EE00")
        # 按照“新的查询”、“部分反馈”、“反馈完毕”排序
        self.tabModel.setSort(12, Qt.AscendingOrder)
        self.tabModel.select()

# 添加记录，最新的记录在最上面
    def do_addRecord(self, win, file):
        file =".\\TempFolderReceive\\{}".format(file)
       # print("the file is {}".format(file))
        with open(file, 'r', encoding='UTF-8') as f:  # 打开文件用于读
            data = json.load(f)
            f.close()

        self.tabModel.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.tabModel.insertRow(0, QModelIndex())
        curIndex = self.tabModel.index(0, 1)
        currow = curIndex.row()
        self.tabModel.setData(self.tabModel.index(currow, 0), self.tabModel.rowCount())  # 添加序号
        self.tabModel.setData(self.tabModel.index(currow, 1), data["查询时间"])
        self.tabModel.setData(self.tabModel.index(currow, 2), data["申请单位"])
        self.tabModel.setData(self.tabModel.index(currow, 3), data["查询内容"])
        self.tabModel.setData(self.tabModel.index(currow, 4), data["对象名称"])
        self.tabModel.setData(self.tabModel.index(currow, 5), data["人数"])
        self.tabModel.setData(self.tabModel.index(currow, 6), data["单位数"])
        self.tabModel.setData(self.tabModel.index(currow, 7), data["查询文件编号"])
        self.tabModel.setData(self.tabModel.index(currow, 11), "新的查询" )     # 12-反馈状态
        self.tabModel.setData(self.tabModel.index(currow, 12), 0)              # 13-sortrank
        self.tabModel.setData(self.tabModel.index(currow, 13), data["查询银行"])   # 14-查询银行编码
        self.tabModel.setData(self.tabModel.index(currow, 14), data["未反馈银行"])
        self.tabModel.setData(self.tabModel.index(currow, 15),  data["短消息"])
        self.tabModel.setData(self.tabModel.index(currow, 16), data["未反馈银行"])  # 17-templist

        res = self.tabModel.submitAll()
        self.tabModel.setSort(12, Qt.AscendingOrder)
        self.tabModel.select()
        if not res:
            QMessageBox.critical(win, "错误", "添加记录失败：\n"+self.tabModel.lastError().text())


    # 处理反馈文书
    modifylist = []
    def do_dealFeedbackFile(self, win, sw):
        self.num_addmore = 0
        # 打开文件选择对话框，获取的是含路径的文件名orignalFeFileName_full
        orignalFeFileName_full,ftype = QtWidgets.QFileDialog.getOpenFileName(win, "Select file", os.getcwd(), "All Files(*)")
        if orignalFeFileName_full == "":
            QMessageBox.critical(win,"错误", "请选择需要反馈的查询结果！")
            return False
        else:
            curIndex = win.tableView_Data.currentIndex()
            currow = curIndex.row()
            curRec = self.tabModel.record(currow)
            # 获取不含路径的反馈文件名 orignalFeFileName_base
            # 这里要区分feio代表的json位置，首次在FolderReceive中，补充反馈在FolderSend中
            orignalFeFileName_base = os.path.basename(orignalFeFileName_full)
            f,self.ftype = os.path.splitext(orignalFeFileName_base)
            if sw =="firstTime":
                orignFileName = win.lineEdit_AskFileName.text()
                jsonfile = '.\\FolderReceive\\{}.json'.format(orignFileName)
            else:
                orignFileName = win.LineEdit_FeedbackID.text()
                jsonfile = '.\\FolderSend\\{}.json'.format(orignFileName)
                if sw == "modify":
                    with open(jsonfile, 'r', encoding='UTF-8') as f:  # 打开文件用于读
                        data = json.load(f)
                        f.close()
                    data["未反馈银行"] = curRec.value("templist")#<<<<<<<<<<<<<<<<<<<????
                    with open(jsonfile, 'w', encoding='UTF-8') as f:  # 打开文件用于读
                        json.dump(data,f)
                        f.close()

            with open(jsonfile, 'r', encoding='UTF-8') as f:  # 打开文件用于读
                data = json.load(f)
                f.close()

            statusdlg = StatusDialog(jsonfile)
            statusdlg.setDatas(orignalFeFileName_full)
            statusdlg.exec_()
            inforeturn = statusdlg.getFullStatus()
           # print("statuslist {}".format(inforeturn)) # ['RH', 'P', '中国银行、广发银行、建设银行', 'sms']

            feID= win.lineEdit_AskFileName.text()
           # banklist = curRec.value("templist")
            if inforeturn[1] == "error":
                QMessageBox.critical(win, "提示", "反馈信息填写不完整！")
            else:
                      # 反馈状态选择对话框，使用非模态对话框，阻塞其父窗口、兄窗口，直到它关闭
                timeStamp = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
                self.tabModel.setData(self.tabModel.index(currow, 8), timeStamp)  # 添加反馈时间
                self.tabModel.setData(self.tabModel.index(currow, 9), orignalFeFileName_full)  # 添加反馈文件名称
                self.tabModel.setData(self.tabModel.index(currow, 12), 1)
                self.tabModel.setData(self.tabModel.index(currow, 14), inforeturn[2])  # 未反馈银行编码
                self.tabModel.setData(self.tabModel.index(currow, 15), inforeturn[3])  # 备注
                self.tabModel.setData(self.tabModel.index(currow, 16), data["未反馈银行"])
                # 首次关联反馈文书
                if sw == "firstTime":
                    if inforeturn[1] == "F":
                        self.tabModel.setData(self.tabModel.index(currow, 10), feID+"-E1")
                        self.tabModel.setData(self.tabModel.index(currow, 11), "全部反馈")
                    else:
                        self.tabModel.setData(self.tabModel.index(currow, 10), feID+"-P1")
                        self.tabModel.setData(self.tabModel.index(currow, 11), "部分反馈")

                if sw == "notFirstTime":
                    newID = curRec.value("反馈文件编号")
                    newID_list = re.split('-', newID)
                   # banklist = hex(curRec.value("查询银行编码"))-hex(curRec.value("查询银行编码"))
                    if inforeturn[1] == "F":
                        newID_list[1] = "E" + str(int(newID_list[1].lstrip("P")) + 1)
                        self.tabModel.setData(self.tabModel.index(currow, 11), "全部反馈")
                    else:
                        newID_list[1] = "P" + str(int(newID_list[1].lstrip("P")) + 1)
                        self.tabModel.setData(self.tabModel.index(currow, 11), "部分反馈")
                    newID = "{}-{}".format(newID_list[0], newID_list[1])
                    self.tabModel.setData(self.tabModel.index(currow, 10), newID)

                # 修改反馈按键调用程序
                if sw == "modify":






                    newID = curRec.value("反馈文件编号")
                    newID_list = re.split('-', newID)
                    num = re.sub('[EP]', '', newID_list[1])
                   # banklist = hex(curRec.value("查询银行编码"))
                    if inforeturn[1] == "F":
                        newID_list[1] = "E"+num
                        self.tabModel.setData(self.tabModel.index(currow, 11), "全部反馈")
                        # 部分反馈时补充按钮提示数字减1
                    else:
                        newID_list[1] = "P" + num
                        self.tabModel.setData(self.tabModel.index(currow, 11),  "部分反馈")
                    newID = "{}-{}".format(newID_list[0], newID_list[1])
                    self.tabModel.setData(self.tabModel.index(currow, 10), newID)

                    path = os.getcwd()
                    filelist = os.listdir("{}{}".format(path, "\\FolderSend\\"))
                    for f in filelist:
                        if newID_list[0] in f:
                            os.remove("{}{}{}".format(path, "\\FolderSend\\", f))
                    # path = os.getcwd()
                    filelist = os.listdir("{}{}".format(path, "\\TempFolderSend\\"))
                    for f in filelist:
                        if newID_list[0] in f:
                            os.remove("{}{}{}".format(path, "\\TempFolderSend\\", f))



                res = self.tabModel.submitAll()
                if res:
                    curRecNo = self.selModel.currentIndex().row()
                    curRec = self.tabModel.record(curRecNo)
                    oldfilename = orignalFeFileName_full
                    newfilename = "{}{}".format(curRec.value("反馈文件编号"), self.ftype)
                    self.do_rename_copyFile(oldfilename, newfilename)
                    jsonFileName = "{}.json".format(curRec.value("反馈文件编号"))
                    self.do_rename_copyFile(".\\FolderReceive\\{}.json".format(curRec.value("查询文件编号")), jsonFileName)
                    with open(".\\TempFolderSend\\{}".format(jsonFileName), 'r', encoding='UTF-8') as f:  # 打开文件用于读
                        data = json.load(f)
                        f.close()
                    date = time.strftime('%Y%m%d', time.localtime(time.time()))
                    data["反馈时间"] = date
                    data["反馈文件名称"] = newfilename
                    data["未反馈银行"] = inforeturn[2]
                    data["短消息"] = inforeturn[3]
                    with open(".\\TempFolderSend\\{}".format(jsonFileName), 'w', encoding='UTF-8') as f:
                        json.dump(data, f)
                        f.close()
                    with open(".\\FolderSend\\{}".format(jsonFileName), 'w', encoding='UTF-8') as f:
                        json.dump(data, f)
                        f.close()

                    win.pushButton_SendFile.setEnabled(True)
                    # 重新排序，把反馈完毕放到后面
                    self.tabModel.setSort(12, Qt.AscendingOrder)
                    self.tabModel.select()

                else:
                    QMessageBox.critical(win, "错误", self.tabModel.lastError().text())
                    self.tabModel.revertAll()
                    return False

                return True


    def do_rename_copyFile(self,oldfilename,newfilename):
        path = os.getcwd()
        dstDir = "{}{}".format(path, "\\FolderSend\\")
        dstfile = dstDir + newfilename
        shutil.copyfile(oldfilename, dstfile)

        kilobytes = 1024
        megabytes = kilobytes * 1000
        chunksize = int(20 * megabytes)  # default chunksize
        # (filepath, tempfilename) = os.path.split(filename);
        # (shotname, extension) = os.path.splitext(tempfilename)

        dstDir_temp = "{}{}".format(path, "\\TempFolderSend\\")
        # for f in os.listdir(todir):
        (filepath, tempfilename) = os.path.split(newfilename);
        (shotname, extension) = os.path.splitext(tempfilename)
        # os.remove(os.path.join(todir, fname))
        partnum = 0
        filesize = os.path.getsize(oldfilename)
        #print("filesize is {}".format(filesize))
        inputfile = open(oldfilename, 'rb')  # open the fromfile
        if filesize > chunksize:
            while True:
                chunk = inputfile.read(chunksize)
                if not chunk:
                    break
                partnum += 1
                filename = os.path.join(dstDir_temp, (shotname + '@part%03d' % partnum + extension))
                fileobj = open(filename, 'wb')  # make partfile
                fileobj.write(chunk)  # write data into partfile
                fileobj.close()
        else:
            dstfile = dstDir_temp + newfilename
            shutil.copyfile(oldfilename, dstfile)


    def do_changeAndRecord(self,win, file):
        if self.tabModel.rowCount() == 0:
            return
        else:
            for i in range(self.tabModel.rowCount()):
                rec = self.tabModel.record(i)
                if rec.value("反馈文件编号") in file:
                    if rec.value("反馈状态") == "部分反馈":
                        self.tabModel.setData(self.tabModel.index(i, 12), 2)
                       # print("未反馈银行编码:{}".format(rec.value("未反馈银行编码")))
                        self.tabModel.setData(self.tabModel.index(i, 16), rec.value("未反馈银行编码"))  # 将未反馈银行编码保存在templist中
                        break
                    if rec.value("反馈状态") == "全部反馈":
                        self.tabModel.setData(self.tabModel.index(i, 12), 3)
                        self.tabModel.setData(self.tabModel.index(i, 11), "结束归档")
                        #print("未反馈银行编码:{}".format(rec.value("未反馈银行编码")))
                        self.tabModel.setData(self.tabModel.index(i, 16), rec.value("未反馈银行编码"))  # 将未反馈银行编码保存在templist中
                        break

            self.tabModel.setSort(12, Qt.AscendingOrder)
            self.tabModel.select()
            res = self.tabModel.submitAll()
            if not res:
                QMessageBox.warning(win, u"错误", u"错误！\n" + self.tabModel.lastError().text())
                self.tabModel.revertAll()




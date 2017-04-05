import time
from ui_main_window import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
# from PyQt5.Qt
from PyQt5.QtGui import *
from card import *

class MainWindow(QMainWindow, Ui_MainWindow):
    """docstring for MainWindow"""
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        path = "./API/mwrf32.dll"
        self.card = Card(path, self.show_output)
        # 初始化界面
        self.__init_gui()
        

        rg = QRegExp("^\d+(\.\d+)?$")
        rgv = QRegExpValidator(rg)
        self.lineEdit_payment.setValidator(rgv)

        # 信号与槽
        self.pushButton_pay.clicked.connect(self.on_pushButton_pay_click)        
        self.pushButton_invalid.clicked.connect(self.on_pushButton_invalid_click)        
        self.pushButton_read.clicked.connect(self.on_pushButton_read_click)
        self.pushButton_unlock.clicked.connect(self.on_pushButton_unlock_click)
        self.pushButton_hand.clicked.connect(self.on_pushButton_hand_click)

    def on_pushButton_read_click(self):
        print("==========read_click")

        state = self.card.search_card()
        if state == 1:
            print("state: %.2x  无卡" % state)

            self.pushButton_hand.setEnabled(True)
        elif state == 4:
            print("state: %.2x  为验证密码" % state)
        elif state == -1:
            self.__init_gui()
            print("读卡失败。")
        else:
            self.lineEdit_payment.setEnabled(True)
            self.pushButton_pay.setEnabled(True)
            self.refresh()
            
            # 是否锁卡
            if self.card.is_lock():
                self.pushButton_unlock.setEnabled(True)


    def on_pushButton_pay_click(self):
        print("===============enter on_pushButton_pay_click")
        init_num = float(self.label_sum.text())
        pay_num = float(self.lineEdit_payment.text())
        count_num = init_num + pay_num
        self.card.set_value(count_num)
        self.refresh()

    def on_pushButton_hand_click(self):
        print("===============enter on_pushButton_hand_click")

        self.card.hand_card()

        

    def on_pushButton_unlock_click(self, info):
        print("===============enter on_pushButton_unlock_click")
        self.card.unlock()

    def on_pushButton_invalid_click(self):
        print("===============enter on_pushButton_invalid_click ")

    def refresh(self):
        value = self.card.get_value()
        self.label_sum.setText("%.2f" % value)
    
    def __init_gui(self):
        self.lineEdit_payment.setEnabled(False)
        self.pushButton_pay.setEnabled(False)
        self.pushButton_invalid.setEnabled(False)
        self.pushButton_hand.setEnabled(False)
        self.pushButton_unlock.setEnabled(False)

    def show_output(self, info):
        self.textBrowser_output.insertPlainText("%s %s\n" %(self.__get_current_time(),info))
        self.textBrowser_output.insertPlainText("----------------------------------------------------------\n")
                
    def __get_current_time(self):
        return time.strftime( "%Y-%m-%d %X", time.localtime() )    # time.localtime(time.time)

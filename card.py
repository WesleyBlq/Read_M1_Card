from ctypes import *
from ctypes.wintypes import *
import binascii

uchar_array_6 = c_ubyte * 6
uchar_array_16 = c_ubyte * 16


class Card(object):
    """docstring for Card"""
    def __init__(self, dll_path,invoke_log=None):
        super(Card, self).__init__()
        self.dll_path = dll_path

        # invoke_log 打印日志回调函数
        self.invoke_log = invoke_log
        # 初始化读卡器
        self.__init_card()

    def __del__(self):
        self.dll.rf_exit(self.icdev)

    # 0：成功 -1：密码错误
    def hand_card(self):   
        # 激活卡片
        self.dll.rf_card(self.icdev, 0, pointer(c_long(0))) 
        # 验证密码区密码
        blockNum = 3
        p_pwd = pointer(uchar_array_6(0xff, 0xff,0xff, 0xff, 0xff, 0xff,))
        state = self.dll.rf_authentication_key(self.icdev, 0, blockNum, p_pwd) 
        print(state)

        # 读取密码区数据
        self.pwd_data = uchar_array_16()
        self.p_pwd_data = pointer(self.pwd_data)
        state = self.dll.rf_read(self.icdev, blockNum, self.p_pwd_data)

        print("hand card =====rf_read")
        print(state)

        if state == 0x4:    
            self.__log("未知密码卡片，无法发卡")
            return -1
        
        # 在Key A密码区写入新密码
        # self.pwd_data = uchar_array_6(0xff, 0xee, 0xdd, 0xcc, 0xbb, 0xaa)
        # self.p_pwd_data = pointer(self.pwd_data)
        self.pwd_data[0] = 0xff
        self.pwd_data[1] = 0xee
        self.pwd_data[2] = 0xdd
        self.pwd_data[3] = 0xcc
        self.pwd_data[4] = 0xbb
        self.pwd_data[5] = 0xaa
        print("hand card =====rf_write before")
        self.__print_char_array(self.p_pwd_data.contents)
        state = self.dll.rf_write(self.icdev, blockNum, self.p_pwd_data)
        print("hand card =====rf_write after")
        self.__print_char_array(self.p_pwd_data.contents)
        
        # 输出日志信息
        print("=================hand card")
        self.__print_char_array(self.p_pwd_data.contents)
        print(hex(state))
        info = "发卡成功" if state == self.beep_state else "发卡失败"
        self.__log(info)

        return 0

    def write_data(self,blockNum=1):
        # self.p_data.contents[3] = 0x41
        state = self.dll.rf_write(self.icdev, blockNum, self.p_data)

        print("====================write card data")
        self.__print_char_array(self.p_data.contents)
        print(hex(state))
        if state == self.beep_state:
            self.__log("写入成功")
        else:
            self.__log("写入失败")

    
    def __init_card(self):
        self.dll = windll.LoadLibrary(self.dll_path)
        self.__connect_card()
        pass

    def __connect_card(self):
        self.icdev = self.dll.rf_init(0, 115200)
        if self.icdev < 0:
            self.__log("连接失败")
        else:
            # 蜂鸣器发声
            state = self.dll.rf_beep(HANDLE(self.icdev), c_uint(300))
            self.beep_state = state
            print("beep state : %s" % hex(state))

            # 获取版本哈
            s = create_string_buffer(19)
            state = self.dll.rf_get_status(HANDLE(self.icdev), s)

            content = s.value
            print("===========connect")
            print("state %s" % state)
            self.__log("连接成功。版本号-%s" % s.value.decode())

    def search_card(self):
        # 0x4 密码错误， 0x1 无卡 , -1 读卡失败，-2 新卡
        print("=========== check card sn")

        blockNum = 1
        sn = pointer(c_long(0))
        state = self.dll.rf_card(self.icdev, 1, sn)
        if state != 1:
            # 验证卡密码
            p_pwd = pointer(uchar_array_6(0xff, 0xee,0xdd, 0xcc, 0xbb, 0xaa,))
            # p_pwd = pointer(uchar_array_6(0xff, 0xff,0xff, 0xff, 0xff, 0xff,))
            state = self.dll.rf_authentication_key(self.icdev, 0, blockNum, p_pwd)

            # 读取数据，获得读取状态
            self.data = uchar_array_16()
            self.p_data = pointer(self.data)
            state = self.dll.rf_read(self.icdev, blockNum, self.p_data)

            print("sn = %s" % hex(sn.contents.value))
            self.__log("读卡成功。卡号：%s" % hex(sn.contents.value))
            print(state)

            # 判断状态
            return 0 if state == self.beep_state else state
        else:
            self.__log("读卡失败.")

            return -1

    def is_lock(self):
        if self.data[3] == 0x41:
            return True
        else:
            return False

    def unlock(self):
        print("==============unlock")
        self.data[3] = 0x00
        self.write_data() 

    def get_value(self):
        print("=========get_value")
        num = (self.data[2] << 16) + (self.data[1] << 8) + self.data[0]
        print("num: %s" % num)
        return float(num / 100)

    def set_value(self, value):
        print("==========set value")
        num = value * 100
        num = hex(int(num))
        num = num[2:]
        length = len(num)
        flag = 6 - length
        if flag > 0:
            for x in range(flag):
                num = '0' + num
        print(num)
        self.data[0] = int(num[4:6], 16)
        self.data[1] = int(num[2:4], 16)
        self.data[2] = int(num[0:2], 16)

        self.write_data()

    def __print_char_array(self, ob, size=16):
        print("0x", end='')
        for x in range(0,size):
            print("%.2x" % ob[x], end='')
        print('')

    def __log(self, info):
        if self.invoke_log != None:
            self.invoke_log(info)

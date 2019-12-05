from serial import Serial, SerialException, SerialTimeoutException
from time import time, sleep
import re
import threading
import glob
import platform
import datetime



class Printer:
    def __init__(self, port: str):
        self.port = port  # 串口号
        self.baud_rate = 115200  # 波特率
        self.name = 'unknown'  # 打印机名字，暂时没什么用
        self.serial = None  # 串口对象
        self.timeout = 5  # 连接超时时间
#        self.data_update_timeout = 1  # 数据更新超时时间

        self.run = False  # 线程开关

        self.updater_t = threading.Thread(target=self.read_data)  # 数据更新线程
        self.updater_t.setDaemon(True)  # 守护线程

        self._command_received = True  # 命令收到标志，打印过程中基本无效，因为会大量输出ok
        self.t_received = True  # 温度是否读取
        self.p_received = True  # 位置是否读取

        # 以下变量按照协议命名，其中0e不是打印进度，是输出的E:xx.xx
        self.t1 = '0.00'
        self.t2 = '0.00'
        self.t3 = '0.00'

        self.x = '0.00'
        self.y = '0.00'
        self.z = '0.00'
        self.e = '0.00'

        #创建串口数据跟踪日志by Yuan
        self.data_time = None
#        self.f1 = None


    def __del__(self):  # 对象被清除时停止线程关闭串口
        if self.serial is not None:
            self.serial.close()
        self.run = False

    def connect(self, baud_rate=None):
        # 初始化
        if self.serial:  # 如果正在运行则先停止线程关闭串口
            self.serial.flushOutput()
            self.run = False
            self.serial.close()
#        self.setDTR(level=True)    
        if baud_rate is not None:  # 如果输入波特率则存为成员变量，没有则保持默认115200
            self.baud_rate = baud_rate
        try:  # 连接串口
            self.serial = Serial(self.port, self.baud_rate, timeout=self.timeout, writeTimeout=self.timeout)
            print (self.serial)
            self.serial.ReadTimeout = 5000
            #获取串口信息
        except SerialException as e:
            print("serial connect fail")
            print(str(e))
            return False
        # 下面所有都是基于CURA里面的代码改的
        sleep(5)  
# CURA:Ensure that we are not talking to the boot loader. 1.5 seconds seems to be the magic number
        # 上面是为了跳过启动时一大堆输出而延时
        successful_responses = 0  # 成功计数

    
        while True:  # 在超时时间内反复连接 -> 计数3次，3次请求成功，则判定为连接成功，否则一直卡在循环里
            self.serial.write(b"\n")
            self.serial.write(b"M105\n")
            print(datetime.datetime.now().strftime('%H:%M:%S') + " Test M105\n")
               # 串口读一行
#            data_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(datetime.datetime.now().strftime('%H:%M:%S') + " Test " + self.serial.readline().decode() + "\n")
            line = self.serial.readline()
 
            if b"ok T:" in line or b"ok == T:" in line or b"'k T:" in line or b"'ok T:" in line or b"ok ":  # 有回复温度则继续发，ok==T是为了适配武汉的板子
                successful_responses += 1
                print(successful_responses)
                self.serial.flushInput()
                                          
            if successful_responses >= 1:  # 三次成功就判定为连接成功
                self.run = True
                self.updater_t.start()  # 启动接收线程
                self.sendCommand('M114')  # 询问温度，因为后面是回了才发，发了才回，如此循环，前面必须有个触发
#                self.sendCommand('M114')  # 询问位置，因为后面是回了才发，发了才回，如此循环，前面必须有个触发
                return True

#        self.serial.close()  # 连接不成功就把痕迹清除
#        self.serial = None
#        return False

    # Send a command to printer.接收平台的指令发送给打印机
    def sendCommand(self, command: str):
        if self.serial is None:  # 串口没连上直接作为失败
            return 'fail'
        command = command.encode()  # 将命令字符串变为字节流
        if not command.endswith(b"\n"):  # 命令必须回车才有效，没有则自动添加
            command += b"\n"
#        timeout_t = time() + self.timeout
        try:
            self.serial.write(command)  # 发送命令
            self.serial.flush()
        except:
            print("write data to printer error")
            pass
        print(datetime.datetime.now().strftime('%H:%M:%S') + "  request: " + command.decode() + "\n")
        self._command_received = False



    # 接收打印机数据，并解析
    def read_data(self):
        temperature_t = time()  # 初始化上一次收到温度数据的时间
        position_t = time()  # 初始化上一次收到位置数据的时间
        while self.run:
            try:  # 串口读行
                line = self.serial.readline()
                print(datetime.datetime.now().strftime('%H:%M:%S') + "  Response: " + line.decode() + "\n")
                sleep(3)
            except:
                print(datetime.datetime.now().strftime('%H:%M:%S') + "  Response:error\n")
                print("read data from printer error")                
#                self.serial.close()
#                ret = self.connect(115200)
#                if not ret:
#                    ret = self.connect(250000)
                continue

#            if _command_received:
#            self.sendCommand('M105')
            # 如果距离上一次收到温度数据的时间超过data_update_timeout则询问以防回了才发，发了才回的循环断开
#            if time() - temperature_t > self.data_update_timeout:
#            self.sendCommand('M105')
            # 如果距离上一次收到位置数据的时间超过data_update_timeout则询问以防回了才发，发了才回的循环断开
#            if time() - position_t > self.data_update_timeout:
            self.sendCommand('M105')
            # 正则表达式取温度信息
            
            if line.startswith(b"ok T") or line.startswith(b"T:") or line.startswith(b"ok == T:") or line.startswith(b" == T:") or line.startswith(b"'k T:") or line.startswith(b"'ok T") or line.startswith(b"k T:"):
#                temperature_t = time()  # 更新上一次获取温度信息的时间
                line1 = line.decode()
                if 'B:' in line1:
                    res = re.findall("B: ?([\-\d\.]+)", line1)
                    self.t3 = res[0]
                    if 'T:' in line1:
                        res = re.findall("T: ?([\-\d\.]+)", line1)
                        self.t1 = res[0]
                    else:
                        res = re.findall("T0: ?([\-\d\.]+)", line1)
                        self.t1 = res[0]
                sleep(3)
                self.serial.flushInput()
                self.sendCommand('M114')

                
                # 在升温过程中是主动发送没有ok不用询问（line.startswith(b"T:" or  b" == T:")）
#                if line.startswith(b"ok T") or line.startswith(b"ok == T:") or line.startswith(b"'k T:") or line.startswith(b"'ok T"):
#            self.sendCommand('M114')   
            # 正则表达式取位置信息
            if line.startswith(b"X:") or line.startswith(b"ok C:") or line.startswith(b"'k C:") or line.startswith(b"'ok C:") or line.startswith(b"k C"):
#                position_t = time()
                line1 = line.decode()
                res = re.findall("X: ?([\-\d\.]+)", line1)
                self.x = res[0]
                res = re.findall("Y: ?([\-\d\.]+)", line1)
                self.y = res[0]
                res = re.findall("Z: ?([\-\d\.]+)", line1)
                self.z = res[0]
                res = re.findall("E: ?([\-\d\.]+)", line1)
                self.e = res[0]
                sleep(3)
                self.serial.flushInput()

#                self.sendCommand('M105')

#            if b"ok" in line:  # 命令是否获取成功的标志量置位
#                self._command_received = True


# 用于单元测试
if __name__ == '__main__':
    if platform.system() == 'Linux':
        COM = glob.glob(r'/dev/ttyUSB*') + glob.glob(r'/dev/ttyACM*')
        if len(COM) == 0:
            COM = '/dev/ttyUSB0'
        else:
            COM = COM[0]
    else:
        COM = 'COM10'
    p = Printer(COM)
    ret = False
    while not ret:
        print('connecting\n'+str(ret))
        ret = p.connect(115200)
        if ret:
            break
        sleep(2)
    while True:
#        print(p.t1)
#        print(p.t3)
#        sleep(1)
        pass

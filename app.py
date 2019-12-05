from flask import Flask, render_template, request
from printer import Printer
from uploader import Uploader
import os
import platform
import time
from led import LED
import glob
import threading
from apscheduler.schedulers.background import BackgroundScheduler

if platform.system() == 'Linux':
    COM = glob.glob(r'/dev/ttyUSB*') + glob.glob(r'/dev/ttyACM*')
    if len(COM) == 0:
        COM = '/dev/ttyUSB0'
    else:
        COM = COM[0]
else:
    COM = 'COM6'

app = Flask(__name__)
#p = Printer(COM)
#u = Uploader(p)
l = LED()
i = 0 
aps = BackgroundScheduler()
settings = {
    'ssid': '',
    'psw': '',
    'ip': '',
    'eid': '',
    'pw': ''
}


@app.route('/')
def enter():
    if os.path.isfile('settings.txt'):
        return render_template('index.html')
    else:
        return render_template('wizard.html')


@app.route('/index')
def index():
    with open('settings.txt', 'w') as f:
        f.write(str(settings))
    if platform.system() == 'Linux':
        return render_template('index.html')
        # os.system('reboot')
    else:
        return render_template('index.html')


@app.route('/setting')
def setting():
    return render_template('settings.html', **settings)


@app.route('/reset')
def reset():
    os.remove('settings.txt')
    if platform.system() == 'Linux':
        os.system('reboot')
    else:
        exit()
    return 200


@app.route('/api/wifi_setting', methods=['GET', 'POST'])
def wifi():
    if request.method == 'POST':
        ssid = request.form['ssid']
        psw = request.form['psw']
        ret = wifi_connect(ssid, psw)
        if ret:
            settings['ssid'] = ssid
            settings['psw'] = psw
            return '连接成功'
        else:
            return '连接失败'


# @app.route('/api/printer_test', methods=['GET', 'POST'])
# def printer_test():
#     if request.method == 'POST':
#         baud_rate = request.form['baud_rate']
#         if platform.system() == 'Linux':
#             global COM
#             COM = glob.glob(r'/dev/ttyUSB*') + glob.glob(r'/dev/ttyACM*')
#             print(COM)
#             if len(COM) == 0:
#                 COM = '/dev/ttyUSB0'
#             else:
#                 COM = COM[0]
#             p.port = COM
#         ret = p.connect(int(baud_rate))
#         if not ret:
#             return '连接失败'
#         else:
#             settings['baud_rate'] = baud_rate
#             return '连接成功'


@app.route('/api/server_save', methods=['GET', 'POST'])
def server_test():
    if request.method == 'POST':
        ip = request.form['ip']
        eid = request.form['eid']
        pw = request.form['pw']
        # ret = u.connect(ip, eid, pw)
        settings['ip'] = ip
        settings['eid'] = eid
        settings['pw'] = pw
        return '保存成功'
        # if not ret:
        #     return '连接失败'
        # else:
        #
        #     return '连接成功'


@app.route('/reboot', methods=['GET','POST'])
def reboot_system():
    if platform.system() == 'Linux':
        os.system('reboot')
    else:
        exit()


def wifi_connect(ssid: str, psw: str):
    if platform.system() == 'Linux':
        r = os.popen('wpa_passphrase "' + ssid  + '" "' + psw + '" >/root/3DP2/3DP2/wpa.conf')
#        time.sleep(3)
        z = os.popen('sh /root/3DP2/3DP2/wireless.sh')
        time.sleep(6)
        os.system('udhcpc -i wlan0 -T 1 -t 15 -n')
        timeout_t = time.time() + 10
        while timeout_t > time.time():
            with open ('/root/3DP2/3DP2/abc.txt') as a:
                for line in a:
                   if(' CTRL-EVENT-CONNECTED' in line):
                       return True
                return False
            return False
        return False
    return True


def configure():
    if platform.system() == 'Linux':
        app.run(host='0.0.0.0', port=80)
    else:
        app.run(host='127.0.0.1', port=80) 

#def check():
#    l.stop()
#    经测试，程序是可以通过aps进来，不过是延时三十秒，不要心急
##    global i
##    if(g == True): #这句话检测出来g没有变成True，所以是传g值发生问题
#        l.stop()   #这个和上面的if构成了检测环节，但是并没有发生该有的现象
##    if (Uploader.g):
##        i = 0
##        Uploader.g = False
##    else:
##        i = i + 1 #  这里经检测无误
##        if(i >= 2):#  这里经检测无误
##            i = 0
##            os.system('reboot')
##            while True:
##                ret_1 = u.connect(settings['ip'], settings['eid'], settings['pw'])
##                if ret_1:
##                    l.t = 1
##                    break
##                else:
##                    pass
         # 测试是否连接上，制造现象    #  这里经检测无误
##    timer = Timer(30,check)
##    timer.start() 


          
if __name__ == '__main__':
    t = threading.Thread(target=configure)
    t.start()
    count = 1
    if os.path.isfile('settings.txt'):
        with open('settings.txt', 'r') as f:
            settings = eval(f.read())
        while True:
            if settings['ssid'] is None or settings['psw'] is None:
                break
            else:
                ret = wifi_connect(settings['ssid'], settings['psw'])
                count += 1
                if ret:
                    os.system('sh ./route.sh')
                    break
                elif count == 3:
                    break
        l.t = 2
##        while True:
##            ret = p.connect(115200)
##            if ret:
##                break
##            ret = p.connect(250000)
##            if ret:
##                break
##            time.sleep(5)
        l.t = 1
#        s = 0
#        b = os.popen('iwconfig wlan0')
        os.system('bash /root/3DP2/3DP2/eth0_0.sh')
#        c = os.popen('ifconfig eth0:0')
        l.t = 0.1
##        while True:
##            ret = u.connect(settings['ip'], settings['eid'], settings['pw'])
##            if ret:
##                break
        l.stop()
##        aps.add_job(check,'interval',seconds=30)
#        l.t = 0.1
##        aps.start()
#        l.t = 2
#        timer = Timer(30,check)
#        timer.start()
        
#        time_out10 = time.time() + 60
#        while(time_out10 > time.time()):
#            if(m == 1):
#                global n
#                n = threading.Timer(30.0,check)
#                n.start()
#        while(time_out10 < time.time()):
#            if(m == 0):
#                restart()
#        l.stop()


import socket
import RPi.GPIO as GPIO
from threading import Thread
    

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

MY_PRE = '>> '
OTHER_PRE = 'A:'
OTHER_IP = '192.168.20.10'
IS_SERVER = True
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ETH = None


def eth_setup(is_server):
    global SOCKET, ETH, IS_SERVER

    IS_SERVER = is_server

    if IS_SERVER:
        SOCKET.bind(('', 5005,))
        SOCKET.listen(1)
        ETH, addr = SOCKET.accept()
    else:
        SOCKET.connect((OTHER_IP, 5005,))
        ETH = SOCKET

    return ETH


def eth_decode(s):
    """
    Startjel: ~
    Végejel: ;
    """
    new_s = ''
    ns = s.decode('utf-8')
    can_read = False

    for ch in ns:
        if ch == '~':
            can_read = True
            continue

        if can_read and ch == ';':
            break
        elif can_read:
            new_s += ch
    else:
        return ''

    return new_s


def eth_encode(s):
    return bytearray(('~' + str(s) + (';' if s[-1] != ';' else '')).encode('utf-8'))


def eth_eval(text):
    cmds = [t for t in text.split(',') if t]
    
    for cmd in cmds:
        if cmd[0] == 'o':
            GPIO.setup(int(cmd[1:]), GPIO.OUT)
        if cmd[0] == 'l':
            GPIO.output(int(cmd[1:]), GPIO.LOW)
        if cmd[0] == 'h':
            GPIO.output(int(cmd[1:]), GPIO.HIGH)
            

if __name__ == '__main__':
    def send_msg():
        while True:
            ETH.send(eth_encode(input(MY_PRE)))

            
    def get_msg():
        while True:
            data = eth_decode(ETH.recv(1024))
            if data:
                print(OTHER_PRE, data)

    ETH = eth_setup(IS_SERVER)
    
    try:
        Thread(target=send_msg).start()
        Thread(target=get_msg).start()
        while True:
            pass
    except:
        print('\nError happened:')
        print(str(e))
        print('\n')
    finally:
        ETH.close()

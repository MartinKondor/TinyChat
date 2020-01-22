import socket
from threading import Thread
    

OTHER_IP = '192.168.1.21'
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
    Startsign: ~
    Endsign: ;
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
            

if __name__ == '__main__':
    def send_msg():
        while True:
            ETH.send(eth_encode(input('>> ')))

            
    def get_msg():
        while True:
            data = eth_decode(ETH.recv(1024))
            if data:
                print(data)

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

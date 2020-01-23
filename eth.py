import socket


class ETHConnection:
    
    def __init__(self, other_ip, is_server, port=5005):
        self.IS_SERVER = is_server
        self.OTHER_IP = other_ip
        self.ETH = None
        self.PORT = port
        self.connect()

    def send(self, s):
        try:
            self.ETH.send(self._eth_encode(s))
        except Exception as e:
            print('Error when sending message ({}):{}\n'.format(s, str(e)))

    def recv(self, n):
        return self._eth_decode(self.ETH.recv(n))

    def connect(self):
        try:
            SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if self.IS_SERVER:
                SOCKET.bind(('', self.PORT,))
                SOCKET.listen(1)
                self.ETH, addr = SOCKET.accept()
            else:
                SOCKET.connect((self.OTHER_IP, self.PORT,))
                self.ETH = SOCKET
        except Exception as e:
            print('Error when connecting:', str(e))

    def reconnect(self):
        self.close()
        self.ETH = None
        self.connect()

    def close(self):
        try:
            self.ETH.close()
        except:
            pass

    def _eth_decode(self, s):
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


    def _eth_encode(self, s):
        return bytearray(('~' + str(s) + (';' if s[-1] != ';' else '')).encode('utf-8'))
            

if __name__ == '__main__':
    """
    from threading import Thread


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
    """
    pass

import socket


class ETHConnection:
    
    def __init__(self, other_ip, is_server, port=5005):
        self.IS_SERVER = is_server
        self.OTHER_IP = other_ip
        self.ETH = None
        self.PORT = port
        self.is_connected = False
        self.connect()

    def send(self, s):
        try:
            self.ETH.send(self._eth_encode(s))
        except Exception as e:
            print('Error when sending message ({}):{}\n'.format(s, str(e)))
            self.reconnect()

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

            self.is_connected = True
        except Exception as e:
            print('Error when connecting:', str(e))
            self.ETH = None
            self.is_connected = False

    def reconnect(self):
        self.close()
        self.connect()

    def close(self):
        try:
            self.ETH.close()
        except:
            pass

    def _eth_decode(self, s):
        return s.decode('utf-8')

    def _eth_encode(self, s):
        return bytearray(str(s).encode('utf-8'))

    def __bool__(self):
        return self.ETH is not None
            

if __name__ == '__main__':
    pass

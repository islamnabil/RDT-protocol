from Server import *


class Client:
    def __init__(self, port):
        self.ip, self.port = local_address(port)
        self.address = (self.ip, self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def request(self, file):
        # Connect to server
        self.socket.connect(self.address)
        print('Connected to', self.address)

        # Send file request
        pkt = Packet(file=file)
        self.socket.send(pkt.__dumb__())

        # Check for response
        try:
            res = self.socket.recv(PACKET_SIZE)
            pkt = Packet(pickled=res)
            pkt.__print__()

            if pkt.__get__('status') == 'found':
                self.recv_file(file)
            else:
                pkt.__print__()
        except ConnectionError:
            pass

    def recv_file(self, file):
        open(file=file, mode='wb').close()
        f = open(file=file, mode='ab')
        while True:
            try:
                res = self.socket.recv(PACKET_SIZE)
                if res:
                    pkt = Packet(pickled=res)
                    pkt.__print__()
                    # Check for corruption
                    if pkt.__validate__():
                        f.write(pkt.__get__('data'))
                        # Send positive ack
                        ack = Packet(seq_num=pkt.__get__('seq_num'), ack='+')
                        self.socket.send(ack.__dumb__())
                    else:  # Send negative ack
                        ack = Packet(seq_num=pkt.__get__('seq_num'), ack='-')
                        self.socket.send(ack.__dumb__())
                else:
                    raise ConnectionError
            except ConnectionError:
                break
        f.close()
        self.socket.close()


requested_file = input('File name: ') or 'text.txt'
c = Client(SERVER_PORT)
c.request(requested_file)

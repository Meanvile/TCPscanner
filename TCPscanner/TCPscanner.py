import sys
import socket
import argparse
import threading
from queue import Queue


class TCPscanner(object):
    def __init__(self, args):
        self.args = args
        self.host = self.args.host
        self.start = int(self.args.start)
        self.end = int(self.args.end)
        self.ip = socket.gethostbyname(self.host)
        self.ports = []
        self.queue = Queue()

    def run(self):
        try:
            for i in range(self.start, self.end):
                sock = socket.socket(socket.AF_INET,
                                     socket.SOCK_STREAM)
                sock.settimeout(5)
                port = sock.connect_ex((self.ip, i))
                if port == 0:
                    self.ports.append(i)
                    print(f'Открыт порт №{i}')
            if self.ports:
                self.write_file()
            else:
                print('Открытых портов в заданном диапазоне нет')
            return self.ports
        except Exception as e:
            print(f'Во время проверки портов произошла ошибка: \n{e}')



    def write_file(self):
        with open('ports.txt', 'w') as result:
            print('Запись произведена успешно')
            result.write(f'Открытые порты {self.host}: {str(self.ports)[1:-1]}')

    def scan_port(self, port):
        try:
            sock = socket.socket(socket.AF_INET,
                                 socket.SOCK_STREAM)
            sock.connect((self.ip, port))
            return True
        except Exception as e:
            return False

    def queue_of_ports(self, start, end):
        for p in range(start, end + 1):
            self.queue.put(p)

    def thread(self):
        while not self.queue.empty():
            port = self.queue.get()
            if self.scan_port(port):
                self.ports.append(port)

    def run_multi(self):
        self.queue_of_ports(self.start, self.end)
        threads = []
        for i in range(500):
            thread = threading.Thread(target=self.thread)
            threads.append(thread)
        for i in threads:
            i.start()
        for i in threads:
            i.join()
        if self.ports:
            for i in sorted(self.ports):
                print(f'Открыт порт №{i}')
            self.write_file()
        else:
            print('Открытых портов в заданном диапазоне нет')
        return self.ports


def set_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', nargs='?', help='enter host',
                        default='localhost')
    parser.add_argument('start', nargs='?', help='port to start from',
                        default=100)
    parser.add_argument('end', nargs='?', help='last port to check',
                        default=140)
    parser.add_argument('mode', nargs='?', help='multi or single threading',
                        default='single')
    return parser


if __name__ == '__main__':
    parser = set_parser()
    args = parser.parse_args(sys.argv[1:])
    TCP = TCPscanner(args)
    if args.mode == 'single':
        r = TCP.run()
    else:
        r = TCP.run_multi()


"""
Socket networking tools

AdvancedSocket difference finder is not complete

"""

import os
import socket
import time

from clay.files.core import FileSizeReport as _FSR

DEF_PORT = 1024
MAX_BUFFER = 10000
MAX_CONN = 1

LOCALHOST = '127.0.0.1'
UNIT_SEP = b'\x1f'
UTF_SET = 'utf8'

def get_ip_address():
    """Returns the IP address of the host"""
    return socket.gethostbyname(socket.gethostname())

def get_next_open_port(ip, port):
    """Returns the next open port for the given IP address starting at port"""
    found = False
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((ip, port))
            found = True
        except:
            port += 1
        finally:
            s.close()
        if found:
            break
    print('next open port ->', port)
    return port

class AdvancedSocket:
    """Super-class for Server and Client socket handlers"""

    def show_info(self):
        """
        Prints information about this socket and is called
        at the beginning of a session

        """
        print(self.sock, 'started')

    def read_bin(self, buffer=MAX_BUFFER):
        """Reads up to `buffer` bytes from the stream"""
        try:
            return self.sock.recv(buffer)
        except:
            return b'quit'

    def read_stream_len(self, length, buffer=MAX_BUFFER):
        """
        Receives and returns a filestream from the stream of given
        length at buffer sized chunks

        """
        stream = bytes()
        while True:
            stuff = self.read_bin(buffer)
            stream += stuff
            if len(stream) >= length:
                print('max reached')
                break
        return stream

    def read_stream(self, buffer=MAX_BUFFER, file=False):
        """Receives and returns a stream of bytes read from a file"""
        stream = bytes()
        while True:
            stuff = self.read_bin(buffer)
            if UNIT_SEP in stuff:
                stream += stuff[:stuff.index(UNIT_SEP)]
                break
            stream += stuff
            if file:
                print('\r' + str(len(stream)), 'bytes', flush=True, end='')
        time.sleep(0.01)
        return stream

    def send_bin(self, text, charset=UTF_SET):
        """Sends the text through the stream"""
        if isinstance(text, str):
            text = text.encode(charset)
        self.sock.send(text)

    def send_sep(self):
        """Sends the end of unit signal"""
        self.sock.send(UNIT_SEP)

    def send_stream(self, stream, buffer=MAX_BUFFER):
        """Sends a stream of bytes to the recipient"""
        for i in range(0, len(stream), buffer):
            try:
                self.send_bin(stream[i:i + buffer])
            except:
                self.send_bin(stream[i:])
            finally:
                pass # alternatively time.sleep(0.01)

    def close(self):
        """Closes this session"""
        print('closing {}'.format(self.__class__))
        self.sock.close()
        print('{} closed'.format(self.__class__))

    def write_stream(self, filename, buffer=MAX_BUFFER, charset=UTF_SET):
        """Write a file stream to the given filename"""
        stream = self.read_stream(buffer, file=True)
        with open(filename, 'wb') as fp:
            print('\r' + str(fp.write(stream)), 'bytes')
        time.sleep(0.1)

    def write_streams(self, files, length, buffer=MAX_BUFFER, charset=UTF_SET):
        """
        Receives file content as one string and parses for each file
        Assumes 'eof' is not contained in the files

        """
        print('expected', length)
        streams = self.read_stream_len(length=length, buffer=buffer)
        print('actual', len(streams))
        for num in range(len(files)):
            stream = streams[:streams.index(b'eof')]
            filename = files[num]
            with open(filename, 'wb') as fp:
                print(filename, '//', str(fp.write(stream)), 'bytes')
            streams = streams[streams.index(UNIT_SEP) + len(UNIT_SEP):]
        time.sleep(0.2)

    def show_diff(self, src, dst):
        """Shows file changes between the given src state and the dst state"""
        changed = []
        removing = []

        self.send_bin(dst.encode(UTF_SET))

        d_src = _FSR(src).generate()

        print('d_src =', d_src)

        stream = self.read_bin()
        d_dst = eval(stream.decode(UTF_SET))
        # check for changed or added
        for thing in d_src:
            if thing in d_dst and d_src[thing] != d_dst[thing] or thing not in d_dst:
                changed.append(thing)
        # check for files to be removed
        for thing in d_dst:
            if thing not in d_src:
                removing.append(thing)

        self.d_src = d_src
        print('changed', changed)
        print('removing', removing)

    def send_diff(self):
        """Send the differences through the steam"""

        recv = self.read_bin().decode(UTF_SET)
        d_dst = _FSR(recv).generate()

        print('d_dst =', d_dst)
        self.send_stream(str(d_dst).encode(UTF_SET))
        self.d_dst = d_dst # debug

class Client(AdvancedSocket):

    """Class Client can be used to connect to a server"""

    def __init__(self, ip=None, port=DEF_PORT):
        """Initializes this advanced client socket"""
        if ip is None:
            ip = input('ip? ')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        print('client connected')
        self.sock = sock

class Server(AdvancedSocket):

    """Class Server can be used to host connections"""

    def __init__(self, ip='0.0.0.0', port=DEF_PORT, maxcon=MAX_CONN):
        """Initializes this advanced server socket"""
        port = get_next_open_port(ip, port)
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serv.bind((ip, port))
        serv.listen(maxcon)
        print('server listening...')
        sock, addr = serv.accept()
        self.sock = sock
        self.addr = addr

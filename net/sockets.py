
"""
Socket networking tools for Python

AdvancedSocket difference finder functionality is not fully implemented


"""


import os
import socket
import time

DEF_PORT = 1024
MAX_BUFFER = 10000
MAX_CONN = 1

FILESEP = b'eof' + b'eof'
LOCALHOST = '127.0.0.1'
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

class AdvancedSocket(object):
    """Super-class for Server and Client socket handlers. Extends `object` ATM"""

    def getbin(self, buffer=MAX_BUFFER):
        """Receives up to `buffer` bytes from the stream"""
        try:
            return self.sock.recv(buffer)
        except:
            return b'quit'

    def getfilestream(self, streamlen, buffer=MAX_BUFFER):
        """Receives and returns a filestream read from the stream of
           given length at buffer sized chunks"""
        stream = bytes()
        while True:
            stuff = self.getbin(buffer)
            stream += stuff
            if len(stream) >= streamlen:
                print('max reached')
                break
        return stream

    # work in progress
    def getstream(self, buffer=MAX_BUFFER, file=False):
        """Receives and returns a stream of bytes read from a file"""
        stream = bytes()
        while True:
            stuff = self.getbin(buffer)
            if FILESEP in stuff:
                stream += stuff[:stuff.index(FILESEP)]
                break
            stream += stuff
            if file:
                print('\r' + str(len(stream)), 'bytes', flush=True, end='')
        time.sleep(0.01)
        return stream

    def sendbin(self, text, charset=UTF_SET):
        """Sends the text through the stream"""
        if type(text) == str:
            text = text.encode(charset)
        self.sock.send(text)

    def sendeof(self):
        """Sends the end of file signal"""
        self.sock.send(FILESEP)

    def sendstream(self, stream, buffer=MAX_BUFFER):
        """Sends a stream of bytes to the recipient"""
        for i in range(0, len(stream), buffer):
            try:
                self.sendbin(stream[i:i+buffer])
            except:
                self.sendbin(stream[i:])
            finally:
                pass # alternatively time.sleep(0.01)

    def test(self):
        """Prints information about this socket and is called
           at the beginning of a session"""
        print(self.sock, 'started')

    def terminate(self):
        """Closes this session"""
        print('closing {}'.format(self.__class__))
        self.sock.close()
        print('{} closed'.format(self.__class__))

    def writestream(self, filename, buffer=MAX_BUFFER, charset=UTF_SET):
        """Write a file stream to the given filename"""
        stream = self.getstream(buffer, file=True)
        with open(filename, 'wb') as fp:
            print('\r' + str(fp.write(stream)), 'bytes')
        time.sleep(0.1)

    def writestreams(self, files, streamlen, buffer=MAX_BUFFER, charset=UTF_SET):
        """Receives file content as one string and parses for each file
           Assumes 'eof' is not contained in the files"""
        print('expected', streamlen)
        streams = self.getfilestream(streamlen=streamlen, buffer=buffer)
        print('actual', len(streams))
        #for num, stream in enumerate(streams[:-3].split(b'eof')):
        for num in range(len(files)):
            stream = streams[:streams.index(b'eof')]
            filename = files[num]
            with open(filename, 'wb') as fp:
                print(filename, '//', str(fp.write(stream)), 'bytes')
            streams = streams[streams.index(FILESEP)+len(FILESEP):]
        time.sleep(0.2)

    def getdiffs(self, src, dst):
        """Detects changes and removals to get from the given src state
           to the dst state"""
        changed = []
        removing = []
        self.sendbin(dst.encode(UTF_SET))

        d_src = self.loaddiff(src)

        print('d_src =', d_src)

        stream = self.getbin()
        d_dst = eval(stream.decode(UTF_SET))
        # check for changed or added
        for thing in d_src:
            if thing in d_dst and d_src[thing] != d_dst[thing] or not(thing in d_dst):
                changed.append(thing)
        # check for files to be removed
        for thing in d_dst:
            if not(thing in d_src):
                removing.append(thing)

        self.d_src = d_src
        print('changed', changed)
        print('removing', removing)

    def senddiffs(self):
        """Send the differences through the steam"""

        from subprocess import check_output

        recv = self.getbin().decode(UTF_SET)
        d_dst = self.loaddiff(recv)

        print('dd =', d_dst)
        self.sendstream(str(d_dst).encode(UTF_SET))
        self.d_dst = d_dst

    def loaddiff(self, Dir):
        """Loads and returns the differces as a dict"""
        Dict = {}
        for root, dirs, files in os.walk(Dir):
            for file in files:
                name = os.path.join(root, file)
                key = name[name.index(os.path.sep)+1:]
                Dict[key] = os.stat(name).st_size
        return Dict.copy()

class Client(AdvancedSocket):

    """Class Client can be used to connect to a server"""

    def __init__(self, ip=None, port=DEF_PORT):
        if ip is None:
            ip = input('ip? ')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        print('client connected')
        self.sock = sock

class Server(AdvancedSocket):

    """Class Server can be used to host connections"""

    def __init__(self, ip='0.0.0.0', port=DEF_PORT, maxcon=MAX_CONN):
        port = get_next_open_port(ip, port)
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serv.bind((ip, port))
        serv.listen(maxcon)
        print('server listening...')
        sock, addr = serv.accept()
        self.sock = sock
        self.addr = addr

if __name__ == '__main__':

    from clay.files.core import FileSizeReport

    report = FileSizeReport(directory='.')
    print('File size report')
    print(report)
    print(report.parse())

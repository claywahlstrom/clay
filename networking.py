
"""
Networking tools for Python

AdvancedSocket difference finder functionality is not fully implemented


"""


import os as _os
import socket
import time

DEF_PORT = 1024
MAX_BUFFER = 10000
MAX_CONN = 1

UTF_CHAR = 'utf8'
FILESEP = b'eof' + b'eof'

def nextopenport(ip, port):
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
    print('port selected ->', port)
    return port

class Report(object):
    """A class for generating reports on file systems
    An exmaple of output:
    
    .\align.py | 587
    .\badquotes.txt | 308
    .\boxes.py | 2027
    .\collections.py | 3391
    .\collections_test.txt | 1363
    ...

    TODO: file IO
    
    """
    def __init__(self, directory='.'):
        """Initializes this report using the given directory and stores
           the result in the string field"""
        self.directory = directory
        self.generate()
        self.string = '\n'.join(['{} | {}'.format(x, y) for x,y in self.report])

    def __repr__(self):
        """Prints the string representation of this report"""
        return self.string

    def generate(self):
        """Generates a report in the format (filename, filesize)"""
        report = []
        Walk = _os.walk(self.directory)

        for root, dirs, files in Walk:
            for file in files:
                filename = _os.path.join(root, file)
                report.append((filename, _os.stat(filename).st_size))
        self.report = report

    def parse(self):
        """Parses the string field and returns the original report"""
        splt = [x.split(' | ') for x in self.string.strip().split('\n')]
        lst = [(x, int(y.strip())) for x, y in splt]
        return lst

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

    def sendbin(self, text, charset=UTF_CHAR):
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
        """Prints information about this socket. Called at the beginning
           of a session"""
        print(self.sock, 'started')

    def terminate(self):
        """Closes this session"""
        print('closing {}'.format(self.__class__))
        self.sock.close()
        print('{} closed'.format(self.__class__))

    def writestream(self, filename, buffer=MAX_BUFFER, charset=UTF_CHAR):
        """Write a file stream to the given filename"""
        stream = self.getstream(buffer, file=True)
        with open(filename, 'wb') as fp:
            print('\r' + str(fp.write(stream)), 'bytes')
        time.sleep(0.1)

    def writestreams(self, files, streamlen, buffer=MAX_BUFFER, charset=UTF_CHAR):
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
        self.sendbin(dst.encode(UTF_CHAR))

        d_src = self.loaddiff(src)

        print('d_src =', d_src)

        stream = self.getbin()
        d_dst = eval(stream.decode(UTF_CHAR))
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

        recv = self.getbin().decode(UTF_CHAR)
        d_dst = self.loaddiff(recv)

        print('dd =', d_dst)
        self.sendstream(str(d_dst).encode(UTF_CHAR))
        self.d_dst = d_dst

    def loaddiff(self, Dir):
        """Loads and returns the differces as a dict"""
        Dict = dict()
        for root, dirs, files in _os.walk(Dir):
            for file in files:
                name = _os.path.join(root, file)
                key = name[name.index(_os.path.sep)+1:]
                Dict[key] = _os.stat(name).st_size
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
        port = nextopenport(ip, port)
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##        serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serv.bind((ip, port))
        serv.listen(maxcon)
        print('server listening...')
        sock, addr = serv.accept()
        self.sock = sock
        self.addr = addr

if __name__ == '__main__':
    report = Report(directory='.')
    print(report)
    print(report.parse())

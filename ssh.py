
import socket
import time

DEF_PORT = 1024
MAX_BUFFER = 10000
MAX_CONN = 1

UTF_CHAR = 'utf8'
FILESEP = b'eof' + b'eof'

def nextopenport(ip, port):
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

def generatereport(directory):
    import os

    report = list()
    Walk = os.walk(directory)

    for root, dirs, files in Walk:
        for file in files:
            filename = os.path.join(root, file)
            report.append((filename, os.stat(filename).st_size))
    return report

def reportasstr(report):
    return '\n'.join(['{} | {}'.format(x, y) for x,y in report])

def parsereport(string):
    splt = [x.split(' | ') for x in string.strip().split('\n')]
    lst = [(x, int(y.strip())) for x, y in splt]
    return lst

class SSH:
    """Super-class for Server and Client socket handlers"""

    def getbin(self, buffer=MAX_BUFFER):
        try:
            return self.sock.recv(buffer)
        except:
            return b'quit'
    def getfilestream(self, streamlen, buffer=MAX_BUFFER):
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
        if type(text) == str:
            text = text.encode(charset)
        self.sock.send(text)
    def sendeof(self):
        self.sock.send(FILESEP)
    def sendstream(self, stream, buffer=MAX_BUFFER):
        for i in range(0, len(stream), buffer):
            try:
                self.sendbin(stream[i:i+buffer])
            except:
                self.sendbin(stream[i:])
            finally:
                pass # time.sleep(0.01)
    def test(self):
        print(self.sock, 'started')
    def terminate(self):
        print('closing {}'.format(self.__class__))
        self.sock.close()
        print('{} closed'.format(self.__class__))
    def writestream(self, filename, buffer=MAX_BUFFER, charset=UTF_CHAR):
        stream = self.getstream(buffer, file=True)
        with open(filename, 'wb') as fp:
            print('\r' + str(fp.write(stream)), 'bytes')
        time.sleep(0.1)
    def writestreams(self, files, streamlen, buffer=MAX_BUFFER, charset=UTF_CHAR):
        """Gets file content as one string and parses for each file
        Assumes 'eof' is not contained in the files
        """
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
        changed = list()
        removing = list()
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
        import os
        from subprocess import check_output
        
        recv = self.getbin().decode(UTF_CHAR)
        d_dst = self.loaddiff(recv)

        print('dd =', d_dst)
        self.sendstream(str(d_dst).encode(UTF_CHAR))
        self.d_dst = d_dst

    def loaddiff(self, Dir):
        import os
        Dict = dict()
        for root, dirs, files in os.walk(Dir):
            for file in files:
                name = os.path.join(root, file)
                key = name[name.index('\\')+1:]
                Dict[key] = os.stat(name).st_size
        return Dict.copy()

class ClientSSH(SSH):
    def __init__(self, ip=None, port=DEF_PORT):
        if ip is None:
            ip = input('ip? ')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        print('client connected')
        self.sock = sock

class ServerSSH(SSH):
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
    report = generatereport('.')
    print(report)
    string = reportasstr(report)
    print(parsereport(string))

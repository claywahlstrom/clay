
"""
searchtools. Use regex to search directories for name or contents
"""

# add percentages based on os.listdir in folder.
#     -If name comes up add to counter and output percent to title

from os import walk, sep
from time import time, sleep
from re import findall
from collections import OrderedDict

EXCLUDE = ['.android', '.AndroidStudio1.5', 'eclipse', '.gradle', '.idlerc',
           '.jmc', '.matplotlib', '.oracle_jre_usage', '.pdfsam', '.phet',
           '3D Objects', 'AppData', 'Application Data', 'eclipse', 'Android']

STR_LIM = 70 # path printing termination number

class Search(object):
    def __init__(self, method='name', folder='.', string=str(), ext=False):
        """Search files by method, folder, string, ext"""
        self.method = method
        self.folder = folder
        self.string = string
        self.ext = ext
        self.duration = None
        self.matches = None
        self.results = OrderedDict()
        self.lens = list([0])
        self.do_search()
        self.build_results()
    def build_results(self):
        self.raw_text = '{} seconds\n'.format(self.duration)
        for res in list(self.results.keys()):
            self.raw_text += res+'\n' # parent
            for val in self.results[res]:
                self.raw_text += '\t'+val+'\n' # children
    def display(self):
        if self.results:
            print(self.raw_text)
        else:
            print('No results')
    def do_search(self):
        self.matches = 0
        walker = walk(self.folder) # root dir
        print('Search in progress...')
        print('Searching: ', end='', flush=True)
        try:
            time_start = time() # start timer
            for root, dirs, files in walker:
                if [x for x in EXCLUDE if x in self.string]: # if excluded
                    self.print_path('excluded dir ({})'.format(root[:STR_LIM]))
                else: # not excluded dirs
                    try:
                        self.print_path(root[:STR_LIM]) # format bad titles
                    except:
                        self.print_path('dir unavailable')
                    for f in files: # search file content
                        flag = False
                        if self.method.startswith('cont'):
                            try:
                                with open(root+sep+f, encoding='latin-1') as fp:
                                    text = fp.read()
                                if findall(self.string, text):
                                    flag = True
                            except Exception as e:
                                print(e)
                        elif self.method.startswith('name') and findall(self.string, f):
                            flag = True
                        if flag:
                            self.matches += 1
                            if self.ext and f.endswith(self.ext) or not self.ext:
                                if root in list(self.results.keys()): # if same dir
                                    self.results[root] += [f]
                                else: # add if not
                                    self.results[root] = [f]

            self.duration = time() - time_start
            ## optional sort if walk doesn't succeed in sorting
##            for key in self.results:
##                self.results[key] = sorted(self.results[key])
        except KeyboardInterrupt:
            print('KeyboardInterrupt')
            if not(fp.closed):
                fp.close()
        print('\nSearch complete')
        print('Results built')
    def get_results(self):
        return self.results
    def print_path(self, arg):
        print('\x08'*self.lens[-1] + ' '*self.lens[-1] + '\x08'*self.lens[-1] + arg, end='', flush=True)
        self.lens.append(len(arg))

def write_output(obj, filename):
    f = open(filename,'w')
    f.write('Search results for "{}" in "{}" with ext "{}"\n{}'.format(obj.string, obj.folder, obj.ext, obj.raw_text))
    f.close()

def executable_search(string, ext='exe'):
    """Returns tuple of program files results"""
    s = Search('name', folder=r'C:\Program Files', string=string, ext=ext)
    t = Search('name', folder=r'C:\Program Files (x86)', string=string, ext=ext)
    return dict({s.folder: s.get_results(), t.folder: t.get_results()})

if __name__ == '__main__':
    s = Search('cont', r'E:\Docs\Clay\General notes', 'the')
    print(executable_search('chrome'))

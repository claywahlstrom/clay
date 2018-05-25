
"""
Search tools can be used to search the file system using regular expressions

"""

# add percentages based on os.listdir in folder.
#     -If name comes up add to counter and output percent to title

from collections import OrderedDict as _OrderedDict
import os as _os
from re import findall
import sys as _sys
import time as _time

from clay.shell import getDocsFolder as _getDocsFolder, isIdle as _isIdle


EXCLUDED = ['.android', '.AndroidStudio1.5', 'eclipse', '.gradle', '.idlerc',
           '.jmc', '.matplotlib', '.oracle_jre_usage', '.pdfsam', '.phet',
           '3D Objects', 'AppData', 'Application Data', 'eclipse', 'Android']

STR_LIM = 75 # path printing termination number

class Search(object):
    """A class for searching a file system"""
    def __init__(self, method='name', folder='.', string=str(), ext=False):
        """Searches files by method, folder, string, ext"""
        # variable initializing
        self.method = method
        self.folder = folder
        self.string = string
        self.ext    = ext

        # actual work
        self.do_search()
        self.build_results()

    def __repr__(self):
        if len(self.results) > 0:
            return self.raw_text
        else:
            return 'No results'

    def build_results(self):
        self.raw_text = '{} seconds\n'.format(self.duration)
        self.raw_text += '\n'.join([res + '\n\t' + \
                                    '\n\t'.join([val for val in self.results[res]]) \
                                    for res in list(self.results.keys())])

    def do_search(self):
        self.results = _OrderedDict()
        self.matches = 0
        self.last_len = 0
        walker = _os.walk(self.folder) # root dir
        print('Search in progress...')
        print('Searching: ', end='', flush=True)
        try:
            time_start = _time.time() # start timer
            for root, dirs, files in walker:
                if any(excl in self.string for excl in EXCLUDED): # if excluded
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
                                with open(_os.path.join(root, f), encoding='latin-1') as fp:
                                    text = fp.read()
                                flag = len(findall(self.string, text)) > 0
                            except Exception as e:
                                print(e)
                        flag = not(flag) and self.method.startswith('name') and findall(self.string, f)
                        if flag:
                            self.matches += 1
                            if self.ext and f.endswith(self.ext) or not self.ext:
                                if root not in list(self.results.keys()): # if same dir, add a file
                                    self.results[root] = list([f])
                                self.results[root].append(f)

            self.duration = _time.time() - time_start
        except KeyboardInterrupt:
            print('KeyboardInterrupt')
            if not(fp.closed):
                fp.close()
        print('\nSearch complete')
        print('Results built')

    def get_results(self):
        """Returns this search results"""
        return self.results

    def print_path(self, arg):
        """Prints the path, helper to the search method"""
        # overwrite the line to clear its contents
        if _isIdle():
            print(arg)
        else:
            print('\x08' * self.last_len + ' ' * self.last_len + \
                  '\x08' * self.last_len + arg, end='', flush=True)
            self.last_len = len(arg)

    def write_output(self, filename):
        """Writes the search query to the given output file"""
        with open(filename, 'w') as fp:
            fp.write('Search results for "{}" in "{}" with ext "{}"\n{}'.format(self.string,
                                                                                self.folder,
                                                                                self.ext))
            fp.write(self.raw_text)

def executable_search(string, ext='exe'):
    """Returns the tuple of results of from searching
       program files directories with the given string"""
    s = Search('name', folder=r'C:\Program Files', string=string, ext=ext)
    t = Search('name', folder=r'C:\Program Files (x86)', string=string, ext=ext)
    return dict({s.folder: s.get_results(), t.folder: t.get_results()})

if __name__ == '__main__':
    s = Search('cont', _os.path.join(_getDocsFolder(), r'Clay\Notes'), 'the')
    print(executable_search('chrome'))


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
            '3D Objects', 'AppData', 'Application Data', 'eclipse', 'Android',
            'NuGet']

STR_LIM = 75 # path printing termination number

class Search(object):
    """A class for searching a file system"""
    def __init__(self, method='name', folder='.', string=str(), ext=None):
        """Searches files by method, folder, regex string, ext"""
        if ext is not None and type(ext) != str:
            raise ValueError('extension must be a string')
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
        self.raw_text = f'Search for "{self.string}" in "{self.folder}" took {round(self.duration, 5)} seconds\n'
        self.raw_text += '\n'.join([res + '\n\t' + \
                                    '\n\t'.join([val for val in self.results[res]]) \
                                    for res in list(self.results.keys())])

    def do_search(self):
        self.results = _OrderedDict()
        self.matches = 0
        self.last_len = 0
        self.duration = 0
        walker = _os.walk(self.folder) # root dir
        print('Search in progress...')
        print('Searching: ', end='', flush=True)
        try:
            time_start = _time.time() # start timer
            for root, dirs, files in walker:
                if any(excl in root for excl in EXCLUDED): # if excluded
                    self.print_path('excluded dir ({})'.format(root[:STR_LIM]))
                else: # not excluded dirs
                    try:
                        self.print_path(root[:STR_LIM]) # format bad titles
                    except:
                        self.print_path('dir unavailable')
                    for f in files: # search file content
                        flag = False
                        try:
                            if self.method.startswith('cont'):

                                with open(_os.path.join(root, f), encoding='latin-1') as fp:
                                    text = fp.read()
                                flag = len(findall(self.string, text)) > 0

                            elif self.method.startswith('name'):
                                flag = findall(self.string, f)
                        except Exception as e:
                            print() # flush stdout
                            input(e)
                            print('Aborting search...')
                            raise KeyboardInterrupt
                        if flag:
                            self.matches += 1
                            if self.ext is None or len(self.ext) > 0 and f.endswith(self.ext):
                                if root not in list(self.results.keys()): # create new entry if dir not entered
                                    self.results[root] = []
                                self.results[root].append(f)

            self.duration = _time.time() - time_start
        except KeyboardInterrupt:
            print('KeyboardInterrupt was raised')
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

def print_containing_files(string, directory, ext=None):
    """Given a string, directory(ies), and optional extension,
       prints the search results for the files containing the
       string"""
    if type(directory) == str:
        directories = [directory]
    else:
        directories = directory
    for d in directories:
        s = Search('cont', folder=d, string=string, ext=ext)
        print()
        print(s)
        print()

if __name__ == '__main__':
    import pprint
    s = Search('cont', _os.path.join(_getDocsFolder(), r'Clay\Notes'), 'the')
    pprint.pprint(executable_search('chrome'))

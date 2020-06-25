
"""
Search tools can be used to search the file system using regular expressions

"""

# add percentages based on os.listdir in folder.
#     -If name comes up add to counter and output percent to title

from collections import OrderedDict as _OrderedDict
import os as _os
from re import findall
import time as _time

from clay.env import is_idle as _is_idle
from clay.settings import CONSOLE_WIDTH, SEARCH_EXCLUSIONS

STR_LIM = CONSOLE_WIDTH - 5 # path printing termination number

class Search(object):
    """Used to search a file system"""
    def __init__(self, method='name', folder='.', string='', ext=None):
        """Searches files by method, folder, regex string, ext"""
        if ext is not None and not isinstance(ext, str):
            raise TypeError('extension must be of type string')
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
        self.raw_text = 'Search results for "{}" with extension "{}" in "{}" took {} seconds\n' \
            .format(self.string, self.ext, self.folder, round(self.duration, 5))
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
                if any(excl in root for excl in SEARCH_EXCLUSIONS): # if excluded
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
                        except PermissionError as e:
                            print() # flush stdout
                            print(e)
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
        # overwrites the line to clear its contents
        if _is_idle():
            print(arg)
        else:
            print('\x08' * self.last_len + ' ' * self.last_len + \
                  '\x08' * self.last_len + arg, end='', flush=True)
            self.last_len = len(arg)

    def results_to_list(self):
        """Returns a list of full path names found in this search"""
        files = []
        for result in self.results:
            for file in self.results[result]:
                files.append(_os.path.join(result, file))
        return files

    def write_output(self, filename):
        """Writes the search query to the given output file"""
        with open(filename, 'w') as fp:
            fp.write(self.raw_text)

def print_files_containing(string, directories, ext=None):
    """Given a string, directory(ies), and optional extension,
       prints the search results for the files containing the
       string"""
    if isinstance(directories, str):
        directories = [directories]

    for d in directories:
        s = Search('cont', folder=d, string=string, ext=ext)
        print()
        print(s) # print results
        print()

def search_executables(string, ext='exe'):
    """Returns the tuple of results of from searching
       program files directories with the given string"""
    s = Search('name', folder=r'C:\Program Files', string=string, ext=ext)
    t = Search('name', folder=r'C:\Program Files (x86)', string=string, ext=ext)
    return dict({s.folder: s.get_results(), t.folder: t.get_results()})

if __name__ == '__main__':
    import pprint
    from clay.settings import DOCS_DIR

    s = Search('cont', _os.path.join(DOCS_DIR, r'Clay\Notes'), 'the')
    pprint.pprint(search_executables('chrome'))

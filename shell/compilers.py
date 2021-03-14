
"""
Compilers

Used to compile source files into binaries and bytecode.

"""

import os as _os

from clay import settings

class Compiler(object):

    """Used to compile source files into bytecode or executable format"""

    def __init__(self, compiler_name, src_ext, dst_ext, sources=None, directory=_os.curdir):
        """
        Initializes this compiler. Default for classes is all in the given
        directory or expects a list or tuple, otherwise and ValueError is thrown

        """
        if sources is not None and not isinstance(sources, (list, set, tuple)):
            raise TypeError('sources must be an iterable')
        self.compiler_name = compiler_name
        self.src_ext = src_ext
        self.dst_ext = dst_ext
        self.sources = sources
        self.directory = directory
        self.flags = []

    def set_path(self, directory):
        """Sets the path of this compiler to the given directory"""
        self.directory = directory

    def add_flag(self, flag):
        """Adds the given flag to the list of flags"""
        self.flags.append(flag)

    def clear_flags(self):
        """Clears the list of flags"""
        self.flags.clear()

    def compile(self, exclude=None, recurse=True, references=None, verbose=False):
        """
        Compiles the source files in this directory with this compiler's
        flags. Keyword parameters are as follows:
            exclude = None or list of strings to exclude
            recurse = boolean to indicate whether all files in this
                compiler's path should be compiled
            references = None or list of refernces for C# sources
            verbose = boolean to indicate whether the system command
                should be printed for each file

        """
        from clay.shell.core import lsgrep

        _os.chdir(self.directory)
        sources = self.sources

        if sources is None:
            sources = [_os.path.splitext(x)[0] for x in lsgrep(self.src_ext, self.directory, recurse=recurse)]
        if exclude is not None and len(exclude) > 0:
            sources = list(filter(lambda x: all(not(y in x) for y in exclude), sources))
        # if any flags, include them
        if len(self.flags) > 0:
            opt_str = '-' + ' -'.join(self.flags)
        else:
            opt_str = ''

        statechanged = False
        for src in sources:
            src_name = src + self.src_ext
            dst_name = src + self.dst_ext

            if not _os.path.exists(src_name):
                print(src, 'doesn\'t exist, skipping...')
                continue

            src_mtime = _os.stat(src_name).st_mtime
            if _os.path.exists(dst_name):
                dst_mtime = _os.stat(dst_name).st_mtime
            else:
                dst_mtime = 0 # file doesn't exist

            # if edited more than five seconds ago, compile it
            if src_mtime - dst_mtime >= 5:
                print('Compiling ({}):'.format(self.compiler_name), src)
                cmd = self.compiler_name
                if self.compiler_name == 'csc': # C Sharp specific handling
                    if references is not None:
                        cmd += ' /r:' + ','.join(references)
                    cmd += ' /out:{} '.format(dst_name)
                cmd += '{} "{}"'.format(opt_str, src_name)
                if verbose:
                    print('cmd:', cmd)
                _os.system(cmd)
                statechanged = True

        if not statechanged:
            print('Nothing new to compile in "{}" when recurse={}'.format(self.directory, recurse))

class CSharpCompiler(Compiler):

    """Used to compile C# source code"""

    def __init__(self, sources=None, directory=_os.curdir):
        """Initializes this compiler"""
        super().__init__('csc', '.cs', '.exe', sources, directory)
        self.add_flag('nologo')

class JavaCompiler(Compiler):

    """Used to compile Java(tm) source files to bytecode"""

    def __init__(self, sources=None, directory=_os.curdir):
        """Initializes this compiler"""
        super().__init__('javac', '.java', '.class', sources, directory)
        self.add_flag('g')
        self.add_flag('Xlint:unchecked')

if __name__ == '__main__':

    if settings.IS_DEVELOPER:
        # only test on developer's machine due to paths constraint
        jc = JavaCompiler(directory=r'E:\Docs\Clay\Tech\Software\java\gravity')
        jc.compile(exclude=['-', 'unused'])

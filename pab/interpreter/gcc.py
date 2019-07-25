# coding: utf-8


class GCC:
    def __init__(self, **kwargs):
        self.name = 'GCC'
        self.tags = ('gcc', 'gnuc', 'g++')
        self.kwargs = kwargs
        self.prefix = kwargs.get('prefix', '')
        self.suffix = kwargs.get('suffix', '')

        self._cmds = {
                'cc':   (self.prefix + 'gcc' + self.suffix, '-c'),
                'cxx':  (self.prefix + 'g++' + self.suffix, '-c'),
                'ar':   (self.prefix + 'ar'  + self.suffix, '-rcs'),
                'ld':   (self.prefix + 'gcc' + self.suffix, ),
                'ldd':  (self.prefix + 'ld.bfd' + self.suffix, ),
                }
        self._compositors = {
                'sysroots':      lambda path, args: f'--sysroot={path}',
                'include_dirs':  lambda path, args: ['-I', path],
                'lib_dirs':      lambda path, args: ['-L', path],
                'libs':          lambda path, args: f'-l{path}',
                'defines':       lambda macro, args: f'-D{macro}',
                }

    def asCmdProvider(self, kwargs):
        return self._cmds

    def asCmdInterpreter(self):
        return self._compositors

    '''
    Interpreter.filterCmd must called at end of Config chain, translate all
    Command properties which like sources, libs, lib_dirs, include_dirs etc.
    rule:
        sources - translate by Command._mergeSources
        dst - translate by interpreter.asCmdFilter
    '''
    def asCmdFilter(self, cmd, kwargs):
        if cmd.name not in ('ar', 'cc', 'cxx', 'ld'):
            return

        '''
        # compile
        gcc -c hello.c
        # link to static lib
        ar -rcs libhello.a hello.o
        gcc -o hello_static main.c -L. -lhello  # or next line:
        gcc -o hello_static main.c libhello.a
        # link to dynamic lib
        gcc -shared -fpic -o libhello.so hello.o
        gcc -o hello main.c libhello.so
        '''
        if cmd.name == 'cc':
            cmd.ccflags += '-Wall'
        elif cmd.name == 'cxx':
            cmd.cxxflags += '-Wall'
        elif cmd.name == 'ld':
            if kwargs['target'].isSharedLib():
                cmd.ldflags += ['-shared', '-fpic']

        if cmd.name == 'ar':
            cmd += cmd.dst
        else:
            cmd += ['-o', cmd.dst]

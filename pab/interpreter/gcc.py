# coding: utf-8

import os


class GCC:
    def __init__(self, **kwargs):
        self.name = 'GCC'
        self.kwargs = kwargs
        self.prefix = kwargs.get('prefix', '')
        self.suffix = kwargs.get('suffix', '')

        self.cmds = {
                'cc':   (self.prefix + 'gcc' + self.suffix, '-c'),
                'cxx':  (self.prefix + 'g++' + self.suffix, '-c'),
                'ar':   (self.prefix + 'ar'  + self.suffix, '-rcs'),
                'ld': (self.prefix + 'gcc' + self.suffix, ),
                'ldd':  (self.prefix + 'ld.bfd' + self.suffix, ),
                }
        self.compositors = {
                'sysroots':      lambda path, args: f'--sysroot={path}',
                'include_dirs':  lambda path, args: ['-I', path],
                'lib_dirs':      lambda path, args: ['-L', path],
                'libs':          lambda path, args: f'-l{path}',
                'defines':       lambda macro, args: f'-D{macro}',
                }

    def matchRequest(self, request):
        return True

    # Interpreter.filterCmd must called at end of Config chain, translate all
    # Command properties which like sources, libs, lib_dirs, include_dirs etc.
    def filterCmd(self, cmd, kwargs):
        if cmd.name not in ('ar', 'cc', 'cxx', 'ld'):
            return

        '''
        # compile
        gcc -c hello.c
        # link to static lib
        ar -rcs libhello.a hello.o
        gcc -o hello_static main.c -L. -lhello
        # link to dynamic lib
        gcc -shared -fpic -o libhello.so hello.o
        gcc -o hello main.c libhello.so
        '''
        if cmd.name == 'ar':
            cmd.sources += cmd.dst
        else:
            cmd.parts += ['-o', cmd.dst]

        if cmd.name == 'cc':
            cmd.ccflags += '-Wall'
            cmd.parts += cmd.sources
        elif cmd.name == 'cxx':
            cmd.cxxflags += '-Wall'
            cmd.parts += cmd.sources
        elif cmd.name == 'ld':
            cmd.composeSources(
                    cmd.sources,
                    os.path.join(kwargs['request'].rootBuild, 'src_list.txt'))
            if kwargs['target'].isSharedLib():
                cmd.ldflags += ['-shared', '-fpic']

        cmd.translate(self.compositors, kwargs)

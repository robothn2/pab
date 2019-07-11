# coding: utf-8

import os


class GCC:
    def __init__(self, **kwargs):
        self.name = 'GCC'
        self.kwargs = kwargs
        self.prefix = kwargs.get('prefix', '')
        self.suffix = kwargs.get('suffix', '')

        self.cmds = {
                'cc': (self.prefix + 'gcc' + self.suffix, 'src', '-c', ),
                'cxx': (self.prefix + 'g++' + self.suffix, 'src', '-c', ),
                'ar': (self.prefix + 'ar' + self.suffix, 'dst', '-rcs'),
                'link': (self.prefix + 'gcc' + self.suffix, 'dst'),
                'ldd': (self.prefix + 'ld.bfd' + self.suffix, ),
                }
        self.cmdFilters = {
                'cc': [
                    ['-Wall'],
                    self._filterSrcListAndDst,
                ],
                'cxx': [
                    ['-Wall'],
                    self._filterSrcListAndDst,
                ],
                'ar': [
                    self._filterSrcListAndDst,
                ],
                'link': [
                    self._filterSrcListAndDst,
                ],
                }
        self.compositors = {
                'sysroot':      lambda path, args: f'--sysroot={path}',
                'includePath':  lambda path, args: ['-I', path],
                'libPath':      lambda path, args: ['-L', path],
                'lib':          lambda path, args: f'-l{path}',
                'define':       lambda macro, args: f'-D{macro}',
                }

    def matchRequest(self, request):
        return True

    def queryCmd(self, cmd_name):
        return self.cmds.get(cmd_name)

    def filterCmd(self, cmd_name, kwargs):
        return self.cmdFilters.get(cmd_name, [])

    def _filterSrcListAndDst(self, args):
        ret = []
        request = args['request']
        cmd = args['cmd']

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
        if 'dst' in args:
            dst = args['dst']
            dst = args['dst']
            if cmd == 'ar':
                ret.append(dst)
            else:
                ret += ['-o', dst]
                if cmd == 'link' and args['target'].isSharedLib():
                    ret += ['-shared', '-fpic']
            args['dst'] = dst

        if 'src' in args:
            src = args['src']
            if isinstance(src, str):
                ret.append(src)
            elif isinstance(src, list):
                # write all source file path into file, and use @file
                tmp_file = os.path.join(request.rootBuild, 'src_list.txt')
                with open(tmp_file, 'w', encoding='utf-8') as f:
                    for o in src:
                        o = os.path.realpath(o)
                        o = o.replace('\\', '/')
                        f.write(o)
                        f.write(' ')
                    f.close()
                ret.append('@' + tmp_file)
        return ret

#coding: utf-8

import os

class GCC:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.prefix = kwargs.get('prefix', '')
        self.postfix = kwargs.get('postfix', '')
        self.root = os.path.dirname(self.prefix)
        if not os.path.exists(self.root):
            raise Exception(r'gcc dir not exist')
        
    def registerAll(self, toolchain):
        toolchain.registerCommand(self, 'cc', self.prefix + 'gcc' + self.postfix)
        toolchain.registerCommand(self, 'cxx', self.prefix + 'g++' + self.postfix)
        toolchain.registerCommand(self, 'as', self.prefix + 'as' + self.postfix)
        toolchain.registerCommand(self, 'link', self.prefix + 'ld' + self.postfix)

        toolchain.registerCommandFilter(self, ['cc', 'cxx'], [
                    ('args', '-c', '-Wall'),
                    self._filterMakeSrcDst,
                ])
        toolchain.registerCommandFilter(self, 'link', [
                    ('compositor', 'lib', 'c'),     # link with libc.a
                    #('compositor', 'lib', 'stdc++'), # link with libstdc++.a
                    self._filterMakeSrcDst,
                ])

        toolchain.registerArgCompositor(self, 'sysroot', lambda path, args: f'--sysroot={path}')
        toolchain.registerArgCompositor(self, 'includePath', lambda path, args: ['-I', path])
        toolchain.registerArgCompositor(self, 'libPath', lambda path, args: ['-L', path])
        toolchain.registerArgCompositor(self, 'lib', lambda path, args: f'-l{path}')

    def _filterMakeSrcDst(self, args):
        ret = []
        #config = args['config']
        cmd = args['cmd']

        if 'dst' in args:
            if cmd == 'link':
                part = args['dst']
                t = args.get('targetType', 'executable')
                if t == 'sharedLib':
                    part += '.so'
                elif t == 'staticLib':
                    part += '.a'
                elif t == 'executable':
                    pass

                ret += ['-o', part]
            else:
                ret += ['-o', args['dst']]
                
        if 'src' in args:
            src = args['src']
            if isinstance(src, str):
                ret.append(src)
            elif isinstance(src, list):
                ret.extend(src)
        return ret

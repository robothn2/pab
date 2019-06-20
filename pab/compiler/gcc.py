#coding: utf-8

import os

class GCC:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.root = kwargs.get('path', '')
        if not os.path.exists(self.root):
            raise Exception(r'gcc dir not exist')
        
    def registerAll(self, toolchain):
        toolchain.registerCommand(self, 'cc', os.path.join(self.root, r'arm-linux-androideabi-gcc.exe'))
        toolchain.registerCommandFilter(self, ['cc', 'cxx'], ('args', '-c', '-Wall'))
        toolchain.registerCommandFilter(self, ['cc', 'cxx'], self._filterMakeSrcDst)

        toolchain.registerCommand(self, 'cxx', os.path.join(self.root, r'arm-linux-androideabi-g++.exe'))        

        toolchain.registerArgCompositor(self, 'sysroot', lambda path, args: f'--sysroot={path}')
        toolchain.registerArgCompositor(self, 'includePath', lambda path, args: ['-I', path])
        toolchain.registerArgCompositor(self, 'libPath', lambda path, args: ['-L', path])
        toolchain.registerArgCompositor(self, 'lib', lambda path, args: f'-l{path}')
        toolchain.registerArgCompositor(self, ['linkOutput', 'compileOutput'], lambda path, args: ['-o', path])

    @staticmethod
    def _filterMakeSrcDst(args):
        ret = []
        if 'dst' in args:
            ret += ['-o', args['dst']]
        src = args.get('src', None)
        if isinstance(src, str):
            ret.append(src)
        elif isinstance(src, list):
            ret.extend(src)
        return ret
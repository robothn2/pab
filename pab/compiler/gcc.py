#coding: utf-8

import os
import re

class GCC:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.root = kwargs.get('path', '')
        if not os.path.exists(self.root):
            raise Exception(r'gcc dir not exist')
        
    def registerAll(self, toolchain):
        toolchain.registerArgCompositor('includePath', lambda path: ['-I', path])
        toolchain.registerArgCompositor('sysroot', lambda path: f'--sysroot={path}')
        toolchain.registerArgCompositor('libPath', lambda path: ['-L', path])
        toolchain.registerArgCompositor('lib', lambda path: f'-l{path}')
        toolchain.registerArgCompositor('linkOutput', lambda path: ['-o', path])

        toolchain.registerCommand('cc', os.path.join(self.rootBin, r'arm-linux-androideabi-gcc'))
        toolchain.registerCommand('cxx', os.path.join(self.rootBin, r'arm-linux-androideabi-g++'))        

    def handleFile(self, config, cat, src, **kwargs):
        return [('args', '-c', '-Wall', '-o', dst, src)]

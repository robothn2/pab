#coding: utf-8

import os
import re

class GCC:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.root = kwargs.get('path', '')
        if not self.root or not os.path.exists(self.root):
            for path in os.environ['path']:
                if not re.match(r'android-ndk-r\d{1,3}\w', os.path.basename(path)):
                    continue
                if not os.path.exists(os.path.join(path, 'toolchains')):
                    continue
                self.root = path
                break
        if not self.root:
            raise(r'Need ndk dir passed as `path` parameter, or ndk dir in `PATH` environment')
        
        toolchain_name = kwargs.get('name', '') # arm-linux-androideabi-4.9
        prebuilt = os.path.join(self.root, f'toolchains/{toolchain_name}/prebuilt')
        if not os.path.exists(prebuilt):
            raise('Ndk toolchain name not exist: %s' % prebuilt)

        self.rootBin = os.path.join(prebuilt, os.listdir(prebuilt)[0], 'bin') # linux-x86_64/bin or windows-x86_64/bin
        
    def registerAll(self, toolchain):
        toolchain.registerArgCompositor('includePath', lambda path: ['-I', path])
        toolchain.registerArgCompositor('sysroot', lambda path: f'--sysroot={path}')
        toolchain.registerArgCompositor('libPath', lambda path: ['-L', path])
        toolchain.registerArgCompositor('lib', lambda path: f'-l{path}')

        toolchain.registerCommand('cc', os.path.join(self.rootBin, r'arm-linux-androideabi-gcc'))
        toolchain.registerCommand('cxx', os.path.join(self.rootBin, r'arm-linux-androideabi-g++'))        

    def handleCompileFile(self, config, src, dst):
        return [('args', '-c', '-Wall', '-o', dst, src)]

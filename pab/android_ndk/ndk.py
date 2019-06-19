#coding: utf-8

import os
import re

class NDK:
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
        
        toolchain_name = kwargs.get('toolchain', '') # arm-linux-androideabi-4.9
        prebuilt = os.path.join(self.root, f'toolchains/{toolchain_name}/prebuilt')
        if not os.path.exists(prebuilt):
            raise('Ndk toolchain name not exist: %s' % prebuilt)

        self.rootBin = os.path.join(prebuilt, os.listdir(prebuilt)[0], 'bin') # linux-x86_64/bin or windows-x86_64/bin
        self.sysroot = os.path.join(self.root, 'platforms',
                                    'android-{}'.format(kwargs.get('platform', 9)),
                                    'arch-{}'.format(kwargs.get('arch', 'arm'))) # android-ndk-r14b/platforms/android-9/arch-arm
        # todo: abi='arm64-v8a', compiler='gcc'
        
    def _register_all(self, toolchain):
        toolchain.registerCommand('link', lambda path: ['-I', path])
        self.cmds['cc'] = os.path.join(self.rootBin, r'arm-linux-androideabi-gcc')
        self.cmds['cxx'] = os.path.join(self.rootBin, r'arm-linux-androideabi-g++')
        self.cmds['link'] = os.path.join(self.rootBin, r'arm-linux-androideabi-ld')

    def handleCompileFile(self, config, src, dst):
        return [('compositor', 'sysroot', self.sysroot)]
    
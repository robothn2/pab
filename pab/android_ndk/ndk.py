#coding: utf-8

import os
import re
from pab.compiler.gcc import GCC

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
            raise Exception(r'Need ndk dir passed as `path` parameter, or ndk dir in `PATH` environment')
        
        self.executablePrefix = ''
        self.toolchains = []
        rootToolchain = os.path.join(self.root, 'toolchains')
        for name in os.listdir(rootToolchain):
            toolchain_path = os.path.join(rootToolchain, name)
            if os.path.isdir(toolchain_path):
                self.toolchains.append(os.path.realpath(toolchain_path))
        
    def applyConfig(self, config):
        arch = config.getArch()
        cpu = config.getCpu()
        platform_level = self.kwargs.get('platform', 21) # android-21+ support 64bit arch
        self.executablePrefix = f'{arch}-linux-android-'
        if arch == 'arm64':
            toolchain_name = 'aarch64-linux-android-4.9'
        elif arch == 'arm':
            toolchain_name = 'arm-linux-androideabi-4.9'
            self.executablePrefix = 'arm-linux-androideabi-'
        elif arch == 'x86_64':
            toolchain_name = 'x86_64-4.9'
        elif arch == 'x86':
            toolchain_name = 'x86-4.9'
        else:
            toolchain_name = 'llvm'
        prebuilt = os.path.join(self.root, f'toolchains/{toolchain_name}/prebuilt')
        if not os.path.exists(prebuilt):
            raise Exception('Ndk toolchain name not exist: %s' % prebuilt)
        
        self.rootBin = os.path.join(prebuilt, os.listdir(prebuilt)[0], 'bin') # linux-x86_64/bin or windows-x86_64/bin
        
        rootPlatform = os.path.join(self.root, f'platforms/android-{platform_level}')
        if not os.path.exists(rootPlatform):
            raise Exception('Ndk platform not exist: %s' % rootPlatform)
        
        self.sysroot = os.path.join(rootPlatform, f'arch-{arch}') # android-ndk-r14b/platforms/android-9/arch-arm
        if not os.path.exists(self.sysroot):
            raise Exception('Ndk sysroot not exist: %s' % self.sysroot)
        # todo: abi='arm64-v8a', compiler='gcc'
    
    def registerAll(self, toolchain):
        toolchain.registerCommandFilter(self, ['cc', 'cxx', 'link'], ('compositor', 'sysroot', self.sysroot))
        # for # include_next <stdint.h> & #include <errno.h>
        toolchain.registerCommandFilter(self, ['cc', 'cxx'], [
                ('compositor', 'sysroot', os.path.join(self.root, 'sysroot')),
                ('compositor', 'includePath', os.path.join(self.root, 'sysroot/usr/include/i686-linux-android')),
                ])
        toolchain.registerCommandFilter(self, 'link', [
                    #('args', '-static'), # Android use static library
                ])
    
        if self.kwargs.get('compiler', 'llvm') == 'gcc':
            toolchain.registerPlugin(GCC(prefix=os.path.join(self.rootBin, self.executablePrefix), postfix='.exe'))
        else:
            pass # todo: llvm

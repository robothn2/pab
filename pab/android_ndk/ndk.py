# coding: utf-8

import os
import re
from pab.compiler.gcc import GCC


class NDK:
    def __init__(self, **kwargs):
        self.name = 'NDK'
        self.kwargs = kwargs
        self.root = kwargs.get('path', '')
        if not self.root or not os.path.exists(self.root):
            for path in os.environ['path']:
                if not re.match(r'android-ndk-r\d{1,3}\w?',
                                os.path.basename(path)):
                    continue
                if not os.path.exists(os.path.join(path, 'toolchains')):
                    continue
                self.root = path
                break
        if not self.root:
            raise Exception(r'Need ndk dir passed as `path` parameter,'
                            'or ndk dir in `PATH` environment')

        self.executablePrefix = ''
        self.toolchains = []
        rootToolchain = os.path.join(self.root, 'toolchains')
        for name in os.listdir(rootToolchain):
            toolchain_path = os.path.join(rootToolchain, name)
            if os.path.isdir(toolchain_path):
                self.toolchains.append(os.path.realpath(toolchain_path))

    def applyConfig(self, config):
        self.executablePrefix, toolchain_name = self.getToolchainName(config)
        self.executableSuffix = config.hostOS.getExecutableSuffix()
        # android-21+ support 64bit arch
        platform_level = self.kwargs.get('platform', 21)
        prebuilt = os.path.join(self.root,
                                f'toolchains/{toolchain_name}/prebuilt')
        if not os.path.exists(prebuilt):
            raise Exception('Ndk toolchain name not exist: %s' % prebuilt)

        # linux-x86_64/bin or windows-x86_64/bin
        self.rootBin = os.path.join(prebuilt, os.listdir(prebuilt)[0], 'bin')

        rootPlatform = os.path.join(self.root,
                                    f'platforms/android-{platform_level}')
        if not os.path.exists(rootPlatform):
            raise Exception('Ndk platform not exist: %s' % rootPlatform)

        # android-ndk-r14b/platforms/android-9/arch-arm
        self.sysroot = os.path.join(rootPlatform,
                                    self.getAndroidPlatformSubfolder(config))
        if not os.path.exists(self.sysroot):
            raise Exception('Ndk sysroot not exist: %s' % self.sysroot)

    def registerAll(self, toolchain):
        toolchain.registerCommandFilter(self, ['cc', 'cxx', 'link'],
                                        ('sysroot', self.sysroot))
        # for #include_next <stdint.h> & #include <errno.h>
        toolchain.registerCommandFilter(self, ['cc', 'cxx'], [
                ('sysroot', os.path.join(self.root, 'sysroot')),
                ('includePath', lambda kwargs: os.path.join(
                        self.root,
                        'sysroot/usr/include',
                        self.getSysrootIncludeSubfolder(kwargs['config']))),
                ])
        toolchain.registerCommandFilter(self, 'cxx', [
                ('includePath', os.path.join(
                        self.root,
                        'sources/cxx-stl/gnu-libstdc++/4.9/include')),
                ('includePath', lambda kwargs: os.path.join(
                        self.root,
                        'sources/cxx-stl/gnu-libstdc++/4.9/libs',
                        self.getCppLibSubfolder(kwargs['config']),
                        'include')),
                ])

        if self.kwargs.get('compiler', 'llvm') == 'gcc':
            gcc = GCC(prefix=os.path.join(self.rootBin, self.executablePrefix),
                      postfix='.exe')
            toolchain.registerPlugin(gcc)
        else:
            pass  # todo: llvm

    def getToolchainName(self, config):
        arch = config.getArch()
        executablePrefix = f'{arch}-linux-android-'
        if arch == 'arm':
            toolchain_name = 'arm-linux-androideabi-4.9'
            executablePrefix = 'arm-linux-androideabi-'
        elif arch == 'arm64':
            toolchain_name = 'aarch64-linux-android-4.9'
            executablePrefix = 'aarch64-linux-android-'
        elif arch == 'x86_64':
            toolchain_name = 'x86_64-4.9'
        elif arch == 'x86':
            toolchain_name = 'x86-4.9'
            executablePrefix = 'i686-linux-android-'
        else:
            toolchain_name = 'llvm'
        return executablePrefix, toolchain_name

    # for $NDK/sysroot/usr/include/
    def getAndroidPlatformSubfolder(self, config):
        arch = config.getArch()
        if arch == 'arm':
            return 'arch-arm'
        elif arch == 'arm64':
            return 'arch-arm64'
        return 'arch-' + arch

    # for $NDK/sysroot/usr/include/
    def getSysrootIncludeSubfolder(self, config):
        arch = config.getArch()
        if arch == 'arm64':
            return 'aarch64-linux-android'
        if arch == 'arm':
            return 'arm-linux-androideabi'
        if arch == 'x86':
            return 'i686-linux-android'
        return arch + '-linux-android'

    # for $NDK/sources/cxx-stl/gnu-libstdc++/4.9/libs/
    def getCppLibSubfolder(self, config):
        arch = config.getArch()
        cpu = config.getCpu()
        if arch == 'arm':
            if cpu == 'v7a':
                return 'armeabi-v7a'
            return 'armeabi'
        if arch == 'arm64':
            if cpu == 'v8a':
                return 'arm64-v8a'
            return 'aarch64'
        return arch

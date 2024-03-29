# coding: utf-8

import os
import re
from pab.interpreter.gcc import GCC
from pab.interpreter.clang import Clang


class NDKStl:
    def __init__(self, root, **kwargs):
        self.include_dirs = []
        self.lib_dirs = []
        self.static_libs = []
        self.shared_libs = []

        stl = os.path.basename(root)
        if stl == 'llvm-libc++':
            self.include_dirs.append(os.path.join(root, 'include'))
            self.include_dirs.append(os.path.join(root, 'include/ext'))
            libpath = os.path.join(root, 'libs', kwargs['arch'])
            self.lib_dirs.append(libpath)
            self.static_libs.append('c++_static')
            self.shared_libs.append(os.path.join(libpath, 'libc++_shared.so'))
        elif stl == 'gnu-libstdc++':
            self.include_dirs.append(os.path.join(root, '4.9/include'))
            self.include_dirs.append(os.path.join(root, '4.9/include/ext'))
            libpath = os.path.join(root, '4.9/libs', kwargs['arch'])
            self.include_dirs.append(os.path.join(libpath, 'include'))  # bits
            self.lib_dirs.append(libpath)
            self.static_libs.append('gnustl_static')
            self.shared_libs.append(os.path.join(libpath, 'libgnustl_shared.so'))


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

        self.stl = None
        self.sysroot = None

    def matchRequest(self, request):
        if 'android' not in request.target_os.tags:
            return 'target_os is not android'

    def initByRequest(self, request):
        request.variables['ndk'] = self.root
        executablePrefix, toolchain_name = self.getToolchainName(request)
        # android-21+ support 64bit arch
        platform_level = self.kwargs.get('platform', 21)
        prebuilt = os.path.join(self.root,
                                f'toolchains/{toolchain_name}/prebuilt')
        if not os.path.exists(prebuilt):
            raise Exception('Ndk toolchain name not exist: %s' % prebuilt)

        rootBin = os.path.join(prebuilt, os.listdir(prebuilt)[0], 'bin')
        rootPlatform = os.path.join(self.root,
                                    f'platforms/android-{platform_level}')
        if not os.path.exists(rootPlatform):
            raise Exception('Ndk platform not exist: %s' % rootPlatform)

        # $NDK/platforms/android-21/arch-arm
        self.sysroot = os.path.join(rootPlatform,
                                    self.getAndroidPlatformSubfolder(request))
        if not os.path.exists(self.sysroot):
            raise Exception('Ndk sysroot not exist: %s' % self.sysroot)

        stl_name = self.kwargs.get('stl', 'gnu-libstdc++')
        self.stl = NDKStl(
                os.path.join(self.root, 'sources/cxx-stl', stl_name),
                arch=self.getCppLibSubfolder(request))

        if self.kwargs.get('compiler', 'gcc') == 'gcc':
            gcc = GCC(prefix=os.path.join(rootBin, executablePrefix),
                      suffix=request.host_os.getExecutableSuffix())
            return [gcc]

        clang = Clang(prefix=os.path.join(
                self.root,
                'toolchains/llvm/prebuilt/windows-x86_64/bin'),
                suffix=request.host_os.getExecutableSuffix())
        return [clang]

    def asCmdFilter(self, cmd, kwargs):
        if cmd.name == 'cc' or cmd.name == 'cxx':
            cmd.defines += ['__ANDROID__', 'ANDROID', '__ELF__']
            cmd.sysroots += [self.sysroot, os.path.join(self.root, 'sysroot')]
            cmd.include_dirs += os.path.join(
                        self.root,
                        'sysroot/usr/include',
                        self.getSysrootIncludeSubfolder(kwargs['request']))
            if cmd.name == 'cxx':
                cmd.include_dirs += self.stl.include_dirs

        elif cmd.name == 'ld':
            cmd.sysroots += self.sysroot
            cmd.lib_dirs += os.path.join(self.sysroot, 'usr/lib')
            if cmd.name == 'cxx':
                cmd.lib_dirs += self.stl.lib_dirs

    def _search_file(self, filename, paths):
        if not filename:
            return None
        for path in paths:
            p = os.path.join(path, filename)
            if os.path.exists(p):
                return p
        return None

    def getToolchainName(self, request):
        if 'armeabi' in request.arch.tags:
            toolchain_name = 'arm-linux-androideabi-4.9'
            executablePrefix = 'arm-linux-androideabi-'
        elif 'arm64' in request.arch.tags:
            toolchain_name = 'aarch64-linux-android-4.9'
            executablePrefix = 'aarch64-linux-android-'
        elif 'x86_64' in request.arch.tags:
            toolchain_name = 'x86_64-4.9'
            executablePrefix = 'x86_64-linux-android-'
        elif 'x86_32' in request.arch.tags:
            toolchain_name = 'x86-4.9'
            executablePrefix = 'i686-linux-android-'
        else:
            toolchain_name = 'llvm'
            executablePrefix = ''
        return executablePrefix, toolchain_name

    # for $NDK/sysroot/usr/include/
    def getAndroidPlatformSubfolder(self, request):
        if 'arm64' in request.arch.tags:
            return 'arch-arm64'
        if 'x64' in request.arch.tags:
            return 'arch-x86_64'
        return 'arch-' + request.arch.name

    # for $NDK/sysroot/usr/include/
    def getSysrootIncludeSubfolder(self, request):
        arch = request.arch.name
        if 'arm64' in request.arch.tags:
            return 'aarch64-linux-android'
        if 'arm32' in request.arch.tags:
            return 'arm-linux-androideabi'
        if 'x86_32' in request.arch.tags:
            return 'i686-linux-android'
        if 'x86_64' in request.arch.tags:
            return 'x86_64-linux-android'
        return arch + '-linux-android'

    # for $NDK/sources/cxx-stl/gnu-libstdc++/4.9/libs/
    def getCppLibSubfolder(self, request):
        if 'arm32' in request.arch.tags:
            if request.arch.arch_org.endswith('v7a'):
                return 'armeabi-v7a'
            return 'armeabi'
        if 'arm64' in request.arch.tags:
            if request.arch.arch_org.endswith('v8a'):
                return 'arm64-v8a'
            return 'aarch64'
        if 'x86_32' in request.arch.tags:
            return 'x86'
        if 'x86_64' in request.arch.tags:
            return 'x86_64'
        return request.arch.name

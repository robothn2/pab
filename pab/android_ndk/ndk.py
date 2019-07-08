# coding: utf-8

import os
import re
from pab.compiler.gcc import GCC
from pab.compiler.clang import Clang


class NDKStl:
    def __init__(self, root, **kwargs):
        self.include_dirs = []
        self.lib_dirs = []
        self.static_libs = []
        self.shared_libs = []

        stl = os.path.basename(root)
        if stl == 'llvm-libc++':
            self.include_dirs.append(os.path.join(root, 'include'))
            libpath = os.path.join(root, 'libs', kwargs['arch'])
            self.lib_dirs.append(libpath)
            self.static_libs.append('c++_static')
            self.shared_libs.append(os.path.join(libpath, 'libc++_shared.so'))
        elif stl == 'gnu-libstdc++':
            self.include_dirs.append(os.path.join(root, '4.9/include'))
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

        self.rootStl = None
        self.sysroot = None
        self.libPaths = []
        self.cmds = {}
        self.cmdFilters = {}

    def matchRequest(self, request):
        if request.target_os != 'android':
            return (False, 'target_os is not android')

        executablePrefix, toolchain_name = self.getToolchainName(request)
        # android-21+ support 64bit arch
        platform_level = self.kwargs.get('platform', 21)
        prebuilt = os.path.join(self.root,
                                f'toolchains/{toolchain_name}/prebuilt')
        if not os.path.exists(prebuilt):
            return (False, 'Ndk toolchain name not exist: %s' % prebuilt)

        rootBin = os.path.join(prebuilt, os.listdir(prebuilt)[0], 'bin')
        rootPlatform = os.path.join(self.root,
                                    f'platforms/android-{platform_level}')
        if not os.path.exists(rootPlatform):
            return (False, 'Ndk platform not exist: %s' % rootPlatform)

        # $NDK/platforms/android-21/arch-arm
        self.sysroot = os.path.join(rootPlatform,
                                    self.getAndroidPlatformSubfolder(request))
        if not os.path.exists(self.sysroot):
            return (False, 'Ndk sysroot not exist: %s' % self.sysroot)

        # $NDK/platforms/android-21/arch-x86/usr/lib/libc.so
        # $NDK/sources/cxx-stl/llvm-libc++/libs/x86/libc++_shared.so
        self.rootStl = NDKStl(
                os.path.join(self.root, 'sources/cxx-stl', request.stl),
                arch=self.getCppLibSubfolder(request))

        self.libPaths = [os.path.join(self.sysroot, 'usr/lib')]
        self.libPaths.extend(self.rootStl.lib_dirs)

        self.cmdFilters = {
                'cc': [
                    ('define', ['__ANDROID__', 'ANDROID']),
                    ('sysroot', self.sysroot),
                    ('sysroot', os.path.join(self.root, 'sysroot')),
                    ('includePath', lambda kwargs: os.path.join(
                        self.root,
                        'sysroot/usr/include',
                        self.getSysrootIncludeSubfolder(kwargs['request']))),
                ],
                'cxx': [
                    ('define', ['__ANDROID__', 'ANDROID']),
                    ('sysroot', self.sysroot),
                    ('sysroot', os.path.join(self.root, 'sysroot')),
                    ('includePath', lambda kwargs: os.path.join(
                        self.root,
                        'sysroot/usr/include',
                        self.getSysrootIncludeSubfolder(kwargs['request']))),
                    ('includePath', self.rootStl.include_dirs),
                ],
                'link': [
                    ('sysroot', self.sysroot),
                    self._filterLinkToLib,
                ],
                }

        if self.kwargs.get('compiler', 'gcc') == 'gcc':
            gcc = GCC(prefix=os.path.join(rootBin, executablePrefix),
                      suffix=request.hostOS.getExecutableSuffix())
            return True, [gcc]

        clang = Clang(prefix=os.path.join(self.root, 'toolchains/llvm/prebuilt/windows-x86_64/bin'),
                    suffix=request.hostOS.getExecutableSuffix())
        return True, [clang]

    def queryCmd(self, cmd_name):
        return self.cmds.get(cmd_name)

    def filterCmd(self, cmd_name):
        return self.cmdFilters.get(cmd_name)

    def _search_file(self, filename, paths):
        if not filename:
            return None
        for path in paths:
            p = os.path.join(path, filename)
            if os.path.exists(p):
                return p
        return None

    def _filterLinkToLib(self, args):
        if args['cmd'] != 'link':
            return

        ret = []
        crtStatic = args.get('crtStatic', False)
        if args['target'].std.startswith('c++'):
            if crtStatic:
                ret.append(('lib', self.rootStl.static_libs))
            else:
                ret.extend(self.rootStl.shared_libs)
        else:
            if crtStatic:
                ret.append(('lib', 'c'))
            else:
                sopath = self._search_file('libc.so', self.libPaths)
                assert(sopath)
                ret.append(sopath)
        return ret

    def getToolchainName(self, request):
        arch = request.arch
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
            executablePrefix = ''
        return executablePrefix, toolchain_name

    # for $NDK/sysroot/usr/include/
    def getAndroidPlatformSubfolder(self, request):
        return 'arch-' + request.arch

    # for $NDK/sysroot/usr/include/
    def getSysrootIncludeSubfolder(self, request):
        arch = request.arch
        if arch == 'arm64':
            return 'aarch64-linux-android'
        if arch == 'arm':
            return 'arm-linux-androideabi'
        if arch == 'x86':
            return 'i686-linux-android'
        return arch + '-linux-android'

    # for $NDK/sources/cxx-stl/gnu-libstdc++/4.9/libs/
    def getCppLibSubfolder(self, request):
        arch = request.arch
        cpu = request.target_cpu
        if arch == 'arm':
            if cpu.endswith('v7a'):
                return 'armeabi-v7a'
            return 'armeabi'
        if arch == 'arm64':
            if cpu.endswith('v8a'):
                return 'arm64-v8a'
            return 'aarch64'
        return arch

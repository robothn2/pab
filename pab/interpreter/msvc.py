# coding: utf-8
import os
import re
from pab._internal.target_utils import ItemList


class WinSDK:
    def __init__(self, ver, **kwargs):
        self.rootBin = {}
        self.lib_dirs = {}
        self.static_libs = {}
        self.shared_libs = {}
        for arch in ('x86', 'x64', 'arm', 'arm64'):
            self.lib_dirs[arch] = ItemList(name=arch)
            self.static_libs[arch] = ItemList(name=arch)
            self.shared_libs[arch] = ItemList(name=arch)
        self.defines = ItemList(name='defines')
        self.include_dirs = ItemList(name='include_dirs')
        self.ldflags = ItemList(name='ldflags')

        if not ver or ver == '8.1':
            root = r'C:\Program Files (x86)\Windows Kits\8.1'
            rootLib = os.path.join(root, r'Lib\winv6.3')
            for arch in ('x86', 'x64', 'arm'):
                self.rootBin[arch] = os.path.join(root, 'bin', arch)
                self.lib_dirs[arch] += os.path.join(rootLib, 'um', arch)

            self.include_dirs += [
                    os.path.join(root, r'include'),
                    os.path.join(root, r'include\um'),
                    os.path.join(root, r'include\shared'),
                    ]

            self._use_sdk_10('10.0.10240.0')  # for corecrt.h

        elif ver == '7.1':
            root = r'C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A'
            self.rootBin['x86'] = os.path.join(root, r'bin')
            self.rootBin['x64'] = os.path.join(root, r'bin\x64')
            self.lib_dirs['x86'] += os.path.join(root, 'lib')
            self.lib_dirs['x64'] += os.path.join(root, r'lib\x64')
            self.include_dirs += os.path.join(root, 'include')
            self._use_sdk_10('10.0.10240.0')  # for corecrt.h
            self.defines += '_USING_V110_SDK71_'
            self.ldflags += '/SUBSYSTEM:CONSOLE",5.01"'

        elif re.match(r'10\.\d+\.\d+\.\d+', ver):
            self._use_sdk_10(ver)

    def _use_sdk_10(self, ver):
        root = r'C:\Program Files (x86)\Windows Kits\10'
        for arch in ('x86', 'x64', 'arm', 'arm64'):
            self.rootBin[arch] = os.path.join(root, 'bin', arch)
            self.lib_dirs[arch] += [
                    os.path.join(root, 'lib', ver, 'ucrt', arch),
                    os.path.join(root, 'lib', ver, 'um', arch),
                    ]

        self.include_dirs += [
                os.path.join(root, fr'Include\{ver}\ucrt'),
                os.path.join(root, fr'Include\{ver}\um'),
                os.path.join(root, fr'Include\{ver}\shared'),
                ]


class MSVC:
    def __init__(self, **kwargs):
        self.name = 'MSVC'
        self.tags = ('msvc', 'vc', 'visualc', 'msc')
        self.kwargs = kwargs
        # Get install path of vs2015:
        ver = kwargs.get('ver', '14.0')
        self.root = fr'C:\Program Files (x86)\Microsoft Visual Studio {ver}'
        if not os.path.exists(self.root):
            raise Exception('Invalid vs dir: %s' % self.root)

        self.sdk = WinSDK(kwargs.get('platform'))
        self._cmds = {}
        for arch in ('x86', 'x64', 'arm', 'arm64'):
            root_bin = self._search_arch_root(arch)
            if not root_bin:
                continue
            self._cmds[arch] = {
                    'cc':   (os.path.join(root_bin, 'cl.exe'),
                             '/nologo', '/TC', '/c'),
                    'cxx':  (os.path.join(root_bin, 'cl.exe'),
                             '/nologo', '/TP', '/c'),
                    'rc':   (os.path.join(self.sdk.rootBin[arch], 'rc.exe'),
                             '/nologo'),
                    'asm':  (os.path.join(root_bin, 'ml.exe'),
                             '/nologo', '/c'),
                    'ar':   (os.path.join(root_bin, 'lib.exe'),
                             '/nologo'),
                    'ld':   (os.path.join(root_bin, 'link.exe'),
                             '/nologo'),
                    }
        #print('?', self._cmds)
        self._cmds['x86_64'] = self._cmds['x64']  # alias

        self._compositors = {
                'sysroots':      lambda path, args: f'/I"{path}"',
                'include_dirs':  lambda path, args: f'/I"{path}"',
                'lib_dirs':      lambda path, args: f'/LIBPATH:"{path}"',
                'libs':          lambda path, args: path,
                'defines':       lambda macro, args: f'/D "{macro}"',
                }

    def _search_arch_root(self, arch):
        search_order = {
                'x86': (r'vc\bin', r'vc\bin\amd64_x86'),
                'x64': (r'vc\bin\amd64', r'vc\bin\x86_amd64'),
                'arm': (r'vc\bin\amd64_arm', r'vc\bin\x86_arm', r'vc\bin\arm'),
                'arm64': (r'vc\bin\arm64', ),
                }
        for sub_path in search_order[arch]:
            path_bin = os.path.join(self.root, sub_path)
            path_cl = os.path.join(path_bin, 'cl.exe')
            if os.path.exists(path_cl):
                return path_bin
            #print('?', arch, 'path:', path_bin, 'not exist')

    def __str__(self):
        return self.name

    def asCmdProvider(self, kwargs):
        return self._cmds.get(kwargs['request'].arch.name, {})

    def asCmdInterpreter(self):
        return self._compositors

    def asCmdFilter(self, cmd, kwargs):
        if cmd.name == 'cxx' or cmd.name == 'cc':
            # $VSROOT\VC\bin\amd64_x86\CL.exe /c /I"..\..\include" /Zi /nologo /W1 /WX- /Od /Oy- /D JSON_DLL /D WIN32 /D _WINDOWS /D _SILENCE_STDEXT_HASH_DEPRECATION_WARNINGS /D NDEBUG /D _USING_V110_SDK71_ /D _UNICODE /D UNICODE /Gm- /EHsc /MD /GS /fp:precise /Zc:wchar_t /Zc:forScope /Zc:inline /Fo"../../build/stdafx.o" /Fd"build/myprj/vc140.pdb" /Gd /TP /wd4819 src\myprj\stdafx.cpp
            cmd.defines += ['WIN32', '_WINDOWS',
                            '_UNICODE', 'UNICODE']
            flags = cmd.get(cmd.name + 'flags')
            if cmd.name == 'cxx':
                flags += '/EHsc'  # enable c++ execption
            flags += ['/Gm-',  # disable minimal rebuild
                      '/GS',   # 启用安全检查，检测堆栈缓冲区溢出
                      '/fp:precise', # 浮点模型: 精度
                      '/Zc:wchar_t', # treat wchar_t as internal type
                      '/Zc:forScope',# for variables only available in for loop
                      '/Zc:inline',
                      '/W3', '/WX-', '/wd4819',  # warnings
                      '/Od',  # optimization level: /Od = disable, /O1~3
                      '/Oy-', # Omit frame pointer: /Oy- = disable
                      '/Gd',  # default call: /Gd = __cdecl, /Gr = __fastcall, /Gz = __stdcall, /Gv = __vectorcall
                      ]

            request = kwargs['request']
            if request.debug:
                cmd.defines += ['DEBUG', '_DEBUG']
                # /MTd: Multithreaded static debug
                # /MDd: Multithreaded DLL debug
                flags += '/MTd' if request.crt_static else '/MDd'
            else:
                cmd.defines += 'NDEBUG'
                flags += '/MT' if request.crt_static else '/MD'
            #flags += '/Zi' '/PDB:"target.pdb"',

            cmd += '/Fo:"%s"' % kwargs['dst']

            cmd.include_dirs += [
                    os.path.join(self.root, r'VC\include'),
                    os.path.join(self.root, r'VC\atlmfc\include'),
                    ]
            cmd.include_dirs += self.sdk.include_dirs
            cmd.defines += self.sdk.defines

        elif cmd.name == 'rc':
            # "C:\Program Files (x86)\Windows Kits/10/bin/x86/rc.exe" /nologo /l 0x804 /I"C:\Program Files (x86)\Windows Kits/10/Include/10.0.17134.0/um" /I"C:\Program Files (x86)\Windows Kits/10/Include/10.0.17134.0/shared" /Fo"d:\lyra.res" D:/src/lyra/lyra.rc
            cmd += ['-l', '0x804']  # language: Chinese Simplyfied
            cmd += '/Fo"%s"' % kwargs['dst']  # Notice: no ':'
            cmd.include_dirs += self.sdk.include_dirs  # for winres.h

        elif cmd.name == 'asm':
            cmd += '/Fo "%s"' % kwargs['dst']

        elif cmd.name == 'ar':
            dst = kwargs['dst']
            cmd += f'/OUT:"{dst}"'
            cmd.ldflags += '/DEBUG'
            cmd.artifacts['link'] = dst

        elif cmd.name == 'ld':
            # $VSROOT\VC\bin\amd64_x86\link.exe /OUT:"build/myprj.exe" /NOLOGO /LIBPATH:..\..\prebuild\Release gbase.lib kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /MANIFEST /MANIFESTUAC:"level='asInvoker' uiAccess='false'" /manifest:embed /DEBUG /PDB:"build/myprj.pdb" /SUBSYSTEM:CONSOLE,"5.01" /LARGEADDRESSAWARE /DYNAMICBASE /NXCOMPAT /IMPLIB:"build/myprj.lib" /MACHINE:X86 /SAFESEH build/*.obj
            dst = kwargs['dst']
            cmd += f'/OUT:"{dst}"'
            cmd.ldflags += [
                    '/LARGEADDRESSAWARE',
                    '/DYNAMICBASE', '/NXCOMPAT',
                    ]
            cmd.ldflags += self.sdk.ldflags
            cmd.libs += [
                    'kernel32.lib', 'user32.lib', 'gdi32.lib', 'advapi32.lib',
                    'shell32.lib', 'ole32.lib', 'oleaut32.lib', 'shell32.lib',
                    'dbghelp.lib', 'userenv.lib', 'shlwapi.lib',
                    # 'winspool.lib', 'comdlg32.lib',
                    # 'uuid.lib', 'odbc32.lib', 'odbccp32.lib',
                    # 'psapi.lib', 'version.lib', 'winmm.lib',
                    ]

            if '64bit' in kwargs['request'].arch.tags:
                cmd.ldflags += '/MACHINE:X64'
                cmd.lib_dirs += [
                        os.path.join(self.root, r'VC\lib\amd64'),
                        os.path.join(self.root, r'VC\atlmfc\lib\amd64'),
                        ]
                cmd.lib_dirs += self.sdk.lib_dirs['x64']
            else:
                cmd.ldflags += ['/MACHINE:X86',
                                '/SAFESEH',  # only available for x86
                                ]
                cmd.lib_dirs += [
                        os.path.join(self.root, r'VC\lib'),
                        os.path.join(self.root, r'VC\atlmfc\lib'),
                        ]
                cmd.lib_dirs += self.sdk.lib_dirs['x86']

            target = kwargs['target']
            if target.isSharedLib():
                dst_base = os.path.splitext(dst)[0]
                dst_lib = dst_base + '.lib'
                dst_pdb = dst_base + '.pdb'
                cmd.ldflags += ['/DLL', '/DEBUG']
                cmd.ldflags += f'/IMPLIB:"{dst_lib}"'
                cmd.ldflags += f'/PDB:"{dst_pdb}"'
                cmd.artifacts['so'] = dst
                cmd.artifacts['link'] = dst_lib
                cmd.artifacts['pdb'] = dst_pdb

            # '/MANIFEST', '''/MANIFESTUAC:"level='asInvoker' uiAccess='false'"''', '/manifest:embed',
            # '/DEBUG'

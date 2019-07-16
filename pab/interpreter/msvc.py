# coding: utf-8

import os
import re


class MSVC:
    def __init__(self, **kwargs):
        self.name = 'MSVC'
        self.kwargs = kwargs
        # Get install path of vs2015:
        ver = kwargs.get('ver', 14)
        self.root = fr'C:\Program Files (x86)\Microsoft Visual Studio {ver}.0'
        if not os.path.exists(self.root):
            raise Exception('Invalid vs dir: %s' % self.root)

        self._cmds = {
                'cc':   (os.path.join(self.root, r'vc\bin\cl.exe'),
                         '/TC', '/nologo', '/c',
                         '/D', 'WIN32', '/D', '_WINDOWS',
                         '/D', '_UNICODE', '/D', 'UNICODE'),
                'cxx':  (os.path.join(self.root, r'vc\bin\cl.exe'),
                         '/TP', '/nologo', '/c',
                         '/D', 'WIN32', '/D', '_WINDOWS',
                         '/D', '_UNICODE', '/D', 'UNICODE'),
                'ar':   (os.path.join(self.root, r'vc\bin\lib.exe'), ),
                'ld':   (os.path.join(self.root, r'vc\bin\link.exe'),
                         '/nologo',),
                }
        self._compositors = {
                'sysroots':      lambda path, args: f'/I"{path}"',
                'include_dirs':  lambda path, args: f'/I"{path}"',
                'lib_dirs':      lambda path, args: f'/LIBPATH:"{path}"',
                'libs':          lambda path, args: path,
                'defines':       lambda macro, args: f'-D{macro}',
                }

    def __str__(self):
        return self.name

    def matchRequest(self, request):
        return True

    def asCmdProvider(self):
        return self._cmds

    def asCmdInterpreter(self):
        return self._compositors

    def asCmdFilter(self, cmd, kwargs):
        if cmd.name == 'cxx' or cmd.name == 'cc':
            flags = cmd.get(cmd.name + 'flags')
            flags += ['/Gm-',  # disable minimalest rebuild
                      '/GS',   # 启用安全检查，检测堆栈缓冲区溢出
                      '/fp:precise', # 浮点模型: 精度
                      '/Zc:wchar_t', # treat wchar_t as internal type
                      '/Zc:forScope',# for variables only available in for loop
                      '/Zc:inline',  # 编译器不再为未引用的代码和数据生成符号信息
                      '/W3', '/WX-', '/wd4819',  # warnings
                      '/Od',  # optimization level: /Od = disable, /O1~3
                      '/Oy-', # Omit frame pointer: /Oy- = disable
                      '/Gd',  # default call: /Gd = __cdecl, /Gr = __fastcall, /Gz = __stdcall, /Gv = __vectorcall
                      ]

            request = kwargs['request']
            if request.hasMember('debug'):
                cmd.defines += ['DEBUG', '_DEBUG']
                if request.hasMember('crt_static'):
                    flags += '/MTd'  # Multithreaded static debug
                else:
                    flags += '/MDd'
            else:
                cmd.defines += 'NDEBUG'
                flags += '/EHsc'  # enable c++ execption
                if request.hasMember('crt_static'):
                    flags += '/MT'  # Multithreaded DLL debug
                else:
                    flags += '/MD'

            dst = kwargs['dst']
            cmd.addPart(f'/Fo:"{dst}"')

            # include path:
            #   stdio.h
            #       C:\Program Files (x86)\Windows Kits\10\Include\10.0.17763.0\ucrt
            #       C:\Program Files (x86)\Windows Kits\10\Include\10.0.10150.0\ucrt
            #       C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\include
            #       C:\Program Files (x86)\Microsoft Visual Studio 11.0\VC\include
            #       C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\include
            #       C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\include
            #   string, vector, map, cstdio, iostream, sstream, ciso646
            #       C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\include
            #       C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\include
            #   ctype.h, corecrt.h
            #       C:\Program Files (x86)\Windows Kits\10\Include\10.0.17134.0\ucrt
            #       C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\include
            #   winnt.h, winsock2.h,
            #       C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Include
            #       C:\Program Files (x86)\Windows Kits\8.1\Include\um
            #       C:\Program Files (x86)\Windows Kits\10\Include\10.0.17134.0\um
            #   commdlg.h, d3d.h, d3d11.h, objbase.h, commctrl.h,
            #       C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Include
            #       C:\Program Files (x86)\Windows Kits\8.1\Include\um
            #       C:\Program Files (x86)\Windows Kits\10\Include\10.0.10150.0\ucrt
            cmd.include_dirs += os.path.join(self.root, r'VC\include')

        elif cmd.name == 'ar':
            pass

        elif cmd.name == 'ld':
            dst = kwargs['dst']
            cmd.addPart(f'/OUT:"{dst}"')
            cmd.addPart(r'/SUBSYSTEM:CONSOLE,"5.01"')
            cmd.ldflags += [
                    r'/SUBSYSTEM:CONSOLE,"5.01"',
                    '/LARGEADDRESSAWARE',
                    '/DYNAMICBASE', '/NXCOMPAT', '/SAFESEH',
                    ]
            cmd.lib_dirs += os.path.join(self.root, r'VC\lib')
            cmd.libs += [
                    'kernel32.lib', 'user32.lib', 'gdi32.lib', 'advapi32.lib',
                    'shell32.lib', 'ole32.lib', 'oleaut32.lib', 'shell32.lib',
                    'dbghelp.lib', 'userenv.lib', 'shlwapi.lib',
                    # 'winspool.lib', 'comdlg32.lib',
                    # 'uuid.lib', 'odbc32.lib', 'odbccp32.lib',
                    # 'psapi.lib', 'version.lib', 'winmm.lib',
                    ]

            if kwargs.get('x64'):
                cmd.ldflags += '/MACHINE:X64'
            else:
                cmd.ldflags += '/MACHINE:X86'

            if kwargs['target'].isSharedLib():
                cmd.ldflags += '/DLL'
            # '/MANIFEST', '''/MANIFESTUAC:"level='asInvoker' uiAccess='false'"''', '/manifest:embed',
            # '/DEBUG', '/Zi', '/PDB:"target.pdb"',
            # '/IMPLIB:"../../build/Publish2015/EngineWorker.lib"',

        target_platform_ver = self.kwargs.get('target_platform_ver', '10.0.14493.0')
        if target_platform_ver == '7.1':
            if cmd.name == 'ld':
                cmd.lib_dirs += r'C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Lib'
            elif cmd.name in ['cc', 'cxx']:
                cmd.include_dirs += r'C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Include'

        elif re.match(r'10\.\d+\.\d+\.\d+', target_platform_ver):
            # default windows kits: 10.0.xxxxx.0
            if cmd.name == 'ld':
                cmd.lib_dirs += [
                        fr'C:\Program Files (x86)\Windows Kits\10\Lib\{target_platform_ver}\ucrt\x86',
                        fr'C:\Program Files (x86)\Windows Kits\10\Lib\{target_platform_ver}\um\x86',
                        ]
            elif cmd.name in ['cc', 'cxx']:
                cmd.include_dirs += [
                        fr'C:\Program Files (x86)\Windows Kits\10\Include\{target_platform_ver}\ucrt',
                        fr'C:\Program Files (x86)\Windows Kits\10\Include\{target_platform_ver}\um',
                        fr'C:\Program Files (x86)\Windows Kits\10\Include\{target_platform_ver}\shared',
                        ]

        else:
            # default windows sdk: 8.1
            if cmd.name == 'ld':
                cmd.lib_dirs += [
                        r'C:\Program Files (x86)\Windows Kits\8.1\Lib\winv6.3\um\x86',  # only 'um' exist
                        r'C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Lib',
                        ]
            elif cmd.name in ['cc', 'cxx']:
                cmd.include_dirs += [
                        r'C:\Program Files (x86)\Windows Kits\8.1\Include\um',
                        r'C:\Program Files (x86)\Windows Kits\8.1\Include\shared',
                        r'C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Include',
                        ]
            # '/D', '_USING_V110_SDK71_',

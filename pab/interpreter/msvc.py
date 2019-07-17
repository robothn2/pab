# coding: utf-8
import os
import re
from pab._internal.target_utils import ItemList


class WinSDK:
    def __init__(self, ver, **kwargs):
        self.include_dirs = ItemList(name='include_dirs')
        self.lib_dirs = {'x86': ItemList(name='x86'), 'x64': ItemList(name='x64')}
        self.static_libs = {'x86': ItemList(name='x86'), 'x64': ItemList(name='x64')}
        self.shared_libs = {'x86': ItemList(name='x86'), 'x64': ItemList(name='x64')}

        if not ver or ver == '8.1':
            root = r'C:\Program Files (x86)\Windows Kits\8.1'
            self.rootBin = os.path.join(root, r'bin')
            self.include_dirs += [
                    os.path.join(root, r'include'),
                    os.path.join(root, r'include\um'),
                    os.path.join(root, r'include\shared'),
                    ]

            root = os.path.join(root, r'Lib\winv6.3')
            self.lib_dirs['x86'] += os.path.join(root, r'um\x86')
            self.lib_dirs['x64'] += os.path.join(root, r'um\x64')
            self._use_sdk_10('10.0.10240.0')  # for corecrt.h

        elif ver == '7.1':
            root = r'C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A'
            self.rootBin = os.path.join(root, r'bin')
            self.include_dirs += os.path.join(root, 'include')
            self.lib_dirs['x86'] += os.path.join(root, 'lib')
            self.lib_dirs['x64'] += os.path.join(root, r'lib\x64')

        elif re.match(r'10\.\d+\.\d+\.\d+', ver):
            self._use_sdk_10(ver)

    def _use_sdk_10(self, ver):
        root = r'C:\Program Files (x86)\Windows Kits\10'
        self.rootBin = os.path.join(root, r'bin\x64')
        self.include_dirs += [
                os.path.join(root, fr'Include\{ver}\ucrt'),
                os.path.join(root, fr'Include\{ver}\um'),
                os.path.join(root, fr'Include\{ver}\shared'),
                ]

        self.lib_dirs['x86'] += [
                os.path.join(root, fr'Lib\{ver}\ucrt\x86'),
                os.path.join(root, fr'Lib\{ver}\um\x86'),
                ]
        self.lib_dirs['x64'] += [
                os.path.join(root, fr'Lib\{ver}\ucrt\x64'),
                os.path.join(root, fr'Lib\{ver}\um\x64'),
                ]


class MSVC:
    def __init__(self, **kwargs):
        self.name = 'MSVC'
        self.kwargs = kwargs
        # Get install path of vs2015:
        ver = kwargs.get('ver', '14.0')
        self.root = fr'C:\Program Files (x86)\Microsoft Visual Studio {ver}'
        if not os.path.exists(self.root):
            raise Exception('Invalid vs dir: %s' % self.root)

        self.sdk = WinSDK(kwargs.get('platform'))
        self._cmds = {
                'cc':   (os.path.join(self.root, r'vc\bin\cl.exe'),
                         '/TC', '/nologo', '/c'),
                'cxx':  (os.path.join(self.root, r'vc\bin\cl.exe'),
                         '/TP', '/nologo', '/c'),
                'rc':   (os.path.join(self.sdk.rootBin, 'rc.exe'),
                         '/nologo'),
                'ar':   (os.path.join(self.root, r'vc\bin\link.exe'),
                         '-lib'),
                'ld':   (os.path.join(self.root, r'vc\bin\link.exe'),
                         '/nologo'),
                }
        self._compositors = {
                'sysroots':      lambda path, args: f'/I"{path}"',
                'include_dirs':  lambda path, args: f'/I"{path}"',
                'lib_dirs':      lambda path, args: f'/LIBPATH:"{path}"',
                'libs':          lambda path, args: path,
                'defines':       lambda macro, args: f'/D "{macro}"',
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
            # $VSROOT\VC\bin\amd64_x86\CL.exe /c /I"..\..\include" /Zi /nologo /W1 /WX- /Od /Oy- /D JSON_DLL /D WIN32 /D _WINDOWS /D _SILENCE_STDEXT_HASH_DEPRECATION_WARNINGS /D NDEBUG /D _USING_V110_SDK71_ /D _UNICODE /D UNICODE /Gm- /EHsc /MD /GS /fp:precise /Zc:wchar_t /Zc:forScope /Zc:inline /Fo"../../build/stdafx.o" /Fd"build/myprj/vc140.pdb" /Gd /TP /wd4819 src\myprj\stdafx.cpp
            cmd.defines += ['WIN32', '_WINDOWS',
                            '_UNICODE', 'UNICODE']
            flags = cmd.get(cmd.name + 'flags')
            if cmd.name == 'cxx':
                flags += '/EHsc'  # enable c++ execption
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
                    flags += '/MDd'  # Multithreaded DLL debug
            else:
                cmd.defines += 'NDEBUG'
                if request.hasMember('crt_static'):
                    flags += '/MT'
                else:
                    flags += '/MD'

            cmd += '/Fo:"%s"' % kwargs['dst']

            cmd.include_dirs += [
                    os.path.join(self.root, r'VC\include'),
                    os.path.join(self.root, r'VC\atlmfc\include'),
                    ]
            cmd.include_dirs += self.sdk.include_dirs

        elif cmd.name == 'rc':
            # "C:\Program Files (x86)\Windows Kits/10/bin/x86/rc.exe" /nologo /l 0x804 /I"C:\Program Files (x86)\Windows Kits/10/Include/10.0.17134.0/um" /I"C:\Program Files (x86)\Windows Kits/10/Include/10.0.17134.0/shared" /Fo"d:\lyra.res" D:/src/lyra/lyra.rc
            cmd += ['-l', '0x804']  # language: Chinese Simplyfied
            cmd += '/Fo"%s"' % kwargs['dst']  # Notice: no ':'
            cmd.include_dirs += self.sdk.include_dirs  # for winres.h

        elif cmd.name == 'ar':
            cmd += '/OUT:"%s"' % kwargs['dst']

        elif cmd.name == 'ld':
            # $VSROOT\VC\bin\amd64_x86\link.exe /OUT:"build/myprj.exe" /NOLOGO /LIBPATH:..\..\prebuild\Release gbase.libkernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /MANIFEST /MANIFESTUAC:"level='asInvoker' uiAccess='false'" /manifest:embed /DEBUG /PDB:"build/myprj.pdb" /SUBSYSTEM:CONSOLE,"5.01" /LARGEADDRESSAWARE /DYNAMICBASE /NXCOMPAT /IMPLIB:"build/myprj.lib" /MACHINE:X86 /SAFESEH build/*.obj
            cmd += '/OUT:"%s"' % kwargs['dst']
            cmd.ldflags += [
                    '/SUBSYSTEM:CONSOLE,"5.01"',
                    '/LARGEADDRESSAWARE',
                    '/DYNAMICBASE', '/NXCOMPAT', '/SAFESEH',
                    ]
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
                cmd.lib_dirs += [
                        os.path.join(self.root, r'VC\lib\amd64'),
                        os.path.join(self.root, r'VC\atlmfc\lib\amd64'),
                        ]
                cmd.lib_dirs += self.sdk.lib_dirs['x64']
            else:
                cmd.ldflags += '/MACHINE:X86'
                cmd.lib_dirs += [
                        os.path.join(self.root, r'VC\lib'),
                        os.path.join(self.root, r'VC\atlmfc\lib'),
                        ]
                cmd.lib_dirs += self.sdk.lib_dirs['x86']

            if kwargs['target'].isSharedLib():
                cmd.ldflags += '/DLL'
            # '/MANIFEST', '''/MANIFESTUAC:"level='asInvoker' uiAccess='false'"''', '/manifest:embed',
            # '/DEBUG', '/Zi', '/PDB:"target.pdb"',
            # '/IMPLIB:"../../build/Release/MyProject.lib"',


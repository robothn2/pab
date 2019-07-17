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
            root = r'C:\Program Files (x86)\Windows Kits\8.1\Include'
            self.include_dirs += os.path.join(root, 'include')
            self.include_dirs += [
                    os.path.join(root, 'um'),
                    os.path.join(root, 'shared'),
                    ]

            root = r'C:\Program Files (x86)\Windows Kits\8.1\Lib\winv6.3'
            self.lib_dirs['x86'] += os.path.join(root, r'um\x86')
            self.lib_dirs['x64'] += os.path.join(root, r'um\x64')

        elif ver == '7.1':
            root = r'C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A'
            self.include_dirs += os.path.join(root, 'include')
            self.lib_dirs['x86'] += os.path.join(root, 'lib')
            self.lib_dirs['x64'] += os.path.join(root, r'lib\x64')

        elif re.match(r'10\.\d+\.\d+\.\d+', ver):
            root = fr'C:\Program Files (x86)\Windows Kits\10\Include\{ver}'
            self.include_dirs += [
                    os.path.join(root, 'ucrt'),
                    os.path.join(root, 'um'),
                    os.path.join(root, 'shared'),
                    ]

            root = fr'C:\Program Files (x86)\Windows Kits\10\Lib\{ver}'
            self.lib_dirs['x86'] += [
                    os.path.join(root, r'ucrt\x86'),
                    os.path.join(root, r'um\x86'),
                    ]
            self.lib_dirs['x64'] += [
                    os.path.join(root, r'ucrt\x64'),
                    os.path.join(root, r'um\x64'),
                    ]


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
                         '/TC', '/nologo', '/c'),
                'cxx':  (os.path.join(self.root, r'vc\bin\cl.exe'),
                         '/TP', '/nologo', '/c'),
                'ar':   (os.path.join(self.root, r'vc\bin\lib.exe'), ),
                'ld':   (os.path.join(self.root, r'vc\bin\link.exe'),
                         '/nologo',),
                }
        self._compositors = {
                'sysroots':      lambda path, args: f'/I"{path}"',
                'include_dirs':  lambda path, args: f'/I"{path}"',
                'lib_dirs':      lambda path, args: f'/LIBPATH:"{path}"',
                'libs':          lambda path, args: path,
                'defines':       lambda macro, args: f'/D "{macro}"',
                }

        self.sdk = WinSDK(kwargs.get('target_platform_ver'))

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
            cmd.defines += ['WIN32', '_WINDOWS',
                            '_UNICODE', 'UNICODE']
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

            cmd.include_dirs += [
                    os.path.join(self.root, r'VC\include'),
                    os.path.join(self.root, r'VC\atlmfc\include'),
                    ]
            cmd.include_dirs += self.sdk.include_dirs

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


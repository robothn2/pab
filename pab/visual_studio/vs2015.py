# coding: utf-8

import os
import re


class VS2015:
    def __init__(self, **kwargs):
        self.name = 'VS2015'
        self.kwargs = kwargs
        # Get install path of vs2015:
        self.root = r'C:\Program Files (x86)\Microsoft Visual Studio 14.0'
        if not os.path.exists(self.root):
            raise Exception('Invalid vs dir: %s' % self.root)

    def __str__(self):
        return self.name

    def applyConfig(self, config):
        pass

    def registerAll(self, toolchain):
        # exe PATH:
        #   C:\Program Files (x86)\MSBuild\14.0\bin
        #       MSBuild.exe, vbc.exe
        #   $VSROOT\VC\BIN\x86_amd64
        #   $VSROOT\VC\BIN
        #       cl.exe, lib.exe, link.exe, nmake.exe, dumpbin.exe
        #   $VSROOT\Common7\Tools
        #       errlook.exe, guidgen.exe, spyxx.exe
        #   C:\Program Files (x86)\Windows Kits\10\bin\10.0.17134.0\x86
        #   C:\Program Files (x86)\Windows Kits\8.1\bin\x86
        #       fxc.exe, rc.exe, midl.exe
        toolchain.registerCommand(self, 'cc',
                                  os.path.join(self.root, r'VC\bin\cl.exe'))
        toolchain.registerCommand(self, 'cxx',
                                  os.path.join(self.root, r'VC\bin\cl.exe'))
        #toolchain.registerCommand(self, 'as', self.prefix + 'as' + self.postfix)
        toolchain.registerCommand(self, 'ld',
                                  os.path.join(self.root, r'VC\bin\link.exe'))

        # $VSROOT\VC\bin\amd64_x86\CL.exe /c /I"..\..\include" /Zi /nologo /W1 /WX- /Od /Oy- /D JSON_DLL /D WIN32 /D _WINDOWS /D _SILENCE_STDEXT_HASH_DEPRECATION_WARNINGS /D NDEBUG /D _USING_V110_SDK71_ /D _UNICODE /D UNICODE /Gm- /EHsc /MD /GS /fp:precise /Zc:wchar_t /Zc:forScope /Zc:inline /Fo"../../build/int/Publish2015/QYTest/" /Fd"../../build/int/Publish2015/QYTest/vc140.pdb" /Gd /TP /wd4819 /analyze- /errorReport:queue ..\..\src\QYTest\main.cpp ..\..\src\QYTest\stdafx.cpp
        toolchain.registerCommandFilter(self, ['cc', 'cxx'], [
                    ['/nologo', '/c',
                     '/D', 'WIN32', '/D', '_WINDOWS',
                     '/D', '_UNICODE', '/D', 'UNICODE'],
                    # '/showIncludes',
                    ('includePath', os.path.join(self.root, r'VC\include')),
                    self._filterByConfig,
                ])

        # $VSROOT\VC\bin\amd64_x86\link.exe /ERRORREPORT:QUEUE /OUT:"../../build/worker.exe" /NOLOGO /LIBPATH:..\..\..\..\prebuild\vs2015\Win32\Release jsoncpp.lib gbase.lib gtest.lib Engine3.lib kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /MANIFEST /MANIFESTUAC:"level='asInvoker' uiAccess='false'" /manifest:embed /DEBUG /PDB:"../../build/EngineWorker.pdb" /SUBSYSTEM:CONSOLE,"5.01" /LARGEADDRESSAWARE /TLBID:1 /DYNAMICBASE /NXCOMPAT /IMPLIB:"../../build/EngineWorker.lib" /MACHINE:X86 /SAFESEH ../../build/int/EngineWorker.obj
        toolchain.registerCommandFilter(self, 'ld', [
                    ['/nologo',
                     # '/errorReport:queue', '/TLBID:1',
                     #'/MANIFEST', '''/MANIFESTUAC:"level='asInvoker' uiAccess='false'"''', '/manifest:embed',
                     '/MACHINE:X86',
                     # '/DLL',
                     # '/DEBUG', '/Zi', '/PDB:"target.pdb"',
                     # '/IMPLIB:"../../build/Publish2015/EngineWorker.lib"',
                     r'/SUBSYSTEM:CONSOLE,"5.01"',
                     '/LARGEADDRESSAWARE',
                     '/DYNAMICBASE', '/NXCOMPAT', '/SAFESEH',
                     'kernel32.lib', 'user32.lib', 'gdi32.lib', 'advapi32.lib',
                     'shell32.lib', 'ole32.lib', 'oleaut32.lib', 'shell32.lib',
                     'dbghelp.lib', 'userenv.lib', 'shlwapi.lib', 'psapi.lib',
                     'version.lib', 'winmm.lib',
                     # 'winspool.lib', 'comdlg32.lib',
                     # 'uuid.lib', 'odbc32.lib', 'odbccp32.lib',
                     ],
                    ('libPath', os.path.join(self.root, r'VC\lib')),
                    self._filterByConfig,
                ])

        toolchain.registerCompositor(self, ['sysroot', 'includePath'],
                                     lambda path, args: f'/I"{path}"')
        toolchain.registerCompositor(self, 'libPath',
                                     lambda path, args: f'/LIBPATH:"{path}"')
        toolchain.registerCompositor(self, 'lib',
                                     lambda path, args: path)
        toolchain.registerCompositor(self, 'define',
                                     lambda m, args: f'-D{m}')

    def _filterByConfig(self, args):
        ret = []
        request = args['request']
        target = args['target']
        cmd = args['cmd']

        if cmd in ['cc', 'cxx']:
            ret += ['/Gm-',  # 禁用最小重新生成
                    '/GS',   # 启用安全检查，检测堆栈缓冲区溢出
                    '/fp:precise',  # 浮点模型: 精度
                    '/Zc:wchar_t',  # treat wchar_t as internal type
                    '/Zc:forScope',  # for variables only available in for loop
                    '/Zc:inline',  # 编译器不再为未引用的代码和数据生成符号信息
                    '/W3', '/WX-', '/wd4819',  # warnings
                    '/Od',  # optimization level: /Od = disable, /O1, /O2, /O3
                    '/Oy-',  # Omit frame pointer: /Oy- = disable
                    '/Gd',  # default call: /Gd = __cdecl, /Gr = __fastcall, /Gz = __stdcall, /Gv = __vectorcall
                    # '/analyze-', '/errorReport:queue'
                    ]
            if request.hasMember('debug'):
                ret += ['/D', 'DEBUG', '/D', '_DEBUG']
                # Multithreaded static debug/release
                ret.append('/MTd' if request.hasMember('crt_static') else '/MT')
            else:
                ret += ['/D', 'NDEBUG',
                        '/EHsc',  # enable c++ execption
                        ]
                # runtime library linkage
                # Multithreaded DLL debug/release
                ret.append('/MDd' if request.hasMember('crt_static') else '/MD')

            if cmd == 'cc':
                ret.append('/TC')   # compile as C code
            elif cmd == 'cxx':
                ret += ['/D', '_SILENCE_STDEXT_HASH_DEPRECATION_WARNINGS']
                ret.append('/TP')   # compile as C++ code

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
        #   ctype.h
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

        # lib path:
        #   kernel32.lib
        #       C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Lib
        #       C:\Program Files (x86)\Windows Kits\8.1\Lib\winv6.3\um\x86
        #       C:\Program Files (x86)\Windows Kits\10\Lib\10.0.17134.0\um\x86
        #   msvcrt.lib, libcmt.lib, msvcprt.lib, msvcurt.lib
        #       C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\lib
        #   ucrt.lib
        #       C:\Program Files (x86)\Windows Kits\10\Lib\10.0.17763.0\ucrt\x86
        #   mfc140u.lib
        #       C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\atlmfc\lib
        target_platform_ver = request.get('target_platform_ver', '10.0.17763.0')
        if target_platform_ver == '7.1':
            if cmd == 'ld':
                ret.append(('libPath', [
                        r'C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Lib'
                        ]))
            elif cmd in ['cc', 'cxx']:
                ret.append(('includePath', [
                            r'C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Include'
                            ]))

        elif re.match(r'10\.\d+\.\d+\.\d+', target_platform_ver):
            # default windows kits: 10.0.xxxxx.0
            if cmd == 'ld':
                ret.append(('libPath', [
                        fr'C:\Program Files (x86)\Windows Kits\10\Lib\{target_platform_ver}\ucrt\x86',
                        fr'C:\Program Files (x86)\Windows Kits\10\Lib\{target_platform_ver}\um\x86',
                        ]))
            elif cmd in ['cc', 'cxx']:
                ret.append(('includePath', [
                        fr'C:\Program Files (x86)\Windows Kits\10\Include\{target_platform_ver}\ucrt',
                        fr'C:\Program Files (x86)\Windows Kits\10\Include\{target_platform_ver}\um',
                        fr'C:\Program Files (x86)\Windows Kits\10\Include\{target_platform_ver}\shared',
                        ]))

        else:
            # default windows sdk: 8.1
            if cmd == 'ld':
                ret.append(('libPath', [
                        r'C:\Program Files (x86)\Windows Kits\8.1\Lib\winv6.3\um\x86',  # only 'um' exist
                        r'C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Lib',
                        ]))
            elif cmd in ['cc', 'cxx']:
                ret.append(('includePath', [
                        r'C:\Program Files (x86)\Windows Kits\8.1\Include\um',
                        r'C:\Program Files (x86)\Windows Kits\8.1\Include\shared',
                        r'C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Include',
                        ]))
            # '/D', '_USING_V110_SDK71_',

        if 'dst' in args:
            if cmd == 'ld':
                dst = args['dst']
                ret.append(f'/OUT:"{dst}"')
            elif cmd in ('cc', 'cxx'):
                ret.append('/Fo:"{}"'.format(args['dst']))
            elif cmd == 'as':
                pass  # todo

        if 'src' in args:
            src = args['src']
            if isinstance(src, str):
                ret.append(src)
            elif isinstance(src, list):
                ret.extend(src)
        return ret

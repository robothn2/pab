#coding: utf-8

import os

class VS2015:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        # Get install path of vs2015:
        #   1.default install path: C:\Program Files (x86)\Microsoft Visual Studio 14.0
        #   2.
        self.root = r'C:\Program Files (x86)\Microsoft Visual Studio 14.0'
        if not os.path.exists(self.root):
            raise Exception('Invalid vs dir: %s' % self.root)
            
        self.rootIncludes = [
                r'C:\Program Files (x86)\Windows Kits\10\Include\10.0.10240.0\ucrt',
                ]
        # exe PATH:
        #   C:\Program Files (x86)\MSBuild\14.0\bin
        #       MSBuild.exe, vbc.exe
        #   C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\BIN\x86_amd64
        #   C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\BIN
        #       cl.exe, lib.exe, link.exe, nmake.exe, dumpbin.exe
        #   C:\Program Files (x86)\Microsoft Visual Studio 14.0\Common7\Tools
        #       errlook.exe, guidgen.exe, spyxx.exe
        #   C:\Program Files (x86)\Windows Kits\10\bin\10.0.17134.0\x86 || C:\Program Files (x86)\Windows Kits\8.1\bin\x86
        #       fxc.exe, rc.exe, midl.exe
        
        # include path:
        #   stdio.h
        #       C:\Program Files (x86)\Windows Kits\10\Include\10.0.17763.0\ucrt
        #       C:\Program Files (x86)\Windows Kits\10\Include\10.0.17134.0\ucrt
        #       C:\Program Files (x86)\Windows Kits\10\Include\10.0.14393.0\ucrt
        #       C:\Program Files (x86)\Windows Kits\10\Include\10.0.10586.0\ucrt
        #       C:\Program Files (x86)\Windows Kits\10\Include\10.0.10240.0\ucrt
        #       C:\Program Files (x86)\Windows Kits\10\Include\10.0.10150.0\ucrt
        #       C:\Program Files (x86)\Microsoft Visual Studio 12.0\VC\include
        #       C:\Program Files (x86)\Microsoft Visual Studio 11.0\VC\include
        #       C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\include
        #       C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\include
        #   string, vector, map, cstdio, iostream, sstream, ciso646
        #       C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\include
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
        #       C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\lib\amd64
        #   ucrt.lib
        #       C:\Program Files (x86)\Windows Kits\10\Lib\10.0.17763.0\ucrt\x86
        #   mfc140u.lib
        #       C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\atlmfc\lib
        
    def registerAll(self, toolchain):
        toolchain.registerCommand(self, 'cc', os.path.join(self.root, r'VC\bin\cl.exe'))
        toolchain.registerCommand(self, 'cxx', os.path.join(self.root, r'VC\bin\cl.exe'))
        #toolchain.registerCommand(self, 'as', self.prefix + 'as' + self.postfix)
        toolchain.registerCommand(self, 'link', os.path.join(self.root, r'VC\bin\link.exe'))
        toolchain.registerCommand(self, 'fxc', os.path.join(self.root, r'VC\bin\link.exe'))

        #C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64_x86\CL.exe /c /I"..\..\include" /Zi /nologo /W1 /WX- /Od /Oy- /D JSON_DLL /D WIN32 /D _WINDOWS /D _SILENCE_STDEXT_HASH_DEPRECATION_WARNINGS /D NDEBUG /D _USING_V110_SDK71_ /D _UNICODE /D UNICODE /Gm- /EHsc /MD /GS /fp:precise /Zc:wchar_t /Zc:forScope /Zc:inline /Fo"../../build/int/Publish2015/QYTest/" /Fd"../../build/int/Publish2015/QYTest/vc140.pdb" /Gd /TP /wd4819 /analyze- /errorReport:queue ..\..\src\QYTest\main.cpp ..\..\src\QYTest\stdafx.cpp
        toolchain.registerCommandFilter(self, ['cc', 'cxx'], [
                    ('args', '/D', 'WIN32', '/D', '_WINDOWS', '/D', '_UNICODE', '/D', 'UNICODE', '/D', 'NDEBUG',
                             '/D', '_SILENCE_STDEXT_HASH_DEPRECATION_WARNINGS', '/D', '_USING_V110_SDK71_',
                             '/Gm-', '/EHsc', '/MD', '/GS',
                             '/fp:precise', '/Zc:wchar_t', '/Zc:forScope', '/Zc:inline',
                             ),
                    ('args', '/nologo', '/c', '/W3', '/WX-', '/Od', '/Oy-',
                     '/Gd', '/TP', '/wd4819', '/analyze-', '/errorReport:queue'),
                    ('compositor', 'includePath', os.path.join(self.root, r'VC\include')),
                    ('compositor', 'includePath', r'C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Include'),
                    ('compositor', 'includePath', r'C:\Program Files (x86)\Windows Kits\10\Include\10.0.10240.0\ucrt'),
                    self._filterMakeCompileDst,
                    self._filterMakeSrc,
                ])

        #C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64_x86\link.exe /ERRORREPORT:QUEUE /OUT:"../../build/worker.exe" /NOLOGO /LIBPATH:..\..\..\..\prebuild\vs2015\Win32\Release jsoncpp.lib gbase.lib gtest.lib Engine3.lib kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /MANIFEST /MANIFESTUAC:"level='asInvoker' uiAccess='false'" /manifest:embed /DEBUG /PDB:"../../build/EngineWorker.pdb" /SUBSYSTEM:CONSOLE,"5.01" /LARGEADDRESSAWARE /TLBID:1 /DYNAMICBASE /NXCOMPAT /IMPLIB:"../../build/EngineWorker.lib" /MACHINE:X86 /SAFESEH ../../build/int/EngineWorker.obj
        toolchain.registerCommandFilter(self, 'link', [
                    ('args', '/nologo',
                             #'/errorReport:queue', '/TLBID:1',
                             #'/MANIFEST', '''/MANIFESTUAC:"level='asInvoker' uiAccess='false'"''', '/manifest:embed',
                             '/MACHINE:X86',
                             #'/DLL',
                             #'/DEBUG', '/PDB:"../../build/Publish2015/EngineWorker.pdb"',
                             #'/IMPLIB:"../../build/Publish2015/EngineWorker.lib"', 
                             r'/SUBSYSTEM:CONSOLE,"5.01"',
                             '/LARGEADDRESSAWARE',
                             '/DYNAMICBASE', '/NXCOMPAT', '/SAFESEH',
                             'kernel32.lib', 'user32.lib', 'gdi32.lib', 'advapi32.lib', 'shell32.lib',
                             #'winspool.lib', 'comdlg32.lib', 'ole32.lib', 'oleaut32.lib', 'uuid.lib', 'odbc32.lib', 'odbccp32.lib',
                             ),
                    ('compositor', 'libPath', [
                            r'C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\lib',
                            r'C:\Program Files (x86)\Windows Kits\10\Lib\10.0.17763.0\ucrt\x86',
                            r'C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Lib',
                            ]),
                    self._filterMakeLinkDst,
                    self._filterMakeSrc,
                ])

        toolchain.registerArgCompositor(self, ['sysroot', 'includePath'], lambda path, args: ['/I', path])
        toolchain.registerArgCompositor(self, 'libPath', lambda path, args: f'/LIBPATH:"{path}"')
        toolchain.registerArgCompositor(self, 'lib', lambda path, args: path)
        #toolchain.registerArgCompositor(self, 'linkOutput', lambda path, args: f'/OUT:"{path}"')

    def _filterMakeCompileDst(self, args):
        if 'dst' in args:
            return '/Fo"{}"'.format(args['dst'])
        return []
    
    def _filterMakeLinkDst(self, args):
        if 'dst' in args:
            return '/OUT:"{}.exe"'.format(args['dst'])
        return []

    def _filterMakeSrc(self, args):
        ret = []
        if 'src' in args:
            src = args['src']
            if isinstance(src, str):
                ret.append(src)
            elif isinstance(src, list):
                ret.extend(src)
        return ret
        
    
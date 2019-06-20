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
        # PATH:
        #   C:\Program Files (x86)\Microsoft Visual Studio 14.0\Common7\IDE\CommonExtensions\Microsoft\TestWindow
        #   C:\Program Files (x86)\MSBuild\14.0\bin
        #   C:\Program Files (x86)\Microsoft Visual Studio 14.0\Common7\IDE\
        #   C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\BIN\x86_amd64
        #   C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\BIN
        #   C:\Program Files (x86)\Microsoft Visual Studio 14.0\Common7\Tools
        #   C:\WINDOWS\Microsoft.NET\Framework\v4.0.30319
        #   C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\VCPackages
        #   C:\Program Files (x86)\HTML Help Workshop
        #   C:\Program Files (x86)\Microsoft Visual Studio 14.0\Team Tools\Performance Tools
        #   C:\Program Files (x86)\Windows Kits\10\bin\x86
        #   C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\NETFX 4.6.1 Tools\
        
    def registerAll(self, toolchain):
        toolchain.registerCommand(self, 'cc', os.path.join(self.root, r'VC\bin\cl.exe'))
        toolchain.registerCommand(self, 'cxx', os.path.join(self.root, r'VC\bin\cl.exe'))
        #toolchain.registerCommand(self, 'as', self.prefix + 'as' + self.postfix)
        toolchain.registerCommand(self, 'link', os.path.join(self.root, r'VC\bin\link.exe'))

        #C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64_x86\CL.exe /c /I"..\..\include" /Zi /nologo /W1 /WX- /Od /Oy- /D JSON_DLL /D WIN32 /D _WINDOWS /D _SILENCE_STDEXT_HASH_DEPRECATION_WARNINGS /D NDEBUG /D _USING_V110_SDK71_ /D _UNICODE /D UNICODE /Gm- /EHsc /MD /GS /fp:precise /Zc:wchar_t /Zc:forScope /Zc:inline /Fo"../../build/int/Publish2015/QYTest/" /Fd"../../build/int/Publish2015/QYTest/vc140.pdb" /Gd /TP /wd4819 /analyze- /errorReport:queue ..\..\src\QYTest\main.cpp ..\..\src\QYTest\stdafx.cpp
        toolchain.registerCommandFilter(self, ['cc', 'cxx'], [
                    ('args', '/D', 'WIN32', '/D', '_WINDOWS', '/D', '_UNICODE', '/D', 'UNICODE', '/D', 'NDEBUG',
                             '/D', '_SILENCE_STDEXT_HASH_DEPRECATION_WARNINGS', '/D', '_USING_V110_SDK71_',
                             '/Gm-', '/EHsc', '/MD', '/GS',
                             '/fp:precise', '/Zc:wchar_t', '/Zc:forScope', '/Zc:inline',
                             ),
                    ('args', '/nologo', '/c', '/W3', '/WX-', '/Od', '/Oy-',
                     '/Gd', '/TP', '/wd4819', '/analyze-', '/errorReport:queue'),
                    self._filterMakeSrcDst,
                ])

        #C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64_x86\link.exe /ERRORREPORT:QUEUE /OUT:"../../build/worker.exe" /NOLOGO /LIBPATH:..\..\..\..\prebuild\vs2015\Win32\Release jsoncpp.lib gbase.lib gtest.lib Engine3.lib kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /MANIFEST /MANIFESTUAC:"level='asInvoker' uiAccess='false'" /manifest:embed /DEBUG /PDB:"../../build/EngineWorker.pdb" /SUBSYSTEM:CONSOLE,"5.01" /LARGEADDRESSAWARE /TLBID:1 /DYNAMICBASE /NXCOMPAT /IMPLIB:"../../build/EngineWorker.lib" /MACHINE:X86 /SAFESEH ../../build/int/EngineWorker.obj
        toolchain.registerCommandFilter(self, 'link', [
                    ('args', '/nologo', '/errorReport:queue',
                             '/MANIFEST', '''/MANIFESTUAC:"level='asInvoker' uiAccess='false'"''', '/manifest:embed',
                             '/DEBUG', '/MACHINE:X86',
                             #'/PDB:"../../build/Publish2015/EngineWorker.pdb"',
                             #'/IMPLIB:"../../build/Publish2015/EngineWorker.lib"', 
                             #r'/SUBSYSTEM:CONSOLE,"5.01"', '/TLBID:1',
                             '/LARGEADDRESSAWARE',
                             '/DYNAMICBASE', '/NXCOMPAT', '/SAFESEH',
                             'kernel32.lib', 'user32.lib', 'gdi32.lib', 'advapi32.lib', 'shell32.lib',
                             #'winspool.lib', 'comdlg32.lib', 'ole32.lib', 'oleaut32.lib', 'uuid.lib', 'odbc32.lib', 'odbccp32.lib',
                             ),
                    ('compositor', 'linkOutput', lambda args: args['dst']),
                    ('compositor', 'includePath', r'C:\Program Files (x86)\Windows Kits\10\Include\10.0.10240.0\ucrt'),
                    self._filterMakeSrcDst,
                ])

        toolchain.registerArgCompositor(self, ['sysroot', 'includePath'], lambda path, args: f'I"{path}"')
        toolchain.registerArgCompositor(self, 'libPath', lambda path, args: '/LIBPATH:"{path}"')
        toolchain.registerArgCompositor(self, 'lib', lambda path, args: f'-l{path}')
        toolchain.registerArgCompositor(self, 'linkOutput', lambda path, args: f'/Fo"{path}"')

    def _filterMakeCompileDst(self, args):
        if 'dst' in args:
            return '/Fo"{}"'.format(args['dst'])
        return []
    
    def _filterMakeSrcDst(self, args):
        ret = []
        if 'src' in args:
            src = args['src']
            if isinstance(src, str):
                ret.append(src)
            elif isinstance(src, list):
                ret.extend(src)
        return ret
        
    
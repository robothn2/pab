#coding: utf-8

import os
import subprocess
import re

class VS2015:
    def __init__(self, **kwargs):
        # Get install path of vs2015:
        #   1.default install path: C:\Program Files (x86)\Microsoft Visual Studio 14.0
        #   2.
        self.root = r'C:\Program Files (x86)\Microsoft Visual Studio 14.0'
        if not os.path.exists(self.root):
            raise('Invalid vs dir: %s' % self.root)
        self._resolve_all(kwargs)
        
    def _resolve_all(self, args):
        self.cmds['cc'] = os.path.join(self.root, r'VC\bin\amd64_x86\cl.exe')
        self.cmds['cxx'] = os.path.join(self.root, r'VC\bin\amd64_x86\cl.exe')
        self.cmds['link'] = os.path.join(self.root, r'VC\bin\amd64_x86\link.exe')

    def compileFile(self, src, dst):
        #r'C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64_x86\CL.exe /c /I"../../../../external/jsoncpp-master/include" /I../../../../external/fw5.1.22/Build/include/gbase /I..\..\include /Zi /nologo /W1 /WX- /Od /Oy- /D JSON_DLL /D WIN32 /D _WINDOWS /D _SILENCE_STDEXT_HASH_DEPRECATION_WARNINGS /D NDEBUG /D _USING_V110_SDK71_ /D _UNICODE /D UNICODE /Gm- /EHsc /MD /GS /fp:precise /Zc:wchar_t /Zc:forScope /Zc:inline /Fo"../../build/int/Publish2015/QYTest/" /Fd"../../build/int/Publish2015/QYTest/vc140.pdb" /Gd /TP /wd4819 /analyze- /errorReport:queue ..\..\src\QYTest\main.cpp ..\..\src\QYTest\stdafx.cpp
    
    def linkFiles(self, src, dst):
        #r'C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64_x86\link.exe /ERRORREPORT:QUEUE /OUT:"../../build/Publish2015/EngineWorker.exe" /NOLOGO /LIBPATH:..\..\..\..\external\fw5.1.22\Build\libs\publish /LIBPATH:..\..\..\..\prebuild\vs2015\Win32\Release /LIBPATH:d:\jk\workspace\VideoHelper\trunk\QYVideoHelper\build\Publish2015\ jsoncpp.lib gbase.lib gtest.lib Engine3.lib kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /MANIFEST /MANIFESTUAC:"level='asInvoker' uiAccess='false'" /manifest:embed /DEBUG /PDB:"../../build/Publish2015/EngineWorker.pdb" /SUBSYSTEM:CONSOLE,"5.01" /LARGEADDRESSAWARE /TLBID:1 /DYNAMICBASE /NXCOMPAT /IMPLIB:"../../build/Publish2015/EngineWorker.lib" /MACHINE:X86 /SAFESEH ../../build/int/Publish2015/EngineWorker/EngineWorker.obj'
    
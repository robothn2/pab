#coding: utf-8

import subprocess

class Toolchain:
    def __init__(self):
        pass

    def nativeCall(self, cmd, args):
        print(args)
        args.insert(0, r'D:\lib\android-ndk-r14b\toolchains\arm-linux-androideabi-4.9\prebuilt\windows-x86_64\bin\arm-linux-androideabi-gcc.exe')
        args.insert(1, '-I')
        args.insert(2, r'D:\lib\android-ndk-r14b\platforms\android-21\arch-arm\usr\include')
        subprocess.check_call(args)

    def compileFile(self, src, dst):
        cmds = [#'-O3', '-Wall',
                #'-std=c99',
                #'-ffast-math', '-pipe',
                #'-fstrict-aliasing', '-Werror=strict-aliasing',
                #'-Wno-psabi', '-Wa,--noexecstack',
                #'-DANDROID',
                #'-DNDEBUG'
                ]
        cmds += ['-c', '-o', dst, src]
        self.nativeCall('cc', cmds)
    
    def archiveFile(self, src, dst):
        pass
    
    def linkFiles(self, src, dst):
        cmds = ['gcc', '-static']
        #cmds += ['-L', lib_path]
        #cmds += [f'-l{lib_name}']
        if isinstance(src, list):
            cmds += src
        else:
            cmds.append(src)
        
        print(cmds)
        self.nativeCall('link', cmds)
    
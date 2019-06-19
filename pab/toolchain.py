#coding: utf-8

import subprocess

class Toolchain:
    def __init__(self):
        self.plugins = []
        self.argCompositors = {}

    def addPlugin(self, plugin):
        self.plugins.append(plugin)
        plugin.registerAll(self)
    
    def registerArgCompositor(self, config, method, args):
        if hasattr(self.argCompositors, method):
            raise('Found duplicate ArgCompositor')

    def nativeCall(self, cmd, args):
        print(args)
        subprocess.check_call(args)

    def compileFile(self, src, dst):
        print(src, '->', dst)
        cmds = []
        for plugin in self.plugins:
            front, args = plugin.handleFile('cc', src)
            if isinstance(args, list):
                if front:
                    cmds.insert(0, args)
                else:
                    cmds.append(args)
        
        cmds += ['-o', dst, '-c', src]
        self.nativeCall('cc', cmds)
    
    def archiveFile(self, src, dst):
        pass
    
    def linkFiles(self, src, dst):
        cmds = ['-static']
        #cmds += ['-L', lib_path]
        #cmds += [f'-l{lib_name}']
        if isinstance(src, list):
            cmds += src
        else:
            cmds.append(src)
        
        cmds.append(r'--sysroot=D:/lib/android-ndk-r14b/platforms/android-9/arch-arm')
        cmds.append(['-o', dst])
        
        print(cmds)
        self.nativeCall('link', cmds)
    
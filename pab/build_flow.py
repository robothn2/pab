#coding: utf-8

import os

class BuildFlow:
    def __init__(self, args):
        pass

    def run(self, config, source_files, toolchain):
        print('root:', source_files.rootSrc)
        print(' obj:', source_files.rootObj)
        print('files:', source_files.files)
        #toolchain.dumpInfo()
        
        objs = []
        
        for cmd,files in source_files.files.items():
            for file in files:
                src = os.path.join(source_files.rootSrc, file)
                obj = os.path.join(source_files.rootObj, file) + '.o'
                
                toolchain.doCommand(cmd, config=config, src=src, dst=obj)
                objs.append(obj)
        
        toolchain.doCommand('link', config=config, src=objs, dst=os.path.join(source_files.rootObj, 'hello'))
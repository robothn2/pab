#coding: utf-8

import os

class BuildFlow:
    def __init__(self, args):
        pass

    def run(self, config, source_files, toolchain, args):
        print('root:', source_files.rootSrc)
        print(' obj:', source_files.rootObj)
        #print('files:', source_files.files)
        #toolchain.dumpInfo()
        
        objs = []
        
        top = args.get('top', 0)
        for cmd,files in source_files.files.items():
            for file in files:
                src = os.path.join(source_files.rootSrc, file)
                obj = os.path.join(source_files.rootObj, file) + '.o'
                
                toolchain.doCommand(cmd, config=config, src=src, dst=obj)
                objs.append(obj)
                if top and len(objs) >= top:
                    return # only process top count files
        
        toolchain.doCommand('link', config=config, src=objs, dst=os.path.join(source_files.rootWorkspace, 'hello'))
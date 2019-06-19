#coding: utf-8

import os

class BuildFlow:
    def __init__(self, args):
        pass

    def run(self, source_files, toolchain):
        print('root:', source_files.rootSrc)
        print(' obj:', source_files.rootObj)
        print('files:', source_files.files)
        objs = []
        for cat,files in source_files.files.items():
            for file in files:
                src = os.path.join(source_files.rootSrc, file)
                obj = os.path.join(source_files.rootObj, file) + '.o'
                
                toolchain.processFile(cat, src, obj)
                objs.append(obj)
        
        toolchain.linkFiles(objs, os.path.join(source_files.rootObj, 'hello'))
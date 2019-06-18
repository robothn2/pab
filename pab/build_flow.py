#coding: utf-8

import os

class BuildFlow:
    def __init__(self, args):
        pass

    def run(self, source_files, toolchain):
        print(source_files.files)
        objs = []
        for ext,files in source_files.files.items():
            for file in files:
                file = os.path.join(source_files.rootSrc, file)
                obj = os.path.join(source_files.rootObj, file) + '.o'
                toolchain.compileFile(file, obj)
                objs.append(obj)
        
        toolchain.linkFiles(objs, os.path.join(source_files.rootObj, 'hello'))
#coding: utf-8

import os
from pab.source_files import SourceFiles

class FolderTarget:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.root = kwargs['root']
        self.rootBuild = kwargs['rootBuild']
        self.target_name = kwargs.get('target_name', os.path.basename(self.root))
        self.files = SourceFiles(self.root, self.rootBuild)
        if not os.path.exists(self.root):
            raise Exception(r'gcc dir not exist')
        
    def registerAll(self, toolchain):
        paths = []
        path = self.kwargs.get('includePath', None)
        if isinstance(path, str):
            paths.append(path)
        elif isinstance(path, list) or isinstance(path, tuple):
            for p in path:
                paths.append(p)
        paths.append(os.path.join(self.root, 'include'))
        paths.append(os.path.join(self.root, '../include'))
        
        # remove non-exist include paths
        include_paths = []
        for p in paths:
            p = os.path.realpath(p)
            if os.path.exists(p):
                include_paths.append(p)
                
        toolchain.registerCommandFilter(self, ['cc', 'cxx'], [
                    ('compositor', 'includePath', include_paths),
                ])
        toolchain.registerCommandFilter(self, 'link', [
                    ('compositor', 'targetName', self.target_name),
                ])

    def build(self, config, toolchain, args):
        print('===Build target:', self.files.rootSrc)
        #print('files:', self.files.files)
        
        objs = []
        
        top = args.get('top', 0)
        for cmd,files in self.files.files.items():
            for file in files:
                out = toolchain.doCommand(cmd, config=config,
                                          src=os.path.join(self.files.rootSrc, file),
                                          dst=os.path.join(self.files.rootObj, file) + '.o')
                if not out:
                    continue
                objs.append(out)
                if top and len(objs) >= top:
                    return # only process top count files
        
        toolchain.doCommand('link', config=config, src=objs, dst=os.path.join(self.files.rootWorkspace, self.target_name))
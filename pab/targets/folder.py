# coding: utf-8

import os
from pab.source_files import SourceFiles


class FolderTarget:
    def __init__(self, **kwargs):
        self.name = 'Target'
        self.root = kwargs['root']
        if not os.path.exists(self.root):
            raise Exception(r'target dir not exist:', self.root)
        self.rootBuild = kwargs['rootBuild']
        self.targetType = kwargs['targetType']
        self.targetName = kwargs.get('targetName', os.path.basename(self.root))
        self.files = SourceFiles(**kwargs)
        self.defines = kwargs.get('defines', [])
        self.kwargs = kwargs

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
                    ('includePath', include_paths),
                ])
        toolchain.registerCommandFilter(self, ['cc', 'cxx'], [
                    ('define', self.defines),
                ])

    def build(self, config, toolchain, args):
        print('===Build target:', self.files.rootSrc)
        # print('files:', self.files.files)

        if not os.path.exists(self.rootBuild):
            os.makedirs(self.rootBuild)

        top = args.get('top', 0)
        cnt = 0
        objs = []
        for cmd, files in self.files.files.items():
            for file in files:
                if top and cnt >= top:
                    break  # only process top count files

                out = toolchain.doCommand(
                        cmd, config=config,
                        src=os.path.join(self.files.rootSrc, file),
                        dst=os.path.join(self.files.rootObj, file) + '.o',
                        **self.kwargs)
                cnt += 1
                if out:
                    objs.append(out)

        if len(objs) == 0:
            return

        if self.targetType == 'staticLib':
            toolchain.doCommand(
                    'ar',
                    config=config, src=objs,
                    dst=os.path.join(self.files.rootWorkspace, self.targetName),
                    **self.kwargs)
        else:
            toolchain.doCommand(
                    'link',
                    config=config, src=objs,
                    dst=os.path.join(self.files.rootWorkspace, self.targetName),
                    **self.kwargs)

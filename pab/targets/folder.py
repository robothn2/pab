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
        self.std = kwargs.get('std', 'c11')  # c99, c11, c++11, c++15, c++17
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
        created_dst_folders = []
        for cmd, files in self.files.files.items():
            for file in files:
                if top and cnt >= top:
                    break  # only process top count files

                sub_folder = os.path.dirname(file)
                if sub_folder and sub_folder not in created_dst_folders:
                    dst_folder = os.path.join(self.files.rootObj, sub_folder)
                    if not os.path.exists(dst_folder):
                        os.makedirs(dst_folder)
                    created_dst_folders.append(sub_folder)

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
                    dst=os.path.join(self.files.rootWorkspace,
                                     self.targetName),
                    **self.kwargs)
        else:
            dst = toolchain.doCommand(
                    'link',
                    config=config, src=objs,
                    dst=os.path.join(self.files.rootWorkspace,
                                     self.targetName),
                    **self.kwargs)

            toolchain.doCommand('ldd', config=config, src=dst)

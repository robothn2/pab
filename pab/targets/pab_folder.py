# coding: utf-8

import os
from pab._internal.source_file_detect import source_file_detect

def _file_read(filename, mode='rU'):
    with open(filename, mode=mode) as f:
        # codecs.open() has different behavior than open() on python 2.6 so use
        # open() and decode manually.
        s = f.read()
        try:
            return s.decode('utf-8')
        # AttributeError is for Py3 compatibility
        except (UnicodeDecodeError, AttributeError):
            return s


class PabTargets:
    def __init__(self, **kwargs):
        self.name = 'PabTargets'
        self.root = kwargs['root']
        self.rootSource = kwargs['rootSource']
        assert(os.path.exists(self.root) and os.path.exists(self.rootSource))
        self.rootBuild = kwargs['rootBuild']
        self.defines = kwargs.get('defines', [])
        self.kwargs = kwargs
        self.targets = {}
        self.targetsSorted = []
        self._parse_pyfiles()

    def __str__(self):
        return self.name + '(' + self.rootSource + ')'

    def _parse_pyfiles(self):
        for file_name in os.listdir(self.root):
            if not file_name.endswith('.py'):
                continue

            global_scope = {}
            local_scope = {}
            content = _file_read(os.path.join(self.root, file_name))
            try:
                exec(content, global_scope, local_scope)
            except SyntaxError as e:
                print('* Exception occupied in', file_name, e)
                continue

            targets = local_scope.get('export_libs', [])
            assert(isinstance(targets, list))
            for target in targets:
                assert(isinstance(target, tuple))
                uri = target[0]['uri']
                self.targets[uri] = target

        print('Parsed targets:', list(self.targets.keys()))
        '''
        if builtin_vars:
            vars_dict.update(builtin_vars)
        if vars_override:
            vars_dict.update({k: v for k, v in vars_override.items() if k in vars_dict})
        '''

    def _sort_targets(self):
        self.targetsSorted = list(self.targets.values())

    def registerAll(self, toolchain):
        paths = []
        path = self.kwargs.get('includePath', None)
        if isinstance(path, str):
            paths.append(path)
        elif isinstance(path, list) or isinstance(path, tuple):
            for p in path:
                paths.append(p)
        paths.append(os.path.join(self.rootSource, 'include'))
        paths.append(os.path.join(self.rootSource, '../include'))

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


    def build(self, request, toolchain, args):
        self._sort_targets()

        print('===Build', str(self))
        if not os.path.exists(self.rootBuild):
            os.makedirs(self.rootBuild)

        objs = []
        created_dst_folders = []
        for target in self.targetsSorted:
            dyn_setting = target[1]
            uri = target[0]['uri']
            target_name = os.path.basename(uri)

            print('==Target:', uri)
            assert(callable(dyn_setting))
            #dyn_setting()
            #toolchain.registerPlugin()
            for file in target[0].get('sources', []):
                sub_folder = os.path.dirname(file)
                if sub_folder and sub_folder not in created_dst_folders:
                    dst_folder = os.path.join(self.rootBuild, sub_folder)
                    if not os.path.exists(dst_folder):
                        os.makedirs(dst_folder)
                    created_dst_folders.append(sub_folder)

                src = os.path.join(self.rootSource, file)
                file_detect = source_file_detect(src)
                if not file_detect.match(request):
                    continue

                out = toolchain.doCommand(
                        file_detect.cmd, config=request,
                        src=src,
                        dst=os.path.join(self.rootBuild, file) + '.o',
                        **self.kwargs)
                if out:
                    objs.append(out)

            if len(objs) == 0:
                continue


            dst = toolchain.doCommand(
                    'link',
                    config=config, src=objs,
                    dst=os.path.join(self.rootBuild, target_name),
                    **self.kwargs)

            toolchain.doCommand('ldd', config=config, src=dst)

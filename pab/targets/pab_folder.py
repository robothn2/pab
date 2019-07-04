# coding: utf-8

import os
from pab._internal.arch import arch_detect
from pab._internal.file_scope import parse_build_file

class Target:
    def __init__(self, tar, rootSource):
        self.dyn_setting = tar[1]
        self.setting = tar[0]
        self.uri = self.setting['uri']
        self.type = self.setting.get('type', 'staticLib')
        self.name = os.path.basename(self.uri)

        include_dirs = self.setting.get('include_dirs', [])
        exist_dirs = []
        for path in include_dirs:
            path = os.path.realpath(os.path.join(rootSource, path))
            if not os.path.exists(path):
                continue
            exist_dirs.append(path)

        self.cmdFilters = {
                'cc': [
                    ('define', self.setting.get('defines', [])),
                    ('includePath', exist_dirs),
                ],
                'cxx': [
                    ('define', self.setting.get('defines', [])),
                    ('includePath', exist_dirs),
                ],
                }

    def get(self, key, defaultValue):
        return self.setting.get(key, defaultValue)

    def filterCmd(self, cmd_name):
        return self.cmdFilters.get(cmd_name, [])

class PabTargets:
    def __init__(self, **kwargs):
        self.name = 'PabTargets'
        self.root = os.path.realpath(kwargs['root'])
        self.rootSource = os.path.realpath(kwargs.get('rootSource', self.root))
        assert(os.path.exists(self.root) and os.path.exists(self.rootSource))
        self.kwargs = kwargs
        self.cmdFilters = {'cc': [], 'cxx': [],}
        self.targets = {}
        self.targetsSorted = []
        self._parse_pyfiles()
        self._init_cmd_filters()

    def __str__(self):
        return self.name + '(' + self.rootSource + ')'

    def _parse_pyfiles(self):
        for file_name in os.listdir(self.root):
            if not file_name.endswith('.py'):
                continue

            targets = parse_build_file(os.path.join(self.root, file_name))
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

    def _init_cmd_filters(self):
        # support include paths & defines from constructor
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
        include_dirs = []
        for p in paths:
            p = os.path.realpath(p)
            if os.path.exists(p):
                include_dirs.append(p)

        cc_filters = self.cmdFilters['cc']
        cxx_filters = self.cmdFilters['cxx']
        if len(include_dirs) > 0:
            cc_filters.append(('includePath', include_dirs))
            cxx_filters.append(('includePath', include_dirs))

        defines = self.kwargs.get('defines', [])
        if len(defines) > 0:
            cc_filters.append(('define', defines))
            cxx_filters.append(('define', defines))

    def filterCmd(self, cmd_name):
        return self.cmdFilters.get(cmd_name, [])

    def build(self, request, configs, builder, kwargs):
        self._sort_targets()

        print('===Build', str(self))
        if not os.path.exists(request.rootBuild):
            os.makedirs(request.rootBuild)

        objs = []
        created_dst_folders = []
        for t in self.targetsSorted:
            target = Target(t, self.rootSource)

            configs.append(target)
            print('==Target:', target.uri)
            for file in target.get('sources', []):
                sub_folder = os.path.dirname(file)
                if sub_folder and sub_folder not in created_dst_folders:
                    dst_folder = os.path.join(request.rootBuild, sub_folder)
                    if not os.path.exists(dst_folder):
                        os.makedirs(dst_folder)
                    created_dst_folders.append(sub_folder)

                src = os.path.join(self.rootSource, file)
                detected = arch_detect(src)
                if not detected.match(request):
                    print('* skipped', file, str(detected))
                    continue

                out = builder.execCommand(
                        detected.cmd, request=request, src=src,
                        dst=os.path.join(request.rootBuild, file) + '.o',
                        **self.kwargs)
                if out:
                    objs.append(out)

            if len(objs) > 0:
                dst = builder.execCommand(
                        'link',
                        request=request, src=objs,
                        dst=os.path.join(request.rootBuild, target.name),
                        targetType=target.type,
                        **self.kwargs)

                # builder.execCommand('ldd', request=request, src=dst)

            configs.remove(target)
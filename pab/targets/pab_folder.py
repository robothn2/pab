# coding: utf-8

import os
from pab._internal.file_scope import parse_build_file
from pab._internal.target import Target


class PabTargets:
    def __init__(self, **kwargs):
        self.name = 'PabTargets'
        self.kwargs = kwargs
        self.cmdFilters = {'cc': [], 'cxx': [],}
        self.targets = {}
        self.targetsSorted = []

        root = os.path.realpath(kwargs['root'])
        assert(os.path.exists(root))
        self.rootSource = kwargs.get('rootSource')
        self._parse_pyfiles(root)
        self._init_cmd_filters()

    def __str__(self):
        return self.name + '(' + self.rootSource + ')'

    def _parse_pyfiles(self, root):
        if os.path.isfile(root):
            self._parse_pyfile(root)
        elif os.path.isdir(root):
            for file_name in os.listdir(root):
                if not file_name.endswith('.py'):
                    continue

                self._parse_pyfile(os.path.join(root, file_name))

        assert(self.rootSource)
        print('Parsed targets:', list(self.targets.keys()))

    def _parse_pyfile(self, pyfile):
        targets = parse_build_file(pyfile)
        assert(isinstance(targets, list))
        for target in targets:
            assert(isinstance(target, tuple))
            uri = target[0]['uri']
            self.targets[uri] = target

            if not self.rootSource:
                path = target[0].get('source_base_dir')
                if not path:
                    return
                if os.path.isabs(path):
                    self.rootSource = path
                else:
                    # relative path based by pyfile
                    pypath = os.path.dirname(pyfile)
                    path = os.path.realpath(os.path.join(pypath, path))
                    if os.path.exists(path):
                        self.rootSource = path

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

        print('=== Build', str(self))
        for t in self.targetsSorted:
            target = Target(t, self.rootSource, request)

            configs.append(target)
            target.build(builder, self.kwargs)
            configs.remove(target)
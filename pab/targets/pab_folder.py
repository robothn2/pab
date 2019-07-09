# coding: utf-8

import os
from pab._internal.file_scope import parse_build_file
from pab._internal.target import Target


class PabTargets:
    def __init__(self, **kwargs):
        self.name = 'PabTargets'
        self.kwargs = kwargs
        self.targets = {}
        self.targetsSorted = []

        root = os.path.realpath(kwargs['root'])
        assert(os.path.exists(root))
        self._parse_pyfiles(root)

    def __str__(self):
        return self.name

    def _parse_pyfiles(self, root):
        if os.path.isfile(root):
            self._parse_pyfile(root)
        elif os.path.isdir(root):
            for file_name in os.listdir(root):
                if not file_name.endswith('.py'):
                    continue

                self._parse_pyfile(os.path.join(root, file_name))

        print('Parsed targets:', list(self.targets.keys()))

    def _parse_pyfile(self, pyfile):
        targets = parse_build_file(pyfile)
        assert(isinstance(targets, list))
        for target in targets:
            assert(isinstance(target, tuple))
            uri = target[0]['uri']
            self.targets[uri] = target

    def _sort_targets(self):
        self.targetsSorted = list(self.targets.values())

    def build(self, request, configs, builder, kwargs):
        self._sort_targets()

        print('=== Build', str(self))
        for t in self.targetsSorted:
            target = Target(t, request)

            configs.append(target)
            target.build(builder, self.kwargs)
            configs.remove(target)

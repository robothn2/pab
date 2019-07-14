# coding: utf-8

import os
from pab._internal.target_utils import parse_target_file
from pab._internal.target import Target
from pab._internal.log import logger


class PabTargets:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.parsedTargets = {}
        self.completedTargets = {}

        root = os.path.realpath(kwargs['root'])
        assert(os.path.exists(root))
        self.name = 'PabTargets(%s)' % root
        self.root = root
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

        logger.info('Parsed targets: {}'.format(
                list(self.parsedTargets.keys())))

    def _parse_pyfile(self, pyfile):
        parsed_targets = parse_target_file(pyfile)
        assert(isinstance(parsed_targets, list))
        for parsed in parsed_targets:
            assert(isinstance(parsed, tuple))
            uri = parsed[0]['uri']
            # [pending, depend_level, target]
            self.parsedTargets[uri] = [True, 0, parsed]

    def _sort_targets_by_deps(self, kwargs):
        round_cnt = 0
        while True:
            found_pending = False
            for uri, entry in self.parsedTargets.items():
                if not entry[0]:
                    continue  # already resolved
                found_pending = True
                tar = entry[2][0]
                result, level_deps = self._is_deps_all_resolved(
                        tar.get('deps'), uri)
                if not result:
                    continue

                result, level_cfgs = self._is_deps_all_resolved(
                        tar.get('configs'), uri)
                if not result:
                    continue

                logger.info(f'round {round_cnt}: {uri} all resolved')
                entry[0] = False  # all deps & configs resolved
                entry[1] = max(level_deps, level_cfgs) + 1
            if not found_pending:
                logger.info(f'round {round_cnt}: no more pending')
                break  # no more
            round_cnt += 1

        sorted_uris = sorted(self.parsedTargets,
                             key=lambda x: self.parsedTargets[x][1])
        logger.info(sorted_uris)
        return [self.parsedTargets[uri][2] for uri in sorted_uris]

    def _is_deps_all_resolved(self, deps, uri):
        if not deps:
            return True, 0

        max_level = 0
        for uri_dep in deps:
            depend_tar = self.parsedTargets.get(uri_dep)
            if not depend_tar:
                raise Exception(f'depend uri({uri_dep}) not found in {uri}')

            if depend_tar[0]:
                return False, 0
            max_level = max(max_level, depend_tar[1])
        return True, max_level

    def build(self, request, configs, builder, **kwargs):
        sortedTars = self._sort_targets_by_deps(kwargs)

        logger.info('= Build: ' + self.name)
        for tar in sortedTars:
            target = Target(tar, request, root=self.root)

            configs.append(target)
            target.build(builder, **self.kwargs, **kwargs)
            configs.remove(target)

            self.completedTargets[target.uri] = target

    def filterCmd(self, cmd_name, kwargs):
        # add command parts for target's deps
        # todo: support configs
        # todo: support ccflags, cxxflags, ldflags, etc for cc/cxx
        target = kwargs.get('target')
        if not target or not target.isArtifact():
            return

        ret = []
        if cmd_name == 'cc' or cmd_name == 'cxx':
            # provide deps.public_include_dirs for cc/cxx
            for dep_name in target.getDepends():
                dep = self.completedTargets.get(dep_name)
                if not dep:
                    continue
                ret.append(('includePath', dep.setting.public_include_dirs))

        elif cmd_name == 'link':
            # provide deps.artifact for link
            for dep_name in target.getDepends():
                dep = self.completedTargets.get(dep_name)
                if not dep or not dep.artifact:
                    continue
                if dep.isSharedLib():
                    ret.append(dep.artifact)
                elif dep.isStaticLib():
                    ret.append(('libPath', os.path.dirname(dep.artifact)))
                    ret.append(('lib', dep.name))
        return ret

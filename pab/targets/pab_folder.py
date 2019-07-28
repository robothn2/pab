# coding: utf-8
import os
from collections import deque
from pab._internal.target_context import parse_target_file
from pab._internal.target import Target
from pab._internal.log import logger


class PabTargets:
    def __init__(self, **kwargs):
        self.parsedTargets = {}
        self.completedTargets = {}

        root_script = os.path.realpath(kwargs['root_script'])
        assert(os.path.exists(root_script))
        kwargs['root_script'] = root_script
        self.kwargs = kwargs
        self.name = f'PabTargets({root_script})'
        self._parse_pyfiles(root_script)

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
            # [is_pending, depend_level, target]
            self.parsedTargets[uri] = [True, 0, parsed]

    def _sort_targets_by_deps(self):
        round_cnt = 0
        logger.debug('Targets sort: totally {}'.format(len(self.parsedTargets)))
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

                logger.debug(f'Targets sort: round {round_cnt} - {uri} all resolved')
                entry[0] = False  # all deps & configs resolved
                entry[1] = max(level_deps, level_cfgs) + 1
            if not found_pending:
                logger.debug(f'Targets sort: round {round_cnt} - no more pending')
                break  # no more
            round_cnt += 1

        sorted_uris = sorted(self.parsedTargets,
                             key=lambda x: self.parsedTargets[x][1])
        logger.info('Sorted targets: {}'.format(
                sorted_uris))
        return [self.parsedTargets[uri][2] for uri in sorted_uris]

    def _is_deps_all_resolved(self, deps, uri):
        if not deps:
            return True, 0

        max_level = 0
        for uri_dep in deps:
            depend_tar = self.parsedTargets.get(uri_dep)
            if not depend_tar:
                raise Exception(f'dep({uri_dep}) not found for {uri}')

            if depend_tar[0]:
                return False, 0  # still pending
            max_level = max(max_level, depend_tar[1])
        return True, max_level

    def _remove_unwanted_targets(self):
        target_name = self.kwargs.get('target_name')
        if not target_name:
            return
        self.kwargs.pop('target_name')

        wanted_tars = {}
        q = deque()
        q.append(target_name)
        while q:
            name = q.popleft()
            tar = self.parsedTargets[name]
            wanted_tars[name] = tar

            for dep in tar[2][0].get('deps', []):
                assert(isinstance(dep, str))
                if dep not in wanted_tars:
                    q.append(dep)

        if len(self.parsedTargets) > len(wanted_tars):
            print('Removed', len(self.parsedTargets) - len(wanted_tars),
                  'unwanted targets')
            self.parsedTargets = wanted_tars

    def build(self, request, builder, **kwargs):
        self._remove_unwanted_targets()
        sortedTars = self._sort_targets_by_deps()
        logger.info('= Build: ' + self.name)
        for tar in sortedTars:
            target = Target(tar, request,
                            **self.kwargs,
                            compiler_tags=builder.compiler.tags)

            builder.configs.append(target)
            target.build(builder, **kwargs)
            builder.configs.remove(target)

            self.completedTargets[target.uri] = target

    def asCmdFilter(self, cmd, kwargs):
        # add command parts for target's deps
        target = kwargs.get('target')
        if not target or not target.isArtifact():
            return

        for cfg_name in target.getConfigs():
            cfg = self.completedTargets.get(cfg_name)
            if not cfg:
                continue
            cmd += cfg

        if cmd.name == 'cc' or cmd.name == 'cxx':
            # provide deps.public_include_dirs for cc/cxx
            for dep_name in target.getDepends():
                dep = self.completedTargets.get(dep_name)
                if not dep:
                    continue
                cmd.defines += dep.setting.public_defines
                cmd.include_dirs += dep.rebasePath(
                        dep.setting.public_include_dirs)

        elif cmd.name == 'ld':
            # provide deps.artifacts for link
            for dep_name in target.getDepends():
                dep = self.completedTargets.get(dep_name)
                if not dep:
                    continue
                cmd.lib_dirs += dep.rebasePath(dep.setting.public_lib_dirs)
                cmd.libs += dep.rebasePath(dep.setting.public_libs)
                if not dep.artifacts:
                    continue
                # msvc link to target.artifacts['link']
                cmd.sources += dep.artifacts.get('link') or dep.artifacts.get('o')

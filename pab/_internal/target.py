# coding: utf-8

import os
import re
import shutil
from .file_detect import file_detect
from .target_context import TargetContext
from .target_utils import ItemList
from .log import logger


class Target:
    def __init__(self, tar_def, request, *deps, **kwargs):
        if isinstance(tar_def, tuple):
            init_setting = tar_def[0]
            self.dyn_setting = tar_def[1]
        else:
            init_setting = tar_def
            self.dyn_setting = None
        base = init_setting.get('source_base_dir')
        if not os.path.isabs(base):
            root_base = kwargs.get('root_source') or kwargs.get('root')
            assert(root_base)
            base = os.path.realpath(os.path.join(root_base, base))
            init_setting['source_base_dir'] = base

        self.request = request
        self.setting = TargetContext(**init_setting, **request.kwargs, **kwargs)
        self.uri = self.setting['uri']
        self.type = self.setting.get('type')
        self.name = re.split(r'[./\\]', self.uri)[-1]
        self.rootSource = base
        self.objs = ItemList(name='objs')
        self.artifacts = {}

    def __str__(self):
        return self.uri

    def isSharedLib(self):
        return self.type == 'sharedLib'

    def isStaticLib(self):
        return self.type == 'staticLib'

    def isArtifact(self):
        return self.type in ('staticLib', 'sharedLib', 'executable')

    def getDepends(self):
        return self.setting.deps

    def getConfigs(self):
        return self.setting.configs

    def rebasePath(self, paths):
        ret = []
        for p in paths:
            if os.path.isabs(p):
                ret.append(p)
            else:
                p_final = os.path.realpath(os.path.join(self.rootSource, p))
                ret.append(p_final)
        return ret

    def asCmdFilter(self, cmd, kwargs):
        if cmd.name == 'cxx':
            cmd.cxxflags += self.setting.cxxflags
            cmd.include_dirs += self.rebasePath(self.setting.include_dirs)
        elif cmd.name == 'cc':
            cmd.ccflags += self.setting.ccflags
            cmd.include_dirs += self.rebasePath(self.setting.include_dirs)
        elif cmd.name == 'ld':
            cmd.ldflags += self.setting.ldflags
            cmd.lib_dirs += self.rebasePath(self.setting.lib_dirs)
            cmd.libs += self.setting.libs

    def build(self, builder, **kwargs):
        print('== Target: {}, type: {}, base: {}'.format(
                self.uri, self.type, self.rootSource))
        if self.dyn_setting:
            self.dyn_setting(self.setting, self.setting)
        # logger.debug('Setting apply: ' + str(self.setting))

        if not self.isArtifact():
            return

        # compile all sources
        created_dst_folders = []
        sources = self.setting.get('sources', [])
        for file in sources:
            if not isinstance(file, str):
                logger.warning(f' invalid file: {file}')
                continue
            # cache for sub folder creation
            sub_folder = os.path.dirname(file)
            if sub_folder and sub_folder not in created_dst_folders:
                dst_folder = os.path.join(self.request.rootBuild, sub_folder)
                if not os.path.exists(dst_folder):
                    os.makedirs(dst_folder)
                created_dst_folders.append(sub_folder)

            src = os.path.realpath(os.path.join(self.rootSource, file))
            detected = file_detect(src)
            if not detected.cmd:
                logger.info(' unhandled ' + file)
                builder.results.unhandled(file)
                continue
            result, reason = detected.match(self.request)
            if not result:
                logger.info(' skipped ' + file)
                builder.results.skipped(file, reason)
                continue

            dst = os.path.join(self.request.rootBuild, file) + '.o'
            builder.poolCommand(
                        detected.cmd, file=file, sources=src, dst=dst,
                        build_title=file, target=self, **kwargs)

        for cmd in builder.waitPoolComplete():
            if cmd.success:
                self.objs += cmd.dst
        if len(self.objs) == 0:
            return

        # generate artifact
        executable = os.path.join(
                self.request.rootBuild, 'lib',
                self.request.target_os.getFullName(self.name, self.type))
        dstfolder = os.path.dirname(executable)
        if not os.path.exists(dstfolder):
            os.makedirs(dstfolder)
        cmd_name = 'ar' if self.isStaticLib() else 'ld'
        print(cmd_name, executable, 'totally', len(self.objs), 'objects')
        cmd = builder.execCommand(
                cmd_name, sources=self.objs, dst=executable,
                target=self, **kwargs)
        if not cmd.success:
            builder.results.error(file, cmd.error)
            return

        # check artifact
        self.artifacts = cmd.artifacts
        builder.results.succeeded(self.artifacts['o'])
        cmd = builder.execCommand('file', sources=self.artifacts['o'])
        print('artifact:', cmd.output)

        # copy public headers to $BUILD
        for header_file in self.setting.public_headers:
            walk_path = header_file
            mapped_path = None
            while not mapped_path and walk_path:
                walk_path = os.path.dirname(walk_path)
                mapped_path = self.setting.install_dirs_map.get(walk_path)

            dst = os.path.join(self.request.rootBuild,
                               mapped_path if mapped_path else header_file)
            if walk_path:
                dst = os.path.join(dst, header_file[len(walk_path)+1:])
            else:
                dst = os.path.join(dst, header_file)
            dst = os.path.realpath(dst)
            dstfolder = os.path.dirname(dst)
            if not os.path.exists(dstfolder):
                os.makedirs(dstfolder)
            src = os.path.realpath(os.path.join(self.rootSource, header_file))
            logger.debug(f'- install header {src} -> {dst}')
            shutil.copyfile(src, dst)

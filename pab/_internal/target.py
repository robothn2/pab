# coding: utf-8

import os
import re
import shutil
from .arch import file_detect
from .target_context import TargetContext
from .target_utils import ItemList
from .log import logger


class Target:
    def __init__(self, tar, request, *deps, **kwargs):
        if isinstance(tar, tuple):
            init_setting = tar[0]
            self.dyn_setting = tar[1]
        else:
            init_setting = tar
            self.dyn_setting = None
        base = init_setting.get('source_base_dir')
        if not os.path.isabs(base):
            base = os.path.realpath(os.path.join(kwargs['root'], base))
            init_setting['source_base_dir'] = base

        self.request = request
        self.setting = TargetContext(**init_setting, **request.kwargs)
        self.uri = self.setting['uri']
        self.type = self.setting.get('type', 'staticLib')
        self.name = re.split(r'[./\\]', self.uri)[-1]
        self.rootSource = base
        self.objs = ItemList(name='objs')
        self.artifact = None

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
        logger.info('== Target: {}, type: {}, base: {}'.format(
                self.uri, self.type, self.rootSource))
        # logger.debug('Setting init: ' + str(self.setting))
        if self.dyn_setting:
            self.dyn_setting(self.setting, self.setting)
        # logger.debug('Setting apply: ' + str(self.setting))

        if not self.isArtifact():
            return

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
                        detected.cmd, sources=src, dst=dst,
                        build_title=file, target=self, **kwargs)

        for cmd in builder.waitPoolComplete():
            self.objs += cmd.dst
        if len(self.objs) == 0:
            return

        executable = os.path.join(
                self.request.rootBuild, 'lib',
                self.request.targetOS.getFullName(self.name, self.type))
        dstfolder = os.path.dirname(executable)
        if not os.path.exists(dstfolder):
            os.makedirs(dstfolder)

        cmd_name = 'ar' if self.isStaticLib() else 'ld'
        logger.info('{} {}'.format(cmd_name, executable))
        cmd = builder.execCommand(
                cmd_name, sources=self.objs, dst=executable,
                target=self, **kwargs)
        if not cmd.success:
            builder.results.error(file, cmd.error)
            return

        self.artifact = cmd.artifacts[0]
        builder.results.succeeded(self.artifact)
        cmd = builder.execCommand('file', sources=self.artifact)
        logger.info(cmd.output)

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

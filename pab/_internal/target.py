# coding: utf-8

import os
import re
import shutil
from .arch import file_detect
from .target_context import TargetContext
from .log import logger


class Target:
    def __init__(self, tar, request, *deps, **kwargs):
        base = tar[0].get('source_base_dir')
        if not os.path.isabs(base):
            base = os.path.realpath(os.path.join(kwargs['root'], base))
            tar[0]['source_base_dir'] = base
        self.dyn_setting = tar[1]
        self.request = request
        self.setting = TargetContext(**tar[0], **request.kwargs)
        self.uri = self.setting['uri']
        self.type = self.setting.get('type', 'staticLib')
        self.name = re.split(r'[./\\]', self.uri)[-1]
        self.std = self.setting.get('std', 'c++11')  # c99, c11, c++11, c++17
        self.rootSource = base
        self.artifact = None

        # todo: relative path rebase: sources, include_dirs, lib_dirs, libs

    def isSharedLib(self):
        return self.type == 'sharedLib'

    def isStaticLib(self):
        return self.type == 'staticLib'

    def isArtifact(self):
        return self.type in ('staticLib', 'sharedLib', 'executable')

    def getDepends(self):
        return self.setting.deps

    def filterCmd(self, cmd, kwargs):
        if cmd.name not in ('cc', 'cxx'):
            return

        if self.std.startswith('c++'):
            cmd.cxxflags += '-std=' + self.std
        else:
            cmd.ccflags += '-std=' + self.std

    def build(self, builder, **kwargs):
        logger.info('== Target: {}, type: {}, base: {}'.format(
                self.uri, self.type, self.rootSource))
        # logger.debug('Setting init: ' + str(self.setting))
        if self.dyn_setting:
            self.dyn_setting(self.setting, self.setting)
        logger.debug('Setting apply: ' + str(self.setting))

        if not self.isArtifact():
            return

        objs = []
        created_dst_folders = []
        for file in self.setting.get('sources', []):
            # cache for sub folders
            if not isinstance(file, str):
                logger.warning(f'invalid file: {file}')
                continue
            sub_folder = os.path.dirname(file)
            if sub_folder and sub_folder not in created_dst_folders:
                dst_folder = os.path.join(self.request.rootBuild, sub_folder)
                if not os.path.exists(dst_folder):
                    os.makedirs(dst_folder)
                created_dst_folders.append(sub_folder)

            src = os.path.realpath(os.path.join(self.rootSource, file))
            detected = file_detect(src)
            if not detected.cmd:
                builder.results.unhandled(file)
                continue
            result, reason = detected.match(self.request)
            if not result:
                builder.results.skipped(file, reason)
                continue

            dst = os.path.join(self.request.rootBuild, file) + '.o'
            result, output = builder.execCommand(
                        detected.cmd, sources=src, dst=dst,
                        target=self, **kwargs)
            if result:
                builder.results.succeeded(file)
                objs.append(dst)

                # result = builder.execCommand('file', sources=dst)
                # print(result[1])
            else:
                builder.results.error(file, output)

        if len(objs) == 0:
            return

        executable = os.path.join(
                self.request.rootBuild, 'lib',
                self.request.targetOS.getFullName(self.name, self.type))
        dstfolder = os.path.dirname(executable)
        if not os.path.exists(dstfolder):
            os.makedirs(dstfolder)

        result, reason = builder.execCommand(
            'ar' if self.isStaticLib() else 'ld',
            sources=objs, dst=executable, target=self, **kwargs)
        if not result:
            builder.results.error(file, reason)
            return

        self.artifact = executable
        builder.results.succeeded(self.artifact)
        result, output = builder.execCommand('file', sources=self.artifact)
        logger.info(output)

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

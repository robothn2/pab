# coding: utf-8

import os
import re
import shutil
from pab._internal.arch import file_detect
from pab._internal.file_scope import FileContext


class Target:
    def __init__(self, tar, request):
        self.dyn_setting = tar[1]
        self.request = request
        self.setting = FileContext(**tar[0], **request.kwargs)
        self.uri = self.setting['uri']
        self.type = self.setting.get('type', 'staticLib')
        self.name = re.split(r'[./\\]', self.uri)[-1]
        self.std = self.setting.get('std', 'c++11')  # c99, c11, c++11, c++17
        self.rootSource = tar[0].get('source_base_dir')
        print('Target:', self.name,
              'type:', self.type,
              'source:', self.rootSource)

        include_dirs = self.setting.get('include_dirs', [])
        exist_dirs = []
        for path in include_dirs:
            path = os.path.realpath(os.path.join(self.rootSource, path))
            if not os.path.exists(path):
                continue
            exist_dirs.append(path)

        self.cmdFilters = {
                'cc': [
                    ('define', self.setting.get('defines', [])),
                    ('includePath', exist_dirs),
                    self.setting.get('ccflags', []),
                ],
                'cxx': [
                    ('define', self.setting.get('defines', [])),
                    ('includePath', exist_dirs),
                    self.setting.get('cxxflags', []),
                ],
                'link': [
                    ('lib', self.setting.get('libs', [])),
                    ('libPath', self.setting.get('lib_dirs', [])),
                    self.setting.get('ldflags', []),
                ],
                }

        if self.std.startswith('c++'):
            self.cmdFilters['cxx'].append('-std=' + self.std)
        else:
            self.cmdFilters['cc'].append('-std=' + self.std)

    def get(self, key, defaultValue):
        return self.setting.get(key, defaultValue)

    def getSuffix(self, request):
        return request.targetOS.getExecutableSuffix(self.type)

    def isSharedLib(self):
        return self.type == 'sharedLib'

    def isStaticLib(self):
        return self.type == 'staticLib'

    def filterCmd(self, cmd_name):
        return self.cmdFilters.get(cmd_name, [])

    def apply(self, **kwargs):
        if self.dyn_setting:
            self.dyn_setting(self.setting, self.setting)

    def build(self, builder, **kwargs):
        print('== Target:', self.uri, ', args:', kwargs)
        self.apply()
        print('Target context:', self.setting)

        objs = []
        created_dst_folders = []
        for file in self.get('sources', []):
            # cache for sub folders
            if not isinstance(file, str):
                print('invalid file:', file)
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
            result = detected.match(self.request)
            if not result[0]:
                builder.results.skipped(file, result[1])
                continue

            dst = os.path.join(self.request.rootBuild, file) + '.o'
            result = builder.execCommand(
                        detected.cmd, request=self.request,
                        src=src, dst=dst, target=self,
                        **kwargs)
            if result[0]:
                builder.results.succeeded(file)
                objs.append(dst)

                # result = builder.execCommand('file', src=dst)
                # print(result[1])
            else:
                builder.results.error(file, result[1])

        if len(objs) == 0:
            return

        executable = os.path.join(
                self.request.rootBuild, 'lib',
                self.request.targetOS.getFullName(self.name, self.type))
        dstfolder = os.path.dirname(executable)
        if not os.path.exists(dstfolder):
            os.makedirs(dstfolder)

        result = builder.execCommand(
            'ar' if self.isStaticLib() else 'link',
            request=self.request, src=objs,
            dst=executable,
            target=self, **kwargs)
        if not result[0]:
            builder.results.error(file, result[1])
            return

        builder.results.succeeded(executable)
        result = builder.execCommand('file', src=executable)
        print(result[1])

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
            print('- install header', src, '->', dst)
            shutil.copyfile(src, dst)

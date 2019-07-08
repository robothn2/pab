# coding: utf-8

import os
from pab._internal.arch import arch_detect
from pab._internal.file_scope import FileContext

class Target:
    def __init__(self, tar, rootSource, request):
        self.dyn_setting = tar[1]
        self.request = request
        self.setting = FileContext(**tar[0], **request.kwargs)
        self.uri = self.setting['uri']
        self.type = self.setting.get('type', 'staticLib')
        self.name = os.path.basename(self.uri)
        self.std = self.setting.get('std', 'c++11')  # c99, c11, c++11, c++17
        self.rootSource = rootSource
        if not self.rootSource:
            self.rootSource = tar[0].get('source_base_dir')
        print('Target:', self.name,
              'type:', self.type,
              'source:', self.rootSource)

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

    def filterCmd(self, cmd_name):
        return self.cmdFilters.get(cmd_name, [])

    def apply(self, **kwargs):
        self.dyn_setting(self.setting, self.setting)

    def build(self, builder, targetsArgs):
        print('== Target:', self.uri)
        self.apply()

        objs = []
        created_dst_folders = []
        for file in self.get('sources', []):
            # cache for sub folders
            sub_folder = os.path.dirname(file)
            if sub_folder and sub_folder not in created_dst_folders:
                dst_folder = os.path.join(self.request.rootBuild, sub_folder)
                if not os.path.exists(dst_folder):
                    os.makedirs(dst_folder)
                created_dst_folders.append(sub_folder)

            src = os.path.realpath(os.path.join(self.rootSource, file))
            detected = arch_detect(src)
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
                        **targetsArgs)
            if result[0]:
                builder.results.succeeded(file)
                objs.append(dst)

                # result = builder.execCommand('file', src=dst)
                # print(result[1])
            else:
                builder.results.error(file, result[1])

        if len(objs) > 0:
            result = builder.execCommand(
                'link',
                request=self.request, src=objs,
                dst=os.path.join(self.request.rootBuild, self.name),
                target=self, **targetsArgs)
            if result[0]:
                builder.results.succeeded(self.name)

            # builder.execCommand('ldd', request=self.request, src=dst)

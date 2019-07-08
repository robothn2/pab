# coding: utf-8

import os
from ._internal.arch import arch_detect, os_detect
from ._internal.os import OS


class Request:
    def __init__(self, **kwargs):
        self.name = 'Request'
        self.kwargs = kwargs
        self.hostOS = OS()
        self.targetOS = OS(os_detect(kwargs['target_os']))
        self.target_os = self.targetOS.name
        self.arch = arch_detect(kwargs['target_cpu']).arch
        self.stl = kwargs.get('stl', 'gnu-libstdc++')
        self.rootBuild = os.path.realpath(kwargs['root_build'])
        if not os.path.exists(self.rootBuild):
            os.makedirs(self.rootBuild)

    def hasMember(self, memberName):
        return memberName in self.cfg

    def __getattr__(self, name):
        return self.kwargs.get(name)

    def getTmpFile(self):
        return

    def match(self, file_detect):
        if file_detect.arch and self.arch != file_detect.arch:
            return False
        if file_detect.target_os and self.target_os != file_detect.target_os:
            return False
        return True

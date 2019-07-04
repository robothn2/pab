# coding: utf-8

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
        self.rootBuild = kwargs['root_build']
        self.std = kwargs.get('std', 'c++11')
        self.stl = kwargs.get('stl', 'gnu-libstdc++')

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

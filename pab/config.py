# coding: utf-8
import os
from .archs import Archs
from .cpus import Cpus
from ._internal.os import OS


class Config:
    def __init__(self, args):
        self.name = 'Config'
        self.cfg = args
        self.archs = Archs()
        self._arch = self.archs.get(args['arch'])
        self.cpus = Cpus()
        self._cpu = self.archs.get(args['cpu'])
        self.hostOS = OS()
        self.targetOS = OS(**args)

    def hasMember(self, memberName):
        return memberName in self.cfg

    def get(self, memberName, defaultValue=None):
        return self.cfg.get(memberName, defaultValue)

    def getArch(self):
        return self._arch

    def getCpu(self):
        return self._cpu

    def getTmpFile(self):
        return

    def registerAll(self, toolchain):
        toolchain.registerCommandFilter(self, ['cc', 'cxx'],
                                        self._filterTargetOS)

    def match(self, file_detect):
        if file_detect.arch and self._arch != file_detect.arch:
            return False
        if file_detect.target_os and self.targetOS.name != file_detect.target_os:
            return False
        return True

    def _filterTargetOS(self, kwargs):
        o = self.targetOS.name
        if o == 'android':
            return ('define', '__ANDROID__')
        return []

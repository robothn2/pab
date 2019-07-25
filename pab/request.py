# coding: utf-8

import os
from ._internal.arch import Arch
from ._internal.os import OS
from ._internal.log import logger


class Request:
    def __init__(self, **kwargs):
        self.name = 'Request'
        self.kwargs = kwargs
        self.host_os = OS()
        self.target_os = OS(kwargs['target_os'])
        self.arch = Arch(kwargs['target_cpu'])
        self.kwargs['target_os_tags'] = self.target_os.tags
        self.kwargs['target_cpu_tags'] = self.arch.tags
        self.variables = {}
        self.options = {}
        self.rootBuild = os.path.realpath(kwargs['root_build'])
        if not os.path.exists(self.rootBuild):
            os.makedirs(self.rootBuild)
        logger.info('OSTags: {}'.format(self.target_os.tags))
        logger.info('ArchTags: {}'.format(self.arch.tags))

    def __getattr__(self, name):
        return self.kwargs.get(name)

    def match(self, file_detected):
        if file_detected.arch and file_detected.arch == self.arch.name:
            return False
        if file_detected.target_os and file_detected.target_os not in self.target_os.tags:
            return False
        return True

# coding: utf-8

import os
from ._internal.arch import arch_detect, os_detect, os_get_tags
from ._internal.os import OS
from ._internal.log import logger


class Request:
    def __init__(self, **kwargs):
        self.name = 'Request'
        self.kwargs = kwargs
        self.hostOS = OS()
        self.targetOS = OS(os_detect(kwargs['target_os']))
        self.target_os = self.targetOS.name
        arch = arch_detect(kwargs['target_cpu'])
        self.arch = arch[0]
        self.target_cpu = arch[1]
        self.kwargs['target_os_tags'] = os_get_tags(self.target_os)
        self.rootBuild = os.path.realpath(kwargs['root_build'])
        if not os.path.exists(self.rootBuild):
            os.makedirs(self.rootBuild)
        logger.info('Request: {} {}'.format(
                self.target_os, self.target_cpu))
        logger.info('OSTags: {}'.format(self.kwargs['target_os_tags']))

    def hasMember(self, memberName):
        return memberName in self.kwargs

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

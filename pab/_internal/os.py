#coding: utf-8

import os

class OS:
    def __init__(self, os_name = None):
        self.name = os_name if os_name else os.sys.platform
        self.suffix = {}
        if self.name == 'win' or self.name == 'win32':
            self.suffix['executable'] = '.exe'
            self.suffix['sharedLib'] = '.dll'
            self.suffix['staticLib'] = '.lib'
        elif self.name == 'linux':
            self.suffix['executable'] = ''
            self.suffix['sharedLib'] = '.so'
            self.suffix['staticLib'] = '.a'
        elif self.name == 'android':
            self.suffix['executable'] = ''
            self.suffix['sharedLib'] = '.so'
            self.suffix['staticLib'] = '.a'
        elif self.name == 'ios':
            self.suffix['executable'] = ''
            self.suffix['sharedLib'] = '.dylib'
            self.suffix['staticLib'] = '.a'
        elif self.name == 'mac' or self.name == 'darwin':
            self.suffix['executable'] = ''
            self.suffix['sharedLib'] = '.so'
            self.suffix['staticLib'] = '.a'

    def __str__(self):
        return 'OS:' + self.name

    def getExecutableSuffix(self, target_type='executable', **kwargs):
        return self.suffix[target_type]

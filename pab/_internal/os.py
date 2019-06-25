#coding: utf-8

import os

class OS:
    def __init__(self, **kwargs):
        self.name = kwargs.get('target_os', os.sys.platform)
        self.postfix = {}
        if self.name == 'win32':
            self.postfix['executable'] = '.exe'
            self.postfix['sharedLib'] = '.dll'
            self.postfix['staticLib'] = '.lib'
        elif self.name == 'linux':
            self.postfix['executable'] = ''
            self.postfix['sharedLib'] = '.so'
            self.postfix['staticLib'] = '.a'
        elif self.name == 'android':
            self.postfix['executable'] = ''
            self.postfix['sharedLib'] = '.so'
            self.postfix['staticLib'] = '.a'
        elif self.name == 'ios':
            self.postfix['executable'] = ''
            self.postfix['sharedLib'] = '.dylib'
            self.postfix['staticLib'] = '.a'
        elif self.name == 'darwin':
            self.postfix['executable'] = ''
            self.postfix['sharedLib'] = '.so'
            self.postfix['staticLib'] = '.a'

    def __str__(self):
        return 'OS:' + self.name
    
    def getTargetPostfix(self, target_type, **kwargs):
        return self.postfix[target_type]

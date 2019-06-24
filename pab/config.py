#coding: utf-8
import os
from .archs import Archs

class Config:
    def __init__(self, args):
        self.cfg = args
        self.archs = Archs()
        self.arch = self.archs.get(self.cfg['arch'])

    def hasMember(self, memberName):
        return memberName in self.cfg
    
    def get(self, memberName, defaultValue = None):
        return self.cfg.get(memberName, defaultValue)
    
    def registerAll(self, toolchain):
        toolchain.registerSourceFileFilter(self, self._filterSourceFile)
        
    def _filterSourceFile(self, args):
        # todo: update args['dst']

        src = args['src']
        parent, name = os.path.split(src)
        parent_dir_name = os.path.dirname(parent)
        arch = self.archs.get(parent_dir_name)
        if arch and arch != self.arch:
            return False, 'mismatched arch subfolder'
            
        _, ext = os.path.splitext(src)
        return True, None
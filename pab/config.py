#coding: utf-8
import os
from .archs import Archs
from .cpus import Cpus
from ._internal.os import OS

class Config:
    def __init__(self, args):
        self.cfg = args
        self.archs = Archs()
        self._arch = self.archs.get(args['arch'])
        self.cpus = Cpus()
        self._cpu = self.archs.get(args['cpu'])
        self.hostOS = OS()
        self.targetOS = OS(**args)

    def hasMember(self, memberName):
        return memberName in self.cfg
    
    def get(self, memberName, defaultValue = None):
        return self.cfg.get(memberName, defaultValue)
    
    def getArch(self):
        return self._arch
    def getCpu(self):
        return self._cpu
    def getTmpFile(self):
        return 
    
    def registerAll(self, toolchain):
        toolchain.registerSourceFileFilter(self, self._filterSourceFile)
        
    def _filterSourceFile(self, args):
        # todo: update args['dst']

        src = args['src']
        p, n = os.path.split(src)
        pname = os.path.basename(p)
        arch = self.archs.get(pname)
        if arch and arch != self._arch:
            return False, 'mismatched arch subfolder, expected {}, parsed {}'.format(self._arch, arch)
            
        # todo: check file name
        #_, ext = os.path.splitext(src)
        return True, None
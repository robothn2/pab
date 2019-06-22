#coding: utf-8

class Config:
    def __init__(self, args):
        self.cfg = args

    def hasMember(self, memberName):
        return memberName in self.cfg
    
    def get(self, memberName, defaultValue = None):
        return self.cfg.get(memberName, defaultValue)
    
    def registerAll(self, toolchain):
        toolchain.registerSourceFileFilter(self, self._filter)
        
    def _filterPreprocessSourceFile(self, args):
        # todo: update args['dst']
        # todo: return False to reject file by config
        return True
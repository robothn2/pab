#coding: utf-8

class Config:
    def __init__(self, args):
        self.cfg = args

    def hasMember(self, memberName):
        return memberName in self.cfg
    
    def get(self, memberName, defaultValue = None):
        return self.cfg.get(memberName, defaultValue)
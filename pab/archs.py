#coding: utf-8

class Archs:
    def __init__(self):
        self.hand_write_archs = [
                ('arm64', 'aarch64'),
                'arm',
                'x86',
                ('x86_64', 'x64'),
                ]
        
        self.archs = []
        self.archsMap = {}
        for archs in self.hand_write_archs:
            if isinstance(archs, str):
                self.archs.append(archs)
                self.archsMap[archs] = archs
            elif isinstance(archs, tuple):
                self.archs.extend(archs)
                for arch in archs:
                    self.archsMap[arch] = archs[0]

    def get(self, memberName, defaultValue = None):
        return self.archsMap.get(memberName, defaultValue)
    
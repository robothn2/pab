#coding: utf-8

class FileDispatcher:
    def __init__(self):
        self._mapper = {
                '.c': 'cc',     # c
                '.cc': 'cxx',   # c++
                '.cpp': 'cxx',
                '.cxx': 'cxx',
                '.asm': 'asm',  # assemble
                '.S': 'asm',
                '.rc': 'rc',    # VS resource
                '.m': 'cxx',    # xcode
                '.mm': 'cxx',
                }
        
    def getCat(self, ext):
        return self._mapper.get(ext, None)
    
    def items(self):
        return self._mapper.items()
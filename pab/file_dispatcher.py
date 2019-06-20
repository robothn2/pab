#coding: utf-8

class FileDispatcher:
    def __init__(self):
        ext_handlers = {
            'cc': ['.c'],
            'cxx': ['.cpp', '.cc', '.cxx',
                    '.m', '.mm' # xcode
                    ],
            'as': ['.asm', '.S'],
            'rc': ['.rc'],  # VS resource
        }
        self._mapper = {} # map file extension to Command name
        for cmd,exts in ext_handlers.items():
            for ext in exts:
                self._mapper[ext] = cmd
        
    def getCat(self, ext):
        return self._mapper.get(ext, None)
    
    def items(self):
        return self._mapper.items()
# coding: utf-8


class BinUtils:
    def __init__(self, **kwargs):
        self.name = 'BinUtils'
        self.kwargs = kwargs
        self.suffix = kwargs.get('suffix', '')
        self._cmds = {
                'file': ('file' + self.suffix, ),  # C:\msys64\usr\bin
                }

    def asCmdProvider(self, kwargs):
        return self._cmds

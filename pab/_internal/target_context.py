# coding: utf-8
from .target_utils import ItemList
from .header_file import HeaderFileReader

class TargetContext(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__({})
        self['options'] = {}
        vars_normal = ['defines', 'public_include_dirs', 'include_dirs',
                       'headers', 'ccflags', 'cxxflags', 'ldflags',
                       'lib_dirs', 'libs', 'deps',
                       ]
        vars_pattern = ['public_headers', 'sources']  # support pattern add/sub
        for v in vars_normal:
            self[v] = ItemList(name=v)
        for v in vars_pattern:
            self[v] = ItemList(name=v, base=kwargs['source_base_dir'])

        for k, v in kwargs.items():
            if isinstance(v, (str, dict)):
                self[k] = v
            elif isinstance(v, (list, tuple)):
                if k in self:
                    self[k] += v
                else:
                    self[k] = ItemList(v)
            else:
                print('* ignore key-value', k, v)

        self.group_vars = list(args)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        return None

    def getVar(self, name):
        for v in self.group_vars:
            if name in v:
                return v[name]
        return None

    def getOption(self, name):
        return self['options'].get(name, False)

    def parseFile(self, filepath, pattern):
        reader = HeaderFileReader(filepath)
        return reader.findall(pattern)

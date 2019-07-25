# coding: utf-8
from .target_utils import ItemList
from .header_file import HeaderFileReader


class TargetContext(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__({})
        self['options'] = {}
        vars_normal = ['defines', 'public_defines',
                       'include_dirs', 'public_include_dirs',
                       'lib_dirs', 'public_lib_dirs',
                       'libs', 'public_libs',
                       'headers', 'sysroots',
                       'ccflags', 'cxxflags', 'arflags', 'ldflags',
                       'deps', 'configs',
                       ]
        vars_pattern = ['public_headers', 'sources']  # support pattern add/sub
        for v in vars_normal:
            self[v] = ItemList(name=v)
        for v in vars_pattern:
            self[v] = ItemList(name=v, base=kwargs['source_base_dir'])

        for k, v in kwargs.items():
            if k in self:
                self[k] += v
            else:
                self[k] = v

        self.group_vars = [{}]
        self.group_vars.extend(args)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        return None

    def getVar(self, key):
        for v in self.group_vars:
            if key in v:
                return v[key]
        return None

    def setVar(self, key, value):
        self.group_vars[0][key] = value

    def enabled(self, key):
        return self['options'].get(key, False)

    def enable(self, key, value=True):
        self['options'][key] = value

    def parseFile(self, filepath, pattern):
        reader = HeaderFileReader(filepath)
        return reader.findall(pattern)


def parse_target_file(filepath):
    global_scope = {}
    local_scope = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    try:
        exec(content, global_scope, local_scope)
    except SyntaxError as e:
        print('* Exception occupied in', filepath, e)
        return []
    return local_scope.get('export_libs', [])

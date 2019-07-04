# coding: utf-8


def _file_read(filename, mode='rU'):
    with open(filename, mode=mode) as f:
        # codecs.open() has different behavior than open() on python 2.6 so use
        # open() and decode manually.
        s = f.read()
        try:
            return s.decode('utf-8')
        # AttributeError is for Py3 compatibility
        except (UnicodeDecodeError, AttributeError):
            return s


class ItemList(list):
    def __init__(self, *args):
        list.__init__(self, args)

    def __iadd__(self, other):
        if isinstance(other, list):
            self.extend(other)
        else:
            self.append(other)
        return self

    def __isub__(self, other):
        if isinstance(other, list):
            for item in other:
                if item in self:
                    self.remove(item)
        else:
            if other in self:
                self.remove(other)
        return self


class FileScope(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(kwargs)
        self.defines = ItemList()
        self.include_dirs = ItemList()
        self.sources = ItemList()
        self.group_vars = args

    def __getattr__(self, name):
        for v in self.group_vars:
            if name in v:
                return v[name]
        return None


def parse_build_file(filepath):
    global_scope = {}
    local_scope = FileScope()
    content = _file_read(filepath)
    try:
        exec(content, global_scope, local_scope)
    except SyntaxError as e:
        print('* Exception occupied in', filepath, e)
        return []
    return local_scope.get('export_libs', [])


if __name__ == '__main__':
    sources = ItemList('c1.c', 'c2.c', 'c3.c')
    print(sources)
    sources += ['c4.c', 'c5.c']
    print(sources)
    sources += 'c6.c'
    print(sources)
    sources -= ['c2.c', 'c4.c']
    print(sources)
    sources -= ['c2.c', 'c4.c']
    print(sources)
    sources -= 'c5.c'
    print(sources)
    sources -= 'c5.c'
    print(sources)

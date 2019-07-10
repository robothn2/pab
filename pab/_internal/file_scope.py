# coding: utf-8
import glob
import os
import re


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

def _str_find_first_of(s, seps):
    for sep in seps:
        if s.find(sep):
            return True
    return False

class ItemList(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, args)
        self.base = kwargs.get('base')
        if self.base:
            self.base = os.path.realpath(self.base)
        self.name = kwargs.get('name')

    def __iadd__(self, other):
        if not other:
            return self
        # print('-', self.name, '+=', other)
        if isinstance(other, list):
            for item in other:
                self._add_str(item)
        else:
            self._add_str(other)
        return self

    def _add_str(self, s):
        if not s or not isinstance(s, str):
            return

        if self.base:
            # support wildcard += if self.base available
            if s[0] == '^':
                # regex match under folder: self.base
                return

            if _str_find_first_of(s, '*?['):
                # wildcard match under folder: self.base
                for f in glob.iglob(self.base + os.sep + s):
                    path = os.path.relpath(f, self.base).replace('\\', '/')
                    self._append_str(path)
                return
        self._append_str(s)

    def _append_str(self, s):
        if s not in self:
            self.append(s)

    def __isub__(self, other):
        if not other:
            return self
        print('-', self.name, '-=', other)
        if isinstance(other, list):
            for item in other:
                self._sub_str(item)
        else:
            self._sub_str(other)
        return self

    def _sub_str(self, s):
        if not s or not isinstance(s, str):
            return
        if s[0] == '^':
            # regex match under folder: self.base
            items_to_remove = [x for x in self if re.match(s, x, re.RegexFlag.ASCII)]
            for item in items_to_remove:
                self.remove(item)
            return
        self._remove_str(s)

    def _remove_str(self, s):
        if s in self:
            self.remove(s)


class FileContext(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__({})
        self['options'] = {}
        vars_normal = ['defines', 'public_include_dirs', 'include_dirs',
                       'headers', 'ccflags', 'cxxflags', 'ldflags',
                       'lib_dirs', 'libs', 'deps',
                       ]
        vars_regex = ['public_headers', 'sources']  # support regex add / sub
        for v in vars_normal:
            self[v] = ItemList(name=v)
        for v in vars_regex:
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
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.read()
            result = re.findall(pattern, lines,
                                re.RegexFlag.MULTILINE + re.RegexFlag.ASCII)
            if result:
                return {entry[0]: entry[1].strip('"') for entry in result}


def parse_build_file(filepath):
    global_scope = {}
    local_scope = {}
    content = _file_read(filepath)
    try:
        exec(content, global_scope, local_scope)
    except SyntaxError as e:
        print('* Exception occupied in', filepath, e)
        return []
    return local_scope.get('export_libs', [])


if __name__ == '__main__':
    sources = ItemList('c1.c', 'c2.c', 'c3.c',
                       name='test', base=r'D:\lib\base')
    print(sources)

    # basic test
    sources -= ''
    sources -= None
    sources += ['c4.c', 'c5.c']
    print(sources)
    sources += 'c6.c'
    print(sources)
    sources -= ['c2.c', 'c4.c']
    print(sources)
    sources -= ['c2.c', 'c4.c']
    print(sources)
    sources -= 'c6.c'
    print(sources)
    sources -= 'c6.c'
    print(sources)
    sources -= ['c1.c', 'c3.c', 'c5.c']

    # wildcard +=
    sources += 'files/file_path.*'
    print(sources)
    sources -= 'files/file_path.cc'
    print(sources)
    sources += 'files/file_path*'
    print(sources)
    # regex -=
    sources -= [r'^files/file_path.*\.cc', 'files/file_path_watcher.h']
    print(sources)

    context = FileContext(source_base_dir='d:/lib/ogre')
    versions = context.parseFile(
            'd:/lib/ogre/OgreMain/include/OgrePrerequisites.h',
            r'^\s*#define\s+(OGRE_VERSION_\S+)\s+(.+)$')
    print(versions)

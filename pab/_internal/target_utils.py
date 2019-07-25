# coding: utf-8
import glob
import os
import re


def _str_find_first_of(s, seps):
    for sep in seps:
        if s.find(sep) >= 0:
            return True
    return False


'''
A list derived class, supports:
    li = ItemList('c1.c', 'c2.c', 'c3.c', base='~/src/myproj')
    li -= ['c3.c', 'c4.c']  # -= list
    li -= 'str'             # -= str
    li -= r'^c[12]\.c'      # -= regex pattern
    li += '*.c'             # += wildcard pattern, self.base must be set first
'''
class ItemList(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, args)
        self.base = kwargs.get('base')
        if self.base:
            self.base = os.path.realpath(self.base)
        self.name = kwargs.get('name')
        self.unique = kwargs.get('unique', True)

    def __iadd__(self, other):
        if not other:
            return self
        # print('-', self.name, '+=', other)
        if isinstance(other, list):
            for item in other:
                self.addPattern(item)
        else:
            self.addPattern(other)
        return self

    def addPattern(self, s):
        if self.base:
            # support wildcard += if self.base available
            if s[0] == '^':
                # regex match under folder: self.base
                return

            if _str_find_first_of(s, '*?['):
                # wildcard match under folder: self.base
                for f in glob.iglob(self.base + os.sep + s, recursive=True):
                    path = os.path.relpath(f, self.base).replace('\\', '/')
                    self._append_str(path)
                return

        self._append_str(s)

    def _append_str(self, s):
        if not self.unique or s not in self:
            self.append(s)

    def __isub__(self, other):
        if not other:
            return self
        # print('-', self.name, '-=', other)
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

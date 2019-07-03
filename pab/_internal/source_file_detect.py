# coding: utf-8

import os


_ext_filters = {
    'cc': ['.c'],
    'cxx': ['.cpp', '.cc', '.cxx',
            '.m', '.mm'  # xcode
            ],
    'as': ['.asm', '.S'],
    'rc': ['.rc'],   # VS resource
}
_ext_map = {ext: cmd
            for cmd in _ext_filters.keys()
            for ext in _ext_filters[cmd]}  # map file extension to Command name

_ostag_filters = [
    ['linux', ],
    ['android', ],
    ['win', 'win32', 'windows', 'winnt'],
    ['mac', 'macos', 'macosx', '.m', '.mm'],
    ['ios', 'iphone', 'iphoneos', 'iphonesimulator'],
]
_os_map = {tag: osname[0]
           for osname in _ostag_filters
           for tag in osname}  # map file tag to OS name

_archtag_filters = [
    ['arm64', 'aarch64', 'arm64'],
    ['arm', 'armv5te', 'armv7a', 'armeabi', 'armeabi-v7a'],
    ['x86', 'x64', 'i386', 'i686'],
    ['mips', 'mipsel', 'mipseb'],
    ['ppc'],
    ['sh4', 'sh'],
    ['sparc'],
]
_arch_map = {tag: arch[0]
             for arch in _archtag_filters
             for tag in arch}  # map file tag to OS name

_insttag_filters = [
    ['neon', 'vfp'],
    ['arm', 'armv5te', 'armv7a', 'armeabi', 'armeabi-v7a'],
    ['x86', 'x64', 'i386', 'i686'],
    ['mips', 'mipsel', 'mipseb'],
    ['ppc'],
    ['sh4', 'sh'],
    ['sparc'],
]
_instruction_map = {tag: inst[0]
             for inst in _insttag_filters
             for tag in inst}  # map file tag to OS name


class SourceFileDetect:
    def __init__(self, filepath):
        self.tags = []
        dirpath, filename = os.path.split(os.path.realpath(filepath))
        if dirpath:
            dirname = os.path.basename(dirpath)
            self.tags.append(dirname)

        name, ext = os.path.splitext(filename)
        self.cmd = _ext_map.get(ext, None)
        self.tags += name.lower().split('_')

        self.target_os = None
        self.arch = None
        self.target_cpu = None
        self.instruction = None
        for tag in self.tags:
            if not self.target_os:
                self.target_os = _os_map.get(tag, None)
            if not self.instruction:
                self.instruction = _instruction_map.get(tag, None)
            if not self.arch:
                self.arch = _arch_map.get(tag, None)

    def match(self, *args):
        for cfg in args:
            if cfg.match(self):
                return True
        return False


def source_file_detect(filepath):
    return SourceFileDetect(filepath)


if __name__ == '__main__':
    d = source_file_detect('files/file_path_watcher_win.cc')
    print(d.cmd, d.target_os, d.arch, d.target_cpu, d.tags)

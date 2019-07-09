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
    ['mac', 'macos', 'macosx', 'darwin', '.m', '.mm'],
    ['ios', 'iphone', 'iphoneos', 'iphonesimulator'],
]
_os_map = {tag: osname[0]
           for osname in _ostag_filters
           for tag in osname}  # map file tag to OS name

_archtag_filters = [
    ['arm64', 'aarch64'],
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

_opt_tag_filters = [
    ['asm', 'x86asm', 'inline-asm', ],
    ['neon', 'vfp', 'armv5te', 'armv6', 'armv6t2', ],
    ['fast-unaligned', 'vsx', 'msa', 'xop'],
    ['fma3', 'fma4', 'aesni', ],
    ['mmx', 'mmxext', 'sse', 'sse2', 'sse3', 'sse4', 'sse42', 'avx', 'avx2', 'avx512'],
    ['altivec', 'amd3dnow', 'amd3dnowext', 'power8'],
    ['mipsdsp', 'mipsdspr2', 'mipsfpu', ],
]
_optimize_map = {tag: opt[0]
             for opt in _opt_tag_filters
             for tag in opt}  # map file tag to OS name


class ArchDetect:
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
        self.optimize = None
        for tag in self.tags:
            if not self.target_os:
                self.target_os = _os_map.get(tag, None)
            #if not self.optimize:
            #    self.optimize = _optimize_map.get(tag, None)
            if not self.arch:
                self.arch = _arch_map.get(tag, None)

    def __str__(self):
        return '{} -> {}, {}, {}, {}'.format(self.tags,
                self.cmd, self.target_os, self.arch, self.target_cpu)

    def match(self, *args):
        for cfg in args:
            if hasattr(cfg, 'match') and cfg.match(self):
                return (True, None)
        return (False, 'OS(%s), CPU(%s) not match' % (self.target_os, self.target_cpu))

def file_detect(filepath):
    return ArchDetect(filepath)

def arch_detect(arch_cpu):
    arch_cpu = arch_cpu.replace('-', '')
    if arch_cpu.startswith('arm'):
        if arch_cpu in ['arm64', 'aarch64']:
            return ('arm64', 'arm64')
        elif arch_cpu.startswith('armv'):
            return ('arm', arch_cpu)
    elif arch_cpu.startswith('x'):
        if arch_cpu in ['x86_64', 'x64']:
            return ('x86_64', 'x86_64')
        if arch_cpu in ['x86', 'x86_32']:
            return ('x86', 'x86')
    return None

def os_detect(osname):
    return ArchDetect(osname).target_os


if __name__ == '__main__':
    d = arch_detect('files/file_path_watcher_win.cc')
    print(d.cmd, d.target_os, d.arch, d.target_cpu, d.tags)

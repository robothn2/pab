# coding: utf-8
import re


def arch_detect(arch):
    if re.match(r'^(?:arm-?v8-?).*', arch) or arch in ('aarch64', 'arm64'):
        arch='aarch64'
    elif re.match(r'^(?:arm|iPad|iPhone).*', arch):
        arch='arm'
    elif re.match(r'^i[3-6]86.*', arch) or arch in ('x86', 'x86_32', 'i86pc', 'BePC'):
        arch='x86'
    elif re.match(r'^(?:i[3-6]|x)86.*', arch) or arch in ('x64', 'x86_64', 'amd64'):
        arch='x64'
    elif re.match(r'^(?:mips|IP).*', arch):
        arch='mips'
        '''
        if arch.endswith('el'):
            add_cppflags -EL
            add_ldflags -EL
        elif arch.endswith('eb'):
            add_cppflags -EB
            add_ldflags -EB
        '''
    elif re.match(r'^(?:parisc|hppa).*', arch):
        arch='parisc'
    elif arch == 'Power Macintosh' or re.match(r'^(?:ppc|powerpc).*', arch):
        arch='ppc'
    elif re.match(r'^s390x?', arch):
        arch='s390'
    elif re.match(r'^sh4?', arch):
        arch='sh4'
    elif re.match(r'^(?:sun4|sparc).*', arch):
        arch='sparc'
    elif re.match(r'^tile-?gx', arch):
        arch='tilegx'
    else:
        return None
    return arch

_arch_tags = {
    'aarch64': ('arm', 'arm64', 'aarch64', '64bit'),
    'arm': ('arm', 'arm32', 'armeabi', '32bit'),
    'x86': ('x86', 'x86_32', 'i386', 'i686', 'intel', '32bit'),
    'x64': ('x86', 'x86_64', 'x64', 'amd64', 'intel', '64bit'),
    'mips': ('mips', 'mipsel', 'mipseb'),
    'ppc': ('ppc', ),
    'sh4': ('sh4', 'sh'),
    'sparc': ('sparc', 'sun'),
    'tilegx': ('tilegx',),
    'parisc': ('parisc', 'hppa'),
    's390': ('s390',),
}

class Arch:
    def __init__(self, handy_arch):
        handy_arch = handy_arch.lower() if isinstance(handy_arch, str) else ''
        self.arch_org = handy_arch.replace('-', '')
        self.name = arch_detect(self.arch_org)
        assert(self.name)
        self.tags = _arch_tags.get(self.name, ())


if __name__ == '__main__':
    assert(arch_detect('iPhone10') == 'arm')
    assert(arch_detect('armv5te') == 'arm')
    assert(arch_detect('armv8a') == 'aarch64')
    assert(arch_detect('arm-v8a') == 'aarch64')
    assert(arch_detect('i686') == 'x86')
    assert(arch_detect('x86') == 'x86')
    assert(arch_detect('x86_64') == 'x64')
    assert(arch_detect('x64') == 'x64')
    assert(arch_detect('mipsel') == 'mips')

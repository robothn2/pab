#coding: utf-8
import os


_filetag_filters = [
    ['linux', ],
    ['android', ],
    ['win', 'win32', 'windows', 'winnt'],
    ['mac', 'macos', 'macosx', 'darwin'],
    ['ios', 'iphone', 'iphoneos', 'iphonesimulator'],
]
_os_normalize = {tag: osname[0]
           for osname in _filetag_filters
           for tag in osname}  # map file tag to OS name

_os_tags = {
    'win': ['win', 'windows', 'win32', 'winnt', 'pc'],
    'mac': ['mac', 'apple', 'macos', 'macosx', 'darwin', 'posix'],
    'ios': ['ios', 'apple', 'iphone', 'ipad'],
    'linux': ['linux', 'posix', ],
    'android': ['android', 'linux', 'posix', ],
}

def os_get_tags(osname):
    return _os_tags.get(osname, ())

class OS:
    def __init__(self, os_name = None):
        os_name = os_name.lower() if isinstance(os_name, str) else ''
        self.name = _os_normalize[os_name if os_name else os.sys.platform]
        self.tags = os_get_tags(self.name)
        self.suffix = {}
        if 'win' in self.tags:
            self.suffix['executable'] = '.exe'
            self.suffix['sharedLib'] = '.dll'
            self.suffix['staticLib'] = '.lib'
        elif 'linux' in self.tags:
            self.suffix['executable'] = ''
            self.suffix['sharedLib'] = '.so'
            self.suffix['staticLib'] = '.a'
        elif 'android' in self.tags:
            self.suffix['executable'] = ''
            self.suffix['sharedLib'] = '.so'
            self.suffix['staticLib'] = '.a'
        elif 'ios' in self.tags:
            self.suffix['executable'] = ''
            self.suffix['sharedLib'] = '.dylib'
            self.suffix['staticLib'] = '.a'
        elif 'mac' in self.tags:
            self.suffix['executable'] = ''
            self.suffix['sharedLib'] = '.so'
            self.suffix['staticLib'] = '.a'
        else:
            raise Exception('Unsupported OS', os_name, self.name)
        print(self.suffix)

    def __str__(self):
        return 'OS:' + self.name

    def getExecutableSuffix(self, target_type='executable', **kwargs):
        return self.suffix[target_type]

    def getFullName(self, base_name, target_type='executable'):
        prefix = '' if 'win' in self.tags or target_type == 'executable' else 'lib'
        if prefix and base_name.startswith('lib'):
            prefix = ''
        return prefix + base_name + self.suffix[target_type]

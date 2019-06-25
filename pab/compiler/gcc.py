#coding: utf-8

import os

class GCC:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.prefix = kwargs.get('prefix', '')
        self.postfix = kwargs.get('postfix', '')
        self.root = os.path.dirname(self.prefix)
        if not os.path.exists(self.root):
            raise Exception(r'gcc dir not exist')
        
    def registerAll(self, toolchain):
        toolchain.registerCommand(self, 'cc', self.prefix + 'gcc' + self.postfix)
        toolchain.registerCommand(self, 'cxx', self.prefix + 'g++' + self.postfix)
        #toolchain.registerCommand(self, 'as', self.prefix + 'as' + self.postfix)
        toolchain.registerCommand(self, 'ar', self.prefix + 'ar' + self.postfix)
        toolchain.registerCommand(self, 'link', self.prefix + 'ld' + self.postfix)

        toolchain.registerCommandFilter(self, ['cc', 'cxx'], [
                    ('args', '-c', '-Wall'),
                    self._filterSrcListAndDst,
                ])
        # i686-linux-android-ar.exe -rcs d:\1.a d:\lib\ffmpeg\build\libavutil\obj\adler32.c.o d:\lib\ffmpeg\build\libavutil\obj\aes.c.o d:\lib\ffmpeg\build\libavutil\obj\aes_ctr.c.o
        # i686-linux-android-nm.exe -s d:\1.a
        # i686-linux-android-ranlib.exe d:\1.a # create archive index, improve performance for large archive
        toolchain.registerCommandFilter(self, 'ar', [
                    ('args', '-rcs'),
                    self._filterSrcListAndDst,
                ])
        toolchain.registerCommandFilter(self, 'link', [
                    ('compositor', 'lib', 'c'),     # link with libc.a
                    #('compositor', 'lib', 'stdc++'), # link with libstdc++.a
                    self._filterSrcListAndDst,
                ])

        toolchain.registerArgCompositor(self, 'sysroot', lambda path, args: f'--sysroot={path}')
        toolchain.registerArgCompositor(self, 'includePath', lambda path, args: ['-I', path])
        toolchain.registerArgCompositor(self, 'libPath', lambda path, args: ['-L', path])
        toolchain.registerArgCompositor(self, 'lib', lambda path, args: f'-l{path}')

    def _filterSrcListAndDst(self, args):
        ret = []
        config = args['config']
        cmd = args['cmd']

        if 'dst' in args:
            dst = args['dst']
            if cmd == 'ar':
                dst += config.targetOS.getTargetPostfix('staticLib')
                ret.append(dst)
            else:
                if cmd == 'link':
                    dst += config.targetOS.getTargetPostfix(args.get('targetType'))
                    ret += ['-o', dst]
                else:
                    ret += ['-o', dst]
            args['dst'] = dst
                
                
        if 'src' in args:
            src = args['src']
            if isinstance(src, str):
                ret.append(src)
            elif isinstance(src, list):
                tmp_file = os.path.join(os.path.dirname(src[0]), 'src_list.txt')
                with open(tmp_file, 'w', encoding='utf-8') as f:
                    for o in src:
                        o = os.path.realpath(o)
                        o = o.replace('\\', '/')
                        f.write(o)
                        f.write(' ')
                    f.close()
                ret.append('@' + tmp_file)
        return ret

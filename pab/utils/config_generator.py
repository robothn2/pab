#coding: utf-8

import os
from pab._internal.command import Command

class ConfigGenerator:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.headers = {}
        self.options = {}
        self.toolchain = None
        self.config = None
        self.tmpFile = os.path.realpath('pabtemp.c')
        self.tmpFileOut = self.tmpFile + '.o'

    def registerAll(self, toolchain):
        pass

    def checkAll(self, toolchain, config):
        self.toolchain = toolchain
        self.config = config

        self.check_cc('const_nan', 'math.h', 'struct { double d; } static const bar[] = { { NAN } }')
        self.check_cc('intrinsics_neon', 'arm_neon.h', 'int16x8_t test = vdupq_n_s16(0)')
        self.check_cc('pragma_deprecated', '', r'_Pragma("GCC diagnostic ignored \"-Wdeprecated-declarations\"")')
        self.check_cc('pthreads', 'pthread.h', 'static pthread_mutex_t atomic_lock = PTHREAD_MUTEX_INITIALIZER')
        self.check_cc('altivec', 'altivec.h', 'vector signed int v1 = (vector signed int) { 0 }')
        self.check_cc('vsx', 'altivec.h', 'int v[4] = { 0 }')
        print(self.options)

        self.check_header(['windows.h', 'd3d11.h', 'dxgidebug.h', 'dxva.h'])
        self.check_header('dxva2api.h', ccflags='-D_WIN32_WINNT=0x0600')
        self.check_header(['direct.h', 'dirent.h', 'dlfcn.h', 'io.h',
                           'malloc.h', 'unistd.h', 'asm/types.h', 'poll.h',
                           'sys/mman.h', 'sys/param.h', 'sys/resource.h',
                           'sys/select.h', 'sys/time.h', 'sys/un.h',
                           'sys/videoio.h'])
        self.check_header(['net/udplite.h', 'mach/mach_time.h'])
        self.check_header(['termios.h', 'jni.h'])
        self.check_header('valgrind/valgrind.h')
        self.check_header('libcrystalhd/libcrystalhd_if.h')
        self.check_header('VideoDecodeAcceleration/VDADecoder.h')
        self.check_header('X11/extensions/XvMClib.h')
        self.check_header(['opencv2/core/core_c.h'])
        self.check_header(['linux/fb.h', 'linux/videodev2.h'])
        self.check_header(['dev/bktr/ioctl_meteor.h',
                           'dev/bktr/ioctl_bt848.h',
                           'machine/ioctl_meteor.h',
                           'machine/ioctl_bt848.h',
                           'dev/video/meteor/ioctl_meteor.h',
                           'dev/video/bktr/ioctl_bt848.h',
                           'dev/ic/bt8xx.h',
                           'soundcard.h'])
        print(self.headers)

    def check_header(self, headers, **kwargs):
        if isinstance(headers, str):
            self.headers[headers] = self.test_cpp(headers,
                        f'#include <{headers}> \nint x;', **kwargs)
        elif isinstance(headers, list):
            for header in headers:
                self.headers[header] = self.test_cpp(header,
                        f'#include <{header}> \nint x;', **kwargs)

    def test_cpp(self, header_name, content=None, **kwargs):
        #print(content)
        with open(self.tmpFile, 'w', encoding='utf-8') as f:
            f.write(content)
            f.close
        return True if self.toolchain.doCommand('cc',
                                 config=self.config,
                                 src=self.tmpFile,
                                 dst=self.tmpFileOut) else False

    def check_cc(self, option_name, headers, code):
        self.options[option_name] = self.test_code('cc', headers, code)

    def test_code(self, cmd, headers, code):
        content = ''
        if isinstance(headers, str):
            content += self.print_include(headers)
        else:
            for header in headers:
                content += self.print_include(header)
        content += 'int main(void) {' + code + '; return 0; }'
        return self.test_cpp(cmd, content)

    def print_include(self, header):
        if not header:
            return ''
        return f'#include "{header}"\n' if header.endswith('.h') else f'#include <{header}>\n'

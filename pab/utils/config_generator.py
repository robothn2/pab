#coding: utf-8

import os
from pab._internal.command import Command

class ConfigGenerator:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.headers = {}
        self.toolchain = None
        self.config = None
        self.tmpFile = ''
        self.tmpFileOut = ''
        
    def registerAll(self, toolchain):
        pass
    
    def checkAll(self, toolchain, config):
        self.toolchain = toolchain
        self.config = config
        self._check_header('d3d11.h')
        self._check_header('direct.h')
        self._check_header('dirent.h')
        self._check_header('dlfcn.h')
        self._check_header('dxgidebug.h')
        self._check_header('dxva.h')
        self._check_header('dxva2api.h', cflags='-D_WIN32_WINNT=0x0600')
        self._check_header('io.h')
        self._check_header('libcrystalhd/libcrystalhd_if.h')
        self._check_header('mach/mach_time.h')
        self._check_header('malloc.h')
        self._check_header('net/udplite.h')
        self._check_header('poll.h')
        self._check_header('sys/mman.h')
        self._check_header('sys/param.h')
        self._check_header('sys/resource.h')
        self._check_header('sys/select.h')
        self._check_header('sys/time.h')
        self._check_header('sys/un.h')
        self._check_header('termios.h')
        self._check_header('unistd.h')
        self._check_header('valgrind/valgrind.h')
        self._check_header('VideoDecodeAcceleration/VDADecoder.h')
        self._check_header('windows.h')
        self._check_header('X11/extensions/XvMClib.h')
        self._check_header('asm/types.h')
        self._check_header('check_header jni.h')
        self._check_header('opencv2/core/core_c.h')
        self._check_header('linux/fb.h')
        self._check_header('linux/videodev2.h')
        self._check_header('sys/videoio.h')
        self._check_header('dev/bktr/ioctl_meteor.h')
        self._check_header('dev/bktr/ioctl_bt848.h')
        self._check_header('machine/ioctl_meteor.h')
        self._check_header('machine/ioctl_bt848.h')
        self._check_header('dev/video/meteor/ioctl_meteor.h')
        self._check_header('dev/video/bktr/ioctl_bt848.h')
        self._check_header('dev/ic/bt8xx.h')
        self._check_header('soundcard.h')

    def _check_header(self, header_name, content=None, **kwargs):
        self.headers[header_name] = False
        if not content:
            content = f'''#include <{header_name}> int x;'''
        if self.toolchain.doCommand('cc',
                                 config=self.config,
                                 src=self.tmpFile,
                                 dst=self.tmpFileOut):
            self.headers[header_name] = True

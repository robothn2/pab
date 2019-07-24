# coding: utf-8

import os


''' xcode clang compile command line:
/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang \
 -c -x c++ -arch x86_64 -O0 -g -mmacosx-version-min=10.14 \
 -std=c++11 -MMD -MT dependencies \
 -MF /Users/nsw/src/frameflow/third_party/work/jsoncpp-arm64/src/test_lib_json/JSONCPP.build/Debug/jsoncpp_test.build/Objects-normal/x86_64/main.d \
 -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.14.sdk \
 -fasm-blocks -fstrict-aliasing -fcolor-diagnostics \
 --serialize-diagnostics /Users/nsw/src/frameflow/third_party/work/jsoncpp-arm64/src/test_lib_json/JSONCPP.build/Debug/jsoncpp_test.build/Objects-normal/x86_64/main.dia \
 -fmessage-length=142 -fdiagnostics-show-note-include-stack -fmacro-backtrace-limit=0 \
 -Wno-trigraphs -fpascal-strings -Wno-missing-field-initializers -Wno-missing-prototypes -Wno-return-type -Wno-non-virtual-dtor -Wno-overloaded-virtual -Wno-exit-time-destructors \
 -Wno-missing-braces -Wparentheses -Wswitch -Wno-unused-function -Wno-unused-label -Wno-unused-parameter -Wno-unused-variable -Wunused-value -Wno-empty-body -Wno-uninitialized \
 -Wno-unknown-pragmas -Wno-shadow -Wno-four-char-constants -Wno-conversion -Wno-constant-conversion -Wno-int-conversion -Wno-bool-conversion -Wno-enum-conversion -Wno-float-conversion \
 -Wno-non-literal-null-conversion -Wno-objc-literal-conversion -Wno-shorten-64-to-32 -Wno-newline-eof -Wno-c++11-extensions -Wdeprecated-declarations -Winvalid-offsetof \
 -Wno-sign-conversion -Wno-infinite-recursion -Wno-move -Wno-comma -Wno-block-capture-autoreleasing -Wno-strict-prototypes -Wno-range-loop-analysis -Wno-semicolon-before-method-body \
 -Wmost -Wno-four-char-constants -Wno-unknown-pragmas -Wall -Wconversion -Wshadow -Werror=conversion -Werror=sign-compare \
 -DCMAKE_INTDIR=\"Debug\" \
 -I/include \
 -I/Users/nsw/src/frameflow/third_party/work/jsoncpp-arm64/src/test_lib_json/Debug/include \
 -I/Users/nsw/src/frameflow/third_party/repo/jsoncpp/src/lib_json/../../include \
 -I/Users/nsw/src/frameflow/third_party/work/jsoncpp-arm64/src/test_lib_json/JSONCPP.build/Debug/jsoncpp_test.build/DerivedSources-normal/x86_64 \
 -I/Users/nsw/src/frameflow/third_party/work/jsoncpp-arm64/src/test_lib_json/JSONCPP.build/Debug/jsoncpp_test.build/DerivedSources/x86_64 \
 -I/Users/nsw/src/frameflow/third_party/work/jsoncpp-arm64/src/test_lib_json/JSONCPP.build/Debug/jsoncpp_test.build/DerivedSources \
 -F/Users/nsw/src/frameflow/third_party/work/jsoncpp-arm64/src/test_lib_json/Debug \
 /Users/nsw/src/frameflow/third_party/repo/jsoncpp/src/test_lib_json/main.cpp \
 -o /Users/nsw/src/frameflow/third_party/work/jsoncpp-arm64/src/test_lib_json/JSONCPP.build/Debug/jsoncpp_test.build/Objects-normal/x86_64/main.o
'''
class Clang:
    def __init__(self, **kwargs):
        self.name = 'clang'
        self.tags = ('clang', )
        self.kwargs = kwargs
        self.suffix = kwargs.get('suffix', '')
        self.prefix = kwargs.get('prefix', '')
        if os.path.isdir(self.prefix):
            self.prefix += os.sep
        self.target_triple = ''

        self._cmds = {
                'cc': (self.prefix + 'clang' + self.suffix, 'src', '-c', '-x', 'c'),
                'cxx': (self.prefix + 'clang' + self.suffix, 'src', '-c', '-x', 'c++'),
                'ar': (self.prefix + 'ar' + self.suffix, 'dst', '-rcs'),
                'ld': (self.prefix + 'clang' + self.suffix, 'dst'),
                #'ldd': (self.prefix + 'ld.bfd' + self.suffix, ),
                }
        self._compositors = {
                'sysroot':      lambda path, args: f'--sysroot={path}',
                'includePath':  lambda path, args: ['-I', path],
                'libPath':      lambda path, args: ['-L', path],
                'lib':          lambda path, args: f'-l{path}',
                'define':       lambda macro, args: f'-D{macro}',
                }

    def matchRequest(self, request):
        self.target_triple = request.target_cpu + '-' + request.target_os
        return True

    def asCmdProvider(self, kwargs):
        return self._cmds

    def asCmdInterpreter(self):
        return self._compositors

    def asCmdFilter(self, cmd, kwargs):
        if cmd.name not in ('ar', 'cc', 'cxx', 'ld'):
            return

        if cmd.name == 'cc':
            cmd.ccflags += ['-Wall', '--target=' + self.target_triple]

        elif cmd.name == 'cxx':
            cmd.cxxflags += ['-Wall', '--target=' + self.target_triple]
            cmd.defines += '_LIBCPP_HAS_THREAD_API_PTHREAD'

        elif cmd.name == 'ld':
            cmd.ldflags += '--target=' + self.target_triple
            cmd.composeSources(
                    cmd.sources,
                    os.path.join(kwargs['request'].rootBuild, 'src_list.txt'))
            if kwargs['target'].isSharedLib():
                cmd.ldflags += ['-shared', '-fpic']

        dst = kwargs['dst']
        if cmd.name == 'ar':
            cmd += dst
        else:
            cmd += ['-o', dst]

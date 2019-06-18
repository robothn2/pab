#coding: utf-8

from pab.builder import Builder
from pab.toolchain import Toolchain

if __name__ == '__main__':
    builder = Builder('test/hello', 'test/hello/build')
    toolchain = Toolchain()
    #toolchain.add_plugin(NDK(path='d:/lib/android-ndk-r14b', platform=21, arch='aarch64', cpu='arm64-v8a', compiler='gcc'))
    builder.build(toolchain)
    
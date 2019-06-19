#coding: utf-8

from pab.builder import Builder
from pab.toolchain import Toolchain
from pab.android_ndk import NDK

if __name__ == '__main__':
    builder = Builder('test/hello', 'test/hello/build')
    toolchain = Toolchain()
    toolchain.addPlugin(NDK(path='d:/lib/android-ndk-r14b', toolchain='arm-linux-androideabi-4.9', platform=21, arch='aarch64', abi='arm64-v8a', compiler='gcc'))
    builder.build(toolchain)
    
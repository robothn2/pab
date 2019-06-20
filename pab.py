#coding: utf-8

from pab.builder import Builder
from pab.toolchain import Toolchain
from pab.android_ndk.ndk import NDK
from pab.visual_studio.vs2015 import VS2015

if __name__ == '__main__':
    #ndk = NDK(path='d:/lib/android-ndk-r14b', toolchain='arm-linux-androideabi-4.9', platform=12, arch='arm', abi='armeabi', compiler='gcc')
    vs = VS2015()
    toolchain = Toolchain(vs)

    builder = Builder('test/hello', 'test/hello/build')
    builder.build(toolchain)
    
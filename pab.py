#coding: utf-8

from pab.builder import Builder
from pab.toolchain import Toolchain
from pab.android_ndk.ndk import NDK
from pab.visual_studio.vs2015 import VS2015
from pab.targets.manual import ManualTarget

if __name__ == '__main__':
    #ndk = NDK(path='d:/lib/android-ndk-r14b', toolchain='arm-linux-androideabi-4.9', platform=12, arch='arm', abi='armeabi', compiler='gcc')
    target = ManualTarget(root='d:/lib/ffmpeg/libavfilter', includePath='d:/lib/ffmpeg')
    vs = VS2015()
    toolchain = Toolchain(vs, target)

    builder = Builder('d:/lib/ffmpeg/libavfilter', 'd:/lib/ffmpeg/build')
    builder.build(toolchain, top=10)
    
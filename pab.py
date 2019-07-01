# coding: utf-8

from pab.builder import Builder
from pab.targets.folder import FolderTarget
from pab.android_ndk.ndk import NDK
from pab.visual_studio.vs2015 import VS2015


if __name__ == '__main__':
    # compiler = VS2015()
    compiler = NDK(path='d:/lib/android-ndk-r14b', platform=24, compiler='gcc')
    builder = Builder(compiler, target_os='android', arch='arm', cpu='armv7a',
                      target_platform_ver='10.0.17763.0')

    target = FolderTarget(
            root='D:/lib/ffmpeg/libavutil',
            depth=0, rescan=True,  # verbose=True,
            rootBuild='D:/lib/ffmpeg/build/libavutil',
            targetType='sharedLib',  # 'executable', 'staticLib', 'sharedLib'
            std='c11',  # c11, c99, c++11, c++15, c++17
            stl='gnu-libstdc++',  # gnu-libstdc++/llvm-libc++abi/llvm-libc++/stlport/gabi++/system
            crtStatic=False,  # True - static, False - shared
            includePath='d:/lib/ffmpeg',
            excludeFiles=['filter_list.c', 'tests'])
    builder.build(target, top=0, check=False)

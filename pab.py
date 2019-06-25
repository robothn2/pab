#coding: utf-8

from pab.builder import Builder
from pab.targets.folder import FolderTarget
from pab.android_ndk.ndk import NDK
from pab.visual_studio.vs2015 import VS2015

if __name__ == '__main__':
    #compiler = VS2015()
    compiler = NDK(path='d:/lib/android-ndk-r14b', platform=21, compiler='gcc')
    builder = Builder(compiler, target_os='android', arch='x86', cpu='i686', target_platform_ver='10.0.17763.0')

    target = FolderTarget(root='d:/lib/ffmpeg/libavutil',
                          depth=0, rescan=True,
                          rootBuild='d:/lib/ffmpeg/build/libavutil',
                          targetType='sharedLib', # 'executable', 'staticLib', 'sharedLib'
                          includePath='d:/lib/ffmpeg',
                          excludeFiles=['filter_list.c', 'tests'])
    builder.build(target, top=0)
    
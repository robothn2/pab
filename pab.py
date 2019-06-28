#coding: utf-8

from pab.builder import Builder
from pab.targets.folder import FolderTarget
from pab.android_ndk.ndk import NDK
from pab.visual_studio.vs2015 import VS2015

if __name__ == '__main__':
    #compiler = VS2015()
    compiler = NDK(path='d:/lib/android-ndk-r14b', platform=23, compiler='gcc')
    builder = Builder(compiler, target_os='android', arch='arm', cpu='armeabi', target_platform_ver='10.0.17763.0')

    target = FolderTarget(root='D:/src/frameflow/src/ffmpeg',
                          depth=0, rescan=True,
                          rootBuild='D:/src/frameflow/src/ffmpeg/build',
                          targetType='sharedLib', # 'executable', 'staticLib', 'sharedLib'
                          defines=['FRAMEFLOW_CONFIG_QT'],
                          includePath=['D:/src/frameflow/include',
                                       'D:/src/frameflow/third_party/externals/ffmpeg/ffmpeg-android-arm/include',
                                       'D:/src/frameflow/third_party/externals/jsoncpp/jsoncpp-android-arm/include',
                                       'D:/Qt/Qt5.12.1/5.12.1/android_armv7/include',
                                       ],
                          excludeFiles=['tests'])
    builder.build(target, top=10, check=False)
    
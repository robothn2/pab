# coding: utf-8

from pab.builder import Builder
from pab.targets.pab_folder import PabTargets
from pab.android_ndk.ndk import NDK
from pab.visual_studio.vs2015 import VS2015

if __name__ == '__main__':
    #compiler = VS2015()
    compiler = NDK(path='d:/lib/android-ndk-r14b', platform=24, compiler='gcc')
    builder = Builder(compiler, target_os='android', arch='x86', cpu='x86',
                      target_platform_ver='10.0.17134.0')

    target = PabTargets(
            targetType='sharedLib',
            std='c++11',  # verbose=True,
            root='test/jsoncpp',  # 'test/skia',
            rootSource='d:/src/frameflow/third_party/repo/jsoncpp', #'D:/lib/skia/third_party/externals/libpng',
            rootBuild='D:/lib/build')
    builder.build(target, top=0, check=False)

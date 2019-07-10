# coding: utf-8

from pab.builder import Builder
from pab.request import Request
from pab.targets.pab_folder import PabTargets
from pab.android_ndk.ndk import NDK
from pab.visual_studio.vs2015 import VS2015


if __name__ == '__main__':
    # compiler = VS2015(target_platform_ver='10.0.17134.0')
    compiler = NDK(path='d:/lib/android-ndk-r14b', platform=9, compiler='gcc')
    request = Request(target_os='android', target_cpu='armv7a',
                      stl='llvm-libc++',  # 'gnu-libstdc++', 'llvm-libc++'
                      root_build='D:/lib/build')

    target = PabTargets(root='test/ogre/ogre.py')
    builder = Builder(request, compiler)
    builder.build(target, dryrun=True, verbose=False)

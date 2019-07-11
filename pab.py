# coding: utf-8
from pab.builder import Builder
from pab.request import Request
from pab.targets.pab_folder import PabTargets
from pab.android_ndk.ndk import NDK
from pab.visual_studio.vs2015 import VS2015

import logging
import logging.handlers


if __name__ == '__main__':
    logger = logging.getLogger("pab")
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)

        log_to_stdout = logging.StreamHandler()
        log_to_stdout.setLevel(logging.INFO)
        log_to_stdout.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(log_to_stdout)

        # log to file
        log_to_file = logging.FileHandler(filename='pab.log', mode='w')
        log_to_file.setLevel(logging.DEBUG)
        log_to_file.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(log_to_file)

    # compiler = VS2015(target_platform_ver='10.0.17134.0')
    compiler = NDK(path='d:/lib/android-ndk-r14b', platform=9, compiler='gcc')
    request = Request(target_os='android', target_cpu='armv7a',
                      stl='llvm-libc++',  # 'gnu-libstdc++', 'llvm-libc++'
                      root_build='D:/lib/build')

    target = PabTargets(root='test/hello')
    builder = Builder(request, compiler)
    builder.build(target, dryrun=False)

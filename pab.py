# coding: utf-8
from pab.builder import Builder
from pab.request import Request
from pab.targets.pab_folder import PabTargets
from pab.android_ndk.ndk import NDK
from pab.interpreter.msvc import MSVC

import logging
import logging.handlers


if __name__ == '__main__':
    logger = logging.getLogger("pab")
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        log_to_stdout = logging.StreamHandler()
        log_to_stdout.setLevel(logging.INFO)
        log_to_stdout.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(log_to_stdout)

        # log to file
        log_to_file = logging.FileHandler(filename='pab.log', mode='w')
        log_to_file.setLevel(logging.DEBUG)
        log_to_file.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(log_to_file)

    compiler = MSVC(ver='14.0', platform='7.1')
    #compiler = NDK(path='d:/lib/android-ndk-r14b', platform=9, compiler='gcc',
    #               stl='llvm-libc++')  # 'gnu-libstdc++', 'llvm-libc++'
    request = Request(target_os='win', target_cpu='x64',
                      root_build='D:/build')
    builder = Builder(request, compiler, dryrun=False, job=10)
    builder.build(PabTargets(root='test/skia', root_source='d:/src/pca_infra/thirdparty-source/skia'))

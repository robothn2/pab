#coding: utf-8

import os

'''
def make_standalone_toolchain(root_ndk, root_sa_toolchain='/ndk_sa/21', arch='arm', android_platform=21):
    ndk_toolchain = os.path.join(root_sa_toolchain, arch)
    if not os.path.exists(ndk_toolchain):
        print(" Creating ndk standalone toolchain at:", ndk_toolchain)
        subprocess.check_call(['sh',
                               f'{root_ndk}/build/tools/make-standalone-toolchain.sh',
                               f'--platform=android-{android_platform}',
                               f'--install-dir={ndk_toolchain}',
                               f'--arch={arch}'])
'''

class NDKStandalone:
    def __init__(self, root_path):
        pass
   
    def cc(self, file_src, file_dst):
        pass
    
    def cxx(self, file_src, file_dst):
        pass

    def asm(self, file_src, file_dst):
        pass

    def ar(self, file_src, file_dst):
        pass
    
    def ld(self, file_src, file_dst):
        pass
    
    
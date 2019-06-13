#coding: utf-8

from source_files import SourceFiles
from configure import Configure

class Builder:
    def __init__(self, src, workspace, **kwargs):
        self.files = SourceFiles(src, workspace)

    def build(self, configure, toolchain):
        self.config = configure
        self.toolchain = toolchain
    
    
if __name__ == '__main__':
    bd = Builder(src='d:/lib/ffmpeg', workspace='d:/ws/ffmpeg')
    bd.build()
    
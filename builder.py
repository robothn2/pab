#coding: utf-8

from source_files import SourceFiles

class Builder:
    def __init__(self, **kwargs):
        self.files = SourceFiles(kwargs)

if __name__ == '__main__':
    bd = Builder(src='d:/lib/ffmpeg', workspace='d:/ws/ffmpeg')
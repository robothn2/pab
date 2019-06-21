#coding: utf-8

from .source_files import SourceFiles
from .config import Config
from .build_flow import BuildFlow

class Builder:
    def __init__(self, src, workspace, **kwargs):
        self.files = SourceFiles(src, workspace)
        self.config = Config(kwargs.get('config', {}))
        self.flow = BuildFlow(kwargs.get('flow', {}))

    def build(self, toolchain, **kwargs):
        #self.config.append(configure)
        self.flow.run(self.config, self.files, toolchain, kwargs)

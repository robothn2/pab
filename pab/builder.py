#coding: utf-8

from .source_files import SourceFiles
from .configure import Configure
from .build_flow import BuildFlow

class Builder:
    def __init__(self, src, workspace, **kwargs):
        self.files = SourceFiles(src, workspace)
        self.config = Configure(kwargs.get('config', {}))
        self.flow = BuildFlow(kwargs.get('flow', {}))

    def build(self, toolchain):
        #self.config.append(configure)
        self.flow.run(self.config, self.files, toolchain)

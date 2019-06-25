#coding: utf-8

from .config import Config
from .toolchain import Toolchain
from .utils.config_generator import ConfigGenerator

class Builder:
    def __init__(self, compiler, **config):
        self.config = Config(config)
        compiler.applyConfig(self.config)
        self.toolchain = Toolchain(compiler)

    def build(self, targets, **kwargs):
        cfgGen = ConfigGenerator(**self.config.cfg, **kwargs)
        self.toolchain.registerPlugin(cfgGen)
        cfgGen.checkAll(self.toolchain)
        self.toolchain.unregisterPlugin(cfgGen)
        
        self.toolchain.registerPlugin(self.config)
        
        if isinstance(targets, list):
            for target in targets:
                self._buildTarget(target, kwargs)
        else:
            self._buildTarget(targets, kwargs)

    def _buildTarget(self, target, args):
        self.toolchain.registerPlugin(target)
        target.build(self.config, self.toolchain, args)
        self.toolchain.unregisterPlugin(target)

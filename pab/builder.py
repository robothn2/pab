#coding: utf-8

from .config import Config

class Builder:
    def __init__(self, **config):
        self.config = Config(config)

    def build(self, toolchain, targets, **kwargs):
        toolchain.registerPlugin(self.config)
        
        if isinstance(targets, list):
            for target in targets:
                self._buildTarget(toolchain, target, kwargs)
        else:
            self._buildTarget(toolchain, targets, kwargs)

    def _buildTarget(self, toolchain, target, args):
        toolchain.registerPlugin(target)
        target.build(self.config, toolchain, args)
        toolchain.unregisterPlugin(target)

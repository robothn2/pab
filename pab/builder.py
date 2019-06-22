#coding: utf-8

from .config import Config

class Builder:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.config = Config(kwargs.get('config', {}))

    def build(self, toolchain, targets, **kwargs):
        if isinstance(targets, list):
            for target in targets:
                self._buildTarget(toolchain, target, kwargs)
        else:
            self._buildTarget(toolchain, targets, kwargs)

    def _buildTarget(self, toolchain, target, args):
        toolchain.registerPlugin(target)
        target.build(self.config, toolchain, args)
        toolchain.unregisterPlugin(target)

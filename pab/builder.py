# coding: utf-8
from ._internal.command import Command
from ._internal.results import Results
from .host_os.bin_utils import BinUtils
from ._internal.log import logger


class Builder:
    def __init__(self, request, *configs):
        self.initialConfigs = configs
        self.request = request
        self.results = Results()
        self.configs = []
        self.interpreters = []
        self.binutils = BinUtils(suffix=request.hostOS.getExecutableSuffix())

    def _collect_available_configs(self):
        self.configs = []
        cfg_queue = list(self.initialConfigs[:])
        while len(cfg_queue) > 0:
            cfg = cfg_queue[0]
            cfg_queue = cfg_queue[1:]

            if not hasattr(cfg, 'matchRequest'):
                # always available
                self.configs.append(cfg)
                continue

            r = cfg.matchRequest(self.request)
            if isinstance(r, bool):
                if r:
                    self.configs.append(cfg)
            elif isinstance(r, tuple):
                if r[0]:
                    self.configs.append(cfg)
                    if isinstance(r[1], list):
                        cfg_queue += r[1]
                else:
                    logger.info('Disabled config: {} {}'.format(
                            cfg.name, r[1]))

        self.configs.append(self.binutils)

        for cfg in self.configs:
            if hasattr(cfg, 'asCmdProvider'):
                self.interpreters.append(cfg)
        logger.info('Enabled configs: {}'.format(
                [cfg.name for cfg in self.configs]))
        logger.info('Interpreters: {}'.format(
                [cfg.name for cfg in self.interpreters]))

    def build(self, targets, **kwargs):
        self._collect_available_configs()

        self.results.reset(title=str(targets))
        self.configs.append(targets)

        targets.build(self.request, self, **kwargs)

        self.configs.remove(targets)
        self.results.dump()

    def execCommand(self, cmd_name, **kwargs):
        if not cmd_name:
            return (False, None)

        cmd = self._createCmd(cmd_name,
                              results=self.results, request=self.request,
                              configs=self.configs, **kwargs)

        print('=', cmd.name, cmd.dst or cmd.sources[0])
        logger.info('cmdline: ' + cmd.getCmdLine())
        if kwargs.get('dryrun', False):
            return True, 'dryrun ok'
        return cmd.execute()

    def _createCmd(self, cmd_name, **kwargs):
        for interpreter in self.interpreters:
            entry = interpreter.asCmdProvider().get(cmd_name)
            if not entry:
                continue
            return Command(interpreter,
                           *entry[1:],  # extra args from command provider
                           name=cmd_name, executable=entry[0],
                           **kwargs)

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
        self.compositor = None
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
                    logger.info('disabled config: {} {}'.format(cfg.name, r[1]))

        self.configs.append(self.binutils)

        for cfg in self.configs:
            if hasattr(cfg, 'compositors'):
                self.compositor = cfg.compositors
                logger.info('compositor: ' + cfg.name)
        logger.info('enabled config: {}'.format([cfg.name for cfg in self.configs]))

    def build(self, target, **kwargs):
        self._collect_available_configs()

        self.results.reset(title=str(target))
        self.configs.append(target)

        target.build(self.request, self.configs, self, **kwargs)

        self.configs.remove(target)
        self.results.dump()

    def execCommand(self, cmd_name, **kwargs):
        if not cmd_name:
            return (False, None)

        cmd_entry = self._find_cmd_entry(cmd_name)
        assert(isinstance(cmd_entry, tuple))
        cmd = Command(name=cmd_name, executable=cmd_entry[0],
                      results=self.results)
        cmd.preprocess(*cmd_entry[2:],  # extra command args by provider
                       filters=self.configs, compositors=self.compositor,
                       **kwargs)

        src = kwargs['src']
        dst = kwargs.get('dst')  # maybe non-exist
        if (len(cmd_entry) > 1 and cmd_entry[1] == 'dst'):
            logger.info('= {} {}'.format(cmd_name, dst))
        else:
            logger.info('= {} {}'.format(cmd_name, src))
        logger.debug('- ' + cmd.getCmdLine())
        if kwargs.get('dryrun', False):
            return True, 'dryrun ok'
        return cmd.execute()

    def _find_cmd_entry(self, cmd_name):
        for cfg in self.configs:
            if not hasattr(cfg, 'queryCmd'):
                continue
            entry = cfg.queryCmd(cmd_name)
            if entry:
                return entry
        return None
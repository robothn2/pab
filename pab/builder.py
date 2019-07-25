# coding: utf-8
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from ._internal.command import Command
from ._internal.results import Results
from .interpreter.bin_utils import BinUtils
from ._internal.log import logger


class Builder:
    def __init__(self, request, *configs, **kwargs):
        self._kwargs = kwargs
        self.initialConfigs = configs
        self.request = request
        self.results = Results()
        self.configs = []
        self.interpreters = []
        self.compiler = None
        self._cmds = []
        self.binutils = BinUtils(suffix=request.host_os.getExecutableSuffix())
        self.lockPoolOut = Lock()

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
                if hasattr(cfg, 'tags'):
                    self.compiler = cfg
        logger.info('Enabled configs: {}'.format(
                [cfg.name for cfg in self.configs]))
        logger.info('Interpreters: {}'.format(
                [cfg.name for cfg in self.interpreters]))
        logger.info('Compiler: {}'.format(self.compiler.tags))

    def build(self, targets):
        self._collect_available_configs()

        self.results.reset(title=str(targets))
        self.configs.append(targets)

        targets.build(self.request, self)

        self.configs.remove(targets)
        self.results.dump()

    def poolCommand(self, cmd_name, **kwargs):
        cmd = self._createCmd(cmd_name,
                              results=self.results, request=self.request,
                              configs=self.configs, **kwargs, **self._kwargs)
        if not cmd:
            print('* fail to create command:', cmd_name, kwargs['sources'])
            return
        self._cmds.append(cmd)

    def waitPoolComplete(self):
        total = len(self._cmds)
        for i in range(total):
            cmd = self._cmds[i]
            cmd.build_index = i + 1
            cmd.build_total = total

        def exec_one_cmd(cmd):
            cmd.execute()

            #self.lockPoolOut.acquire()
            if cmd.success:
                self.results.succeeded(cmd.file)
            else:
                self.results.error(cmd.file, cmd.error)
            #self.lockPoolOut.release()
            return cmd

        with ThreadPoolExecutor(max_workers=self._kwargs.get('job', 1)) as pool:
            results = pool.map(exec_one_cmd, self._cmds)
            self._cmds = []
            return results

    def execCommand(self, cmd_name, **kwargs):
        cmd = self._createCmd(cmd_name,
                              results=self.results, request=self.request,
                              configs=self.configs, **kwargs)
        if not cmd:
            print('* fail to create command:', cmd_name, kwargs['sources'])
            return
        cmd.execute()
        return cmd

    def _createCmd(self, cmd_name, **kwargs):
        for interpreter in self.interpreters:
            entry = interpreter.asCmdProvider(kwargs).get(cmd_name)
            if not entry:
                continue
            return Command(interpreter,
                           *entry[1:],  # extra args from command provider
                           name=cmd_name, executable=entry[0],
                           **kwargs)

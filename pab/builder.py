# coding: utf-8

from ._internal.command import Command


class Builder:
    def __init__(self, request, *configs):
        self.initialConfigs = configs
        self.request = request
        self.configs = []
        self.compositor = None

    def _match_configs(self):
        self.configs = []
        cfg_queue = list(self.initialConfigs[:])
        while len(cfg_queue) > 0:
            cfg = cfg_queue[0]
            cfg_queue = cfg_queue[1:]

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
                    print(cfg.name, 'disabled:', r[1])

        for cfg in self.configs:
            print(cfg.name, 'enabled')
            if hasattr(cfg, 'compositors'):
                self.compositor = cfg.compositors
                print(cfg.name, 'is compositor')

    def build(self, target, **kwargs):
        self._match_configs()

        self.configs.append(target)
        target.build(self.request, self.configs, self, kwargs)
        self.configs.remove(target)

    def execCommand(self, cmd_name, **kwargs):
        if not cmd_name:
            return None
        cmd_entry = self._find_cmd_entry(cmd_name)
        if not cmd_entry:
            print('unsupport Command', cmd_name)
            return None  # unsupport Command

        src = kwargs['src']
        cmd = Command(name=cmd_name, executable=cmd_entry[0])
        dst = cmd.preprocess(cmd=cmd_name, filters=self.configs,
                             compositors=self.compositor, **kwargs)
        custom_log = cmd_entry[1]
        if (custom_log == 'src'):
            print('=', cmd_name, src)
        elif (custom_log == 'dst'):
            print('=', cmd_name, dst)
        return dst if cmd.execute(kwargs.get('verbose', False)) else None

    def _find_cmd_entry(self, cmd_name):
        for cfg in self.configs:
            if not hasattr(cfg, 'queryCmd'):
                continue
            entry = cfg.queryCmd(cmd_name)
            if entry:
                return entry
        return None
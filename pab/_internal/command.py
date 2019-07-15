# coding: utf-8

import subprocess
import os
from .output_analyze import output_analyze
from .target_utils import ItemList
from .log import logger
'''
A Command consists of multiple parts, each one includes many CommandPart which
provided by a Plugin.
A CommandPart can be a string for supportting special compiler, a tuple for
supportting command composition, a lambda/function for supportting config
specialization, and a list of string, a list of tuple.
'''

_props_of_cmd = [
        'defines', 'include_dirs', 'sysroots', 'sources',
        'ccflags', 'cxxflags', 'ldflags',
        'lib_dirs', 'libs',
        'parts',
        ]


class Command(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__({})
        self.executable = kwargs['executable']
        self.name = kwargs['name']
        self.cmds = []
        self.appendixs = []  # collect args which including `"`
        self.dst = ''
        self.results = kwargs['results']
        for v in _props_of_cmd:
            self[v] = ItemList(name=v)

        for k, v in kwargs.items():
            if k in self:
                self[k] += v
            else:
                self[k] = v

    def __getattr__(self, name):
        if name in self:
            return self[name]
        return None

    def __iadd__(self, other):
        if not other:
            return self
        if isinstance(other, object):
            # merge other into self
            for k in _props_of_cmd:
                if hasattr(other, k):
                    self[k] += other.k
        return self

    def composeSources(self, sources, tmp_file_path):
        # write all source file path into file, and use @file
        tmp_file = tmp_file_path
        with open(tmp_file, 'w', encoding='utf-8') as f:
            for o in sources:
                o = os.path.realpath(o)
                o = o.replace('\\', '/')
                f.write(o)
                f.write(' ')
            f.close()
        self.parts += '@' + tmp_file

    def translate(self, compositors, kwargs):
        for prop in ('defines', 'sysroots', 'include_dirs', 'lib_dirs', 'libs'):
            c = compositors.get('define')
            if not c:
                continue
            for v in self[prop]:
                self._addCmdPart(c(v, kwargs))

        # 'ccflags', 'cxxflags', 'ldflags',
        values = self.get(self.name + 'flags')
        if values:
            for v in values:
                self._addCmdPart(v)

        for v in self['sources']:
            self._addCmdPart(v)
        print('interpreter translate', self)

    def preprocess(self, interpreter, *extra_args, **kwargs):
        self.appendixs = []
        self.cmds = [self.executable]  # executable must be first element
        # extra command args by provider
        for arg in extra_args:
            self._addCmdPart(arg)

        self.sources += kwargs.get('sources')
        self.dst = kwargs.get('dst')
        for cfg in kwargs['configs']:
            if cfg == interpreter or not hasattr(cfg, 'filterCmd'):
                continue
            cfg.filterCmd(self, kwargs)

        if hasattr(interpreter, 'filterCmd'):
            interpreter.filterCmd(self, kwargs)

    def getCmdLine(self):
        return subprocess.list2cmdline(self.cmds) \
            + ' ' + ' '.join(self.parts) \
            + ' ' + ' '.join(self.appendixs)

    def execute(self):
        # using appendixs to avoid incorrect quote on cmd part which existing
        #   double quote `"`
        cmdline = self.getCmdLine()
        exitcode, output = subprocess.getstatusoutput(cmdline)
        if exitcode != 0:
            error = output_analyze(cmdline, output)
            return False, error
        return True, output

    def _addCmdPart(self, part):
        if not part:
            return
        if '"' in part:
            self.appendixs.append(part)
        else:
            self.cmds.append(part)

# coding: utf-8
'''
A Command consists of multiple parts, each one includes many CommandPart which
provided by Configs.
'''

import subprocess
import os
from .output_analyze import output_analyze
from .target_utils import ItemList
from .target import Target
from .log import logger

_props_all = (
        'defines', 'include_dirs', 'sysroots', 'sources',
        'ccflags', 'cxxflags', 'ldflags',
        'lib_dirs', 'libs',
        )

_props_cmd = {
        'cc': ('defines', 'include_dirs', 'sysroots', 'ccflags'),
        'cxx': ('defines', 'include_dirs', 'sysroots', 'cxxflags'),
        'ld': ('sysroots', 'ldflags', 'lib_dirs', 'libs'),
        'ar': (),
        }

class Command(dict):
    def __init__(self, interpreter, *extra_args, **kwargs):
        dict.__init__({})
        self.name = kwargs['name']
        self.interpreter = interpreter

        self.results = kwargs['results']
        self.success = False
        self.retcode = 0
        self.output = ''
        self.error = ''

        self.cmds = [kwargs['executable']]  # executable must be first element
        for arg in extra_args:
            self.addPart(arg)

        self.appendixs = []  # collect args which including `"`
        self['parts'] = ItemList(name='parts', unique=False)
        for v in _props_all:
            self[v] = ItemList(name=v)

        for k, v in kwargs.items():
            if k in self:
                self[k] += v
            else:
                self[k] = v

        self.sources += kwargs.pop('sources')
        self.dst = kwargs.get('dst')

        self += kwargs.get('target')  # merge target's props: defines, etc.

        self._preprocess(kwargs)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        return None

    def __iadd__(self, other):
        if not other:
            return self
        assert(isinstance(other, Target))
        # merge other into self
        logger.debug('- merge Config(%s) into Command' % str(other))
        for k in _props_cmd.get(self.name):
            prop_target = other.setting.get(k)
            self[k] += prop_target
            if prop_target:
                logger.debug('   {}: {} -> {}'.format(k, prop_target, self[k]))
        return self

    def _preprocess(self, kwargs):
        for cfg in kwargs.pop('configs', []):
            if cfg == self.interpreter or not hasattr(cfg, 'asCmdFilter'):
                continue
            cfg.asCmdFilter(self, kwargs)

        if hasattr(self.interpreter, 'asCmdFilter'):
            self.interpreter.asCmdFilter(self, kwargs)

        if hasattr(self.interpreter, 'asCmdInterpreter'):
            self._translate(self.interpreter.asCmdInterpreter(), kwargs)
        else:
            self.parts += self.sources

    def _translate(self, compositors, kwargs):
        self._mergeSources(
                os.path.join(kwargs['request'].rootBuild, 'src_list.txt'))

        for prop in ('defines', 'sysroots', 'include_dirs', 'lib_dirs', 'libs'):
            c = compositors.get(prop)
            if not c:
                logger.warning('* cant translate ' + prop)
                continue
            for v in self[prop]:
                v_trans = c(v, kwargs)
                # logger.debug('   {} -> {}'.format(v, v_trans))
                self.parts += v_trans

        # 'ccflags', 'cxxflags', 'ldflags',
        self.parts += self.get(self.name + 'flags')

    def _mergeSources(self, tmp_file_path):
        # write all source file path into file, and use @file
        if len(self.sources) < 5:
            self.parts += self.sources
            return

        tmp_file = tmp_file_path
        with open(tmp_file, 'w', encoding='utf-8') as f:
            for o in self.sources:
                o = os.path.realpath(o)
                o = o.replace('\\', '/')
                f.write(o)
                f.write(' ')
            f.close()
        self.parts += '@' + tmp_file

    def execute(self):
        # using appendixs to avoid incorrect quote on cmd part which existing
        #   double quote `"`
        cmdline = self.getCmdLine()
        self.retcode, self.output = subprocess.getstatusoutput(cmdline)

        if self.retcode != 0:
            self.error = output_analyze(cmdline, self.output)
            self.success = False
        else:
            self.success = True
        return self.success

    def getCmdLine(self):
        return subprocess.list2cmdline(self.cmds) \
            + ' ' + ' '.join(self.parts) \
            + ' ' + ' '.join(self.appendixs)

    def addPart(self, part):
        if not part:
            return
        assert(isinstance(part, str))
        if '"' in part:
            self.appendixs.append(part)
        else:
            self.cmds.append(part)

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

_all_props = (
        'defines', 'include_dirs', 'sysroots', 'sources',
        'ccflags', 'cxxflags', 'ldflags',
        'lib_dirs', 'libs',
        )

_cmd_affected_props = {
        'cc': ('defines', 'include_dirs', 'sysroots', 'ccflags'),
        'cxx': ('defines', 'include_dirs', 'sysroots', 'cxxflags'),
        'ld': ('sysroots', 'ldflags', 'lib_dirs', 'libs'),
        'ar': (),
        'rc': ('defines', 'include_dirs'),
        }

class Command(dict):
    def __init__(self, interpreter, *extra_args, **kwargs):
        dict.__init__({})
        self.name = kwargs['name']
        self.build_index = 0
        self.build_total = 0
        self.build_title = kwargs.get('build_title')
        self._interp = interpreter
        self._kwargs = kwargs

        self.success = False
        self.retcode = 0
        self.output = ''
        self.error = ''
        self.artifacts = []

        self._front_cmds = [kwargs['executable']]  # executable must be first element
        for arg in extra_args:
            self.addPart(arg)

        self._quoted_cmds = []  # collect args which including `"`
        self._tail_cmds = ItemList(name='tail_cmds', unique=False)
        for v in _all_props:
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
        if isinstance(other, Target):
            # merge Config into Command
            # logger.debug('- merge Config(%s) into Command' % str(other))
            for k in _cmd_affected_props.get(self.name, ()):
                prop_target = other.setting.get(k)
                self[k] += prop_target
                #if prop_target:
                #    logger.debug('   {}: {} -> {}'.format(k, prop_target, self[k]))
        elif isinstance(other, list):
            for item in other:
                assert(isinstance(item, str))
                self.addPart(item)
        elif isinstance(other, str):
            self.addPart(other)
        return self

    def _preprocess(self, kwargs):
        for cfg in kwargs.pop('configs', []):
            if cfg == self._interp or not hasattr(cfg, 'asCmdFilter'):
                continue
            cfg.asCmdFilter(self, kwargs)

        if hasattr(self._interp, 'asCmdFilter'):
            self._interp.asCmdFilter(self, kwargs)

        if hasattr(self._interp, 'asCmdInterpreter'):
            self._translateAllExceptSources(self._interp.asCmdInterpreter(), kwargs)

        # MS sdk's rc.exe need sources at tail
        self._translateSources(kwargs)

    def _translateAllExceptSources(self, compositors, kwargs):
        for prop in ('defines', 'sysroots', 'include_dirs', 'lib_dirs', 'libs'):
            c = compositors.get(prop)
            if not c:
                logger.warning('* cant translate ' + prop)
                continue
            for v in self[prop]:
                v_trans = c(v, kwargs)
                # logger.debug('   {} -> {}'.format(v, v_trans))
                self._tail_cmds += v_trans

        # 'ccflags', 'cxxflags', 'ldflags',
        self._tail_cmds += self.get(self.name + 'flags')

    def _translateSources(self, kwargs):
        # write all source file path into file, and use @file
        if len(self.sources) < 5:
            self._tail_cmds += self.sources
            return

        tmp_file = os.path.join(kwargs['request'].rootBuild, 'src_list.txt')
        with open(tmp_file, 'w', encoding='utf-8') as f:
            for o in self.sources:
                o = os.path.realpath(o)
                o = o.replace('\\', '/')
                f.write(o)
                f.write(' ')
            f.close()
        self._tail_cmds += '@' + tmp_file

    def execute(self):
        # using appendixs to avoid incorrect quote on cmd part which existing
        #   double quote `"`
        cmdline = self._getCmdLine()
        if self.build_total > 1 and self.build_title:
            print('{:>3}/{} {} {}'.format(self.build_index,
                        self.build_total, self.name, self.build_title))
        logger.debug('cmdline: ' + cmdline)

        if self._kwargs.get('dryrun', False):
            self.success = True
            return

        self.retcode, self.output = subprocess.getstatusoutput(cmdline)

        if self.retcode != 0:
            self.error = output_analyze(cmdline, self.output)
            self.success = False
        else:
            self.success = True
            self.artifacts.append(self.dst)
        return self.success

    def _getCmdLine(self):
        return subprocess.list2cmdline(self._front_cmds) \
            + ' ' + ' '.join(self._quoted_cmds) \
            + ' ' + ' '.join(self._tail_cmds)

    def addPart(self, part):
        if not part:
            return
        assert(isinstance(part, str))
        if '"' in part:
            self._quoted_cmds.append(part)
        else:
            self._front_cmds.append(part)

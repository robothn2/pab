# coding: utf-8

import subprocess
import os
from pab._internal.output_analyze import output_analyze
from pab._internal.target_utils import ItemList
from pab._internal.log import logger
'''
A Command consists of multiple parts, each one includes many CommandPart which
provided by a Plugin.
A CommandPart can be a string for supportting special compiler, a tuple for
supportting command composition, a lambda/function for supportting config
specialization, and a list of string, a list of tuple.
'''

_vars_normal = [
        'defines', 'include_dirs', 'sources',
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
        for v in _vars_normal:
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
            for k in _vars_normal:
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

    def translate(self, compositors):
        pass

    def preprocess(self, *extra_args, **kwargs):
        filters = kwargs['filters']
        compositors = kwargs['compositors']

        logger.debug('> compositor of ' + self.name)
        self.appendixs = []
        self.cmds = [self.executable]  # executable must be first element
        # extra command args by provider
        for arg in extra_args:
            self._addCmdPart(arg)

        cnt_before_filter = len(self.cmds) + len(self.appendixs)
        for cfg in filters:
            if not hasattr(cfg, 'filterCmd'):
                continue
            resultByCfg = cfg.filterCmd(self.name, kwargs)
            if not resultByCfg:
                continue

            for cmd_filter in resultByCfg:
                logger.debug('- compositor: ' + str(cmd_filter))
                result = self._recursiveFilter(cmd_filter, compositors, kwargs)
                logger.debug('-> ' + str(result))
                self._addListOrStr(result)

        if cnt_before_filter == len(self.cmds) + len(self.appendixs):
            # support simple command only accept 'src' parameter'
            src = kwargs.get('src')
            if src:
                self._addListOrStr(src)

        return kwargs.get('dst', None)

    def getCmdLine(self):
        return subprocess.list2cmdline(self.cmds) \
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

    def _recursiveFilter(self, cmd_filter, compositors, kwargs):
        if isinstance(cmd_filter, str):
            return cmd_filter

        elif isinstance(cmd_filter, list):
            # GCC: ['-c', '-Wall']
            ret = []
            for f in cmd_filter:
                result = self._recursiveFilter(f, compositors, kwargs)
                self._combineListAndResult(ret, result)
            return ret

        elif callable(cmd_filter):
            return self._recursiveFilter(cmd_filter(kwargs),
                                         compositors, kwargs)

        elif isinstance(cmd_filter, tuple):
            assert(len(cmd_filter) == 2)
            compositor = compositors.get(cmd_filter[0], None)
            assert(callable(compositor))
            param = cmd_filter[1]
            if isinstance(param, str):
                # ('sysroot', self.sysroot)
                return self._recursiveFilter(compositor(param, kwargs),
                                             compositors, kwargs)
            elif isinstance(param, list):
                # ('libPath', ['lib', '../lib'])
                ret = []
                for p in param:
                    result = compositor(p, kwargs)
                    self._combineListAndResult(
                        ret,
                        self._recursiveFilter(result, compositors, kwargs))
                return ret

            elif callable(param):
                # ('includePath', lambda kwargs: kwargs['config'].getArch())
                result = compositor(param(kwargs), kwargs)
                return self._recursiveFilter(result, compositors, kwargs)

        raise Exception('Invalid filter:', cmd_filter)

    @staticmethod
    def _combineListAndResult(listExist, result):
        if isinstance(result, list):
            listExist.extend(result)
        elif isinstance(result, str):
            listExist.append(result)

    def _addListOrStr(self, result):
        if isinstance(result, list):
            for part in result:
                self._addCmdPart(part)
        elif isinstance(result, str):
            self._addCmdPart(result)

    def _addCmdPart(self, part):
        if '"' in part:
            self.appendixs.append(part)
        else:
            self.cmds.append(part)

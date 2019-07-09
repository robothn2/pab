# coding: utf-8

import subprocess
from pab._internal.output_analyze import output_analyze

'''
A Command consists of multiple parts, each one includes many CommandPart which
provided by a Plugin.
A CommandPart can be a string for supportting special compiler, a tuple for
supportting command composition, a lambda/function for supportting config
specialization, and a list of string, a list of tuple.
'''


class Command:
    def __init__(self, **kwargs):
        self.executable = kwargs['executable']
        self.name = kwargs['name']
        self.cmds = []
        self.appendixs = []  # collect args which including `"`
        self.dst = ''
        self.results = kwargs['results']

    def __str__(self):
        return 'Command(%s)' % self.name

    def preprocess(self, *extra_args, **kwargs):
        filters = kwargs['filters']
        compositors = kwargs['compositors']
        verbose = kwargs.get('verbose', False)

        if verbose:
            print('> compositor of', self.name)
        self.appendixs = []
        self.cmds = [self.executable]  # executable must be first element
        # extra command args by provider
        for arg in extra_args:
            self._addCmdPart(arg)

        cnt_before_filter = len(self.cmds) + len(self.appendixs)
        for cfg in filters:
            if not hasattr(cfg, 'filterCmd'):
                continue
            resultByCfg = cfg.filterCmd(self.name)
            if not resultByCfg:
                continue

            for cmd_filter in resultByCfg:
                if verbose:
                    print('- compositor:', cmd_filter)
                result = self._recursiveFilter(cmd_filter, compositors, kwargs)
                if verbose:
                    print('->', result)
                self._addListOrStr(result)

        if cnt_before_filter == len(self.cmds) + len(self.appendixs):
            # support simple command only accept 'src' parameter'
            src = kwargs.get('src')
            if src:
                self._addListOrStr(src)

        return kwargs.get('dst', None)

    def execute(self, verbose=False):
        # using appendixs to avoid incorrect quote on cmd part which existing
        #   double quote `"`
        cmdline = subprocess.list2cmdline(self.cmds) \
            + ' ' + ' '.join(self.appendixs)
        # if verbose:
        print('-', cmdline)
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
            # print('-', cmd_filter, '->', ret)
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

#coding: utf-8

import subprocess

'''
  A Command can be divided to multiple CommandParts, each one includes many CommandPart
which provided by a Plugin.
  CommandPart can be a raw string for supportting special compiler, a tuple for
supportting command composition, a lambda/function for supportting config specialization,
and a list of raw string, a list of tuple.
'''
class Command:
    def __init__(self, **kwargs):
        self.executable = kwargs['executable']
        self.name = kwargs['name']
        self.cmds = []
        self.appendixs = [] # collect args which including `"`
        self.dst = ''

    def __str__(self):
        return 'Command:'
    
    def preprocess(self, **kwargs):
        filters = kwargs['filters']
        compositors = kwargs['compositors']

        self.appendixs = []
        self.cmds = [self.executable] # executable must be first element
        for cmd_filter in filters.get(self.name, []):
            self._compositorArgs(compositors, cmd_filter, kwargs)
        
        return kwargs['dst']

    def execute(self):
        # using appendixs to avoid incorrect quote on cmd part which existing
        #   double quote `"`
        cmdline = subprocess.list2cmdline(self.cmds) + ' ' + ' '.join(self.appendixs)
        exitcode,output = subprocess.getstatusoutput(cmdline)
        if exitcode != 0:
            print(cmdline)
            print(output)
            return False
        return True
    
    def _compositorArgs(self, compositors, cmd_filter, kwargs):
        if isinstance(cmd_filter, tuple):
            if len(cmd_filter) >= 2:
                if cmd_filter[0] == 'compositor':
                    compositor = compositors.get(cmd_filter[1])
                    if not callable(compositor):
                        raise Exception("Unhandled compositor name:", cmd_filter)
                    assert(len(cmd_filter) == 3)
                    param = cmd_filter[2]
                    if isinstance(param, str):
                         # support: ('compositor', 'sysroot', self.sysroot)
                        self._addCompositorResult(compositor(param, kwargs))
                    elif isinstance(param, list) or isinstance(param, tuple):
                         # support ('compositor', 'libPath', ['../lib', '../../lib'])
                        for p in param:
                            self._addCompositorResult(compositor(p, kwargs))
                    elif callable(param):
                        # support: ('compositor', 'linkOutput', lambda args: args['dst'])
                        self._addCompositorResult(compositor(param(kwargs), kwargs))
                    else:
                        raise Exception('Invalid filter prefix:', cmd_filter)

                elif cmd_filter[0] == 'args':
                    self._addCompositorResult(cmd_filter[1:])
                    
                else:
                    raise Exception('Invalid filter prefix:', cmd_filter)
        elif callable(cmd_filter):
            self._addCompositorResult(cmd_filter(kwargs))
        else:
            raise Exception('Invalid filter:', cmd_filter)
    
    def _addCompositorResult(self, result):
        if isinstance(result, list) or isinstance(result, tuple):
            for part in result:
                self._addCmdPart(part)
        elif isinstance(result, str):
            self._addCmdPart(result)

    def _addCmdPart(self, part):
        if '"' in part:
            self.appendixs.append(part)
        else:
            self.cmds.append(part)

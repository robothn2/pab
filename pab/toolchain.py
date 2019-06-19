#coding: utf-8

import subprocess

class Toolchain:
    def __init__(self):
        self.plugins = []
        self.registerCompositors = {}
        self.registerCmds = {}

    def addPlugin(self, plugin):
        self.plugins.append(plugin)
        plugin.registerAll(self)
    
    def registerCommand(self, cmd_name, cmd_exec_path):
        if hasattr(self.registerCmds, cmd_name):
            raise('Found duplicate ArgCompositor')
        self.registerCmds[cmd_name] = cmd_exec_path
        
    def registerArgCompositor(self, config, method, func):
        if hasattr(self.registerCompositors, method):
            raise('Found duplicate ArgCompositor')
        self.registerCompositors[method] = func

    def dumpInfo(self):
        pass
    
    def nativeCall(self, cmds):
        print(cmds)
        subprocess.check_call(cmds)

    def processFile(self, config, cat, src, dst):
        print(cat, src, '->', dst)
        if not cat in self.registerCmds:
            return
        
        cmds = [self.registerCmds[cat]]
        for plugin in self.plugins:
            ret = plugin.handleFile(config, cat, src, dst)
            print(plugin.name, 'handleFile() returns', ret)
            if isinstance(ret, list):
                for t in ret:
                    cmds.append(self._compositorArgs(t))
            elif isinstance(ret, tuple):
                cmds.append(self._compositorArgs(ret))
            else:
                print('Unsupport return value:', ret)
        
        self.nativeCall(cmds)
        
    def _compositorArgs(self, args):
        if not isinstance(args, tuple) or len(args) <= 2:
            return
        if args[0] == 'compositor':
            func = self.registerCompositors.get(args[0])
            if not func:
                return
            if isinstance(func, str):
                return func
            if callable(func):
                return func(args[2] if len(args) == 3 else args[2:])
        elif args[0] == 'args':
            return args[1:]
        print('Unsupport compositor:', args)
        
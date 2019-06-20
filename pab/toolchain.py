#coding: utf-8

import subprocess
import logging

class Toolchain:
    def __init__(self, *plugins):
        self.registerCmds = {}
        self.registerCmdFilters = {}
        self.registerCompositors = {}
        self.plugins = []
        for plugin in plugins:
            self.registerPlugin(plugin)

    def registerPlugin(self, plugin):
        self.plugins.append(plugin)
        plugin.registerAll(self)
    
    '''
    Command 提供命令对应的可执行文件路径
    '''
    def registerCommand(self, plugin, cmd_name, cmd_exec_path):
        if hasattr(self.registerCmds, cmd_name):
            raise Exception('Found duplicate ArgCompositor')
        self.registerCmds[cmd_name] = cmd_exec_path
        
    '''
    CommandFilter 参与命令行参数构造
    '''
    def registerCommandFilter(self, plugin, cmd_names, filters_new):
        if isinstance(cmd_names, str):
            self._registerOneCommandFilter(plugin, cmd_names, filters_new)
        elif isinstance(cmd_names, list):
            for cmd_name in cmd_names:
                if isinstance(cmd_name, str):
                    self._registerOneCommandFilter(plugin, cmd_name, filters_new)

    def _registerOneCommandFilter(self, plugin, cmd_name, filters_new):
        if cmd_name in self.registerCmdFilters:
            filters = self.registerCmdFilters[cmd_name]
        else:
            self.registerCmdFilters[cmd_name] = []
            filters = self.registerCmdFilters[cmd_name]
        
        if isinstance(filters_new, list):
            filters += filters_new
        elif isinstance(filters_new, tuple):
            filters.append(filters_new)
        elif callable(filters_new):
            filters.append(filters_new)
        else:
            logging.warning('Unsupport filter:', filters_new)
        
    '''
    ArgCompositor 提供命令行参数合成函数，例如: 每个编译器支持的包含库路径在命令行内写法不同
    '''
    def registerArgCompositor(self, plugin, arg_names, compositor_func):
        if isinstance(arg_names, str):
            self._registerOneArgCompositor(plugin, arg_names, compositor_func)
        elif isinstance(arg_names, list):
            for arg_name in arg_names:
                if isinstance(arg_name, str):
                    self._registerOneArgCompositor(plugin, arg_name, compositor_func)
                    
    def _registerOneArgCompositor(self, plugin, arg_name, compositor_func):
        if hasattr(self.registerCompositors, arg_name):
            raise Exception('Found duplicate ArgCompositor %s' % arg_name)
        self.registerCompositors[arg_name] = compositor_func
        
    def dumpInfo(self):
        print('=toolchain dump begin')
        #print(self.registerCmds)
        for cmd, cmd_filters in self.registerCmdFilters.items():
            print(cmd, cmd_filters)
        for arg, compositor in self.registerCompositors.items():
            print(arg, compositor)
        print('=toolchain dump end')
    
    def _execCommand(self, cmd_name, cmds):
        print('=', cmd_name, cmds)
        out = subprocess.getoutput(cmds)
        print(out)

    def doCommand(self, cmd_name, **kwargs):
        if not cmd_name in self.registerCmds:
            raise Exception('Unsupport Command:', cmd_name)
            return
        
        cmdline = [self.registerCmds[cmd_name]] # executable
        cmd_filters = self.registerCmdFilters.get(cmd_name)
        for cmd_filter in cmd_filters:
            ret = self._compositorArgs(cmd_filter, kwargs)
            #print('filter', cmd_filter, 'returns:', ret)
            if isinstance(ret, list):
                cmdline += ret
            elif isinstance(ret, tuple):
                cmdline += list(ret)
            elif isinstance(ret, str):
                cmdline.append(ret)
        
        self._execCommand(cmd_name, cmdline)
        
    def _compositorArgs(self, cmd_filter, kwargs):
        if isinstance(cmd_filter, tuple):
            if len(cmd_filter) >= 2:
                if cmd_filter[0] == 'compositor':
                    assert(len(cmd_filter) == 3)
                    compositor = self.registerCompositors.get(cmd_filter[1])
                    if callable(compositor):
                        if isinstance(cmd_filter[2], str):
                            return compositor(cmd_filter[2], kwargs)
                        if callable(cmd_filter[2]):
                            return compositor(cmd_filter[2](kwargs), kwargs)
                elif cmd_filter[0] == 'args':
                    return cmd_filter[1:]
        elif callable(cmd_filter):
            return cmd_filter(kwargs)
        raise Exception('Unsupport compositor:', cmd_filter)
        
#coding: utf-8

from ._internal.command import Command

class Toolchain:
    def __init__(self, *plugins):
        self.cmds = {}
        self.cmdFilters = {}
        self.compositors = {}
        self.sourceFileFilters = []
        self.plugins = []
        for plugin in plugins:
            self.registerPlugin(plugin)

    def registerPlugin(self, plugin):
        print('Register plugin:', plugin)
        self.plugins.append(plugin)
        plugin.registerAll(self)
    
    def unregisterPlugin(self, plugin):
        pass
    
    '''
    Command 提供命令对应的可执行文件路径
    '''
    def registerCommand(self, plugin, cmd_name, cmd_exec_path, *cmd_extra_parts):
        if hasattr(self.cmds, cmd_name):
            raise Exception('Found duplicate ArgCompositor')
        self.cmds[cmd_name] = (plugin.name, cmd_exec_path)
        self.registerCommandFilter(plugin, cmd_name, cmd_extra_parts)
        
    '''
    SourceFileFilter 可以根据条件排除文件参与构建
    '''
    def registerSourceFileFilter(self, plugin, filter_func):
        if not callable(filter_func):
            raise Exception('Invalid SourceFileFilter')
        self.sourceFileFilters.append((plugin, filter_func))
        
    '''
    CommandFilter 参与命令行参数构造
    '''
    def registerCommandFilter(self, plugin, cmd_names, filters_new):
        if not filters_new or not cmd_names:
            return
        if isinstance(cmd_names, str):
            self._registerOneCommandFilter(plugin, cmd_names, filters_new)
        elif isinstance(cmd_names, list):
            for cmd_name in cmd_names:
                if isinstance(cmd_name, str):
                    self._registerOneCommandFilter(plugin, cmd_name, filters_new)

    def _registerOneCommandFilter(self, plugin, cmd_name, filters_new):
        if cmd_name in self.cmdFilters:
            filters = self.cmdFilters[cmd_name]
        else:
            self.cmdFilters[cmd_name] = []
            filters = self.cmdFilters[cmd_name]
        
        if isinstance(filters_new, list):
            for filter_one in filters_new:
                filters.append((plugin.name, filter_one))
        elif isinstance(filters_new, tuple):
            filters.append((plugin.name, filters_new))
        elif callable(filters_new):
            filters.append((plugin.name, filters_new))
        else:
            raise Exception('Invalid filter format:', filters_new)
        
    '''
    Compositor 提供命令行参数合成函数，例如: 每个编译器支持的包含库路径在命令行内写法不同
    '''
    def registerCompositor(self, plugin, arg_names, compositor_func):
        if isinstance(arg_names, str):
            self._registerOneCompositor(plugin, arg_names, compositor_func)
        elif isinstance(arg_names, list):
            for arg_name in arg_names:
                if isinstance(arg_name, str):
                    self._registerOneCompositor(plugin, arg_name, compositor_func)
                    
    def _registerOneCompositor(self, plugin, arg_name, compositor_func):
        if hasattr(self.compositors, arg_name):
            raise Exception('Found duplicate ArgCompositor %s' % arg_name)
        self.compositors[arg_name] = (plugin.name, compositor_func)
        
    def dumpInfo(self):
        print('=toolchain dump begin')
        print(self.cmds)
        for cmd, cmd_filters in self.cmdFilters.items():
            print(cmd, cmd_filters)
        for arg, compositor in self.compositors.items():
            print(arg, compositor)
        print('=toolchain dump end')
    
    def doCommand(self, cmd_name, **kwargs):
        if not cmd_name in self.cmds:
            return None # unsupport Command
        src = kwargs['src']
        if isinstance(src, str): # skip Command: link, ar
            for file_filter in self.sourceFileFilters:
                ret, reason = file_filter[1](kwargs)
                if not ret:
                    print('*', cmd_name, kwargs['src'], 'rejected:', reason)
                    return None # file reject by filter
        
        cmd = Command(name=cmd_name, executable=self.cmds[cmd_name][1])
        dst = cmd.preprocess(cmd=cmd_name, filters=self.cmdFilters, compositors=self.compositors, **kwargs)
        print('=', cmd_name, dst)
        return dst if cmd.execute() else None
        
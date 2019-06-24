#coding: utf-8

from ._internal.command import Command

class Toolchain:
    def __init__(self, *plugins):
        self.registerCmds = {}
        self.registerCmdFilters = {}
        self.registerCompositors = {}
        self.registerSourceFileFilters = []
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
    def registerCommand(self, plugin, cmd_name, cmd_exec_path):
        if hasattr(self.registerCmds, cmd_name):
            raise Exception('Found duplicate ArgCompositor')
        self.registerCmds[cmd_name] = cmd_exec_path
        
    '''
    Command 提供命令对应的可执行文件路径
    '''
    def registerSourceFileFilter(self, plugin, filter_func):
        if not callable(filter_func):
            raise Exception('Invalid SourceFileFilter')
        self.registerSourceFileFilters.append(filter_func)
        
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
            raise Exception('Invalid filter format:', filters_new)
        
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
    
    def doCommand(self, cmd_name, **kwargs):
        if not cmd_name in self.registerCmds:
            return None # unsupport Command
        
        if cmd_name != 'link':
            for file_filter in self.registerSourceFileFilters:
                ret, reason = file_filter(kwargs)
                if not ret:
                    print(' reject by SourceFileFilter:', reason)
                    return None # file reject by filter
        
        print('=', cmd_name, kwargs.get('dst'))
        cmd = Command(name=cmd_name, executable=self.registerCmds[cmd_name])
        return cmd.execute(cmd=cmd_name, filters=self.registerCmdFilters, compositors=self.registerCompositors, **kwargs)
        
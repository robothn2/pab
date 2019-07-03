# coding: utf-8

from ._internal.command import Command


class Toolchain:
    def __init__(self, *plugins):
        self.cmds = {}
        self.cmdFilters = {}
        self.compositors = {}
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
    def registerCommand(self, plugin, name, executable,
                        custom_log='src', *extra_parts):
        if hasattr(self.cmds, name):
            raise Exception('Found duplicate ArgCompositor')
        self.cmds[name] = (plugin.name, executable, custom_log)
        self.registerCommandFilter(plugin, name, extra_parts)

    '''
    CommandFilter 参与命令行参数构造
    '''
    def registerCommandFilter(self, plugin, cmd_names, filters):
        if not filters or not cmd_names:
            return
        if isinstance(cmd_names, str):
            self._registerOneCommandFilter(plugin, cmd_names, filters)
        elif isinstance(cmd_names, list):
            for cmd_name in cmd_names:
                if isinstance(cmd_name, str):
                    self._registerOneCommandFilter(plugin, cmd_name, filters)

    def _registerOneCommandFilter(self, plugin, cmd_name, filters_new):
        if cmd_name in self.cmdFilters:
            filters = self.cmdFilters[cmd_name]
        else:
            self.cmdFilters[cmd_name] = []
            filters = self.cmdFilters[cmd_name]

        if isinstance(filters_new, list):
            for filter_one in filters_new:
                filters.append((plugin.name, filter_one))
        elif isinstance(filters_new, tuple) or isinstance(filters_new, str):
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
                    self._registerOneCompositor(plugin, arg_name,
                                                compositor_func)

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
        if cmd_name not in self.cmds:
            return None  # unsupport Command

        src = kwargs['src']
        cmd_entry = self.cmds[cmd_name]
        cmd = Command(name=cmd_name, executable=cmd_entry[1])
        dst = cmd.preprocess(cmd=cmd_name, filters=self.cmdFilters,
                             compositors=self.compositors, **kwargs)
        custom_log = cmd_entry[2]
        if (custom_log == 'src'):
            print('=', cmd_name, src)
        elif (custom_log == 'dst'):
            print('=', cmd_name, dst)
        return dst if cmd.execute(kwargs.get('verbose', False)) else None

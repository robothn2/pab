# Description
pab(python auto build) 是一个自动化构建引擎，实现在自动编译各大开源项目的功能
support projects：ffmpeg, ogre, skia, tensorflow
support Host OS：Windows(10), Linux(Ubuntu 18.04), MacOSX(10.13+)
support Target OS：Windows(7+), Linux(Ubuntu 18.04), MacOSX(10.13+), iOS, Android

# Features
* suggestion on build fail
* 构建流程支持交互模式，失败时可以暂停整个流程，解决后可以继续执行
* 构建流程支持并行模式，尽可能快的执行，但失败时直接退出，无法继续执行

# Modules
> setting 提供配置项访问功能
* 当打开 verbose 选项时，追踪配置的每次修改来源(文件和行)和值，用于调试错误时打印本次构建的修改历史纪录
> builder 构造器主体
> source_files 需要处理的文件集合
> source_file_dispatcher 将文件分类处理 
> command_group_queue 将 source_files 分类，翻译成 command_group 加入队列
> command_group 将 command 翻译成一条或多条 toolchain 命令并执行
> command 提供各种预制和自定义功能
>> compile 提供编译功能
* headers  编译时的头文件包含路径列表
子项字段：content(unique path), source(category, path, line)
支持操作：add, has, dump
来源列表：depend, toolchain, std, environ(path), custom(cmdline), config(configure, cmake)
* flags   编译时标志列表
子项字段：content(unique flag), source(category, path, line), force(True for overwrite final value)
支持操作：add, has, dump
来源列表：toolchain, std, custom(cmdline), config(configure, cmake)
* 编译生成的临时文件仅存在于指定的目的路径，方便清理和加速
* 编译失败时给出建议: 头文件找不到，宏找不到，函数找不到
>> ar      archive 文件管理
>> link    提供链接功能
* 支持将超多 .o 文件分批链接
* 支持依据相同函数名来区分不同指令集
* 链接失败时给出建议
>> sdk     提供sdk制作功能
* sdk public header + static/dynamic library(.a, .so)
* framework xcode .framework
> command_queue 将 command 翻译成一条或多条 toolchain 命令并执行
>> toolchain 编译器命令封装
* 支持操作：cc, cxx, asm, rc, ar, lipo, ld, strip, ranlib, addr, ...
>> system 操作系统命令封装
* 
> utils
* SDK/package 搜索：在本目录、系统环境PATH内搜索
* 头文件搜索
* 
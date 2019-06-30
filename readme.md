# Description
pab(python auto build) is a extendable build engine, used to simply build open source projects, likes: ffmpeg, skia
support Host OS：Windows(10), Linux(Ubuntu 18.04), MacOSX(10.13+)
support Target OS：Windows(7+), Linux(Ubuntu 18.04), MacOSX(10.13+), iOS, Android

# Usage
from pab.builder import Builder
from pab.targets.folder import FolderTarget
from pab.android_ndk.ndk import NDK

compiler = NDK(path='d:/lib/android-ndk-r14b', platform=21, compiler='gcc')
builder = Builder(compiler, target_os='android', arch='x86', cpu='i686', target_platform_ver='10.0.17763.0')

target = FolderTarget(root='~/ffmpeg/libavutil',
                      depth=0, rescan=True,
                      rootBuild='~/ffmpeg/build/libavutil',
                      targetType='sharedLib', # 'executable', 'staticLib', 'sharedLib'
                      includePath='~/ffmpeg',
                      excludeFiles=['tests'])
builder.build(target)

# BuildFlow
* 选择编译器：NDK gcc/llvm, VisualC, IntelC, ...
* 选择目标：OS, Platform, Arch, CPU
* 选择项目：子目录和 Target 对应关系需手动指定，每个 Target 内 Obj 自动按 Arch & CPU 分组，如果有更详细分组需手动指定
* 尝试各种构建系统文件解析生成 Target 树，并将 SourceFiles 分配给各个 Target，支持的构建系统：cmake, configure, gn, subfolder, pab, custom(provider a Module)
* 编译Obj：SourceFile -> Obj
* 生成Product：Target -> (StaticLib, SharedLib, Executable
* 编译Artifact：将公共头文件、库文件、动态库文件、资源文件合并为 SDK, Framework, APP

# Features
* suggestion on build fails
* 依据cmake, configure, 或者手动划分 targets 下的文件，文件可以归属于多个不同 target
* 易于扩充的插件系统
* Extendable BuildFlow: Plugin can register new BuildStep, and insert it into BuildFlow
* 当打开 verbose 选项时，追踪配置的每次修改来源(文件和行)和值，用于调试错误时打印本次构建内指定设置项的修改历史纪录
* 编译生成的临时文件仅存在于指定的目的路径，方便清理和加速
* 编译失败时给出建议: 头文件找不到，宏找不到，函数找不到
* 支持将超多 .o 文件分批链接
* 自动链接不同指令集的相同函数名
* 构建流程支持交互模式，失败时可以暂停整个流程，解决后可以继续执行
* 构建流程支持并行模式，尽可能快的执行，但失败时直接退出，无法继续执行

# Todo
* 支持 Plugin 反注册
* FolderTarget 支持从独立 py 文件内读取，每个开源项目有对应文件，文件力求简单易配置
* 使用 llvm 编译出 arm 架构的 so
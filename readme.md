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
* 尝试各种构建系统文件解析生成 Target 树，并将 SourceFiles 分配给各个 Target，支持的构建系统：cmake, configure, gn, subfolder, pab
* 编译Obj：SourceFile -> Obj
* 生成Target：Target -> (StaticLib, SharedLib, Executable
* 编译Artifact：将公共头文件、库文件、动态库文件、资源文件合并为 SDK, Framework, APP

# Features
* 易于扩充的插件系统
* 当打开 verbose 选项时，追踪配置的每次修改来源(文件和行)和值，用于调试错误时打印本次构建内指定设置项的修改历史纪录
* 编译生成的临时文件仅存在于指定的目的路径，方便清理和加速
* 支持一次链接超多 .o 文件

# Todo
* FolderTarget 支持从独立 py 文件内读取，每个开源项目有对应文件，文件力求简单易配置 (参考 skia/BUILD.gn)
*   自动分析源文件名对应的 arch(根据目录名、名字), cpu(根据目录名、名字), cmd(根据后缀)，自动排除和当前配置不匹配的源文件
*   由文件自己决定使用哪种 Command 处理，在编译失败时自动分析失败原因
*   Plugin rename to Config, it includes: defines, libs, sources, ccflags, cxxflags, libPath, includePath, ldflags, etc.
*   允许单个 Target 内既有 c 也有 c++ 源文件，分别组合不同 Config 进行编译
*   通过 target 依赖性自动推导构建流程
*   依据cmake, configure, 或者手动划分 targets 下的文件，文件可以归属于多个不同 target
* 仅传入 cpu，解析出 arch 和 cpu (参考 ffmpeg/configure)
*   自动链接不同指令集的相同函数名
* 使用 llvm/clang 编译出 arm 架构的 so
* 依据传入的 target_os 和 target_cpu 自动选择 toolchain, compiler
* 支持 Config 反注册
* 编译失败时提供建议
*   头文件找不到：提示该头文件在哪里
*   宏找不到：
*   链接时函数找不到：提示该函数需要链接哪个 lib
* 构建流程支持交互模式，失败时可以暂停整个流程，解决后可以继续执行
* 构建流程支持并行模式，尽可能快的执行，但失败时直接退出，无法继续执行
* 输出 ninja 脚本

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
* 生成Target：Target -> (StaticLib, SharedLib, Executable)
* 编译Artifact：将公共头文件、库文件、动态库文件、资源文件合并为 SDK, Framework, APP

# Features
* 易于扩充的插件系统
* 当打开 verbose 选项时，追踪配置的每次修改来源(文件和行)和值，用于调试错误时打印本次构建内指定设置项的修改历史纪录
* 编译生成的临时文件仅存在于指定的目的路径，方便清理和加速
* 支持一次链接超多 .o 文件

# Todo
* Target from standalone python scripts
*   Config support: ccflags, cxxflags, ldflags, lib_dirs, libs
*   通过 target 依赖性自动推导构建流程
* 使用 llvm/clang 编译出 arm 架构的 so
* 显示变量的多途径来源和变化历史
* suggestion on fails:
*   header not found: search header file in system
*   macro not found:
*   unresolved referenced function: link to which lib
* interactive build mode: pause build flow, can resume it too
* parellel build mode: as possible as soon, exit on fails, cannot resume
* output ninja build script


# Description
pab(python auto build) is a extendable build engine, used to simply build open source projects, likes: ffmpeg, skia
support Host OS：Windows(10), Linux(Ubuntu 18.04), MacOSX(10.13+)
support Target OS：Windows(7+), Linux(Ubuntu 18.04), MacOSX(10.13+), iOS, Android

# Usage
from pab.builder import Builder
from pab.request import Request
from pab.targets.pab_folder import PabTargets
from pab.android_ndk.ndk import NDK

compiler = NDK(path='d:/lib/android-ndk-r14b', platform=24, compiler='clang')
request = Request(target_os='android',
                  target_cpu='x86_64',
                  stl='gnu-libstdc++',
                  root_build='D:/lib/build')

target = PabTargets(root='test/base', rootSource='D:/lib/chromium/base')
builder = Builder(request, compiler)
builder.build(target, top=0, check=False)

# BuildFlow
* 选择编译器：NDK gcc/llvm, VisualC, IntelC, ...
* 选择目标：target_os, target_cpu, target_platform(android: api level, win: sdk version)
* 选择项目：Target 通过 py 文件定义
* 尝试各种构建系统文件解析生成 Target 树，并将 SourceFiles 分配给各个 Target，支持的构建系统：cmake, configure, gn, subfolder, pab
* 编译Obj：SourceFile -> Obj
* 生成Target：Target -> (StaticLib, SharedLib, Executable)
* 编译Artifact：将公共头文件、库文件、动态库文件、资源文件合并为 SDK, Framework, APP

# Features
* 通过 python 文件定义 Targets
* 编译生成的临时文件仅存在于指定的目的路径，方便清理和加速
* 支持一次链接超多 .o 文件

# Todo
* 统计 Target 链接时少掉哪些引用
* OS 可能有多个标志，例如：MacOS 还会有 Posix
* 通过 target 依赖性自动推导构建流程
* 使用 clang 编译出 arm 架构的 so
* 显示变量的来源和变化历史
* suggestion on fails:
*   header not found: search header file in system
*   macro not found:
*   unresolved referenced function: link to which lib
* interactive build mode: pause build flow, can resume it too
* parellel build mode: as possible as soon, exit on fails, cannot resume
* output ninja build script


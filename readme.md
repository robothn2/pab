# Description
pab(python auto build) is a extendable build engine, for simply build open source projects: ffmpeg, skia, ogre
support Host OS：Windows(10), Linux(Ubuntu 18.04), MacOSX(10.13+)
support Target OS：Windows(7+), Linux(Ubuntu 18.04), MacOSX(10.13+), iOS, Android

# Usage
from pab.builder import Builder
from pab.request import Request
from pab.targets.pab_folder import PabTargets
from pab.android_ndk.ndk import NDK

compiler = NDK(path='d:/lib/android-ndk-r14b', platform=9, compiler='gcc')
request = Request(target_os='android', target_cpu='armv7a',
                  stl='llvm-libc++',
                  root_build='D:/lib/build')
target = PabTargets(root='test/base', rootSource='D:/lib/chromium/base')
builder = Builder(request, compiler)
builder.build(target, top=0, check=False)

# BuildFlow
* 编译器：NDK gcc/llvm, VisualC, IntelC, LLVM8.0
* 构建需求：target_os, target_cpu, target_platform(android: api level, win: sdk version)
* 项目定义：通过定义文件(.py)解析 Targets
* 编译: Target.sources -> intermediate .o files
* 生成: .o files -> (StaticLib, SharedLib, Executable)
* 安装: 将公共头文件、库文件、动态库文件、资源文件合并为 SDK, Framework, APP

# Features
* 通过 python 文件定义 Targets，支持依赖关系
* 编译生成的临时文件仅存在于指定的目的路径，方便清理和加速
* 支持一次链接超多 .o 文件

# Todo
* 定义文件: 支持环境检测: check_header, check_function
* 定义文件: 支持生成头文件: export_header, gen_header
* 使用 clang 编译出 arm 架构的 so
* 显示变量的来源和变化历史
* suggestion on fails:
*   header not found: search header file in system
*   macro not found:
*   unresolved referenced function: link to which lib
* interactive build mode: pause build flow, can resume it too
* parellel build mode: as possible as soon, exit on fails, cannot resume
* output ninja build script


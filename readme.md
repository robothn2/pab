# Description
* pab(python auto build) is a extendable build engine, for simply build open source projects: ffmpeg, skia, ogre
* support Host OS：Windows(10), Linux(Ubuntu 18.04), MacOSX(10.13+)
* support Target OS：Windows(7+), Linux(Ubuntu 18.04), MacOSX(10.13+), iOS, Android

# Usage
    from pab.builder import Builder
    from pab.request import Request
    from pab.targets.pab_folder import PabTargets
    from pab.android_ndk.ndk import NDK

    compiler = NDK(path='~/lib/android-ndk-r14b', platform=9, compiler='gcc', stl='llvm-libc++')
    #compiler = MSVC(ver='14.0', platform='8.1')
    request = Request(target_os='android', target_cpu='armv7a', root_build='~/lib/build')
    builder = Builder(request, compiler, dryrun=True, job=10)
    builder.build(PabTargets(root='test/base'))

# BuildFlow
* Compiler: NDK gcc/llvm, VisualC, IntelC, LLVM8.0
* Request: target_os, target_cpu, target_platform(android: api level, win: sdk version)
* Define: define Targets in python script
* Compile: Target.sources -> .o files
* Link: .o files -> (StaticLib, SharedLib, Executable)
* Install: generate SDK, Framework, APP

# Features
* target script: define Targets in python script, support dependencies
* link many .o files by using @FILE

# Todo
* target script: support check_header, check_function
* target script: support export_header, gen_header
* support tracing source & history on specified variable
* suggestion on fails: header not found: search header file in system
* suggestion on fails: unresolve referenced function: link to which lib
* interactive build mode: pause/resume build flow
* generate ninja build script
* generate visual studio project
* generate xcode project

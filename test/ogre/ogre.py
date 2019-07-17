# coding: utf-8

lib_common = {
    'uri': 'common',
    'type': 'config',
    'cxxflags': [
        '-std=c++11',
        ],
    'source_base_dir': 'd:/lib/ogre',
    'install_dirs_map': {
        },
}


def dyn_common(lib, context):
    c = context
    versions = c.parseFile(
            'OgreMain/include/OgrePrerequisites.h',
            r'^\s*#define\s+(OGRE_VERSION_\S+)\s+(.+)')

    c.setVar('OGRE_VERSION', '{}.{}.{}{}'.format(
            versions['OGRE_VERSION_MAJOR'], versions['OGRE_VERSION_MINOR'],
            versions['OGRE_VERSION_PATCH'], versions['OGRE_VERSION_SUFFIX']))
    c.setVar('OGRE_SOVERSION', '{}.{}.{}'.format(
            versions['OGRE_VERSION_MAJOR'], versions['OGRE_VERSION_MINOR'],
            versions['OGRE_VERSION_PATCH']))
    c.setVar('OGRE_VERSION_DASH_SEPARATED', '{}-{}-{}{}'.format(
            versions['OGRE_VERSION_MAJOR'], versions['OGRE_VERSION_MINOR'],
            versions['OGRE_VERSION_PATCH'], versions['OGRE_VERSION_SUFFIX']))

    print('Configuring OGRE', c.OGRE_VERSION)
    target_os = c.target_os_tags
    target_cpu = c.target_cpu_tags
    compiler = c.compiler_tags
    if 'sse' in target_cpu:
        lib.cxxflags += '-msse'

    if 'vs' in compiler:
        lib.defines += ['_MT', '_USRDLL']
        lib.cxxflags += ['/wd4661', '/wd4251', '/wd4275',
                         '/fp:fast', '/Oi', '/bigobj', '/MP']
    elif 'mingw' in compiler:
        lib.defines += ['_WIN32_WINNT=0x0501', '_USRDLL']
        lib.cxxflags += ['-fno-tree-slp-vectorize']
    elif 'gcc' in compiler or 'clang' in compiler:
        lib.defines += 'OGRE_GCC_VISIBILITY'

    if 'apple' in target_os:
        #SET(CMAKE_SIZEOF_VOID_P 4)
        #set(CMAKE_XCODE_ATTRIBUTE_GCC_VERSION "com.apple.compilers.llvm.clang.1_0")
        lib.stl = 'libc++'
        if 'ios' in target_os:
            lib.type = 'staticLib'
            '''
            set(CMAKE_EXE_LINKER_FLAGS "-framework OpenGLES -framework Foundation -framework CoreGraphics -framework QuartzCore -framework UIKit")
            set(XCODE_ATTRIBUTE_GCC_UNROLL_LOOPS "YES")
            set(XCODE_ATTRIBUTE_LLVM_VECTORIZE_LOOPS "YES")
            set(XCODE_ATTRIBUTE_CODE_SIGN_IDENTITY "iPhone Developer")
            set(XCODE_ATTRIBUTE_GCC_PRECOMPILE_PREFIX_HEADER "YES")
            set(OGRE_BUILD_RENDERSYSTEM_GLES2 TRUE CACHE BOOL "Forcing OpenGL ES 2 RenderSystem for iOS" FORCE)
            set(OGRE_STATIC TRUE CACHE BOOL "Forcing static build for iOS" FORCE)
            set(MACOSX_BUNDLE_GUI_IDENTIFIER "com.yourcompany.\${PRODUCT_NAME:rfc1034identifier}")
            '''
        else:
            c.setVar('XCODE_ATTRIBUTE_SDKROOT', 'macosx')
            # 'xcodebuild -version -sdk "${XCODE_ATTRIBUTE_SDKROOT}" Path | head -n 1 OUTPUT_VARIABLE CMAKE_OSX_SYSROOT'
            c.setVar('CMAKE_OSX_SYSROOT', 'macosx')

            # Make sure that the OpenGL render system is selected for non-iOS Apple builds
            c.setVar('OGRE_BUILD_RENDERSYSTEM_GLES2', False)

    elif 'android' in target_os:
        c.setVar('OGRE_PLATFORM', 'OGRE_PLATFORM_ANDROID')
        c.options += [
                ('OGRE_CONFIG_ENABLE_VIEWPORT_ORIENTATIONMODE', False),
                ('OGRE_BUILD_ANDROID_JNI_SAMPLE', False),  #
                ('OGRE_BUILD_RENDERSYSTEM_GLES2', True),  # Forcing OpenGL ES 2 RenderSystem for Android
                ('OGRE_BUILD_PLUGIN_PCZ', False),  # Disable pcz on Android
                ('OGRE_BUILD_PLUGIN_BSP', False),  # Disable bsp scenemanager on Android
                ('OGRE_BUILD_TOOLS', False),  # Disable tools on Android
                ('OGRE_STATIC', True),  # Forcing static build for Android
                ]
    elif 'win' in target_os:
        pass

    if c.getOption('OGRE_BUILD_COMPONENT_MESHLODGENERATOR'):
        c.setVar('OGRE_CONFIG_ENABLE_MESHLOD', True)

    # Enable the PVRTC codec if OpenGL ES is being built
    if c.getOption('OGRE_BUILD_RENDERSYSTEM_GLES2'):
        c.setVar('OGRE_CONFIG_ENABLE_PVRTC', True)
        c.setVar('OGRE_CONFIG_ENABLE_ETC', True)

    # Enable the ETC codec if OpenGL 3+ is being built
    if c.getOption('OGRE_BUILD_RENDERSYSTEM_GL3PLUS'):
        c.setVar('OGRE_CONFIG_ENABLE_ETC', True)

'''
configure_file("${OGRE_TEMPLATES_DIR}/version.txt.in" "${OGRE_BINARY_DIR}/version.txt" @ONLY)

set(OGRE_RESOURCEMANAGER_STRICT "2" CACHE STRING
  "Make ResourceManager strict for faster operation. Possible values:
  0 - OFF search in all groups twice - for case sensitive and insensitive lookup [DEPRECATED]
  1 - PEDANTIC require an explicit resource group. Case sensitive lookup.
  2 - STRICT search in default group if not specified otherwise. Case sensitive lookup.
  ")
set_property(CACHE OGRE_RESOURCEMANAGER_STRICT PROPERTY STRINGS 0 1 2)

    cmake_dependent_option(OGRE_BUILD_RENDERSYSTEM_D3D9 "Build Direct3D9 RenderSystem" TRUE "WIN32;DirectX9_FOUND;NOT WINDOWS_STORE;NOT WINDOWS_PHONE" FALSE)
    cmake_dependent_option(OGRE_BUILD_RENDERSYSTEM_D3D11 "Build Direct3D11 RenderSystem" TRUE "WIN32;DirectX11_FOUND OR WINDOWS_STORE OR WINDOWS_PHONE" FALSE)
    cmake_dependent_option(OGRE_BUILD_RENDERSYSTEM_GL3PLUS "Build OpenGL 3+ RenderSystem" TRUE "OPENGL_FOUND;NOT WINDOWS_STORE;NOT WINDOWS_PHONE" FALSE)
    cmake_dependent_option(OGRE_BUILD_RENDERSYSTEM_GL "Build OpenGL RenderSystem" TRUE "OPENGL_FOUND;NOT APPLE_IOS;NOT WINDOWS_STORE;NOT WINDOWS_PHONE" FALSE)
    cmake_dependent_option(OGRE_BUILD_RENDERSYSTEM_GLES2 "Build OpenGL ES 2.x RenderSystem" FALSE "OPENGLES2_FOUND;NOT WINDOWS_STORE;NOT WINDOWS_PHONE" FALSE)
    option(OGRE_BUILD_PLUGIN_BSP "Build BSP SceneManager plugin" TRUE)
    option(OGRE_BUILD_PLUGIN_OCTREE "Build Octree SceneManager plugin" TRUE)
    option(OGRE_BUILD_PLUGIN_PFX "Build ParticleFX plugin" TRUE)
    cmake_dependent_option(OGRE_BUILD_PLUGIN_PCZ "Build PCZ SceneManager plugin" TRUE "" FALSE)
    cmake_dependent_option(OGRE_BUILD_COMPONENT_PAGING "Build Paging component" TRUE "" FALSE)
    cmake_dependent_option(OGRE_BUILD_COMPONENT_MESHLODGENERATOR "Build MeshLodGenerator component" TRUE "" FALSE)
    cmake_dependent_option(OGRE_BUILD_COMPONENT_TERRAIN "Build Terrain component" TRUE "" FALSE)
    cmake_dependent_option(OGRE_BUILD_COMPONENT_VOLUME "Build Volume component" TRUE "" FALSE)
    cmake_dependent_option(OGRE_BUILD_COMPONENT_PROPERTY "Build Property component" TRUE "" FALSE)
    cmake_dependent_option(OGRE_BUILD_PLUGIN_CG "Build Cg plugin" TRUE "Cg_FOUND;NOT APPLE_IOS;NOT WINDOWS_STORE;NOT WINDOWS_PHONE" FALSE)
    cmake_dependent_option(OGRE_BUILD_COMPONENT_OVERLAY "Build Overlay component" TRUE "FREETYPE_FOUND" FALSE)
    option(OGRE_BUILD_COMPONENT_HLMS "Build HLMS component" TRUE)
    cmake_dependent_option(OGRE_BUILD_COMPONENT_BITES "Build OgreBites component" TRUE "OGRE_BUILD_COMPONENT_OVERLAY" FALSE)
    cmake_dependent_option(OGRE_BUILD_COMPONENT_PYTHON "Build Python bindings" TRUE "NOT OGRE_STATIC" FALSE)
    option(OGRE_BUILD_COMPONENT_JAVA "Build Java (JNI) bindings" TRUE)
    option(OGRE_BUILD_COMPONENT_RTSHADERSYSTEM "Build RTShader System component" TRUE)
    cmake_dependent_option(OGRE_BUILD_RTSHADERSYSTEM_CORE_SHADERS "Build RTShader System FFP core shaders" TRUE "OGRE_BUILD_COMPONENT_RTSHADERSYSTEM" FALSE)
    cmake_dependent_option(OGRE_BUILD_RTSHADERSYSTEM_EXT_SHADERS "Build RTShader System extensions shaders" TRUE "OGRE_BUILD_COMPONENT_RTSHADERSYSTEM" FALSE)

    cmake_dependent_option(OGRE_BUILD_SAMPLES "Build Ogre demos" TRUE "OGRE_BUILD_COMPONENT_OVERLAY;OGRE_BUILD_COMPONENT_BITES" FALSE)
    cmake_dependent_option(OGRE_BUILD_TOOLS "Build the command-line tools" TRUE "NOT APPLE_IOS;NOT WINDOWS_STORE;NOT WINDOWS_PHONE" FALSE)
    cmake_dependent_option(OGRE_BUILD_XSIEXPORTER "Build the Softimage exporter" FALSE "Softimage_FOUND" FALSE)
    cmake_dependent_option(OGRE_BUILD_LIBS_AS_FRAMEWORKS "Build frameworks for libraries on OS X." TRUE "APPLE;NOT OGRE_BUILD_PLATFORM_APPLE_IOS" FALSE)
    option(OGRE_BUILD_TESTS "Build the unit tests & PlayPen" FALSE)
    option(OGRE_CONFIG_DOUBLE "Use doubles instead of floats in Ogre" FALSE)
    option(OGRE_CONFIG_NODE_INHERIT_TRANSFORM "Tells the node whether it should inherit full transform from it's parent node or derived position, orientation and scale" FALSE)
    set(OGRE_CONFIG_THREADS "3" CACHE STRING
    	"Enable Ogre thread safety support for multithreading. Possible values:
    	0 - no thread safety. DefaultWorkQueue is not threaded.
    	1 - background resource preparation and loading is thread safe. Threaded DefaultWorkQueue. [DEPRECATED]
    	2 - only background resource preparation is thread safe. Threaded DefaultWorkQueue. [DEPRECATED]
    	3 - no thread safety. Threaded DefaultWorkQueue."
    )
    set_property(CACHE OGRE_CONFIG_THREADS PROPERTY STRINGS 0 1 2 3)
    set(OGRE_CONFIG_THREAD_PROVIDER "std" CACHE STRING
    	"Select the library to use for thread support. Possible values:
    	boost - Boost thread library. [DEPRECATED]
    	poco  - Poco thread library. [DEPRECATED]
    	tbb   - ThreadingBuildingBlocks library. [DEPRECATED]
    	std   - STL thread library (requires compiler support)."
    )
    set_property(CACHE OGRE_CONFIG_THREAD_PROVIDER PROPERTY STRINGS boost poco tbb std)
    cmake_dependent_option(OGRE_BUILD_PLUGIN_FREEIMAGE "Build FreeImage codec." TRUE "FreeImage_FOUND" FALSE)
    cmake_dependent_option(OGRE_BUILD_PLUGIN_EXRCODEC "Build EXR Codec plugin" TRUE "OPENEXR_FOUND;" FALSE)
    option(OGRE_BUILD_PLUGIN_STBI "Enable STBI image codec." TRUE)
    option(OGRE_CONFIG_ENABLE_MESHLOD "Enable Mesh Lod." TRUE)
    option(OGRE_CONFIG_ENABLE_DDS "Build DDS codec." TRUE)
    option(OGRE_CONFIG_ENABLE_PVRTC "Build PVRTC codec." FALSE)
    option(OGRE_CONFIG_ENABLE_ETC "Build ETC codec." TRUE)
    option(OGRE_CONFIG_ENABLE_ASTC "Build ASTC codec." FALSE)
    option(OGRE_CONFIG_ENABLE_QUAD_BUFFER_STEREO "Enable stereoscopic 3D support" FALSE)
    cmake_dependent_option(OGRE_CONFIG_ENABLE_ZIP "Build ZIP archive support. If you disable this option, you cannot use ZIP archives resource locations. The samples won't work." TRUE "ZZip_FOUND" FALSE)
    option(OGRE_CONFIG_ENABLE_VIEWPORT_ORIENTATIONMODE "Include Viewport orientation mode support." FALSE)
    cmake_dependent_option(OGRE_CONFIG_ENABLE_GLES2_CG_SUPPORT "Enable Cg support to ES 2 render system" FALSE "OGRE_BUILD_RENDERSYSTEM_GLES2" FALSE)
    cmake_dependent_option(OGRE_CONFIG_ENABLE_GLES2_GLSL_OPTIMISER "Enable GLSL optimiser use in GLES 2 render system" FALSE "OGRE_BUILD_RENDERSYSTEM_GLES2" FALSE)
    cmake_dependent_option(OGRE_CONFIG_ENABLE_GL_STATE_CACHE_SUPPORT "Enable OpenGL state cache management" FALSE "OGRE_BUILD_RENDERSYSTEM_GL OR OGRE_BUILD_RENDERSYSTEM_GLES2 OR OGRE_BUILD_RENDERSYSTEM_GL3PLUS" FALSE)
    cmake_dependent_option(OGRE_CONFIG_ENABLE_GLES3_SUPPORT "Enable OpenGL ES 3.x Features" FALSE "OPENGLES3_FOUND;OGRE_BUILD_RENDERSYSTEM_GLES2" FALSE)
    option(OGRE_CONFIG_ENABLE_TBB_SCHEDULER "Enable TBB's scheduler initialisation/shutdown." TRUE)
    # Customise what to install
    option(OGRE_INSTALL_CMAKE "Install CMake scripts." TRUE)
    option(OGRE_INSTALL_SAMPLES "Install Ogre demos." TRUE)
    option(OGRE_INSTALL_TOOLS "Install Ogre tools." TRUE)
    option(OGRE_INSTALL_DOCS "Install documentation." TRUE)
    option(OGRE_INSTALL_SAMPLES_SOURCE "Install samples source files." FALSE)
    cmake_dependent_option(OGRE_INSTALL_PDB "Install debug pdb files" TRUE "MSVC" FALSE)
    option(OGRE_PROFILING "Enable internal profiling support." FALSE)
    cmake_dependent_option(OGRE_CONFIG_STATIC_LINK_CRT "Statically link the MS CRT dlls (msvcrt)" FALSE "MSVC" FALSE)
    set(OGRE_LIB_DIRECTORY "lib${LIB_SUFFIX}" CACHE STRING "Install path for libraries, e.g. 'lib64' on some 64-bit Linux distros.")

# Setup RenderSystems
add_subdirectory(RenderSystems)

# Setup Plugins
add_subdirectory(PlugIns)

# Setup Components
add_subdirectory(Components)

# Install media files
if (OGRE_INSTALL_SAMPLES OR OGRE_INSTALL_SAMPLES_SOURCE)
  add_subdirectory(Samples/Media)
endif ()
'''

lib_OgreMain = {
    'uri': 'OgreMain',
    'source_base_dir': 'd:/lib/ogre/OgreMain',
    'type': 'staticLib',
    'options': {
        'OGRE_CONFIG_ENABLE_DDS': True,
        'OGRE_CONFIG_ENABLE_PVRTC': True,
        'OGRE_CONFIG_ENABLE_ETC': True,
        'OGRE_CONFIG_ENABLE_ASTC': True,
        'OGRE_CONFIG_ENABLE_ZIP': True,
        },
    'public_include_dirs': [],
    'include_dirs': [
        'include',
        'include/Threading',
        'src',
        ],
    'defines': [],
    'ccflags': [],
    'libs': [],

    'configs': [
        'common',
        ],
    'deps': [
        'freetype',
        'zziplib',
        ],
    'install_dirs_map': {
        'include': 'include/OGRE',
        },
    'public_headers': [
        'include/*.h',
        'include/Threading/OgreThreadDefinesNone.h',
        'include/Threading/OgreDefaultWorkQueueStandard.h',
        ],
    'sources': [
        'src/*.cpp',
        'src/Threading/OgreDefaultWorkQueueStandard.cpp',
        ],
}


'''
get_native_precompiled_header(OgreMain)
add_native_precompiled_header(OgreMain 'src/OgreStableHeaders.h')

generate_export_header(OgreMain
    EXPORT_MACRO_NAME _OgreExport
    NO_EXPORT_MACRO_NAME _OgrePrivate
    DEPRECATED_MACRO_NAME OGRE_DEPRECATED
    EXPORT_FILE_NAME ${CMAKE_BINARY_DIR}/include/OgreExports.h)
target_include_directories(OgreMain PUBLIC
  '$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>'
  '$<BUILD_INTERFACE:${OGRE_BINARY_DIR}/include>'
  $<INSTALL_INTERFACE:include/OGRE>)

set_target_properties(OgreMain PROPERTIES VERSION ${OGRE_SOVERSION} SOVERSION ${OGRE_SOVERSION})
'''

def dyn_OgreMain(lib, context):
    target_os = context.target_os_tags

    # Remove optional header files
    lib.sources -= [
        'src/OgreFileSystemLayerNoOp.cpp',
        'src/OgreDDSCodec.cpp',
        'src/OgrePVRTCCodec.cpp',
        'src/OgreETCCodec.cpp',
        'src/OgreZip.cpp',
        'src/OgreSearchOps.cpp',
        ]
    lib.headers -= [
        'include/OgreDDSCodec.h',
        'include/OgrePVRTCCodec.h',
        'include/OgreETCCodec.h',
        'include/OgreZip.h',
        ]

    if context.getOption('OGRE_CONFIG_ENABLE_DDS'):
        lib.headers += 'include/OgreDDSCodec.h'
        lib.sources += 'src/OgreDDSCodec.cpp'
    if context.getOption('OGRE_CONFIG_ENABLE_PVRTC'):
        lib.headers += 'include/OgrePVRTCCodec.h'
        lib.sources += 'src/OgrePVRTCCodec.cpp'
    if context.getOption('OGRE_CONFIG_ENABLE_ETC'):
        lib.headers += 'include/OgreETCCodec.h'
        lib.sources += 'src/OgreETCCodec.cpp'
    if context.getOption('OGRE_CONFIG_ENABLE_ASTC'):
        lib.headers += 'include/OgreASTCCodec.h'
        lib.sources += 'src/OgreASTCCodec.cpp'
    if context.getOption('OGRE_CONFIG_ENABLE_ZIP'):
        lib.headers += 'include/OgreZip.h'
        lib.sources += 'src/OgreZip.cpp'
        if 'android' in target_os:
            lib.defines += 'ZZIP_OMIT_CONFIG_H'
        if 'win' in target_os:
            lib.defines += 'ZZIP_DLL'
            lib.libs += 'zlib'
        else:
            lib.libs += 'z'
        lib.deps += 'zziplib'

    if 'win' in target_os:
        lib.files += 'src/WIN32/*.cpp'
    if 'apple' in target_os:
        '''
        if(OGRE_BUILD_LIBS_AS_FRAMEWORKS)
            set_target_properties(OgreMain PROPERTIES	OUTPUT_NAME Ogre)
        endif()
        '''
        if 'ios' in target_os:
            lib.include_dirs += 'src/iOS'
            lib.sources += ['src/iOS/*.cpp', 'src/iOS/*.mm']
            lib.libs = []
            # set_target_properties(OgreMain PROPERTIES INSTALL_NAME_DIR 'OGRE')
        else:
            lib.include_dirs += 'src/OSX'
            lib.sources += ['src/OSX/*.cpp', 'src/OSX/*.mm']
            lib.ldflags += ['-framework', 'IOKit', '-framework', 'Cocoa',
                            '-framework', 'Carbon', '-framework', 'OpenGL',
                            '-framework', 'CoreVideo']

            '''
            set(OGRE_OSX_BUILD_CONFIGURATION '$(PLATFORM_NAME)/$(CONFIGURATION)')

            if(OGRE_BUILD_LIBS_AS_FRAMEWORKS)
              add_custom_command(TARGET OgreMain POST_BUILD
                  COMMAND mkdir ARGS -p ${OGRE_BINARY_DIR}/lib/${OGRE_OSX_BUILD_CONFIGURATION}/Ogre.framework/Headers/Threading
                  COMMAND ditto
                  ${OGRE_SOURCE_DIR}/OgreMain/include/Threading/*.h ${OGRE_BINARY_DIR}/lib/${OGRE_OSX_BUILD_CONFIGURATION}/Ogre.framework/Headers/Threading
                  COMMAND cd ${OGRE_BINARY_DIR}/lib/${OGRE_OSX_BUILD_CONFIGURATION}/Ogre.framework/Headers
                  )

              foreach(HEADER_PATH ${THREAD_HEADER_FILES})
                  get_filename_component(HEADER_FILE ${HEADER_PATH} NAME)
                  set(FWK_HEADER_PATH ${OGRE_BINARY_DIR}/lib/${OGRE_OSX_BUILD_CONFIGURATION}/Ogre.framework/Headers/${HEADER_FILE})
                  add_custom_command(TARGET OgreMain POST_BUILD
                      COMMAND rm -f ${FWK_HEADER_PATH}
                      )
              endforeach()
            endif()

            ogre_config_framework(OgreMain)
            '''

    if 'android' in target_os:
        # required by OgrePlatformInformation.cpp
        lib.include_dirs += '${ANDROID_NDK}/sources/android/cpufeatures'
        lib.sources += 'src/Android/*.cpp'
        lib.libs += ['atomic', 'dl']
    if 'unix' in target_os:
        lib.sources += 'src/GLX/*.cpp'
        lib.libs += 'pthread'
    if 'win' not in target_os:
        lib.sources += 'src/OgreSearchOps.cpp'

install = {
    'uri': 'install',
    'source_base_dir': 'd:/lib/ogre',
    'type': 'config',
    'deps': [
        'OgreMain',
        ],
    'install_dirs_map': {
        '': 'include/OGRE',
        },
    'public_headers': [
        'include/OgreBuildSettings.h',
        'include/OgreExports.h',
        ],
}

export_libs = [
    (lib_common, None),
    (lib_OgreMain, dyn_OgreMain),
    (install, None),
]

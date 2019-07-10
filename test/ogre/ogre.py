# coding: utf-8

lib_common = {
    'uri': 'common',
    'type': 'config',
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

'''
set(OGRE_TEMPLATES_DIR "${OGRE_SOURCE_DIR}/CMake/Templates")
set(OGRE_WORK_DIR ${OGRE_BINARY_DIR})

configure_file("${OGRE_TEMPLATES_DIR}/version.txt.in" "${OGRE_BINARY_DIR}/version.txt" @ONLY)

# determine if we are compiling for a 32bit or 64bit system
if (APPLE AND NOT ANDROID)
  SET(CMAKE_SIZEOF_VOID_P 4)
  set(CMAKE_XCODE_ATTRIBUTE_GCC_VERSION "com.apple.compilers.llvm.clang.1_0")
  set(CMAKE_XCODE_ATTRIBUTE_CLANG_CXX_LANGUAGE_STANDARD "c++11")
  set(CMAKE_XCODE_ATTRIBUTE_CLANG_CXX_LIBRARY "libc++")

  # otherwise apple defines a macro named check that conflicts with boost
  add_definitions(-D__ASSERT_MACROS_DEFINE_VERSIONS_WITHOUT_UNDERSCORES=0)
endif ()

include(CheckTypeSize)
CHECK_TYPE_SIZE("void*" OGRE_PTR_SIZE BUILTIN_TYPES_ONLY)
if (OGRE_PTR_SIZE EQUAL 8)
  set(OGRE_PLATFORM_X64 TRUE)
else ()
  set(OGRE_PLATFORM_X64 FALSE)
endif ()

# Set compiler specific build flags
if (NOT ANDROID AND UNIX OR MINGW)
  include(CheckCXXCompilerFlag)
  check_cxx_compiler_flag(-msse OGRE_GCC_HAS_SSE)
  if (OGRE_GCC_HAS_SSE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -msse")
  endif ()
endif()

if(UNIX)
  # This is a set of sensible warnings that provide meaningful output
  set(OGRE_WARNING_FLAGS "-Wall -Winit-self -Wcast-qual -Wwrite-strings -Wextra -Wundef -Wmissing-declarations -Wno-unused-parameter -Wshadow -Wno-missing-field-initializers -Wno-long-long")
  if (EMSCRIPTEN)
      set(OGRE_WARNING_FLAGS "${OGRE_WARNING_FLAGS} -Wno-warn-absolute-paths")
  endif ()
  set(CMAKE_CXX_FLAGS "${OGRE_WARNING_FLAGS} ${CMAKE_CXX_FLAGS}")
endif ()
if (MSVC)
  add_definitions(-D_MT -D_USRDLL)
  # MSVC does not like Ogre::Singleton (header pragma is enough for MSVC2015+ though)
  add_definitions(/wd4661)
  if (CMAKE_BUILD_TOOL STREQUAL "nmake")
    # set variable to state that we are using nmake makefiles
	set(NMAKE TRUE)
  endif ()
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /fp:fast")
  # Enable intrinsics on MSVC in debug mode
  set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Oi")
  if (CMAKE_CL_64)
    # Visual Studio bails out on debug builds in 64bit mode unless
	# this flag is set...
	set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /bigobj")
	set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELWITHDEBINFO} /bigobj")
  endif ()

  if (OGRE_PROJECT_FOLDERS)
    # Turn on the ability to create folders to organize projects (.vcproj)
    # It creates "CMakePredefinedTargets" folder by default and adds CMake
    # defined projects like INSTALL.vcproj and ZERO_CHECK.vcproj
    set_property(GLOBAL PROPERTY USE_FOLDERS ON)
  endif()

  if (MSVC_VERSION GREATER 1500 OR MSVC_VERSION EQUAL 1500)
    option(OGRE_BUILD_MSVC_MP "Enable build with multiple processes in Visual Studio" TRUE)
  else()
    set(OGRE_BUILD_MSVC_MP FALSE CACHE BOOL "Compiler option /MP requires at least Visual Studio 2008 (VS9) or newer" FORCE)
  endif()
  if(OGRE_BUILD_MSVC_MP)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /MP")
  endif ()
  if(MSVC_VERSION GREATER 1400 OR MSVC_VERSION EQUAL 1400)
    option(OGRE_BUILD_MSVC_ZM "Add /Zm256 compiler option to Visual Studio to fix PCH errors" TRUE)
  else()
    set(OGRE_BUILD_MSVC_ZM FALSE CACHE BOOL "Compiler option /Zm256 requires at least Visual Studio 2005 (VS8) or newer" FORCE)
  endif()
  if(OGRE_BUILD_MSVC_ZM)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /Zm256")
  endif ()
endif ()
if (MINGW)
  add_definitions(-D_WIN32_WINNT=0x0501)
  if( CMAKE_SIZEOF_VOID_P EQUAL 4 )
    # set architecture to i686, since otherwise some versions of MinGW can't link
    # the atomic primitives
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=i686")
  endif ()
  # disable this optimisation because it breaks release builds (reason unknown)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-tree-slp-vectorize")
  # Ignore some really annoying warnings which also happen in dependencies
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-error=cast-qual -Wno-unused-local-typedefs")
endif ()

include(GenerateExportHeader)
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN TRUE)

if((CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU") AND NOT OGRE_STATIC)
  set(OGRE_VISIBILITY_FLAGS "-DOGRE_GCC_VISIBILITY") # for legacy headers
endif()

# determine system endianess
if (MSVC OR ANDROID OR EMSCRIPTEN OR APPLE_IOS)
  # This doesn't work on VS 2010
  # MSVC only builds for intel anyway
  # all IOS devices are little endian
  set(OGRE_TEST_BIG_ENDIAN FALSE)
else()
  include(TestBigEndian)
  test_big_endian(OGRE_TEST_BIG_ENDIAN)
endif()

# Add OgreMain include path
if (APPLE_IOS)
  # Set static early for proper dependency detection
  set(OGRE_STATIC TRUE)
endif()

# definitions for samples
set(OGRE_LIBRARIES OgreMain)
set(OGRE_MeshLodGenerator_LIBRARIES OgreMeshLodGenerator)
set(OGRE_Paging_LIBRARIES OgrePaging)
set(OGRE_Terrain_LIBRARIES OgreTerrain)
set(OGRE_Volume_LIBRARIES OgreVolume)
set(OGRE_Plugin_PCZSceneManager_LIBRARIES Plugin_PCZSceneManager)
set(OGRE_Plugin_OctreeZone_LIBRARIES Plugin_OctreeZone)

# Specify build paths
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${OGRE_BINARY_DIR}/lib")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${OGRE_BINARY_DIR}/lib")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${OGRE_BINARY_DIR}/bin")
if (WIN32 OR APPLE)
  if (CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    # We don't want to install in default system location, install is really for the SDK, so call it that
    set(CMAKE_INSTALL_PREFIX
	  "${OGRE_BINARY_DIR}/sdk" CACHE PATH "OGRE install prefix" FORCE
    )
  endif (CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
endif(WIN32 OR APPLE)

# Set up iOS overrides.
if (APPLE_IOS)
  set(CMAKE_EXE_LINKER_FLAGS "-framework OpenGLES -framework Foundation -framework CoreGraphics -framework QuartzCore -framework UIKit")
  set(XCODE_ATTRIBUTE_GCC_UNROLL_LOOPS "YES")
  set(XCODE_ATTRIBUTE_LLVM_VECTORIZE_LOOPS "YES")
  set(XCODE_ATTRIBUTE_CODE_SIGN_IDENTITY "iPhone Developer")
  set(XCODE_ATTRIBUTE_GCC_PRECOMPILE_PREFIX_HEADER "YES")
  set(OGRE_BUILD_RENDERSYSTEM_GLES2 TRUE CACHE BOOL "Forcing OpenGL ES 2 RenderSystem for iOS" FORCE)
  set(OGRE_STATIC TRUE CACHE BOOL "Forcing static build for iOS" FORCE)
  set(MACOSX_BUNDLE_GUI_IDENTIFIER "com.yourcompany.\${PRODUCT_NAME:rfc1034identifier}")
elseif (ANDROID)
  set(TargetPlatform "Android")
  set(OGRE_PLATFORM OGRE_PLATFORM_ANDROID)
  set(OGRE_CONFIG_ENABLE_VIEWPORT_ORIENTATIONMODE FALSE CACHE BOOL "Disable viewport orientation Android" FORCE)
  option(OGRE_BUILD_ANDROID_JNI_SAMPLE "Enable JNI Sample" FALSE)

  set(OGRE_BUILD_RENDERSYSTEM_GLES2 TRUE CACHE BOOL "Forcing OpenGL ES 2 RenderSystem for Android" FORCE)

  set(OGRE_BUILD_PLUGIN_PCZ FALSE CACHE BOOL "Disable pcz on Android" FORCE)
  set(OGRE_BUILD_PLUGIN_BSP FALSE CACHE BOOL "Disable bsp scenemanager on Android" FORCE)
  set(OGRE_BUILD_TOOLS FALSE CACHE BOOL "Disable tools on Android" FORCE)
  set(OGRE_STATIC TRUE CACHE BOOL "Forcing static build for Android" FORCE)

  # workaround for the legacy android toolchain
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
elseif(EMSCRIPTEN)
  add_definitions(-DEMSCRIPTEN=1 -D__EMSCRIPTEN__=1)
  set(TargetPlatform "Emscripten")
  set(OGRE_PLATFORM OGRE_PLATFORM_EMSCRIPTEN)

  set(OGRE_BUILD_RENDERSYSTEM_GLES2 TRUE CACHE BOOL "Forcing OpenGL ES 2 RenderSystem for Emscripten" FORCE)
  set(OGRE_BUILD_RENDERSYSTEM_GL FALSE CACHE BOOL "Disable OpenGL RenderSystem for Emscripten" FORCE)

  set(OGRE_BUILD_PLUGIN_STBI TRUE CACHE BOOL "Enable STBIImageCodec on Emscripten (Smaller Footprint)" FORCE)
  set(OGRE_BUILD_PLUGIN_FREEIMAGE FALSE CACHE BOOL "Disable Freeimage on Emscripten (Smaller Footprint)" FORCE)
  set(OGRE_BUILD_PLUGIN_PCZ FALSE CACHE BOOL "Disable pcz on Emscripten" FORCE)
  set(OGRE_BUILD_PLUGIN_BSP FALSE CACHE BOOL "Disable pcz on Emscripten" FORCE)
  set(OGRE_BUILD_TOOLS FALSE CACHE BOOL "Disable tools on Emscripten" FORCE)
  set(OGRE_BUILD_TESTS FALSE CACHE BOOL "Disable tests on Emscripten" FORCE)
  set(OGRE_BUILD_COMPONENT_VOLUME FALSE CACHE BOOL "Disable volume component on Emscripten" FORCE)
  set(OGRE_BUILD_COMPONENT_PAGING FALSE CACHE BOOL "Disable paging component on Emscripten" FORCE)
  set(OGRE_BUILD_COMPONENT_TERRAIN FALSE CACHE BOOL "Disable terrain component on Emscripten" FORCE)
  set(OGRE_STATIC TRUE CACHE BOOL "Forcing static build for Emscripten" FORCE)

  set(OGRE_CONFIG_THREADS "0" CACHE STRING "Threading is unstable on Emscripten" FORCE)
elseif (APPLE AND NOT APPLE_IOS)

  set(XCODE_ATTRIBUTE_SDKROOT macosx)
  if(CMAKE_GENERATOR STREQUAL "Unix Makefiles")
    execute_process(COMMAND xcodebuild -version -sdk "${XCODE_ATTRIBUTE_SDKROOT}" Path | head -n 1 OUTPUT_VARIABLE CMAKE_OSX_SYSROOT)
    string(REGEX REPLACE "(\r?\n)+$" "" CMAKE_OSX_SYSROOT "${CMAKE_OSX_SYSROOT}")
  else()
    set(CMAKE_OSX_SYSROOT macosx)
  endif()

  if (NOT CMAKE_OSX_ARCHITECTURES)
    if(OGRE_BUILD_RENDERSYSTEM_GL3PLUS)
      if(CMAKE_GENERATOR STREQUAL "Unix Makefiles")
        set(CMAKE_OSX_ARCHITECTURES "${ARCHS_STANDARD_64_BIT}")
      else()
        set(CMAKE_OSX_ARCHITECTURES "$(ARCHS_STANDARD_64_BIT)")
      endif()
    else()
      if(CMAKE_GENERATOR STREQUAL "Unix Makefiles")
        set(CMAKE_OSX_ARCHITECTURES "${ARCHS_STANDARD_32_64_BIT}")
      else()
        set(CMAKE_OSX_ARCHITECTURES "$(ARCHS_STANDARD_32_64_BIT)")
      endif()
    endif()
  endif()

  # Make sure that the OpenGL render system is selected for non-iOS Apple builds
  set(OGRE_BUILD_RENDERSYSTEM_GLES2 FALSE)
endif ()

if(OGRE_BUILD_COMPONENT_MESHLODGENERATOR)
  set(OGRE_CONFIG_ENABLE_MESHLOD TRUE CACHE BOOL "Forcing Mesh Lod" FORCE)
endif()

# Enable the PVRTC codec if OpenGL ES is being built
if(OGRE_BUILD_RENDERSYSTEM_GLES2)
  set(OGRE_CONFIG_ENABLE_PVRTC TRUE CACHE BOOL "Forcing PVRTC codec for OpenGL ES" FORCE)
  set(OGRE_CONFIG_ENABLE_ETC TRUE CACHE BOOL "Forcing ETC codec for OpenGL ES" FORCE)
endif()

# Enable the ETC codec if OpenGL 3+ is being built
if(OGRE_BUILD_RENDERSYSTEM_GL3PLUS)
  set(OGRE_CONFIG_ENABLE_ETC TRUE CACHE BOOL "Forcing ETC codec for OpenGL 3+" FORCE)
endif()

# Find dependencies
include(Dependencies)

######################################################################
# Provide user options to customise the build process
######################################################################

# Customise what to build
option(OGRE_STATIC "Static build" FALSE)
option(OGRE_ENABLE_PRECOMPILED_HEADERS "Use precompiled headers to speed up build" TRUE)
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
if (WIN32)
	option(OGRE_INSTALL_VSPROPS "Install Visual Studio Property Page." FALSE)
	if (OGRE_INSTALL_VSPROPS)
		configure_file(${OGRE_TEMPLATES_DIR}/OGRE.props.in ${OGRE_BINARY_DIR}/OGRE.props)
		install(FILES ${OGRE_BINARY_DIR}/OGRE.props DESTINATION "${CMAKE_INSTALL_PREFIX}")
	endif ()
endif ()

# determine threading options
include(PrepareThreadingOptions)

# For Visual studio enable project folders by default.
# Hide option from other compilers.
if (MSVC)
	option(OGRE_PROJECT_FOLDERS "Organize project into project folders." TRUE)
endif ()

# hide advanced options
mark_as_advanced(
  OGRE_BUILD_RTSHADERSYSTEM_CORE_SHADERS
  OGRE_BUILD_RTSHADERSYSTEM_EXT_SHADERS
  OGRE_CONFIG_DOUBLE
  OGRE_CONFIG_NODE_INHERIT_TRANSFORM
  OGRE_CONFIG_ENABLE_MESHLOD
  OGRE_CONFIG_ENABLE_DDS
  OGRE_CONFIG_ENABLE_PVRTC
  OGRE_CONFIG_ENABLE_ETC
  OGRE_CONFIG_ENABLE_ASTC
  OGRE_CONFIG_ENABLE_VIEWPORT_ORIENTATIONMODE
  OGRE_CONFIG_ENABLE_ZIP
  OGRE_CONFIG_ENABLE_GL_STATE_CACHE_SUPPORT
  OGRE_CONFIG_ENABLE_GLES2_CG_SUPPORT
  OGRE_CONFIG_ENABLE_GLES2_GLSL_OPTIMISER
  OGRE_CONFIG_ENABLE_GLES3_SUPPORT
  OGRE_CONFIG_ENABLE_TBB_SCHEDULER
  OGRE_INSTALL_SAMPLES_SOURCE
  OGRE_PROFILING
  OGRE_CONFIG_STATIC_LINK_CRT
  OGRE_LIB_DIRECTORY
)

###################################################################
# configure global build settings based on selected build options
###################################################################
include(ConfigureBuild)

set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/${OGRE_LIB_DIRECTORY}")
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

###################################################################
# disable way too common compiler warnings on project level
###################################################################
if(MSVC)
	add_definitions( /wd4251 /wd4275 )
endif()

##################################################################
# Now setup targets
##################################################################

# install resource files
include(InstallResources)

# enable PCH support
include(PrecompiledHeader)

# Setup OgreMain project
add_subdirectory(OgreMain)

# Setup RenderSystems
add_subdirectory(RenderSystems)

# Setup Plugins
add_subdirectory(PlugIns)

# Setup Components
add_subdirectory(Components)

# Setup tests (before samples so that PlayPen is included in browser)
if (OGRE_BUILD_TESTS)
  # enable CTest
  ENABLE_TESTING()
  INCLUDE(CTest)
  add_subdirectory(Tests)
endif ()

# Setup samples
add_subdirectory(Samples)

# Setup command-line tools
if (OGRE_BUILD_TOOLS)
  add_subdirectory(Tools)
endif ()

# Setup XSIExporter
if (OGRE_BUILD_XSIEXPORTER)
  add_subdirectory(Tools/XSIExport)
endif ()

# Install documentation
add_subdirectory(Docs)

# Install media files
if (OGRE_INSTALL_SAMPLES OR OGRE_INSTALL_SAMPLES_SOURCE)
  add_subdirectory(Samples/Media)
endif ()
'''

install_root = {
    'uri': 'install',
    'source_base_dir': 'd:/lib/ogre',
    'type': 'config',
    'install_dirs_map': {
        '': 'include/OGRE',
        },
    'public_headers': [
        'include/OgreBuildSettings.h',
        'include/OgreExports.h',
        ],
}

lib_OgreMain = {
    'uri': 'OgreMain',
    'source_base_dir': 'd:/lib/ogre/OgreMain',
    'type': 'staticLib',
    'std': 'c++11',
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
    'cxxflags': [],
    'libs': [],
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


export_libs = [
    (lib_OgreMain, dyn_OgreMain),
    (install_root, None),
]

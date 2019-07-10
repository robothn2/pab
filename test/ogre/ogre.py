# coding: utf-8

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
    print('os tags:', target_os)
    if context.getOption('build_shared_libs'):
        if target_os == 'win':
            lib.defines += ['ZZIP_DLL']
            lib.libs += ['zlib']

    # Remove optional header files
    lib.sources -= [
        'src/OgreFileSystemLayerNoOp.cpp'
        'src/OgreDDSCodec.cpp'
        'src/OgrePVRTCCodec.cpp'
        'src/OgreETCCodec.cpp'
        'src/OgreZip.cpp'
        'src/OgreSearchOps.cpp'
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
        lib.deps += 'zziplib'
        lib.libs += 'z'

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
    (install_root, None),
    (lib_OgreMain, dyn_OgreMain),
]

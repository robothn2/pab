# coding: utf-8


lyra_lib = {
    'uri': 'lyra',
    'source_base_dir': r'D:\src\pca_infra\lyra\lyra\lyra',
    'type': 'sharedLib',
    'install_dirs_map': {
        'include': 'include/lyra',
        },

    'defines': [
        'LYRA_EXPORTS', 'LYRA_DLL_BUILD',
        '_SILENCE_STDEXT_HASH_DEPRECATION_WARNINGS',
        '_CRT_SECURE_NO_WARNINGS',

        'USE_QYBASE_SHAREDMEMORY=1',
        'SKIA_DLL', 'SK_RELEASE', 'SK_ANGLE', 'DEFAULT_TO_ANGLE',
        'COMPONENT_BUILD', 'NO_SUPPORT_OPENGL', 'EGL_EGLEXT_PROTOTYPES',
        ],
    'cxxflags': [
        '-std=c++11',
        ],
    'include_dirs': [
        'include',
    	'src',
    	'src/core',
    	'src/resmanager',
        ],
    'public_headers': [
        'include/*.h',
        ],
    'sources': [
        'src/**',
        #'src/*.c',
        ],
}

def lyra_dyn(lib, context):
    import os
    lyra_external = os.environ['QY_FRMEXTERNAL_PATH']
    lib.include_dirs += [
            os.path.join(lyra_external, 'gbase'),
            os.path.join(lyra_external, 'qybase/include'),
            os.path.join(lyra_external, 'skia/include'),
            os.path.join(lyra_external, 'skia/include/angle'),
            os.path.join(lyra_external, 'skia/include/nvapi'),
            os.path.join(lyra_external, 'zlib/include/contrib/minizip'),
            os.path.join(lyra_external, 'zlib/include'),
            ]
    lib.sources -= ['^src/platform/[^/]+/.+$']
    target_os = context.target_os_tags
    if 'win32' in target_os:
        lib.defines += ['NOMINMAX', 'ZLIB_WINAPI']
        lib.ccflags -= '-std=c++11'
        lib.cxxflags -= '-std=c++11'
        lib.include_dirs += 'src/platform/win'
        lib.sources += [
                'src/platform/win/*.cpp',
                'src/platform/win/*.c',
                ]
        lib.lib_dirs += [
                os.path.join(lyra_external, 'gbase/build/Release/lib'),
                os.path.join(lyra_external, 'qybase/lib/x86'),
                os.path.join(lyra_external, 'zlib/lib/x86'),
                os.path.join(lyra_external, 'skia/lib/x86/release'),
                ]
        lib.libs += ['skia.lib', 'gbase.lib', 'zlibstat.lib', 'nvapi.lib']
        lib.libs += ['OpenGL32.lib', 'libEGLForLyra.lib', 'ComCtl32.lib']

    elif 'linux' in target_os:
        lib.include_dirs += 'src/platform/linux'
        lib.sources += [
                'src/platform/linux/*.cpp',
                ]
        lib.libs += ['skia', 'gbase', 'zlibstat', 'nvapi']

    elif 'macosx' in target_os:
        lib.include_dirs += 'src/platform/mac'
        lib.sources += [
                'src/platform/mac/*.cpp',
                'src/platform/mac/*.mm',
                ]
        lib.libs += ['skia', 'gbase', 'zlibstat', 'nvapi']
        lib.ldflags += ['-framework', 'Carbon', '-framework', 'Cocoa']

    elif 'ios' in target_os:
        lib.include_dirs += 'src/platform/ios'
        lib.sources += [
                'src/platform/ios/*.cpp',
                'src/platform/ios/*.mm',
                ]
        lib.libs += ['skia', 'gbase', 'z', 'nvapi']

    elif 'android' in target_os:
        lib.include_dirs += 'src/platform/android'
        lib.sources += [
                'src/platform/android/*.cpp',
                ]
        lib.libs += ['skia', 'gbase', 'z', 'nvapi']
        lib.libs += ['GLES2', 'libc++_shared']

    lib.sources -= [
         	'src/ext/UISystem.cpp',
        	'src/core/KeyEvent.cpp',
        	'src/core/MouseEvent.cpp',
        	'src/core/NativeEvent.cpp',
        	'src/core/RenderInput.cpp',
        	'src/core/TouchEvent.cpp',
        	'src/core/TouchPoint.cpp',
        	'src/core/WheelEvent.cpp',
        	'src/core/UIEvent.cpp',
        	'src/core/GraphicsContext3D.cpp',
            'src/platform/win/PlatformNativeEvent_win.cpp',
            ]

export_libs = [
    (lyra_lib, lyra_dyn),
]

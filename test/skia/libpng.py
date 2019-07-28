# coding: utf-8

libpng_lib = {
    'uri': '//third_party/libpng',
    'type': 'sharedLib',
    'source_base_dir': 'third_party/libpng',

    'public_defines': ['PNG_USE_DLL', 'PNG_DLL_IMPORT'],
    'public_include_dirs': ['.', 'libpng'],

    'defines': [
        'PNG_IMPEXP=PNG_DLL_EXPORT',
        ],
    'deps': [
        '//third_party/zlib',
        ],
    'sources': [
        "png.c",
        "pngerror.c",
        "pngget.c",
        "pngmem.c",
        "pngpread.c",
        "pngread.c",
        "pngrio.c",
        "pngrtran.c",
        "pngrutil.c",
        "pngset.c",
        "pngtrans.c",
        "pngwio.c",
        "pngwrite.c",
        "pngwtran.c",
        "pngwutil.c",
        ],
}


def libpng_dyn(lib, ctx):
    if 'x86' in ctx.target_cpu_tags:
        lib.defines += 'PNG_INTEL_SSE'
        lib.sources += [
                'contrib/intel/filter_sse2_intrinsics.c',
                'contrib/intel/intel_init.c',
                ]
    elif 'arm' in ctx.target_os_tags:
        lib.sources += [
                'arm/arm_init.c',
                'arm/filter_neon_intrinsics.c',
                ]


export_libs = [
    (libpng_lib, libpng_dyn),
]

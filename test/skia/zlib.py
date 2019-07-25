# coding: utf-8


zlib_lib = {
    'uri': '//third_party/zlib',
    'type': 'sharedLib',
    'source_base_dir': 'third_party/externals/zlib',
    'public_include_dirs': [
        '.',
        ],
    'public_defines': ['ZLIB_DLL'],
    'defines': ['ZLIB_DLL', 'ZLIB_INTERNAL'],
    'sources': [
        'adler32.c',
        'compress.c',
        'crc32.c',
        'deflate.c',
        'gzclose.c',
        'gzlib.c',
        'gzread.c',
        'gzwrite.c',
        'infback.c',
        'inffast.c',
        'inflate.c',
        'inftrees.c',
        'trees.c',
        'uncompr.c',
        'zutil.c',
        ],
}

def zlib_dyn(lib, context):
    if 'x86' in context.target_cpu_tags:
        lib.sources += [
                'crc_folding.c',
                'fill_window_sse.c',
                'x86.c',
                ]
        if 'msvc' not in context.compiler_tags:
            lib.ccflags += ['-msse4.2', '-mpclmul']
    else:
        lib.sources += 'simd_stub.c'


export_libs = [
    (zlib_lib, zlib_dyn),
]

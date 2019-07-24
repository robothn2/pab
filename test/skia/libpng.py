# coding: utf-8

libpng_lib = {
    'uri': '//third_party/libpng',
    'type': 'sharedLib',
    'source_base_dir': 'third_party/libpng',
    'public_include_dirs': [
        ".",
        "libpng",
        ],

    'defines': [
        "PNG_SET_OPTION_SUPPORTED"
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


def libpng_dyn(lib, context):
    target_os = context.target_os_tags
    if 'android' in target_os:
        lib.defines += []
        lib.sources += []


export_libs = [
    (libpng_lib, libpng_dyn),
]

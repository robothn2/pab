# coding: utf-8

libpng = {
    'uri': '//third_party/libpng',
    'type': 'sharedLib',
    'std': 'c11',
    'source_base_dir': 'd:/lib/chromium/third_party/libpng',
    'public_include_dirs': [
        ".",
        "libpng",
    ],

    'defines': [
        "PNG_SET_OPTION_SUPPORTED"
    ],
    'deps': [
        "//third_party/zlib",
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
    'libs': [
        'c', 'z',
    ],
}


def libpng_apply(lib, context):
    target_os = context.target_os
    if target_os == "android":
        lib.defines += [
            'TEST_DEFINE',
            ]
        lib.sources += [
            ]


export_libs = [
    (libpng, libpng_apply),
]

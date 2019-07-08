# coding: utf-8

libpng = {
    'uri': '//third_party/libpng',
    'type': 'sharedLib',
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
}


def libpng_apply(lib, context):
    # print(context.target_os, context.target_cpu)
    target_cpu = context.target_cpu
    if target_cpu == "arm" or target_cpu == "arm64":
        lib.defines += [
            'TEST_DEFINE',
            ]
        lib.sources += [
            "arm/arm_init.c",
            "arm/filter_neon_intrinsics.c",
            "arm/palette_neon_intrinsics.c",
            ]

    if target_cpu == "x86" or target_cpu == "x64":
        lib.defines += ["PNG_INTEL_SSE"]
        lib.sources += [
          "intel/filter_sse2_intrinsics.c",
          "intel/intel_init.c",
        ]


export_libs = [
    (libpng, libpng_apply),
]

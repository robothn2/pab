# coding: utf-8

libpng = {
    'uri': '//third_party/libpng',
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


def libpng_dyn_setting(lib):
    if (target_cpu == "arm" or target_cpu == "arm64"):
        lib.sources += [
            "arm/arm_init.c",
            "arm/filter_neon_intrinsics.c",
            "arm/palette_neon_intrinsics.c",
            ]

    if (target_cpu == "x86" or target_cpu == "x64"):
        lib.defines += ["PNG_INTEL_SSE"]
        lib.sources += [
          "intel/filter_sse2_intrinsics.c",
          "intel/intel_init.c",
        ]


export_libs = [
    (libpng, libpng_dyn_setting),
]

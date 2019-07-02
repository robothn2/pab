# coding: utf-8

libpng = {
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


def libpng_dyn_setting(lib, env):
    if (env.current_cpu == "arm" or env.current_cpu == "arm64"):
        lib.sources += [
            "arm/arm_init.c",
            "arm/filter_neon_intrinsics.c",
            "arm/palette_neon_intrinsics.c",
            ]

    if (env.current_cpu == "x86" or env.current_cpu == "x64"):
        lib.defines += ["PNG_INTEL_SSE"]
        lib.sources += [
          "intel/filter_sse2_intrinsics.c",
          "intel/intel_init.c",
        ]


all_lib = [
    (libpng, libpng_dyn_setting)
]

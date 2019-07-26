# coding: utf-8


libjpeg_lib = {
    'uri': '//third_party/libjpeg',
    'type': 'sharedLib',
    'source_base_dir': 'third_party/externals/libjpeg-turbo',
    'public_include_dirs': [
        '.',
        ],
    'defines': [
        'TURBO_FOR_WINDOWS',
        ],
    'sources': [
        'jaricom.c',
        'jcapimin.c',
        'jcapistd.c',
        'jcarith.c',
        'jccoefct.c',
        'jccolor.c',
        'jcdctmgr.c',
        'jchuff.c',
        'jcinit.c',
        'jcmainct.c',
        'jcmarker.c',
        'jcmaster.c',
        'jcomapi.c',
        'jcparam.c',
        'jcphuff.c',
        'jcprepct.c',
        'jcsample.c',
        'jdapimin.c',
        'jdapistd.c',
        'jdarith.c',
        'jdcoefct.c',
        'jdcolor.c',
        'jddctmgr.c',
        'jdhuff.c',
        'jdinput.c',
        'jdmainct.c',
        'jdmarker.c',
        'jdmaster.c',
        'jdmerge.c',
        'jdphuff.c',
        'jdpostct.c',
        'jdsample.c',
        'jerror.c',
        'jfdctflt.c',
        'jfdctfst.c',
        'jfdctint.c',
        'jidctflt.c',
        'jidctfst.c',
        'jidctint.c',
        'jidctred.c',
        'jmemmgr.c',
        'jmemnobs.c',
        'jquant1.c',
        'jquant2.c',
        'jutils.c',
        ],
}

def libjpeg_dyn(lib, ctx):
    if 'arm32' in ctx.target_cpu_tags and 'ios' not in ctx.target_os_tags:
        lib.sources += [
                'simd/jsimd_arm.c',
                'simd/jsimd_arm_neon.S',
                ]
    elif 'arm64' in ctx.target_cpu_tags and 'ios' not in ctx.target_os_tags:
        lib.sources += [
                'simd/jsimd_arm64.c',
                'simd/jsimd_arm64_neon.S',
                ]
    else:
        lib.sources += [ 'jsimd_none.c' ]


export_libs = [
    (libjpeg_lib, libjpeg_dyn),
]

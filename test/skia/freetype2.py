# coding: utf-8


freetype2_lib = {
    'uri': '//third_party/freetype2',
    'type': 'sharedLib',
    'source_base_dir': 'third_party/externals/freetype',
    'public_include_dirs': [ '.', ],
    #'public_defines': [ 'SK_FREETYPE_MINIMUM_RUNTIME_VERSION=(((FREETYPE_MAJOR) << 24) | ((FREETYPE_MINOR) << 16) | ((FREETYPE_PATCH) << 8))' ],
    'defines': [
        'FT2_BUILD_LIBRARY',
        'FT_CONFIG_MODULES_H=<include/freetype-android/ftmodule.h>',
        'FT_CONFIG_OPTIONS_H=<include/freetype-android/ftoption.h>',
        ],
    'deps': [
        '//third_party/libpng',
        ],
    'include_dirs': [
        '../../freetype',  # 'third_party/freetype'
        'include',
        ],
    'sources': [
        'src/autofit/autofit.c',
        'src/base/ftbase.c',
        'src/base/ftbbox.c',
        'src/base/ftbitmap.c',
        'src/base/ftdebug.c',
        'src/base/ftfntfmt.c',
        'src/base/ftfstype.c',
        'src/base/ftgasp.c',
        'src/base/ftglyph.c',
        'src/base/ftinit.c',
        'src/base/ftlcdfil.c',
        'src/base/ftmm.c',
        'src/base/ftpatent.c',
        'src/base/ftstroke.c',
        'src/base/ftsynth.c',
        'src/base/ftsystem.c',
        'src/base/fttype1.c',
        'src/base/ftwinfnt.c',
        'src/cff/cff.c',
        'src/gzip/ftgzip.c',
        'src/pshinter/pshinter.c',
        'src/psnames/psnames.c',
        'src/raster/raster.c',
        'src/sfnt/sfnt.c',
        'src/smooth/smooth.c',
        'src/truetype/truetype.c',
        ],
}

def freetype2_dyn(lib, ctx):
    pass


export_libs = [
    (freetype2_lib, freetype2_dyn),
]

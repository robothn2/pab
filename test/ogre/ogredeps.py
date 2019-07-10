# coding: utf-8

lib_zziplib = {
    'uri': 'zziplib',
    'source_base_dir': 'd:/lib/ogredeps/src/zziplib/zzip',
    'type': 'staticLib',
    'std': 'c11',
    'public_include_dirs': [],
    'include_dirs': [
        '..',
        '../../src/zlib',
        ],
    'defines': [],
    'ccflags': [],
    'cxxflags': [],
    'deps': [],
    'libs': ['c', 'z'],
    'install_dirs_map': {
        '': 'include/zzip',
        },
    'public_headers': [
        'conf.h',
        '_config.h',
        'types.h',
        'zzip.h',
        'plugin.h',
        '_msvc.h',
        ],
    'sources': [
        'dir.c',
        'err.c',
        'fetch.c',
        'file.c',
        'fseeko.c',
        'info.c',
        'memdisk.c',
        'mmapped.c',
        'plugin.c',
        'stat.c',
        'write.c',
        'zip.c',
        ],
}


def dyn_zziplib(lib, context):
    target_os = context.target_os
    if context.getOption('build_shared_libs'):
        if target_os == 'win':
            lib.defines += ['ZZIP_DLL']
            lib.libs += ['zlib']

    if target_os == 'ios':
        pass


lib_freetype = {
    'uri': 'freetype',
    'source_base_dir': 'd:/lib/ogredeps/src/freetype',
    'type': 'staticLib',
    'std': 'c11',
    'include_dirs': [
        'include',
    ],
    'defines': [
        'FT2_BUILD_LIBRARY',
    ],
    'ccflags': [],
    'cxxflags': [],
    'deps': [],
    'libs': ['c', 'z'],
    'public_include_dirs': [],
    'install_dirs_map': {
        'include': 'include',
        },
    'install_header_dir': 'freetype',
    'public_headers': [
        'include/ft2build.h',
        'include/freetype/config/ftconfig.h',
        'include/freetype/config/ftheader.h',
        'include/freetype/config/ftmodule.h',
        'include/freetype/config/ftoption.h',
        'include/freetype/config/ftstdlib.h',
        'include/freetype/freetype.h',
        'include/freetype/ftadvanc.h',
        'include/freetype/ftbbox.h',
        'include/freetype/ftbdf.h',
        'include/freetype/ftbitmap.h',
        'include/freetype/ftbzip2.h',
        'include/freetype/ftcache.h',
        'include/freetype/ftchapters.h',
        'include/freetype/ftcid.h',
        'include/freetype/fterrdef.h',
        'include/freetype/fterrors.h',
        'include/freetype/ftgasp.h',
        'include/freetype/ftglyph.h',
        'include/freetype/ftgxval.h',
        'include/freetype/ftgzip.h',
        'include/freetype/ftimage.h',
        'include/freetype/ftincrem.h',
        'include/freetype/ftlcdfil.h',
        'include/freetype/ftlist.h',
        'include/freetype/ftlzw.h',
        'include/freetype/ftmac.h',
        'include/freetype/ftmm.h',
        'include/freetype/ftmodapi.h',
        'include/freetype/ftmoderr.h',
        'include/freetype/ftotval.h',
        'include/freetype/ftoutln.h',
        'include/freetype/ftpfr.h',
        'include/freetype/ftrender.h',
        'include/freetype/ftsizes.h',
        'include/freetype/ftsnames.h',
        'include/freetype/ftstroke.h',
        'include/freetype/ftsynth.h',
        'include/freetype/ftsystem.h',
        'include/freetype/fttrigon.h',
        'include/freetype/fttypes.h',
        'include/freetype/ftwinfnt.h',
        'include/freetype/ftxf86.h',
        'include/freetype/t1tables.h',
        'include/freetype/ttnameid.h',
        'include/freetype/tttables.h',
        'include/freetype/tttags.h',
        'include/freetype/ttunpat.h',
    ],
    'sources': [
        'src/autofit/autofit.c',
        'src/base/ftbase.c',
        'src/base/ftbbox.c',
        'src/base/ftbitmap.c',
        'src/base/ftfstype.c',
        'src/base/ftgasp.c',
        'src/base/ftglyph.c',
        'src/base/ftinit.c',
        'src/base/ftmm.c',
        'src/base/ftpfr.c',
        'src/base/ftstroke.c',
        'src/base/ftsynth.c',
        'src/base/ftsystem.c',
        'src/base/fttype1.c',
        'src/base/ftwinfnt.c',
        'src/bdf/bdf.c',
        'src/bzip2/ftbzip2.c',
        'src/cache/ftcache.c',
        'src/cff/cff.c',
        'src/cid/type1cid.c',
        'src/gzip/ftgzip.c',
        'src/lzw/ftlzw.c',
        'src/pcf/pcf.c',
        'src/pfr/pfr.c',
        'src/psaux/psaux.c',
        'src/pshinter/pshinter.c',
        'src/psnames/psmodule.c',
        'src/raster/raster.c',
        'src/sfnt/sfnt.c',
        'src/smooth/smooth.c',
        'src/truetype/truetype.c',
        'src/type1/type1.c',
        'src/type42/type42.c',
        'src/winfonts/winfnt.c',
    ],
}


def dyn_freetype(lib, context):
    target_os = context.target_os
    if target_os == 'ios':
        lib.defines += [
            'HAVE_QUICKDRAW_CARBON=0',
            'HAVE_QUICKDRAW_TOOLBOX=0',
            'HAVE_ATS=0',
            'HAVE_FSREF=0',
            'HAVE_FSSPEC=0',
            'DARWIN_NO_CARBON=1',
            'FT_CONFIG_OPTION_NO_ASSEMBLER=1',
        ]


export_libs = [
    (lib_zziplib, dyn_zziplib),
    (lib_freetype, dyn_freetype),
]

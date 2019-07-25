# coding: utf-8


declare_args() {
  skia_use_angle = false
  skia_use_egl = false
  skia_use_expat = true
  skia_use_experimental_xform = false
  skia_use_ffmpeg = false
  skia_use_fontconfig = is_linux
  skia_use_fonthost_mac = is_mac
  skia_use_freetype = is_android || is_fuchsia || is_linux
  skia_use_fixed_gamma_text = is_android
  skia_use_libjpeg_turbo = true
  skia_use_libpng = true
  skia_use_libwebp = !is_fuchsia
  skia_use_lua = is_skia_dev_build && !is_ios
  skia_use_opencl = false
  skia_use_piex = !is_win
  skia_use_wuffs = false
  skia_use_zlib = true
  skia_use_metal = false
  skia_use_dawn = false
  skia_use_libheif = is_skia_dev_build
  skia_use_x11 = is_linux
  skia_use_xps = true
}

declare_args() {
  skia_android_serial = ""
  skia_enable_ccpr = true
  skia_enable_nvpr = !skia_enable_flutter_defines
  skia_enable_discrete_gpu = true
  skia_enable_pdf = true
  skia_enable_spirv_validation = is_skia_dev_build && is_debug && !skia_use_dawn
  skia_enable_skpicture = true
  skia_enable_sksl_interpreter = is_skia_dev_build
  skia_enable_skvm_jit =
      is_skia_dev_build && ((target_cpu == "x64" && (is_linux || is_mac)) ||
                            (target_cpu == "arm64" && is_android))
  skia_enable_vulkan_debug_layers = is_skia_dev_build && is_debug
  skia_qt_path = getenv("QT_PATH")
  skia_compile_processors = false
  skia_generate_workarounds = false
  skia_lex = false

  skia_skqp_global_error_tolerance = 0

  skia_llvm_path = ""
  skia_llvm_lib = "LLVM"

  skia_tools_require_resources = false
  skia_include_multiframe_procs = false
}

if (skia_use_dawn) {
  import("third_party/externals/dawn/scripts/dawn_features.gni")
}

declare_args() {
  skia_use_dng_sdk = !is_fuchsia && skia_use_libjpeg_turbo && skia_use_zlib
  skia_use_sfntly = skia_use_icu
  skia_enable_atlas_text = is_skia_dev_build && skia_enable_gpu
  skia_enable_fontmgr_empty = false
  skia_enable_fontmgr_custom =
      is_linux && skia_use_freetype && !skia_use_fontconfig
  skia_enable_fontmgr_custom_empty = is_fuchsia && skia_use_freetype
  skia_enable_fontmgr_android = skia_use_expat && skia_use_freetype
  skia_enable_fontmgr_fuchsia = is_fuchsia
  skia_enable_fontmgr_win = is_win
  skia_enable_fontmgr_win_gdi = is_win

  if (is_mac) {
    skia_gl_standard = "gl"
  } else if (is_ios) {
    skia_gl_standard = "gles"
  } else {
    skia_gl_standard = ""
  }

  if (is_android) {
    skia_use_vulkan = defined(ndk_api) && ndk_api >= 24
  } else if (is_fuchsia) {
    skia_use_vulkan = fuchsia_use_vulkan
  } else {
    skia_use_vulkan = defined(skia_moltenvk_path) && skia_moltenvk_path != ""
  }

  if (is_ios) {
    skia_ios_identity = ".*Google.*"
    skia_ios_profile = "Google Development"
  }
}

if (defined(skia_settings)) {
  import(skia_settings)
}

# Skia public API, generally provided by :skia.
config("skia_public") {
  include_dirs = [ "." ]

  defines = []
  if (is_component_build) {
    defines += [ "SKIA_DLL" ]
  }
  if (is_fuchsia || is_linux) {
    defines += [ "SK_R32_SHIFT=16" ]
  }
  if (skia_enable_flutter_defines) {
    defines += flutter_defines
  }
  if (!skia_enable_gpu) {
    defines += [ "SK_SUPPORT_GPU=0" ]
  }
  if (skia_enable_atlas_text) {
    defines += [ "SK_SUPPORT_ATLAS_TEXT=1" ]
  }
  if (is_fuchsia) {
    defines += fuchsia_defines
  }
  if (skia_gl_standard == "gles") {
    defines += [ "SK_ASSUME_GL_ES=1" ]
  } else if (skia_gl_standard == "gl") {
    defines += [ "SK_ASSUME_GL=1" ]
  } else if (skia_gl_standard == "webgl") {
    defines += [ "SK_ASSUME_WEBGL=1" ]
  }
}

# Skia internal APIs, used by Skia itself and a few test tools.
config("skia_private") {
  visibility = [ ":*" ]

  defines = [ "SK_GAMMA_APPLY_TO_A8" ]
  if (skia_use_fixed_gamma_text) {
    defines += [
      "SK_GAMMA_EXPONENT=1.4",
      "SK_GAMMA_CONTRAST=0.0",
    ]
  }
  if (is_skia_dev_build) {
    defines += [
      "SK_ALLOW_STATIC_GLOBAL_INITIALIZERS=1",
      "GR_TEST_UTILS=1",
    ]
  }
  libs = []
  lib_dirs = []
  if (skia_use_angle) {
    defines += [ "SK_ANGLE" ]
  }
  if (skia_llvm_path != "") {
    defines += [ "SK_LLVM_AVAILABLE" ]
    include_dirs += [ "$skia_llvm_path/include" ]
    libs += [ skia_llvm_lib ]
    lib_dirs += [ "$skia_llvm_path/lib/" ]
  }
}

# Any code that's linked into Skia-the-library should use this config via += skia_library_configs.
config("skia_library") {
  visibility = [ ":*" ]
  defines = [ "SKIA_IMPLEMENTATION=1" ]
}

skia_library_configs = [
  ":skia_public",
  ":skia_private",
  ":skia_library",
]

# Use for CPU-specific Skia code that needs particular compiler flags.
template("opts") {
  visibility = [ ":*" ]
  if (invoker.enabled) {
    source_set(target_name) {
      check_includes = false
      forward_variables_from(invoker, "*")
      configs += skia_library_configs
    }
  } else {
    # If not enabled, a phony empty target that swallows all otherwise unused variables.
    source_set(target_name) {
      check_includes = false
      forward_variables_from(invoker,
                             "*",
                             [
                               "sources",
                               "cflags",
                             ])
    }
  }
}

is_x86 = current_cpu == "x64" || current_cpu == "x86"

opts("none") {
  enabled = !is_x86 && current_cpu != "arm" && current_cpu != "arm64"
  sources = skia_opts.none_sources
  cflags = []
}

opts("armv7") {
  enabled = current_cpu == "arm"
  sources = skia_opts.armv7_sources + skia_opts.neon_sources
  cflags = []
}

opts("arm64") {
  enabled = current_cpu == "arm64"
  sources = skia_opts.arm64_sources
  cflags = []
}

opts("crc32") {
  enabled = current_cpu == "arm64"
  sources = skia_opts.crc32_sources
  cflags = [ "-march=armv8-a+crc" ]
}

opts("sse2") {
  enabled = is_x86
  sources = skia_opts.sse2_sources
  if (!is_clang && is_win) {
    defines = [ "SK_CPU_SSE_LEVEL=SK_CPU_SSE_LEVEL_SSE2" ]
  } else {
    cflags = [ "-msse2" ]
  }
}

opts("ssse3") {
  enabled = is_x86
  sources = skia_opts.ssse3_sources
  if (!is_clang && is_win) {
    defines = [ "SK_CPU_SSE_LEVEL=SK_CPU_SSE_LEVEL_SSSE3" ]
  } else {
    cflags = [ "-mssse3" ]
  }
}

opts("sse41") {
  enabled = is_x86
  sources = skia_opts.sse41_sources
  if (!is_clang && is_win) {
    defines = [ "SK_CPU_SSE_LEVEL=SK_CPU_SSE_LEVEL_SSE41" ]
  } else {
    cflags = [ "-msse4.1" ]
  }
}

opts("sse42") {
  enabled = is_x86
  sources = skia_opts.sse42_sources
  if (!is_clang && is_win) {
    defines = [ "SK_CPU_SSE_LEVEL=SK_CPU_SSE_LEVEL_SSE42" ]
  } else {
    cflags = [ "-msse4.2" ]
  }
}

opts("avx") {
  enabled = is_x86
  sources = skia_opts.avx_sources
  if (is_win) {
    cflags = [ "/arch:AVX" ]
  } else {
    cflags = [ "-mavx" ]
  }
}

opts("hsw") {
  enabled = is_x86
  sources = skia_opts.hsw_sources
  if (is_win) {
    cflags = [ "/arch:AVX2" ]
  } else {
    cflags = [ "-march=haswell" ]
  }
}

# Any feature of Skia that requires third-party code should be optional and use this template.
template("optional") {
  visibility = [ ":*" ]
  if (invoker.enabled) {
    config(target_name + "_public") {
      if (defined(invoker.public_defines)) {
        defines = invoker.public_defines
      }
      if (defined(invoker.public_configs)) {
        configs = invoker.public_configs
      }
    }
    source_set(target_name) {
      check_includes = false
      forward_variables_from(invoker,
                             "*",
                             [
                               "public_defines",
                               "sources_when_disabled",
                               "configs_to_remove",
                             ])
      all_dependent_configs = [ ":" + target_name + "_public" ]
      configs += skia_library_configs
      if (defined(invoker.configs_to_remove)) {
        configs -= invoker.configs_to_remove
      }
    }
  } else {
    source_set(target_name) {
      forward_variables_from(invoker,
                             "*",
                             [
                               "public_defines",
                               "public_deps",
                               "deps",
                               "libs",
                               "sources",
                               "sources_when_disabled",
                               "configs_to_remove",
                             ])
      if (defined(invoker.sources_when_disabled)) {
        sources = invoker.sources_when_disabled
      }
      configs += skia_library_configs
    }
  }
}

optional("fontmgr_android") {
  enabled = skia_enable_fontmgr_android

  deps = [
    ":typeface_freetype",
    "//third_party/expat",
  ]
  sources = [
    "src/ports/SkFontMgr_android.cpp",
    "src/ports/SkFontMgr_android_factory.cpp",
    "src/ports/SkFontMgr_android_parser.cpp",
  ]
}

optional("fontmgr_custom") {
  enabled = skia_enable_fontmgr_custom

  deps = [
    ":typeface_freetype",
  ]
  sources = [
    "src/ports/SkFontMgr_custom.cpp",
    "src/ports/SkFontMgr_custom.h",
    "src/ports/SkFontMgr_custom_directory.cpp",
    "src/ports/SkFontMgr_custom_directory_factory.cpp",
    "src/ports/SkFontMgr_custom_embedded.cpp",
    "src/ports/SkFontMgr_custom_empty.cpp",
  ]
}

optional("fontmgr_custom_empty") {
  enabled = skia_enable_fontmgr_custom_empty

  deps = [
    ":typeface_freetype",
  ]
  sources = [
    "src/ports/SkFontMgr_custom.cpp",
    "src/ports/SkFontMgr_custom_empty.cpp",
    "src/ports/SkFontMgr_custom_empty_factory.cpp",
  ]
}

optional("fontmgr_empty") {
  enabled = skia_enable_fontmgr_empty
  sources = [
    "src/ports/SkFontMgr_empty_factory.cpp",
  ]
}

optional("fontmgr_fontconfig") {
  enabled = skia_use_freetype && skia_use_fontconfig

  deps = [
    ":typeface_freetype",
    "//third_party:fontconfig",
  ]
  sources = [
    "src/ports/SkFontConfigInterface.cpp",
    "src/ports/SkFontConfigInterface_direct.cpp",
    "src/ports/SkFontConfigInterface_direct_factory.cpp",
    "src/ports/SkFontMgr_FontConfigInterface.cpp",
    "src/ports/SkFontMgr_fontconfig.cpp",
    "src/ports/SkFontMgr_fontconfig_factory.cpp",
  ]
}

optional("fontmgr_fuchsia") {
  enabled = skia_enable_fontmgr_fuchsia

  deps = []

  if (is_fuchsia && using_fuchsia_sdk) {
    deps += [ "$fuchsia_sdk_root/fidl:fuchsia.fonts" ]
  } else {
    deps += [ "//sdk/fidl/fuchsia.fonts" ]
  }
  sources = [
    "src/ports/SkFontMgr_fuchsia.cpp",
    "src/ports/SkFontMgr_fuchsia.h",
  ]
}

optional("fontmgr_wasm") {
  enabled = !skia_enable_fontmgr_empty && target_cpu == "wasm"

  deps = [
    ":typeface_freetype",
  ]
  sources = [
    "src/ports/SkFontMgr_custom.cpp",
    "src/ports/SkFontMgr_custom.h",
    "src/ports/SkFontMgr_custom_embedded.cpp",
    "src/ports/SkFontMgr_custom_embedded_factory.cpp",
  ]
}

optional("fontmgr_win") {
  enabled = skia_enable_fontmgr_win

  sources = [
    "src/fonts/SkFontMgr_indirect.cpp",
    "src/ports/SkFontMgr_win_dw.cpp",
    "src/ports/SkFontMgr_win_dw_factory.cpp",
    "src/ports/SkScalerContext_win_dw.cpp",
    "src/ports/SkTypeface_win_dw.cpp",
  ]
}

optional("fontmgr_win_gdi") {
  enabled = skia_enable_fontmgr_win_gdi

  sources = [
    "src/ports/SkFontHost_win.cpp",
  ]
  libs = [ "Gdi32.lib" ]
}

if (skia_lex) {
  executable("sksllex") {
    sources = [
      "src/sksl/lex/Main.cpp",
      "src/sksl/lex/NFA.cpp",
      "src/sksl/lex/RegexNode.cpp",
      "src/sksl/lex/RegexParser.cpp",
    ]
    include_dirs = [ "." ]
  }

  action("run_sksllex") {
    script = "gn/run_sksllex.py"
    deps = [
      ":sksllex(//gn/toolchain:$host_toolchain)",
    ]
    sources = [
      "src/sksl/lex/sksl.lex",
    ]

    # GN insists its outputs should go somewhere underneath target_out_dir, so we trick it with a
    # path that starts with target_out_dir and then uses ".." to back up into the src dir.
    outputs = [
      "$target_out_dir/" +
          rebase_path("src/sksl/lex/SkSLLexer.h", target_out_dir),
      # the script also modifies the corresponding .cpp file, but if we tell GN that it gets
      # confused due to the same file being named by two different paths
    ]
    sksllex_path = "$root_out_dir/"
    sksllex_path += "sksllex"
    if (host_os == "win") {
      sksllex_path += ".exe"
    }
    args = [
      rebase_path(sksllex_path),
      rebase_path("bin/clang-format"),
      rebase_path("src"),
    ]
  }
} else {
  group("run_sksllex") {
  }
}

if (skia_compile_processors) {
  executable("skslc") {
    defines = [ "SKSL_STANDALONE" ]
    sources = [
      "src/sksl/SkSLMain.cpp",
    ]
    sources += skia_sksl_sources
    sources += skia_sksl_gpu_sources
    include_dirs = [ "." ]
    deps = [
      ":run_sksllex",
      "//third_party/spirv-tools",
    ]
  }

  skia_gpu_processor_outputs = []
  foreach(src, skia_gpu_processor_sources) {
    dir = get_path_info(src, "dir")
    name = get_path_info(src, "name")

    # GN insists its outputs should go somewhere underneath target_out_dir, so we trick it with a
    # path that starts with target_out_dir and then uses ".." to back up into the src dir.
    skia_gpu_processor_outputs += [
      "$target_out_dir/" +
          rebase_path("$dir/generated/$name.h", target_out_dir),
      # the script also modifies the corresponding .cpp file, but if we tell GN that it gets
      # confused due to the same file being named by two different paths
    ]
  }

  action("create_sksl_enums") {
    script = "gn/create_sksl_enums.py"
    sources = [
      "include/private/GrSharedEnums.h",
    ]
    outputs = [
      "$target_out_dir/" +
          rebase_path("src/sksl/sksl_enums.inc", target_out_dir),
    ]
    args = [
      rebase_path(sources[0]),
      rebase_path(outputs[0]),
    ]
  }

  action("compile_processors") {
    script = "gn/compile_processors.py"
    deps = [
      ":create_sksl_enums",
      ":skslc(//gn/toolchain:$host_toolchain)",
    ]
    sources = skia_gpu_processor_sources
    outputs = skia_gpu_processor_outputs
    skslc_path = "$root_out_dir/"
    if (host_toolchain != default_toolchain_name) {
      skslc_path += "$host_toolchain/"
    }
    skslc_path += "skslc"
    if (host_os == "win") {
      skslc_path += ".exe"
    }
    args = [
      rebase_path(skslc_path),
      rebase_path("bin/clang-format"),
    ]
    args += rebase_path(skia_gpu_processor_sources)
  }
} else {
  skia_gpu_processor_outputs = []
  group("compile_processors") {
  }
}

optional("gpu") {
  enabled = skia_enable_gpu
  deps = [
    ":compile_processors",
    ":run_sksllex",
  ]
  if (skia_generate_workarounds) {
    deps += [ ":workaround_list" ]
  }
  public_defines = [ "SK_GL" ]
  public_configs = []
  public_deps = []

  sources =
      skia_gpu_sources + skia_sksl_gpu_sources + skia_gpu_processor_outputs
  if (!skia_enable_ccpr) {
    sources -= skia_ccpr_sources
    sources += [ "src/gpu/ccpr/GrCoverageCountingPathRenderer_none.cpp" ]
  }
  if (!skia_enable_nvpr) {
    sources -= skia_nvpr_sources
    sources += [ "src/gpu/GrPathRendering_none.cpp" ]
  }

  # These paths need to be absolute to match the ones produced by shared_sources.gni.
  sources -= get_path_info([ "src/gpu/gl/GrGLMakeNativeInterface_none.cpp" ],
                           "abspath")
  libs = []
  if (is_android) {
    sources += [ "src/gpu/gl/egl/GrGLMakeNativeInterface_egl.cpp" ]

    # this lib is required to link against AHardwareBuffer
    if (defined(ndk_api) && ndk_api >= 26) {
      libs += [ "android" ]
    }
  } else if (skia_use_egl) {
    sources += [ "src/gpu/gl/egl/GrGLMakeNativeInterface_egl.cpp" ]
    libs += [ "EGL" ]
  } else if (is_linux && skia_use_x11) {
    sources += [ "src/gpu/gl/glx/GrGLMakeNativeInterface_glx.cpp" ]
    libs += [ "GL" ]
  } else if (is_mac) {
    sources += [ "src/gpu/gl/mac/GrGLMakeNativeInterface_mac.cpp" ]
  } else if (is_ios) {
    sources += [ "src/gpu/gl/iOS/GrGLMakeNativeInterface_iOS.cpp" ]
  } else if (is_win) {
    sources += [ "src/gpu/gl/win/GrGLMakeNativeInterface_win.cpp" ]
    if (target_cpu != "arm64") {
      libs += [ "OpenGL32.lib" ]
    }
  } else {
    sources += [ "src/gpu/gl/GrGLMakeNativeInterface_none.cpp" ]
  }

  if (skia_use_vulkan) {
    public_defines += [ "SK_VULKAN" ]
    deps += [ "third_party/vulkanmemoryallocator" ]
    sources += skia_vk_sources
    if (skia_enable_vulkan_debug_layers) {
      public_defines += [ "SK_ENABLE_VK_LAYERS" ]
    }
    if (is_fuchsia) {
      if (using_fuchsia_sdk) {
        public_deps += [ "$fuchsia_sdk_root/pkg:vulkan" ]
      } else {
        public_deps += [ "//src/graphics/lib/vulkan" ]
      }
    }
  }

  if (skia_use_dawn) {
    public_defines += [ "SK_DAWN" ]
    sources += skia_dawn_sources
    public_deps += [
      "//third_party/dawn:dawn_headers",
      "//third_party/dawn:libdawn",
      "//third_party/dawn:libdawn_native_sources",
    ]
    if (dawn_enable_d3d12) {
      libs += [
        "d3d12.lib",
        "dxgi.lib",
        "d3dcompiler.lib",
      ]
    } else if (dawn_enable_metal) {
      libs += [ "Metal.framework" ]
    }
  }

  cflags_objcc = []
  if (skia_use_metal) {
    public_defines += [ "SK_METAL" ]
    sources += skia_metal_sources
    libs += [ "Metal.framework" ]
    libs += [ "Foundation.framework" ]
    cflags_objcc += [ "-fobjc-arc" ]
  }

  if (skia_enable_atlas_text) {
    sources += skia_atlas_text_sources
  }

  if (is_debug) {
    public_defines += [ "SK_ENABLE_DUMP_GPU" ]
  }
}

optional("gif") {
  enabled = !skia_use_wuffs
  sources = [
    "src/codec/SkGifCodec.cpp",
    "third_party/gif/SkGifImageReader.cpp",
  ]
}

optional("heif") {
  enabled = skia_use_libheif
  public_defines = [ "SK_HAS_HEIF_LIBRARY" ]

  deps = []

  sources = [
    "src/codec/SkHeifCodec.cpp",
  ]
}

optional("jpeg") {
  enabled = skia_use_libjpeg_turbo
  public_defines = [ "SK_HAS_JPEG_LIBRARY" ]

  deps = [
    "//third_party/libjpeg-turbo:libjpeg",
  ]
  public = [
    "include/encode/SkJpegEncoder.h",
  ]
  sources = [
    "src/codec/SkJpegCodec.cpp",
    "src/codec/SkJpegDecoderMgr.cpp",
    "src/codec/SkJpegUtility.cpp",
    "src/images/SkJPEGWriteUtility.cpp",
    "src/images/SkJpegEncoder.cpp",
  ]
}

optional("pdf") {
  enabled = skia_use_zlib && skia_enable_pdf
  public_defines = [ "SK_SUPPORT_PDF" ]

  deps = [
    "//third_party/zlib",
  ]
  if (skia_use_libjpeg_turbo) {
    deps += [ ":jpeg" ]
  }
  sources = skia_pdf_sources
  sources_when_disabled = [ "src/pdf/SkDocument_PDF_None.cpp" ]
  if (skia_use_icu && skia_use_harfbuzz && skia_pdf_subset_harfbuzz) {
    deps += [ "//third_party/harfbuzz" ]
    defines = [ "SK_PDF_USE_HARFBUZZ_SUBSET" ]
  } else if (skia_use_icu && skia_use_sfntly) {
    deps += [ "//third_party/sfntly" ]
    defines = [ "SK_PDF_USE_SFNTLY" ]
  }
}

optional("png") {
  enabled = skia_use_libpng
  public_defines = [ "SK_HAS_PNG_LIBRARY" ]

  deps = [
    "//third_party/libpng",
  ]
  sources = [
    "src/codec/SkIcoCodec.cpp",
    "src/codec/SkPngCodec.cpp",
    "src/images/SkPngEncoder.cpp",
  ]
}

optional("raw") {
  enabled = skia_use_dng_sdk && skia_use_libjpeg_turbo && skia_use_piex
  public_defines = [ "SK_CODEC_DECODES_RAW" ]

  deps = [
    "//third_party/dng_sdk",
    "//third_party/libjpeg-turbo:libjpeg",
    "//third_party/piex",
  ]

  # SkRawCodec catches any exceptions thrown by dng_sdk, insulating the rest of
  # Skia.
  configs_to_remove = [ "//gn:no_exceptions" ]

  sources = [
    "src/codec/SkRawCodec.cpp",
  ]
}

import("third_party/skcms/skcms.gni")
source_set("skcms") {
  cflags = []
  if (!is_win || is_clang) {
    cflags += [
      "-w",
      "-std=c11",
    ]
  }

  public = [
    "include/third_party/skcms/skcms.h",
  ]
  include_dirs = [ "include/third_party/skcms" ]
  sources = rebase_path(skcms_sources, ".", "third_party/skcms")
}

optional("typeface_freetype") {
  enabled = skia_use_freetype

  deps = [
    "//third_party/freetype2",
  ]
  sources = [
    "src/ports/SkFontHost_FreeType.cpp",
    "src/ports/SkFontHost_FreeType_common.cpp",
  ]
}

optional("webp") {
  enabled = skia_use_libwebp
  public_defines = [ "SK_HAS_WEBP_LIBRARY" ]

  deps = [
    "//third_party/libwebp",
  ]
  sources = [
    "src/codec/SkWebpCodec.cpp",
    "src/images/SkWebpEncoder.cpp",
  ]
}

optional("wuffs") {
  enabled = skia_use_wuffs
  public_defines = [ "SK_HAS_WUFFS_LIBRARY" ]

  deps = [
    "//third_party/wuffs",
  ]
  sources = [
    "src/codec/SkWuffsCodec.cpp",
  ]
}

optional("xml") {
  enabled = skia_use_expat
  public_defines = [ "SK_XML" ]

  deps = [
    "//third_party/expat",
  ]
  sources = [
    "src/svg/SkSVGCanvas.cpp",
    "src/svg/SkSVGDevice.cpp",
    "src/xml/SkDOM.cpp",
    "src/xml/SkXMLParser.cpp",
    "src/xml/SkXMLWriter.cpp",
  ]
}

optional("sksl_interpreter") {
  enabled = skia_enable_sksl_interpreter
  public_defines = [ "SK_ENABLE_SKSL_INTERPRETER" ]
}

optional("skvm_jit") {
  enabled = skia_enable_skvm_jit
  public_defines = [ "SKVM_JIT" ]
}

if (skia_enable_gpu && skia_generate_workarounds) {
  action("workaround_list") {
    script = "tools/build_workaround_header.py"

    inputs = [
      "src/gpu/gpu_workaround_list.txt",
    ]

    # see comments in skia_compile_processors about out dir path shenanigans.
    output_file =
        rebase_path("include/gpu/GrDriverBugWorkaroundsAutogen.h", root_out_dir)

    outputs = [
      "$root_out_dir/$output_file",
    ]
    args = [
      "--output-file",
      "$output_file",
    ]

    foreach(file, inputs) {
      args += [ rebase_path(file, root_build_dir) ]
    }
  }
}

component("skia") {
  public_configs = [ ":skia_public" ]
  configs += skia_library_configs

  public_deps = [
    ":gpu",
    ":pdf",
    ":skcms",
  ]

  deps = [
    ":arm64",
    ":armv7",
    ":avx",
    ":compile_processors",
    ":crc32",
    ":fontmgr_android",
    ":fontmgr_custom",
    ":fontmgr_custom_empty",
    ":fontmgr_empty",
    ":fontmgr_fontconfig",
    ":fontmgr_fuchsia",
    ":fontmgr_wasm",
    ":fontmgr_win",
    ":fontmgr_win_gdi",
    ":gif",
    ":heif",
    ":hsw",
    ":jpeg",
    ":none",
    ":png",
    ":raw",
    ":sksl_interpreter",
    ":skvm_jit",
    ":sse2",
    ":sse41",
    ":sse42",
    ":ssse3",
    ":webp",
    ":wuffs",
    ":xml",
  ]

  # This file (and all GN files in Skia) are designed to work with an
  # empty sources assignment filter; we handle all that explicitly.
  # We clear the filter here for clients who may have set up a global filter.
  set_sources_assignment_filter([])

  public = skia_core_public
  public += skia_utils_public
  public += skia_effects_public
  public += skia_effects_imagefilter_public
  public += skia_xps_public

  sources = []
  sources += skia_core_sources
  sources += skia_utils_sources
  if (skia_use_xps) {
    sources += skia_xps_sources
  }
  sources += skia_effects_sources
  sources += skia_effects_imagefilter_sources
  sources += skia_sksl_sources
  sources += [
    "src/android/SkAndroidFrameworkUtils.cpp",
    "src/android/SkAnimatedImage.cpp",
    "src/android/SkBitmapRegionCodec.cpp",
    "src/android/SkBitmapRegionDecoder.cpp",
    "src/codec/SkAndroidCodec.cpp",
    "src/codec/SkAndroidCodecAdapter.cpp",
    "src/codec/SkBmpBaseCodec.cpp",
    "src/codec/SkBmpCodec.cpp",
    "src/codec/SkBmpMaskCodec.cpp",
    "src/codec/SkBmpRLECodec.cpp",
    "src/codec/SkBmpStandardCodec.cpp",
    "src/codec/SkCodec.cpp",
    "src/codec/SkCodecImageGenerator.cpp",
    "src/codec/SkColorTable.cpp",
    "src/codec/SkEncodedInfo.cpp",
    "src/codec/SkMaskSwizzler.cpp",
    "src/codec/SkMasks.cpp",
    "src/codec/SkSampledCodec.cpp",
    "src/codec/SkSampler.cpp",
    "src/codec/SkStreamBuffer.cpp",
    "src/codec/SkSwizzler.cpp",
    "src/codec/SkWbmpCodec.cpp",
    "src/images/SkImageEncoder.cpp",
    "src/ports/SkDiscardableMemory_none.cpp",
    "src/ports/SkGlobalInitialization_default.cpp",
    "src/ports/SkImageGenerator_skia.cpp",
    "src/ports/SkMemory_malloc.cpp",
    "src/ports/SkOSFile_stdio.cpp",
    "src/sfnt/SkOTTable_name.cpp",
    "src/sfnt/SkOTUtils.cpp",
    "src/utils/mac/SkStream_mac.cpp",
  ]

  defines = []
  if (!skia_enable_skpicture) {
    defines = [ "SK_DISABLE_SKPICTURE" ]
    public -= skia_skpicture_public
    sources -= skia_skpicture_sources
    sources -= [ "//src/effects/imagefilters/SkPictureImageFilter.cpp" ]
    sources += [ "src/core/SkPicture_none.cpp" ]
  }

  libs = []

  if (is_win) {
    sources += [
      "src/ports/SkDebug_win.cpp",
      "src/ports/SkImageEncoder_WIC.cpp",
      "src/ports/SkImageGeneratorWIC.cpp",
      "src/ports/SkOSFile_win.cpp",
      "src/ports/SkOSLibrary_win.cpp",
      "src/ports/SkTLS_win.cpp",
    ]
    libs += [
      "FontSub.lib",
      "Ole32.lib",
      "OleAut32.lib",
      "User32.lib",
      "Usp10.lib",
    ]
  } else {
    sources += [
      "src/ports/SkOSFile_posix.cpp",
      "src/ports/SkOSLibrary_posix.cpp",
      "src/ports/SkTLS_pthread.cpp",
    ]
    libs += [ "dl" ]
  }

  if (is_android) {
    deps += [ "//third_party/expat" ]
    if (defined(ndk) && ndk != "") {
      deps += [ "//third_party/cpu-features" ]
    }
    sources += [ "src/ports/SkDebug_android.cpp" ]
    libs += [
      "EGL",
      "GLESv2",
      "log",
    ]
  }

  if (is_linux || target_cpu == "wasm") {
    sources += [ "src/ports/SkDebug_stdio.cpp" ]
    if (skia_use_egl) {
      libs += [ "GLESv2" ]
    }
  }

  if (skia_use_fonthost_mac) {
    sources += [ "src/ports/SkFontHost_mac.cpp" ]
  }

  if (is_mac) {
    sources += [
      "src/ports/SkDebug_stdio.cpp",
      "src/ports/SkImageEncoder_CG.cpp",
      "src/ports/SkImageGeneratorCG.cpp",
    ]
    libs += [
      # AppKit symbols NSFontWeightXXX may be dlsym'ed.
      "AppKit.framework",
      "ApplicationServices.framework",
      "OpenGL.framework",
    ]
  }

  if (is_ios) {
    sources += [
      "src/ports/SkDebug_stdio.cpp",
      "src/ports/SkFontHost_mac.cpp",
      "src/ports/SkImageEncoder_CG.cpp",
      "src/ports/SkImageGeneratorCG.cpp",
    ]
    libs += [
      "CoreFoundation.framework",
      "CoreGraphics.framework",
      "CoreText.framework",
      "ImageIO.framework",
      "MobileCoreServices.framework",

      # UIKit symbols UIFontWeightXXX may be dlsym'ed.
      "UIKit.framework",
    ]
  }

  if (is_fuchsia) {
    sources += [ "src/ports/SkDebug_stdio.cpp" ]
  }

  if (skia_enable_spirv_validation) {
    deps += [ "//third_party/spirv-tools" ]
    defines += [ "SK_ENABLE_SPIRV_VALIDATION" ]
  }

  if (skia_include_multiframe_procs) {
    sources += [ "tools/SkSharingProc.cpp" ]
  }
}

# DebugCanvas used in experimental/wasm-skp-debugger
if (target_cpu == "wasm") {
  static_library("debugcanvas") {
    public_configs = [ ":skia_public" ]

    sources = [
      "tools/SkSharingProc.cpp",
      "tools/UrlDataManager.cpp",
      "tools/debugger/DebugCanvas.cpp",
      "tools/debugger/DrawCommand.cpp",
      "tools/debugger/JsonWriteBuffer.cpp",
    ]

    deps = [
      ":fontmgr_wasm",
    ]
  }
}

static_library("pathkit") {
  check_includes = false
  public_configs = [ ":skia_public" ]
  configs += skia_library_configs

  deps = [
    ":arm64",
    ":armv7",
    ":avx",
    ":crc32",
    ":hsw",
    ":none",
    ":sse2",
    ":sse41",
    ":sse42",
    ":ssse3",
  ]

  # This file (and all GN files in Skia) are designed to work with an
  # empty sources assignment filter; we handle all that explicitly.
  # We clear the filter here for clients who may have set up a global filter.
  set_sources_assignment_filter([])

  sources = []
  sources += skia_pathops_sources
  sources += skia_pathops_public
  sources += [
    "src/core/SkAnalyticEdge.cpp",
    "src/core/SkArenaAlloc.cpp",
    "src/core/SkContourMeasure.cpp",
    "src/core/SkCubicMap.cpp",
    "src/core/SkEdge.cpp",
    "src/core/SkEdgeBuilder.cpp",
    "src/core/SkEdgeClipper.cpp",
    "src/core/SkGeometry.cpp",
    "src/core/SkLineClipper.cpp",
    "src/core/SkMallocPixelRef.cpp",
    "src/core/SkMath.cpp",
    "src/core/SkMatrix.cpp",
    "src/core/SkOpts.cpp",
    "src/core/SkPaint.cpp",
    "src/core/SkPath.cpp",
    "src/core/SkPathEffect.cpp",
    "src/core/SkPathMeasure.cpp",
    "src/core/SkPathRef.cpp",
    "src/core/SkPoint.cpp",
    "src/core/SkRRect.cpp",
    "src/core/SkRect.cpp",
    "src/core/SkSemaphore.cpp",
    "src/core/SkStream.cpp",
    "src/core/SkString.cpp",
    "src/core/SkStringUtils.cpp",
    "src/core/SkStroke.cpp",
    "src/core/SkStrokeRec.cpp",
    "src/core/SkStrokerPriv.cpp",
    "src/core/SkThreadID.cpp",
    "src/core/SkUtils.cpp",
    "src/effects/SkDashPathEffect.cpp",
    "src/effects/SkTrimPathEffect.cpp",
    "src/ports/SkDebug_stdio.cpp",
    "src/ports/SkMemory_malloc.cpp",
    "src/utils/SkDashPath.cpp",
    "src/utils/SkParse.cpp",
    "src/utils/SkParsePath.cpp",
    "src/utils/SkUTF.cpp",
  ]
}

group("modules") {
  deps = [
    "modules/particles",
    "modules/skottie",
    "modules/skshaper",
  ]
}

executable("cpu_modules") {
  sources = [
    "tools/cpu_modules.cpp",
  ]
  deps = [
    ":skia",
    "modules/particles",
  ]
}

# Targets guarded by skia_enable_tools may use //third_party freely.
if (skia_enable_tools) {
  skia_public_includes = [
    "include/android",
    "include/atlastext",
    "include/c",
    "include/codec",
    "include/config",
    "include/core",
    "include/docs",
    "include/effects",
    "include/encode",
    "include/gpu",
    "include/pathops",
    "include/ports",
    "include/svg",
    "include/utils",
    "include/utils/mac",
    "modules/sksg/include",
    "modules/skshaper/include",
    "modules/skottie/include",
  ]

  # Used by gn_to_bp.py to list our public include dirs.
  source_set("public") {
    configs += [ ":skia_public" ]
    include_dirs = skia_public_includes
  }

  config("skia.h_config") {
    include_dirs = [ "$target_gen_dir" ]
  }
  action("skia.h") {
    public_configs = [ ":skia.h_config" ]
    skia_h = "$target_gen_dir/skia.h"
    script = "gn/find_headers.py"

    args = [ rebase_path("//bin/gn") ] + [ rebase_path("//") ] +
           [ rebase_path(skia_h, root_build_dir) ] +
           rebase_path(skia_public_includes)
    depfile = "$skia_h.deps"
    outputs = [
      skia_h,
    ]
  }

  if (target_cpu == "x64") {
    executable("fiddle") {
      check_includes = false
      libs = []
      sources = [
        "tools/fiddle/draw.cpp",
        "tools/fiddle/fiddle_main.cpp",
      ]

      if (skia_use_egl) {
        sources += [ "tools/fiddle/egl_context.cpp" ]
      } else {
        sources += [ "tools/fiddle/null_context.cpp" ]
      }
      testonly = true
      deps = [
        ":flags",
        ":gpu_tool_utils",
        ":skia",
        ":skia.h",
        "modules/skottie",
        "modules/skshaper",
      ]
    }
  }

  config("our_vulkan_headers") {
    # We add this directory to simulate the client already have
    # vulkan/vulkan_core.h on their path.
    include_dirs = [ "include/third_party/vulkan" ]
  }

  source_set("public_headers_warnings_check") {
    sources = [
      "tools/public_headers_warnings_check.cpp",
    ]
    configs -= [ "//gn:warnings_except_public_headers" ]
    configs += [ ":our_vulkan_headers" ]
    deps = [
      ":skia",
      ":skia.h",
      "modules/skottie",
      "modules/skshaper",
    ]

    if (skia_use_dawn) {
      deps += [ "//third_party/dawn:dawn_headers" ]
    }
  }

  template("test_lib") {
    config(target_name + "_config") {
      if (defined(invoker.public_defines)) {
        defines = invoker.public_defines
      }
    }
    source_set(target_name) {
      forward_variables_from(invoker, "*", [])
      check_includes = false
      public_configs = [
        ":" + target_name + "_config",
        ":skia_private",
      ]

      if (!defined(deps)) {
        deps = []
      }
      deps += [ ":skia" ]
      testonly = true
    }
  }

  template("test_app") {
    if (is_ios) {
      app_name = target_name
      gen_path = target_gen_dir

      action("${app_name}_generate_info_plist") {
        script = "//gn/gen_plist_ios.py"
        outputs = [
          "$gen_path/${app_name}_Info.plist",
        ]
        args = [ rebase_path("$gen_path/$app_name", root_build_dir) ]
      }

      bundle_data("${app_name}_bundle_info_plist") {
        public_deps = [
          ":${app_name}_generate_info_plist",
        ]
        sources = [
          "$gen_path/${app_name}_Info.plist",
        ]
        outputs = [
          "{{bundle_root_dir}}/Info.plist",
        ]
      }

      has_skps = "True" == exec_script("//gn/checkdir.py",
                                       [ rebase_path("skps", root_build_dir) ],
                                       "trim string")
      bundle_data("${app_name}_bundle_resources") {
        sources = [
          "resources",
        ]
        outputs = [
          # iOS reserves the folders 'Resources' and 'resources' so store one level deeper
          "{{bundle_resources_dir}}/data/resources",
        ]
      }
      if (has_skps) {
        bundle_data("${app_name}_bundle_skps") {
          sources = [
            "skps",
          ]
          outputs = [
            # Store in same folder as resources
            "{{bundle_resources_dir}}/data/skps",
          ]
        }
      }

      executable("${app_name}_generate_executable") {
        forward_variables_from(invoker,
                               "*",
                               [
                                 "output_name",
                                 "visibility",
                                 "is_shared_library",
                               ])
        configs += [ ":skia_private" ]
        testonly = true
        output_name = rebase_path("$gen_path/$app_name", root_build_dir)
      }

      bundle_data("${app_name}_bundle_executable") {
        public_deps = [
          ":${app_name}_generate_executable",
        ]
        sources = [
          "$gen_path/$app_name",
        ]
        outputs = [
          "{{bundle_executable_dir}}/$app_name",
        ]
        testonly = true
      }

      bundle_data("${app_name}_bundle_symbols") {
        public_deps = [
          ":${app_name}_generate_executable",
        ]
        sources = [
          "$gen_path/${app_name}.dSYM",
        ]
        outputs = [
          "{{bundle_executable_dir}}/${app_name}.dSYM",
        ]
        testonly = true
      }

      create_bundle("$app_name") {
        product_type = "com.apple.product-type.application"
        testonly = true

        bundle_root_dir = "${root_build_dir}/${target_name}.app"
        bundle_resources_dir = bundle_root_dir
        bundle_executable_dir = bundle_root_dir

        deps = [
          ":${app_name}_bundle_executable",
          ":${app_name}_bundle_info_plist",
          ":${app_name}_bundle_resources",
          ":${app_name}_bundle_symbols",
        ]
        if (has_skps) {
          deps += [ ":${app_name}_bundle_skps" ]
        }

        # should only code sign when running on a device, not the simulator
        if (target_cpu != "x64") {
          code_signing_script = "//gn/codesign_ios.py"
          code_signing_sources = [ "$target_gen_dir/$app_name" ]
          code_signing_outputs = [
            "$bundle_root_dir/_CodeSignature/CodeResources",
            "$bundle_root_dir/embedded.mobileprovision",
          ]
          code_signing_args = [
            rebase_path("$bundle_root_dir", root_build_dir),
            skia_ios_identity,
            skia_ios_profile,
          ]
        }
      }
    } else {
      # !is_ios

      if (defined(invoker.is_shared_library) && invoker.is_shared_library) {
        shared_library("lib" + target_name) {
          forward_variables_from(invoker, "*", [ "is_shared_library" ])
          configs += [ ":skia_private" ]
          testonly = true
        }
      } else {
        _executable = target_name
        executable(_executable) {
          check_includes = false
          forward_variables_from(invoker, "*", [ "is_shared_library" ])
          configs += [ ":skia_private" ]
          testonly = true
        }
      }
      if (is_android && skia_android_serial != "" && defined(_executable)) {
        action("push_" + target_name) {
          script = "gn/push_to_android.py"
          deps = [
            ":" + _executable,
          ]
          _stamp = "$target_gen_dir/$_executable.pushed_$skia_android_serial"
          outputs = [
            _stamp,
          ]
          args = [
            rebase_path("$root_build_dir/$_executable"),
            skia_android_serial,
            rebase_path(_stamp),
          ]
          testonly = true
        }
      }
    }
  }

  config("moltenvk_config") {
    if (defined(skia_moltenvk_path) && skia_moltenvk_path != "") {
      if (is_ios) {
        moltenvk_framework_path = "$skia_moltenvk_path/MoltenVK/iOS"
      } else {
        moltenvk_framework_path = "$skia_moltenvk_path/MoltenVK/macOS"
      }
      cflags = [ "-F$moltenvk_framework_path" ]
      ldflags = [ "-F$moltenvk_framework_path" ]
      libs = [
        "MoltenVK.framework",
        "Metal.framework",
        "IOSurface.framework",
        "QuartzCore.framework",
        "Foundation.framework",
      ]
      if (is_ios) {
        libs += [ "UIKit.framework" ]
      } else {
        libs += [ "IOKit.framework" ]
      }
      defines = [ "SK_MOLTENVK" ]
    }
  }

  source_set("moltenvk") {
    public_configs = [ ":moltenvk_config" ]
  }

  test_lib("gpu_tool_utils") {
    public_defines = []

    # Bots and even devs may not have Vulkan headers, so put
    # include/third_party/vulkan on our path so they're always available.
    all_dependent_configs = [ ":our_vulkan_headers" ]

    defines = []
    if (skia_enable_discrete_gpu) {
      defines += [ "SK_ENABLE_DISCRETE_GPU" ]
    }

    deps = []
    public_deps = []
    sources = [
      "tools/gpu/GrContextFactory.cpp",
      "tools/gpu/GrTest.cpp",
      "tools/gpu/MemoryCache.cpp",
      "tools/gpu/MemoryCache.h",
      "tools/gpu/ProxyUtils.cpp",
      "tools/gpu/TestContext.cpp",
      "tools/gpu/YUVUtils.cpp",
      "tools/gpu/YUVUtils.h",
      "tools/gpu/atlastext/GLTestAtlasTextRenderer.cpp",
      "tools/gpu/gl/GLTestContext.cpp",
      "tools/gpu/gl/command_buffer/GLTestContext_command_buffer.cpp",
      "tools/gpu/mock/MockTestContext.cpp",
    ]
    libs = []

    if (is_android || skia_use_egl) {
      sources += [ "tools/gpu/gl/egl/CreatePlatformGLTestContext_egl.cpp" ]
    } else if (is_ios) {
      sources += [ "tools/gpu/gl/iOS/CreatePlatformGLTestContext_iOS.mm" ]
      libs += [ "OpenGLES.framework" ]
    } else if (is_linux) {
      sources += [ "tools/gpu/gl/glx/CreatePlatformGLTestContext_glx.cpp" ]
      libs += [
        "GLU",
        "X11",
      ]
    } else if (is_mac) {
      sources += [ "tools/gpu/gl/mac/CreatePlatformGLTestContext_mac.cpp" ]
    } else if (is_win) {
      sources += [ "tools/gpu/gl/win/CreatePlatformGLTestContext_win.cpp" ]
      libs += [ "Gdi32.lib" ]
      if (target_cpu != "arm64") {
        libs += [ "OpenGL32.lib" ]
      }
    }

    cflags_objcc = [ "-fobjc-arc" ]

    if (skia_use_angle) {
      deps += [ "//third_party/angle2" ]
      sources += [ "tools/gpu/gl/angle/GLTestContext_angle.cpp" ]
    }

    if (skia_use_vulkan) {
      sources += [ "tools/gpu/vk/VkTestContext.cpp" ]
      sources += [ "tools/gpu/vk/VkTestUtils.cpp" ]
      if (defined(skia_moltenvk_path) && skia_moltenvk_path != "") {
        public_deps += [ ":moltenvk" ]
      }
    }
    if (skia_use_metal) {
      sources += [ "tools/gpu/mtl/MtlTestContext.mm" ]
    }
    if (skia_use_dawn) {
      public_deps += [ "//third_party/dawn:dawn_headers" ]
      sources += [ "tools/gpu/dawn/DawnTestContext.cpp" ]
    }
  }

  test_lib("flags") {
    sources = [
      "tools/flags/CommandLineFlags.cpp",
    ]
  }

  test_lib("common_flags_config") {
    sources = [
      "tools/flags/CommonFlagsConfig.cpp",
    ]
    deps = [
      ":flags",
    ]
    public_deps = [
      ":gpu_tool_utils",
    ]
  }
  test_lib("common_flags_gpu") {
    sources = [
      "tools/flags/CommonFlagsGpu.cpp",
    ]
    deps = [
      ":flags",
    ]
    public_deps = [
      ":gpu_tool_utils",
    ]
  }
  test_lib("common_flags_images") {
    sources = [
      "tools/flags/CommonFlagsImages.cpp",
    ]
    deps = [
      ":flags",
    ]
  }
  test_lib("common_flags_aa") {
    sources = [
      "tools/flags/CommonFlagsAA.cpp",
    ]
    deps = [
      ":flags",
    ]
  }

  test_lib("trace") {
    deps = [
      ":flags",
    ]
    sources = [
      "tools/trace/ChromeTracingTracer.cpp",
      "tools/trace/ChromeTracingTracer.h",
      "tools/trace/EventTracingPriv.cpp",
      "tools/trace/EventTracingPriv.h",
      "tools/trace/SkDebugfTracer.cpp",
      "tools/trace/SkDebugfTracer.h",
    ]
  }

  test_lib("tool_utils") {
    sources = [
      "tools/AndroidSkDebugToStdOut.cpp",
      "tools/AutoreleasePool.h",
      "tools/CrashHandler.cpp",
      "tools/DDLPromiseImageHelper.cpp",
      "tools/DDLTileHelper.cpp",
      "tools/LsanSuppressions.cpp",
      "tools/ProcStats.cpp",
      "tools/Resources.cpp",
      "tools/SkMetaData.cpp",
      "tools/SkMetaData.h",
      "tools/SkSharingProc.cpp",
      "tools/ToolUtils.cpp",
      "tools/UrlDataManager.cpp",
      "tools/debugger/DebugCanvas.cpp",
      "tools/debugger/DrawCommand.cpp",
      "tools/debugger/JsonWriteBuffer.cpp",
      "tools/fonts/RandomScalerContext.cpp",
      "tools/fonts/TestEmptyTypeface.h",
      "tools/fonts/TestFontMgr.cpp",
      "tools/fonts/TestFontMgr.h",
      "tools/fonts/TestSVGTypeface.cpp",
      "tools/fonts/TestSVGTypeface.h",
      "tools/fonts/TestTypeface.cpp",
      "tools/fonts/TestTypeface.h",
      "tools/fonts/ToolUtilsFont.cpp",
      "tools/random_parse_path.cpp",
      "tools/timer/TimeUtils.h",
      "tools/timer/Timer.cpp",
    ]
    libs = []
    if (is_ios) {
      sources += [ "tools/ios_utils.m" ]
      sources += [ "tools/ios_utils.h" ]
      if (skia_use_metal) {
        sources += [ "tools/AutoreleasePool.mm" ]
      }
      libs += [ "Foundation.framework" ]
    } else if (is_mac) {
      if (skia_use_metal) {
        sources += [ "tools/AutoreleasePool.mm" ]
        libs += [ "Foundation.framework" ]
      }
    } else if (is_win) {
      libs += [ "DbgHelp.lib" ]
    }

    defines = []
    if (skia_tools_require_resources) {
      defines += [ "SK_TOOLS_REQUIRE_RESOURCES" ]
    }
    deps = [
      ":experimental_svg_model",
      ":flags",
    ]
    public_deps = [
      ":gpu_tool_utils",
    ]
  }

  test_lib("etc1") {
    sources = [
      "third_party/etc1/etc1.cpp",
    ]
  }

  if (skia_use_ffmpeg) {
    test_lib("video_decoder") {
      sources = [
        "experimental/ffmpeg/SkVideoDecoder.cpp",
        "experimental/ffmpeg/SkVideoDecoder.h",
        "experimental/ffmpeg/SkVideoEncoder.cpp",
        "experimental/ffmpeg/SkVideoEncoder.h",
      ]
      libs = [
        "swscale",
        "avcodec",
        "avformat",
        "avutil",
      ]
    }
  }

  import("gn/gm.gni")
  test_lib("gm") {
    sources = gm_sources
    deps = [
      ":etc1",
      ":flags",
      ":skia",
      ":tool_utils",
      "modules/skottie",
      "modules/skottie:gm",
      "modules/sksg",
      "modules/skshaper",
    ]
    public_deps = [
      ":gpu_tool_utils",
    ]

    if (skia_use_ffmpeg) {
      deps += [ ":video_decoder" ]
      sources += [ "gm/video_decoder.cpp" ]
    }
  }

  test_lib("skvm_builders") {
    sources = [
      "tools/SkVMBuilders.cpp",
      "tools/SkVMBuilders.h",
    ]
  }

  import("gn/tests.gni")
  test_lib("tests") {
    sources = tests_sources + pathops_tests_sources
    if (skia_use_metal) {
      sources += metal_tests_sources
    }
    if (!skia_enable_fontmgr_android) {
      sources -= [ "//tests/FontMgrAndroidParserTest.cpp" ]
    }
    if (!(skia_use_freetype && skia_use_fontconfig)) {
      sources -= [ "//tests/FontMgrFontConfigTest.cpp" ]
    }
    deps = [
      ":experimental_svg_model",
      ":flags",
      ":skia",
      ":skvm_builders",
      ":tool_utils",
      "modules/skottie:tests",
      "modules/skparagraph:tests",
      "modules/sksg:tests",
      "modules/skshaper",
      "//third_party/libpng",
      "//third_party/libwebp",
      "//third_party/zlib",
    ]
    public_deps = [
      ":gpu_tool_utils",  # Test.h #includes headers from this target.
    ]
  }

  import("gn/bench.gni")
  test_lib("bench") {
    sources = bench_sources
    deps = [
      ":flags",
      ":gm",
      ":gpu_tool_utils",
      ":skia",
      ":skvm_builders",
      ":tool_utils",
      "modules/skparagraph:bench",
      "modules/skshaper",
    ]
  }

  test_lib("experimental_svg_model") {
    if (skia_use_expat) {
      sources = [
        "experimental/svg/model/SkSVGAttribute.cpp",
        "experimental/svg/model/SkSVGAttributeParser.cpp",
        "experimental/svg/model/SkSVGCircle.cpp",
        "experimental/svg/model/SkSVGClipPath.cpp",
        "experimental/svg/model/SkSVGContainer.cpp",
        "experimental/svg/model/SkSVGDOM.cpp",
        "experimental/svg/model/SkSVGEllipse.cpp",
        "experimental/svg/model/SkSVGGradient.cpp",
        "experimental/svg/model/SkSVGLine.cpp",
        "experimental/svg/model/SkSVGLinearGradient.cpp",
        "experimental/svg/model/SkSVGNode.cpp",
        "experimental/svg/model/SkSVGPath.cpp",
        "experimental/svg/model/SkSVGPattern.cpp",
        "experimental/svg/model/SkSVGPoly.cpp",
        "experimental/svg/model/SkSVGRadialGradient.cpp",
        "experimental/svg/model/SkSVGRect.cpp",
        "experimental/svg/model/SkSVGRenderContext.cpp",
        "experimental/svg/model/SkSVGSVG.cpp",
        "experimental/svg/model/SkSVGShape.cpp",
        "experimental/svg/model/SkSVGStop.cpp",
        "experimental/svg/model/SkSVGTransformableNode.cpp",
        "experimental/svg/model/SkSVGUse.cpp",
        "experimental/svg/model/SkSVGValue.cpp",
      ]
      deps = [
        ":skia",
        ":xml",
      ]
    }
  }

  test_lib("experimental_xform") {
    sources = [
      "experimental/xform/SkShape.cpp",
      "experimental/xform/SkXform.cpp",
      "experimental/xform/XContext.cpp",
    ]
    deps = [
      ":skia",
    ]
  }

  if (skia_use_lua) {
    test_lib("lua") {
      sources = [
        "src/utils/SkLua.cpp",
        "src/utils/SkLuaCanvas.cpp",
      ]
      deps = [
        "modules/skshaper",
        "//third_party/lua",
      ]
    }

    test_app("lua_app") {
      sources = [
        "tools/lua/lua_app.cpp",
      ]
      deps = [
        ":lua",
        ":skia",
        "//third_party/lua",
      ]
    }

    test_app("lua_pictures") {
      sources = [
        "tools/lua/lua_pictures.cpp",
      ]
      deps = [
        ":flags",
        ":lua",
        ":skia",
        ":tool_utils",
        "//third_party/lua",
      ]
    }
  }

  if (is_linux || is_mac) {
    test_app("skottie_tool") {
      deps = [
        "modules/skottie:tool",
      ]
    }
  }

  test_app("make_skqp_model") {
    sources = [
      "tools/skqp/make_skqp_model.cpp",
    ]
    deps = [
      ":skia",
    ]
  }

  if (target_cpu != "wasm") {
    import("gn/samples.gni")
    test_lib("samples") {
      sources = samples_sources
      public_deps = [
        ":tool_utils",
      ]
      deps = [
        ":experimental_svg_model",
        ":flags",
        ":gpu_tool_utils",
        ":xml",
        "modules/skparagraph:samples",
        "modules/sksg",
        "modules/skshaper",
      ]

      if (skia_use_lua) {
        sources += [ "samplecode/SampleLua.cpp" ]
        deps += [
          ":lua",
          "//third_party/lua",
        ]
      }
    }
    test_app("imgcvt") {
      sources = [
        "tools/imgcvt.cpp",
      ]
      deps = [
        ":skcms",
        ":skia",
      ]
    }
    test_lib("hash_and_encode") {
      sources = [
        "tools/HashAndEncode.cpp",
        "tools/HashAndEncode.h",
      ]
      deps = [
        ":flags",
        ":skia",
        "//third_party/libpng",
      ]
    }
    test_app("fm") {
      sources = [
        "tools/fm/fm.cpp",
      ]
      deps = [
        ":common_flags_aa",
        ":common_flags_gpu",
        ":experimental_svg_model",
        ":flags",
        ":gm",
        ":gpu_tool_utils",
        ":hash_and_encode",
        ":skia",
        ":tool_utils",
        ":trace",
        "modules/skottie",
        "modules/skottie:utils",
      ]
    }
    test_app("dm") {
      sources = [
        "dm/DM.cpp",
        "dm/DMGpuTestProcs.cpp",
        "dm/DMJsonWriter.cpp",
        "dm/DMSrcSink.cpp",
      ]
      deps = [
        ":common_flags_aa",
        ":common_flags_config",
        ":common_flags_gpu",
        ":common_flags_images",
        ":experimental_svg_model",
        ":flags",
        ":gm",
        ":gpu_tool_utils",
        ":hash_and_encode",
        ":skia",
        ":tests",
        ":tool_utils",
        ":trace",
        "modules/skottie",
        "modules/skottie:utils",
        "modules/sksg",
      ]
    }
  }

  if (!is_win) {
    test_app("remote_demo") {
      sources = [
        "tools/remote_demo.cpp",
      ]
      deps = [
        ":skia",
      ]
    }
  }

  test_app("nanobench") {
    sources = [
      "bench/nanobench.cpp",
    ]
    deps = [
      ":bench",
      ":common_flags_aa",
      ":common_flags_config",
      ":common_flags_gpu",
      ":common_flags_images",
      ":experimental_svg_model",
      ":flags",
      ":gm",
      ":gpu_tool_utils",
      ":skia",
      ":tool_utils",
      ":trace",
      "modules/skparagraph:bench",
      "modules/sksg",
      "modules/skshaper",
    ]
  }

  test_app("skpinfo") {
    sources = [
      "tools/skpinfo.cpp",
    ]
    deps = [
      ":flags",
      ":skia",
    ]
  }

  if (skia_use_ffmpeg) {
    test_app("skottie2movie") {
      sources = [
        "tools/skottie2movie.cpp",
      ]
      deps = [
        ":flags",
        ":skia",
        ":video_decoder",
        "modules/skottie",
        "modules/skottie:utils",
      ]
    }
  }

  test_app("skpbench") {
    sources = [
      "tools/skpbench/skpbench.cpp",
    ]
    deps = [
      ":common_flags_config",
      ":common_flags_gpu",
      ":flags",
      ":gpu_tool_utils",
      ":skia",
      ":tool_utils",
    ]
  }

  test_app("sktexttopdf") {
    sources = [
      "tools/using_skia_and_harfbuzz.cpp",
    ]
    deps = [
      ":skia",
      "modules/skshaper",
    ]
  }

  test_app("create_test_font") {
    sources = [
      "tools/fonts/create_test_font.cpp",
    ]
    deps = [
      ":skia",
    ]
    assert_no_deps = [
      # tool_utils requires the output of this app.
      ":tool_utils",
    ]
  }

  if (skia_use_expat) {
    test_app("create_test_font_color") {
      sources = [
        "tools/fonts/create_test_font_color.cpp",
      ]
      deps = [
        ":flags",
        ":skia",
        ":tool_utils",
      ]
    }
  }

  test_app("get_images_from_skps") {
    sources = [
      "tools/get_images_from_skps.cpp",
    ]
    deps = [
      ":flags",
      ":skia",
    ]
  }

  if (!is_ios && target_cpu != "wasm" && !(is_win && target_cpu == "arm64")) {
    test_app("skiaserve") {
      sources = [
        "tools/skiaserve/Request.cpp",
        "tools/skiaserve/Response.cpp",
        "tools/skiaserve/skiaserve.cpp",
        "tools/skiaserve/urlhandlers/BreakHandler.cpp",
        "tools/skiaserve/urlhandlers/ClipAlphaHandler.cpp",
        "tools/skiaserve/urlhandlers/CmdHandler.cpp",
        "tools/skiaserve/urlhandlers/ColorModeHandler.cpp",
        "tools/skiaserve/urlhandlers/DataHandler.cpp",
        "tools/skiaserve/urlhandlers/DownloadHandler.cpp",
        "tools/skiaserve/urlhandlers/EnableGPUHandler.cpp",
        "tools/skiaserve/urlhandlers/ImgHandler.cpp",
        "tools/skiaserve/urlhandlers/InfoHandler.cpp",
        "tools/skiaserve/urlhandlers/OpBoundsHandler.cpp",
        "tools/skiaserve/urlhandlers/OpsHandler.cpp",
        "tools/skiaserve/urlhandlers/OverdrawHandler.cpp",
        "tools/skiaserve/urlhandlers/PostHandler.cpp",
        "tools/skiaserve/urlhandlers/QuitHandler.cpp",
        "tools/skiaserve/urlhandlers/RootHandler.cpp",
      ]
      deps = [
        ":flags",
        ":gpu_tool_utils",
        ":skia",
        ":tool_utils",
        "//third_party/libmicrohttpd",
      ]
    }
  }

  test_app("fuzz") {
    sources = [
      "fuzz/Fuzz.cpp",
      "fuzz/FuzzCanvas.cpp",
      "fuzz/FuzzCommon.cpp",
      "fuzz/FuzzDrawFunctions.cpp",
      "fuzz/FuzzEncoders.cpp",
      "fuzz/FuzzGradients.cpp",
      "fuzz/FuzzMain.cpp",
      "fuzz/FuzzParsePath.cpp",
      "fuzz/FuzzPathMeasure.cpp",
      "fuzz/FuzzPathop.cpp",
      "fuzz/FuzzPolyUtils.cpp",
      "fuzz/FuzzRegionOp.cpp",
      "fuzz/oss_fuzz/FuzzAndroidCodec.cpp",
      "fuzz/oss_fuzz/FuzzAnimatedImage.cpp",
      "fuzz/oss_fuzz/FuzzImage.cpp",
      "fuzz/oss_fuzz/FuzzImageFilterDeserialize.cpp",
      "fuzz/oss_fuzz/FuzzIncrementalImage.cpp",
      "fuzz/oss_fuzz/FuzzJSON.cpp",
      "fuzz/oss_fuzz/FuzzPathDeserialize.cpp",
      "fuzz/oss_fuzz/FuzzRegionDeserialize.cpp",
      "fuzz/oss_fuzz/FuzzRegionSetPath.cpp",
      "fuzz/oss_fuzz/FuzzSKSL2GLSL.cpp",
      "fuzz/oss_fuzz/FuzzSKSL2Metal.cpp",
      "fuzz/oss_fuzz/FuzzSKSL2Pipeline.cpp",
      "fuzz/oss_fuzz/FuzzSKSL2SPIRV.cpp",
      "fuzz/oss_fuzz/FuzzTextBlobDeserialize.cpp",
      "tools/UrlDataManager.cpp",
      "tools/debugger/DebugCanvas.cpp",
      "tools/debugger/DrawCommand.cpp",
      "tools/debugger/JsonWriteBuffer.cpp",
    ]
    deps = [
      ":flags",
      ":gpu_tool_utils",
      ":skia",
      "modules/skottie:fuzz",
    ]
  }

  test_app("pathops_unittest") {
    sources = pathops_tests_sources + [
                rebase_path("tests/skia_test.cpp"),
                rebase_path("tests/Test.cpp"),
              ]
    deps = [
      ":flags",
      ":gpu_tool_utils",
      ":skia",
      ":tool_utils",
    ]
  }

  test_app("dump_record") {
    sources = [
      "tools/DumpRecord.cpp",
      "tools/dump_record.cpp",
    ]
    deps = [
      ":flags",
      ":skia",
    ]
  }

  test_app("skdiff") {
    sources = [
      "tools/skdiff/skdiff.cpp",
      "tools/skdiff/skdiff_html.cpp",
      "tools/skdiff/skdiff_main.cpp",
      "tools/skdiff/skdiff_utils.cpp",
    ]
    deps = [
      ":skia",
      ":tool_utils",
    ]
  }

  test_app("skp_parser") {
    sources = [
      "tools/skp_parser.cpp",
    ]
    deps = [
      ":skia",
      ":tool_utils",
    ]
  }

  if (!is_win) {
    test_lib("skqp_lib") {
      defines =
          [ "SK_SKQP_GLOBAL_ERROR_TOLERANCE=$skia_skqp_global_error_tolerance" ]
      sources = [
        "dm/DMGpuTestProcs.cpp",
        "tools/skqp/src/skqp.cpp",
        "tools/skqp/src/skqp_model.cpp",
      ]
      deps = [
        ":gm",
        ":gpu_tool_utils",
        ":skia",
        ":tests",
        ":tool_utils",
      ]
    }
    test_app("skqp") {
      sources = [
        "tools/skqp/src/skqp_main.cpp",
      ]
      deps = [
        ":skia",
        ":skqp_lib",
        ":tool_utils",
      ]
    }
    test_app("jitter_gms") {
      sources = [
        "tools/skqp/jitter_gms.cpp",
      ]
      deps = [
        ":gm",
        ":skia",
        ":skqp_lib",
      ]
    }
  }
  if (is_android) {
    test_app("skqp_app") {
      is_shared_library = true
      sources = [
        "tools/skqp/src/jni_skqp.cpp",
      ]
      deps = [
        ":skia",
        ":skqp_lib",
        ":tool_utils",
      ]
      libs = [ "android" ]
    }
  }
  if (is_android && skia_enable_gpu) {
    test_app("skottie_android") {
      is_shared_library = true

      sources = [
        "platform_tools/android/apps/skottie/src/main/cpp/JavaInputStreamAdaptor.cpp",
        "platform_tools/android/apps/skottie/src/main/cpp/native-lib.cpp",
      ]
      libs = []

      deps = [
        ":skia",
        "modules/skottie",
        "modules/sksg:samples",
      ]
    }
  }

  test_app("list_gms") {
    sources = [
      "tools/list_gms.cpp",
    ]
    deps = [
      ":gm",
      ":skia",
    ]
  }
  test_app("list_gpu_unit_tests") {
    sources = [
      "dm/DMGpuTestProcs.cpp",
      "tools/list_gpu_unit_tests.cpp",
    ]
    deps = [
      ":skia",
      ":tests",
    ]
  }

  test_lib("sk_app") {
    public_deps = [
      ":gpu_tool_utils",
      ":skia",
    ]
    sources = [
      "tools/sk_app/CommandSet.cpp",
      "tools/sk_app/GLWindowContext.cpp",
      "tools/sk_app/Window.cpp",
    ]
    libs = []

    if (is_android) {
      sources += [
        "tools/sk_app/android/GLWindowContext_android.cpp",
        "tools/sk_app/android/RasterWindowContext_android.cpp",
        "tools/sk_app/android/Window_android.cpp",
        "tools/sk_app/android/main_android.cpp",
        "tools/sk_app/android/surface_glue_android.cpp",
      ]
      libs += [ "android" ]
    } else if (is_linux) {
      sources += [
        "tools/sk_app/unix/GLWindowContext_unix.cpp",
        "tools/sk_app/unix/RasterWindowContext_unix.cpp",
        "tools/sk_app/unix/Window_unix.cpp",
        "tools/sk_app/unix/keysym2ucs.c",
        "tools/sk_app/unix/main_unix.cpp",
      ]
      libs += [
        "GL",
        "X11",
      ]
    } else if (is_win) {
      sources += [
        "tools/sk_app/win/GLWindowContext_win.cpp",
        "tools/sk_app/win/RasterWindowContext_win.cpp",
        "tools/sk_app/win/Window_win.cpp",
        "tools/sk_app/win/main_win.cpp",
      ]
      if (skia_use_angle) {
        sources += [ "tools/sk_app/win/ANGLEWindowContext_win.cpp" ]
      }
    } else if (is_mac) {
      sources += [
        "tools/sk_app/mac/GLWindowContext_mac.mm",
        "tools/sk_app/mac/RasterWindowContext_mac.mm",
        "tools/sk_app/mac/Window_mac.mm",
        "tools/sk_app/mac/main_mac.mm",
      ]
      libs += [
        "QuartzCore.framework",
        "Cocoa.framework",
        "Foundation.framework",
      ]
    } else if (is_ios) {
      sources += [
        "tools/sk_app/ios/GLWindowContext_ios.cpp",
        "tools/sk_app/ios/RasterWindowContext_ios.cpp",
        "tools/sk_app/ios/Window_ios.cpp",
        "tools/sk_app/ios/main_ios.cpp",
      ]
    }

    if (skia_use_vulkan) {
      sources += [ "tools/sk_app/VulkanWindowContext.cpp" ]
      if (is_android) {
        sources += [ "tools/sk_app/android/VulkanWindowContext_android.cpp" ]
      } else if (is_linux) {
        sources += [ "tools/sk_app/unix/VulkanWindowContext_unix.cpp" ]
        libs += [ "X11-xcb" ]
      } else if (is_win) {
        sources += [ "tools/sk_app/win/VulkanWindowContext_win.cpp" ]
      } else if (is_mac) {
        sources += [ "tools/sk_app/mac/VulkanWindowContext_mac.mm" ]
        libs += [ "MetalKit.framework" ]
      }
    }

    if (skia_use_metal) {
      sources += [ "tools/sk_app/MetalWindowContext.mm" ]
      if (is_mac) {
        sources += [ "tools/sk_app/mac/MetalWindowContext_mac.mm" ]
      }
      libs += [ "MetalKit.framework" ]
    }

    deps = [
      ":tool_utils",
    ]
    if (is_android) {
      deps += [ "//third_party/native_app_glue" ]
    } else if (is_ios) {
      deps += [ "//third_party/libsdl" ]
    }
    if (skia_use_angle) {
      deps += [ "//third_party/angle2" ]
    }
  }

  if (!skia_use_vulkan && (is_mac || is_linux || is_win)) {
    test_app("fiddle_examples") {
      sources = [
        "tools/fiddle/all_examples.cpp",
        "tools/fiddle/examples.cpp",
        "tools/fiddle/examples.h",
      ]
      if (is_win) {
        cflags = [ "/wd4756" ]  # Overflow in constant arithmetic
      }
      deps = [
        ":skia",
        ":skia.h",
        "modules/skottie",
        "modules/skshaper",
      ]
    }
  }
  test_app("viewer") {
    is_shared_library = is_android
    sources = [
      "tools/viewer/AnimTimer.h",
      "tools/viewer/BisectSlide.cpp",
      "tools/viewer/GMSlide.cpp",
      "tools/viewer/ImGuiLayer.cpp",
      "tools/viewer/ImageSlide.cpp",
      "tools/viewer/ParticlesSlide.cpp",
      "tools/viewer/SKPSlide.cpp",
      "tools/viewer/SampleSlide.cpp",
      "tools/viewer/SkottieSlide.cpp",
      "tools/viewer/SlideDir.cpp",
      "tools/viewer/StatsLayer.cpp",
      "tools/viewer/SvgSlide.cpp",
      "tools/viewer/TouchGesture.cpp",
      "tools/viewer/TouchGesture.h",
      "tools/viewer/Viewer.cpp",
    ]
    libs = []

    deps = [
      ":common_flags_gpu",
      ":experimental_svg_model",
      ":flags",
      ":gm",
      ":gpu_tool_utils",
      ":samples",
      ":sk_app",
      ":skia",
      ":tool_utils",
      ":trace",
      "modules/particles",
      "modules/skottie",
      "modules/skottie:utils",
      "modules/sksg",
      "modules/sksg:samples",
      "//third_party/imgui",
    ]
    if (skia_use_experimental_xform) {
      deps += [ ":experimental_xform" ]
      sources += [ "gm/xform.cpp" ]
    }
  }

  if (!skia_use_angle && (is_linux || is_win || is_mac)) {
    test_app("HelloWorld") {
      sources = [
        "example/HelloWorld.cpp",
      ]
      libs = []

      deps = [
        ":flags",
        ":gpu_tool_utils",
        ":sk_app",
        ":skia",
        ":tool_utils",
      ]
    }
  }

  if (is_linux || is_mac || is_ios) {
    test_app("SkiaSDLExample") {
      sources = [
        "example/SkiaSDLExample.cpp",
      ]
      libs = []
      deps = [
        ":gpu_tool_utils",
        ":skia",
        "//third_party/libsdl",
      ]
    }
  }

  if (skia_qt_path != "" && (is_win || is_linux || is_mac)) {
    action_foreach("generate_mocs") {
      script = "gn/call.py"
      sources = [
        "tools/mdbviz/MainWindow.h",
      ]
      outputs = [
        "$target_gen_dir/mdbviz/{{source_name_part}}_moc.cpp",
      ]
      args = [
        "$skia_qt_path" + "/bin/moc",
        "{{source}}",
        "-o",
        "gen/mdbviz/{{source_name_part}}_moc.cpp",
      ]
    }
    action_foreach("generate_resources") {
      script = "gn/call.py"
      sources = [
        "tools/mdbviz/resources.qrc",
      ]
      outputs = [
        "$target_gen_dir/mdbviz/{{source_name_part}}_res.cpp",
      ]
      args = [
        "$skia_qt_path" + "/bin/rcc",
        "{{source}}",
        "-o",
        "gen/mdbviz/{{source_name_part}}_res.cpp",
      ]
    }
    test_app("mdbviz") {
      if (is_win) {
        # on Windows we need to disable some exception handling warnings due to the Qt headers
        cflags = [ "/Wv:18" ]  # 18 -> VS2013, 19 -> VS2015, 1910 -> VS2017
      }
      sources = [
        "tools/UrlDataManager.cpp",
        "tools/debugger/DebugCanvas.cpp",
        "tools/debugger/DrawCommand.cpp",
        "tools/debugger/JsonWriteBuffer.cpp",
        "tools/mdbviz/MainWindow.cpp",
        "tools/mdbviz/Model.cpp",
        "tools/mdbviz/main.cpp",

        # generated files
        "$target_gen_dir/mdbviz/MainWindow_moc.cpp",
        "$target_gen_dir/mdbviz/resources_res.cpp",
      ]
      lib_dirs = [ "$skia_qt_path/lib" ]
      libs = [
        "Qt5Core.lib",
        "Qt5Gui.lib",
        "Qt5Widgets.lib",
      ]
      include_dirs = [
        "$skia_qt_path/include",
        "$skia_qt_path/include/QtCore",
        "$skia_qt_path/include/QtWidgets",
      ]
      deps = [
        ":generate_mocs",
        ":generate_resources",
        ":skia",
      ]
    }
  }

  if (is_android && defined(ndk) && ndk != "") {
    copy("gdbserver") {
      sources = [
        "$ndk/$ndk_gdbserver",
      ]
      outputs = [
        "$root_out_dir/gdbserver",
      ]
    }
  }

  if (skia_use_opencl) {
    test_app("hello-opencl") {
      sources = [
        "tools/hello-opencl.cpp",
      ]
      deps = [
        "//third_party/opencl",
      ]
    }
  }

  test_app("editor") {
    is_shared_library = is_android
    sources = [
      "experimental/editor/editor.cpp",
      "experimental/editor/editor.h",
      "experimental/editor/editor_application.cpp",
      "experimental/editor/run_handler.cpp",
      "experimental/editor/run_handler.h",
      "experimental/editor/stringslice.cpp",
      "experimental/editor/stringslice.h",
    ]
    deps = [
      ":sk_app",
      ":skia",
      "modules/skshaper",
    ]
  }

  if (skia_enable_skvm_jit) {
    test_app("skvmtool") {
      defines = [
        "SKVM_JIT",
        "SKVM_PERF_DUMPS",
      ]
      include_dirs = [ "." ]
      sources = [
        "src/core/SkSpinlock.cpp",
        "src/core/SkThreadID.cpp",
        "src/core/SkVM.cpp",
        "tools/SkVMTool.cpp",
      ]
      if (target_cpu == "x64") {
        sources += [ "src/core/SkCpu.cpp" ]
      }
    }
  }
}

# coding: utf-8

def component_skia():
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
  if (skia_use_xps):
    sources += skia_xps_sources

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
  if not skia_enable_skpicture:
    defines = [ "SK_DISABLE_SKPICTURE" ]
    public -= skia_skpicture_public
    sources -= skia_skpicture_sources
    sources -= [ "//src/effects/imagefilters/SkPictureImageFilter.cpp" ]
    sources += [ "src/core/SkPicture_none.cpp" ]

  libs = []

  if is_win:
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
  else:
    sources += [
      "src/ports/SkOSFile_posix.cpp",
      "src/ports/SkOSLibrary_posix.cpp",
      "src/ports/SkTLS_pthread.cpp",
    ]
    libs += [ "dl" ]

  if (is_android):
    deps += [ "//third_party/expat" ]
    if (defined(ndk) and ndk != ""):
      deps += [ "//third_party/cpu-features" ]

    sources += [ "src/ports/SkDebug_android.cpp" ]
    libs += [
      "EGL",
      "GLESv2",
      "log",
    ]


  if (is_linux or target_cpu == "wasm"):
    sources += [ "src/ports/SkDebug_stdio.cpp" ]
    if (skia_use_egl):
      libs += [ "GLESv2" ]



  if (skia_use_fonthost_mac):
    sources += [ "src/ports/SkFontHost_mac.cpp" ]


  if (is_mac):
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


  if (is_ios):
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


  if (is_fuchsia):
    sources += [ "src/ports/SkDebug_stdio.cpp" ]


  if (skia_enable_spirv_validation):
    deps += [ "//third_party/spirv-tools" ]
    defines += [ "SK_ENABLE_SPIRV_VALIDATION" ]

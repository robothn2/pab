# coding: utf-8

lib = {
    'uri': 'jsoncpp',
    'source_base_dir': r'D:\src\frameflow\third_party\repo\jsoncpp',
    'type': 'sharedLib',
    'std': 'c++11',
    'install_dirs_map': {
        'include': 'include',
        },

    'defines': [
        'JSON_DLL_BUILD'
        ],
    'include_dirs': [
        'include',
        ],
    'public_headers': [
        'include/json/config.h',
        'include/json/forwards.h',
        'include/json/features.h',
        'include/json/value.h',
        'include/json/reader.h',
        'include/json/writer.h',
        'include/json/assertions.h',
        'include/json/version.h',
        ],

    'sources': [
        'src/lib_json/json_reader.cpp',
        'src/lib_json/json_value.cpp',
        'src/lib_json/json_writer.cpp',
        ],
}

export_libs = [
    (lib, None),
]

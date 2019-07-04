# coding: utf-8

lib = {
    'uri': 'jsoncpp',
    'type': 'sharedLib',
    'include_dirs': [
        '../../include',
    ],

    'public_headers': [
        'json/config.h',
        'json/forwards.h',
        'json/features.h',
        'json/value.h',
        'json/reader.h',
        'json/writer.h',
        'json/assertions.h',
        'json/version.h',
    ],

    'defines': [
        'JSON_DLL_BUILD'
    ],
    'sources': [
        'src/lib_json/json_reader.cpp',
        'src/lib_json/json_value.cpp',
        'src/lib_json/json_writer.cpp',
        'src/lib_json/json_tool.h',
        'src/lib_json/json_valueiterator.inl',
        'src/lib_json/version.h.in',
    ],
}

def lib_dyn_setting(lib, options):
    pass
    if target_os == 'android':
        lib.sources -= [
            'base_paths_posix.cc',
            'files/file_path_watcher_kqueue.cc',
            'files/file_path_watcher_stub.cc',
            'system_monitor/system_monitor_posix.cc',
        ],
        lib.sources += [
            'files/file_path_watcher_linux.cc',
            'process_util_linux.cc',
            'sys_info_linux.cc',
            'sys_string_conversions_posix.cc',
            'worker_pool_linux.cc',
        ],

export_libs = [
    (lib, lib_dyn_setting),
]

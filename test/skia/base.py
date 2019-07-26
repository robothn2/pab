# coding: utf-8


base_lib = {
    'uri': 'base',
    'source_base_dir': 'd:/lib/base',
    'type': 'sharedLib',
    'install_dirs_map': {
        '': 'include/base',
        },

    'defines': [
        'BASE_IMPLEMENTATION',
		'_GLIBCXX_PERMIT_BACKWARD_HASH',
        ],
    'cxxflags': [
        '-std=c++11',
        ],
    'include_dirs': [
        '..',
        '.',
        ],
    'public_headers': [
        '*.h',
        'android/*.h',
        'chromeos/*.h',
        'ios/*.h',
        'mac/*.h',
        'nix/*.h',
        'posix/*.h',
        'win/*.h',
        ],
    'sources': [
        '*.cc',
        'allocator/*.cc',
        'containers/*.cc',
        #'data/*.cc',
        'debug/*.cc',
        'files/*.cc',
        #'i18n/*.cc',
        'json/*.cc',
        'memory/*.cc',
        'message_loop/*.cc',
        'metrics/*.cc',
        'numerics/*.cc',
        'power_monitor/*.cc',
        'process/*.cc',
        'profiler/*.cc',
        'sampling_heap_profiler/*.cc',
        'strings/*.cc',
        'synchronization/*.cc',
        'system/*.cc',
        #'system_monitor/*.cc',
        'task/*.cc',
        #'test/*.cc',
        'third_party/*.cc',
        'threading/*.cc',
        'time/*.cc',
        'timer/*.cc',
        'trace_event/*.cc',
        #'util/*.cc',
        ],
}


def base_dyn(lib, context):
    import os

    base_external = os.environ['QY_FRMEXTERNAL_PATH']
    lib.include_dirs += [
            os.path.join(base_external, 'zlib/include'),
            ]

    target_os = context.target_os_tags
    if not context.getOption('use_glib'):
        lib.sources -= [
            '^nix/.+$',
            ]
        lib.sources -= [
            'atomicops_internals_x86_gcc.cc',
            'message_pump_glib.cc',
            'message_pump_aurax11.cc',
            ]

    if not context.getOption('toolkit_uses_gtk'):
        lib.sources -= [
            'message_pump_gtk.cc',
            ]

    if 'win' in target_os:
        lib.defines += ['NOMINMAX',
                        '_SILENCE_STDEXT_HASH_DEPRECATION_WARNINGS',
                        'ZLIB_WINAPI']
        lib.cxxflags -= '-std=c++11'
        lib.include_dirs += [
            'third_party/wtl/include',
            ]
        lib.sources += [
            'win/*.cc',
            ]
        lib.sources -= [
            'event_recorder_stubs.cc',
            'file_descriptor_shuffle.cc',
            'files/file_path_watcher_kqueue.cc',
            'files/file_path_watcher_stub.cc',
            'message_pump_libevent.cc',
            # Not using sha1_win.cc because it may have caused a
            # regression to page cycler moz.
            'sha1_win.cc',
            'string16.cc',

            '^.+_posix\.cc$',
            ]
        lib.lib_dirs += [
                os.path.join(base_external, 'zlib/lib/x86'),
                ]
        #lib.libs += ['zlibstat.lib']

    if 'android' in target_os:
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

    if 'ios' in target_os:
        lib.sources += [
            'atomicops_internals_mac',
            'base_paths_mac',
            'file_util_mac',
            'file_version_info_mac',
            'mac/bind_objc_block',
            'mac/bundle_locations',
            'mac/foundation_util',
            'mac/mac_logging',
            'mac/objc_property_releaser',
            'mac/scoped_nsautorelease_pool',
            'message_pump_mac',
            'threading/platform_thread_mac',
            'sys_string_conversions_mac',
            'time_mac',
            'worker_pool_mac',
            ],
        # Exclude all process_util except the minimal implementation
        # needed on iOS (mostly for unit tests).
        lib.sources -= [
            'process_util.cc',
            ],
    if 'mac' in target_os:
        pass
    if 'mac' in target_os or 'ios' in target_os:
        lib.sources -= [
            'files/file_path_watcher_stub.cc',
            'base_paths_posix.cc',
            'native_library_posix.cc',
            'sys_string_conversions_posix.cc',
            ]

    if 'linux' in target_os:
        lib.sources += [
            'files/file_path_watcher_kqueue.cc',
            'files/file_path_watcher_stub.cc',
            ]

    lib.sources -= '^.+_unittest\.cc'


export_libs = [
    (base_lib, base_dyn),
]

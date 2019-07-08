# coding: utf-8

lib = {
    'uri': 'ffmpeg',
    'public_include_dirs': [
    ],
    'include_dirs': [
        '.',
    ],
    'defines': [
    ],
    'deps': [
    ],
    'sources': [

        'win/wrapped_window_proc.h',
    ],
}

def lib_dyn(lib, request, options):
    if not options('use_glib'):
        lib.sources -= [
            'nix',
        ]
        lib.sources -= [
            'atomicops_internals_x86_gcc.cc',
            'message_pump_glib.cc',
            'message_pump_aurax11.cc',
        ]

    if not options('toolkit_uses_gtk'):
        lib.sources -= [
            'message_pump_gtk.cc',
        ]

    if request.target_os == 'android':
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

    if request.target_os == 'ios':
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

            'process_util_ios.mm',
        ],
        # Exclude all process_util except the minimal implementation
        # needed on iOS (mostly for unit tests).
        lib.sources -= [
            'process_util',
        ],
    if request.target_os == 'mac':
        lib.sources += [
            'mac/scoped_aedesc.h'
        ]
    if request.target_os == 'mac' or request.target_os == 'ios':
        lib.sources -= [
            'files/file_path_watcher_stub.cc',
            'base_paths_posix.cc',
            'native_library_posix.cc',
            'sys_string_conversions_posix.cc',
        ]

    if request.target_os == 'win':
        lib.include_dirs += [
            'third_party/wtl/include',
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
        ]

    if request.target_os == 'linux':
        lib.sources += [
            'files/file_path_watcher_kqueue.cc',
            'files/file_path_watcher_stub.cc',
        ]

export_libs = [
    (lib, lib_dyn),
]

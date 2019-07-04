# coding: utf-8

lib = {
    'uri': 'base',
    'public_include_dirs': [
    ],
    'include_dirs': [
        '..',
    ],
    'defines': [
        'BASE_IMPLEMENTATION'
    ],
    'deps': [
        '//third_party/zlib',
    ],
    'sources': [
        'third_party/dmg_fp/dmg_fp.h',
        'third_party/dmg_fp/g_fmt.cc',
        'third_party/dmg_fp/dtoa_wrapper.cc',
        'third_party/icu/icu_utf.cc',
        'third_party/icu/icu_utf.h',
        'third_party/nspr/prtime.cc',
        'third_party/nspr/prtime.h',
        'third_party/nspr/prcpucfg_linux.h',
        'third_party/xdg_mime/xdgmime.h',
        'allocator/allocator_extension.cc',
        'allocator/allocator_extension.h',
        'allocator/type_profiler_control.cc',
        'allocator/type_profiler_control.h',
        'android/base_jni_registrar.cc',
        'android/base_jni_registrar.h',
        'android/build_info.cc',
        'android/build_info.h',
        'android/scoped_java_ref.cc',
        'android/scoped_java_ref.h',
        'android/jni_android.cc',
        'android/jni_android.h',
        'android/jni_array.cc',
        'android/jni_array.h',
        'android/jni_helper.cc',
        'android/jni_helper.h',
        'android/jni_registrar.cc',
        'android/jni_registrar.h',
        'android/jni_string.cc',
        'android/jni_string.h',
        'android/locale_utils.cc',
        'android/locale_utils.h',
        'android/path_service_android.cc',
        'android/path_service_android.h',
        'android/path_utils.cc',
        'android/path_utils.h',
        'at_exit.cc',
        'at_exit.h',
        'atomic_ref_count.h',
        'atomic_sequence_num.h',
        'atomicops.h',
        'atomicops_internals_gcc.h',
        'atomicops_internals_mac.h',
        'atomicops_internals_x86_gcc.cc',
        'atomicops_internals_x86_gcc.h',
        'atomicops_internals_x86_msvc.h',
        'base_export.h',
        'base_paths.cc',
        'base_paths.h',
        'base_paths_android.cc',
        'base_paths_android.h',
        'base_paths_mac.h',
        'base_paths_mac.mm',
        'base_paths_posix.cc',
        'base_paths_posix.h',
        'base_paths_win.cc',
        'base_paths_win.h',
        'base_switches.h',
        'base64.cc',
        'base64.h',
        'basictypes.h',
        'bind.h',
        'bind_helpers.cc',
        'bind_helpers.h',
        'bind_internal.h',
        'bind_internal_win.h',
        'bits.h',
        'build_time.cc',
        'build_time.h',
        'callback.h',
        'callback_helpers.h',
        'callback_internal.cc',
        'callback_internal.h',
        'cancelable_callback.h',
        'chromeos/chromeos_version.cc',
        'chromeos/chromeos_version.h',
        'command_line.cc',
        'command_line.h',
        'compiler_specific.h',
        'cpu.cc',
        'cpu.h',
        'critical_closure.h',
        'critical_closure_ios.mm',
        'debug/alias.cc',
        'debug/alias.h',
        'debug/debug_on_start_win.cc',
        'debug/debug_on_start_win.h',
        'debug/debugger.cc',
        'debug/debugger.h',
        'debug/debugger_posix.cc',
        'debug/debugger_win.cc',
        'debug/leak_annotations.h',
        'debug/leak_tracker.h',
        'debug/profiler.cc',
        'debug/profiler.h',
        'debug/stack_trace.cc',
        'debug/stack_trace.h',
        'debug/stack_trace_android.cc',
        'debug/stack_trace_posix.cc',
        'debug/stack_trace_win.cc',
        'debug/trace_event.cc',
        'debug/trace_event.h',
        'debug/trace_event_impl.cc',
        'debug/trace_event_impl.h',
        'debug/trace_event_win.cc',
        'eintr_wrapper.h',
        'environment.cc',
        'environment.h',
        'file_descriptor_posix.h',
        'file_path.cc',
        'file_path.h',
        'file_util.cc',
        'file_util.h',
        'file_util_android.cc',
        'file_util_linux.cc',
        'file_util_mac.mm',
        'file_util_posix.cc',
        'file_util_win.cc',
        'file_util_proxy.cc',
        'file_util_proxy.h',
        'file_version_info.h',
        'file_version_info_mac.h',
        'file_version_info_mac.mm',
        'file_version_info_win.cc',
        'file_version_info_win.h',
        'files/dir_reader_fallback.h',
        'files/dir_reader_linux.h',
        'files/dir_reader_posix.h',
        'files/file_path_watcher.cc',
        'files/file_path_watcher.h',
        'files/file_path_watcher_kqueue.cc',
        'files/file_path_watcher_linux.cc',
        'files/file_path_watcher_stub.cc',
        'files/file_path_watcher_win.cc',
        'float_util.h',
        'format_macros.h',
        'global_descriptors_posix.cc',
        'global_descriptors_posix.h',
        'gtest_prod_util.h',
        'guid.cc',
        'guid.h',
        'guid_posix.cc',
        'guid_win.cc',
        'hash.cc',
        'hash.h',
        'hash_tables.h',
        'hi_res_timer_manager_posix.cc',
        'hi_res_timer_manager_win.cc',
        'hi_res_timer_manager.h',
        'id_map.h',
        'ios/device_util.h',
        'ios/device_util.mm',
        'ios/scoped_critical_action.h',
        'ios/scoped_critical_action.mm',
        'json/json_file_value_serializer.cc',
        'json/json_file_value_serializer.h',
        'json/json_parser.cc',
        'json/json_parser.h',
        'json/json_reader.cc',
        'json/json_reader.h',
        'json/json_string_value_serializer.cc',
        'json/json_string_value_serializer.h',
        'json/json_value_converter.h',
        'json/json_writer.cc',
        'json/json_writer.h',
        'json/string_escape.cc',
        'json/string_escape.h',
        'lazy_instance.cc',
        'lazy_instance.h',
        'linked_list.h',
        'location.cc',
        'location.h',
        'logging.cc',
        'logging.h',
        'logging_win.cc',
        'logging_win.h',
        'mac/authorization_util.h',
        'mac/authorization_util.mm',
        'mac/bind_objc_block.h',
        'mac/bind_objc_block.mm',
        'mac/bundle_locations.h',
        'mac/bundle_locations.mm',
        'mac/cocoa_protocols.h',
        'mac/crash_logging.h',
        'mac/crash_logging.mm',
        'mac/foundation_util.h',
        'mac/foundation_util.mm',
        'mac/launchd.cc',
        'mac/launchd.h',
        'mac/mac_logging.h',
        'mac/mac_logging.cc',
        'mac/mac_util.h',
        'mac/mac_util.mm',
        'mac/objc_property_releaser.h',
        'mac/objc_property_releaser.mm',
        'mac/os_crash_dumps.cc',
        'mac/os_crash_dumps.h',
        'mac/scoped_aedesc.h',
        'mac/scoped_authorizationref.h',
        'mac/scoped_cftyperef.h',
        'mac/scoped_ioobject.h',
        'mac/scoped_launch_data.h',
        'mac/scoped_nsautorelease_pool.h',
        'mac/scoped_nsautorelease_pool.mm',
        'mac/scoped_nsexception_enabler.h',
        'mac/scoped_nsexception_enabler.mm',
        'mac/scoped_sending_event.h',
        'mac/scoped_sending_event.mm',
        'mach_ipc_mac.h',
        'mach_ipc_mac.mm',
        'memory/aligned_memory.cc',
        'memory/aligned_memory.h',
        'memory/linked_ptr.h',
        'memory/mru_cache.h',
        'memory/raw_scoped_refptr_mismatch_checker.h',
        'memory/ref_counted.cc',
        'memory/ref_counted.h',
        'memory/ref_counted_memory.cc',
        'memory/ref_counted_memory.h',
        'memory/scoped_handle.h',
        'memory/scoped_nsobject.h',
        'memory/scoped_open_process.h',
        'memory/scoped_policy.h',
        'memory/scoped_ptr.h',
        'memory/scoped_vector.h',
        'memory/singleton.cc',
        'memory/singleton.h',
        'memory/weak_ptr.cc',
        'memory/weak_ptr.h',
        'message_loop.cc',
        'message_loop.h',
        'message_loop_proxy.cc',
        'message_loop_proxy.h',
        'message_loop_proxy_impl.cc',
        'message_loop_proxy_impl.h',
        'message_pump.cc',
        'message_pump.h',
        'message_pump_android.cc',
        'message_pump_android.h',
        'message_pump_default.cc',
        'message_pump_default.h',
        'message_pump_win.cc',
        'message_pump_win.h',
        'metrics/sample_vector.cc',
        'metrics/sample_vector.h',
        'metrics/bucket_ranges.cc',
        'metrics/bucket_ranges.h',
        'metrics/histogram.cc',
        'metrics/histogram.h',
        'metrics/histogram_base.cc',
        'metrics/histogram_base.h',
        'metrics/histogram_flattener.h',
        'metrics/histogram_samples.cc',
        'metrics/histogram_samples.h',
        'metrics/histogram_snapshot_manager.cc',
        'metrics/histogram_snapshot_manager.h',
        'metrics/sparse_histogram.cc',
        'metrics/sparse_histogram.h',
        'metrics/statistics_recorder.cc',
        'metrics/statistics_recorder.h',
        'metrics/stats_counters.cc',
        'metrics/stats_counters.h',
        'metrics/stats_table.cc',
        'metrics/stats_table.h',
        'move.h',
        'native_library.h',
        'native_library_mac.mm',
        'native_library_posix.cc',
        'native_library_win.cc',
        'observer_list.h',
        'observer_list_threadsafe.h',
        'os_compat_android.cc',
        'os_compat_android.h',
        'os_compat_nacl.cc',
        'os_compat_nacl.h',
        'path_service.cc',
        'path_service.h',
        'pending_task.cc',
        'pending_task.h',
        'pickle.cc',
        'pickle.h',
        'platform_file.cc',
        'platform_file.h',
        'platform_file_posix.cc',
        'platform_file_win.cc',
        'port.h',
        'posix/unix_domain_socket.cc',
        'posix/unix_domain_socket.h',
        'process.h',
        'process_info.h',
        'process_info_mac.cc',
        'process_info_win.cc',
        'process_linux.cc',
        'process_posix.cc',
        'process_util.cc',
        'process_util.h',
        'process_util_freebsd.cc',
        'process_util_ios.mm',
        'process_util_linux.cc',
        'process_util_mac.mm',
        'process_util_openbsd.cc',
        'process_util_posix.cc',
        'process_util_win.cc',
        'process_win.cc',
        'profiler/scoped_profile.cc',
        'profiler/scoped_profile.h',
        'profiler/alternate_timer.cc',
        'profiler/alternate_timer.h',
        'profiler/tracked_time.cc',
        'profiler/tracked_time.h',
        'rand_util.cc',
        'rand_util.h',
        'rand_util_nacl.cc',
        'rand_util_posix.cc',
        'rand_util_win.cc',
        'run_loop.cc',
        'run_loop.h',
        'safe_strerror_posix.cc',
        'safe_strerror_posix.h',
        'scoped_native_library.cc',
        'scoped_native_library.h',
        'scoped_temp_dir.cc',
        'scoped_temp_dir.h',
        'sequenced_task_runner.cc',
        'sequenced_task_runner.h',
        'sequenced_task_runner_helpers.h',
        'sha1.h',
        'sha1_portable.cc',
        'sha1_win.cc',
        'shared_memory.h',
        'shared_memory_android.cc',
        'shared_memory_nacl.cc',
        'shared_memory_posix.cc',
        'shared_memory_win.cc',
        'single_thread_task_runner.h',
        'stack_container.h',
        'stl_util.h',
        'string_number_conversions.cc',
        'string_number_conversions.h',
        'string_piece.cc',
        'string_piece.h',
        'string_split.cc',
        'string_split.h',
        'string_tokenizer.h',
        'string_util.cc',
        'string_util.h',
        'string_util_posix.h',
        'string_util_win.h',
        'string16.cc',
        'string16.h',
        'stringize_macros.h',
        'stringprintf.cc',
        'stringprintf.h',
        'supports_user_data.cc',
        'supports_user_data.h',
        'synchronization/cancellation_flag.cc',
        'synchronization/cancellation_flag.h',
        'synchronization/condition_variable.h',
        'synchronization/condition_variable_posix.cc',
        'synchronization/condition_variable_win.cc',
        'synchronization/lock.cc',
        'synchronization/lock.h',
        'synchronization/lock_impl.h',
        'synchronization/lock_impl_posix.cc',
        'synchronization/lock_impl_win.cc',
        'synchronization/spin_wait.h',
        'synchronization/waitable_event.h',
        'synchronization/waitable_event_posix.cc',
        'synchronization/waitable_event_watcher.h',
        'synchronization/waitable_event_watcher_posix.cc',
        'synchronization/waitable_event_watcher_win.cc',
        'synchronization/waitable_event_win.cc',
        'system_monitor/system_monitor.cc',
        'system_monitor/system_monitor.h',
        'system_monitor/system_monitor_android.cc',
        'system_monitor/system_monitor_ios.mm',
        'system_monitor/system_monitor_mac.mm',
        'system_monitor/system_monitor_posix.cc',
        'system_monitor/system_monitor_win.cc',
        'sys_byteorder.h',
        'sys_info.h',
        'sys_info_android.cc',
        'sys_info_chromeos.cc',
        'sys_info_freebsd.cc',
        'sys_info_ios.mm',
        'sys_info_linux.cc',
        'sys_info_mac.cc',
        'sys_info_openbsd.cc',
        'sys_info_posix.cc',
        'sys_info_win.cc',
        'sys_string_conversions.h',
        'sys_string_conversions_mac.mm',
        'sys_string_conversions_posix.cc',
        'sys_string_conversions_win.cc',
        'task_runner.cc',
        'task_runner.h',
        'task_runner_util.h',
        'template_util.h',
        'thread_task_runner_handle.cc',
        'thread_task_runner_handle.h',
        'threading/non_thread_safe.h',
        'threading/non_thread_safe_impl.cc',
        'threading/non_thread_safe_impl.h',
        'threading/platform_thread.h',
        'threading/platform_thread_mac.mm',
        'threading/platform_thread_posix.cc',
        'threading/platform_thread_win.cc',
        'threading/post_task_and_reply_impl.cc',
        'threading/post_task_and_reply_impl.h',
        'threading/sequenced_worker_pool.cc',
        'threading/sequenced_worker_pool.h',
        'threading/simple_thread.cc',
        'threading/simple_thread.h',
        'threading/thread.cc',
        'threading/thread.h',
        'threading/thread_checker.h',
        'threading/thread_checker_impl.cc',
        'threading/thread_checker_impl.h',
        'threading/thread_collision_warner.cc',
        'threading/thread_collision_warner.h',
        'threading/thread_local.h',
        'threading/thread_local_posix.cc',
        'threading/thread_local_storage.h',
        'threading/thread_local_storage_posix.cc',
        'threading/thread_local_storage_win.cc',
        'threading/thread_local_win.cc',
        'threading/thread_restrictions.h',
        'threading/thread_restrictions.cc',
        'threading/watchdog.cc',
        'threading/watchdog.h',
        'threading/worker_pool.h',
        'threading/worker_pool.cc',
        'threading/worker_pool_posix.cc',
        'threading/worker_pool_posix.h',
        'threading/worker_pool_win.cc',
        'time.cc',
        'time.h',
        'time_mac.cc',
        'time_posix.cc',
        'time_win.cc',
        'timer.cc',
        'timer.h',
        'tracked_objects.cc',
        'tracked_objects.h',
        'tracking_info.cc',
        'tracking_info.h',
        'tuple.h',
        'utf_offset_string_conversions.cc',
        'utf_offset_string_conversions.h',
        'utf_string_conversion_utils.cc',
        'utf_string_conversion_utils.h',
        'utf_string_conversions.cc',
        'utf_string_conversions.h',
        'values.cc',
        'values.h',
        'value_conversions.cc',
        'value_conversions.h',
        'version.cc',
        'version.h',
        'vlog.cc',
        'vlog.h',
        'nix/mime_util_xdg.cc',
        'nix/mime_util_xdg.h',
        'nix/xdg_util.cc',
        'nix/xdg_util.h',
        'win/enum_variant.h',
        'win/enum_variant.cc',
        'win/event_trace_consumer.h',
        'win/event_trace_controller.cc',
        'win/event_trace_controller.h',
        'win/event_trace_provider.cc',
        'win/event_trace_provider.h',
        'win/i18n.cc',
        'win/i18n.h',
        'win/iat_patch_function.cc',
        'win/iat_patch_function.h',
        'win/iunknown_impl.h',
        'win/iunknown_impl.cc',
        'win/metro.cc',
        'win/metro.h',
        'win/object_watcher.cc',
        'win/object_watcher.h',
        'win/registry.cc',
        'win/registry.h',
        'win/resource_util.cc',
        'win/resource_util.h',
        'win/sampling_profiler.cc',
        'win/sampling_profiler.h',
        'win/scoped_bstr.cc',
        'win/scoped_bstr.h',
        'win/scoped_co_mem.h',
        'win/scoped_com_initializer.h',
        'win/scoped_comptr.h',
        'win/scoped_gdi_object.h',
        'win/scoped_handle.cc',
        'win/scoped_handle.h',
        'win/scoped_hdc.h',
        'win/scoped_hglobal.h',
        'win/scoped_process_information.cc',
        'win/scoped_process_information.h',
        'win/scoped_select_object.h',
        'win/shortcut.cc',
        'win/shortcut.h',
        'win/startup_information.cc',
        'win/startup_information.h',
        'win/scoped_variant.cc',
        'win/scoped_variant.h',
        'win/text_services_message_filter.cc',
        'win/text_services_message_filter.h',
        'win/windows_version.cc',
        'win/windows_version.h',
        'win/win_util.cc',
        'win/win_util.h',
        'win/wrapped_window_proc.cc',
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

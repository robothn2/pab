# coding: utf-8


hello_dynamic_lib = {
    'uri': 'hello',
    'type': 'sharedLib',
    'source_base_dir': '.',
    'sources': ['hello.c'],
}

hello_static_lib = {
    'uri': 'hello_static',
    'type': 'staticLib',
    'source_base_dir': '.',
    'sources': ['hello.c'],
}

main_exe = {
    'uri': 'mainWithSo',
    'type': 'executable',
    'source_base_dir': '.',
    'deps': ['hello'],
    'sources': ['main.c'],
}


def hello_dyn(lib, context):
    print('nothing to do')


main_exe_standalone = {
    'uri': 'main',
    'type': 'executable',
    'source_base_dir': '.',
    'deps': ['hello_static'],
    'sources': ['main.c'],
}


export_libs = [
    (main_exe, None),
    (hello_dynamic_lib, hello_dyn),
    (hello_static_lib, None),
    (main_exe_standalone, None),
]

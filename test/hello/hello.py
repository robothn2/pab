# coding: utf-8


hello_static_lib = {
    'uri': 'hello_static',
    'type': 'staticLib',
    'source_base_dir': '.',
    'defines': ['HELLO_STATIC'],
    'sources': ['hello.c'],
}

main_exe_standalone = {
    'uri': 'main_sa',
    'type': 'executable',
    'source_base_dir': '.',
    'defines': ['HELLO_STATIC'],
    'deps': ['hello_static'],
    'sources': ['main.c'],
}

hello_dynamic_lib = {
    'uri': 'hello',
    'type': 'sharedLib',
    'source_base_dir': '.',
    'defines': ['HELLO_EXPORTS'],
    'sources': ['hello.c'],
}

main_exe_with_so = {
    'uri': 'main',
    'type': 'executable',
    'source_base_dir': '.',
    'deps': ['hello'],
    'sources': ['main.c'],
}


export_libs = [
    (main_exe_standalone, None),
    (hello_static_lib, None),
    (main_exe_with_so, None),
    (hello_dynamic_lib, None),
]

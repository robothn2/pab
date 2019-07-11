# coding: utf-8

hello_lib = {
    'uri': 'hello',
    'type': 'sharedLib',
    'source_base_dir': '.',
    'sources': ['hello.c'],
}

main_exe = {
    'uri': 'main',
    'type': 'executable',
    'source_base_dir': '.',
    'deps': ['hello'],
    'sources': ['main.c'],
}

def hello_dyn(lib, context):
    print('nothing to do')

export_libs = [
    (main_exe, None),
    (hello_lib, hello_dyn),
]

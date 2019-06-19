#coding: utf-8

import os
import json

class SourceFiles:
    def __init__(self, src, workspace):
        self.ext_filter = [
                '.c', '.cc', '.cpp', '.cxx',
                '.asm', '.S', # assemble
                '.rc', # VS resource
                '.m', '.mm', # xcode
                ]
        self.files = {}
        for ext in self.ext_filter:
            self.files[ext] = []
        self.rootSrc = os.path.realpath(src)
        self.rootWorkspace = os.path.realpath(workspace)
        self.rootObj = os.path.join(self.rootWorkspace, 'obj')
        ws_file = os.path.join(self.rootWorkspace, 'ws.json')
        if not os.path.exists(self.rootWorkspace):
            os.makedirs(self.rootWorkspace)
        elif os.path.exists(ws_file):
            with open(ws_file, 'r', encoding='utf-8') as f:
                self.files = json.load(f)
        if not os.path.exists(self.rootObj):
            os.makedirs(self.rootObj)
        
        total_files = 0
        for ext, files in self.files.items():
            total_files += len(files)
        if total_files == 0:
            self._search_folder(self.rootSrc)

        total_files = 0
        for (ext, files) in self.files.items():
            cnt = len(files)
            total_files += cnt
            print('{:>10s}:{}'.format(ext, cnt))
        print('{:>10s}:{}'.format('totally', total_files))
        
        with open(ws_file, 'w', encoding='utf-8') as f:
            json.dump(self.files, f, indent=4)
        
    def _search_folder(self, fullpath):
        for file_name in os.listdir(fullpath):
            src = os.path.join(fullpath, file_name)
            if os.path.islink(src):
                continue
    
            if os.path.isfile(src):
                self._add_source_file(src, file_name)
            elif os.path.isdir(src):
                if file_name[0] != '.':
                    self._search_folder(src)  # sub folder recursive

    def _add_source_file(self, fullpath, file_name):
        _, ext = os.path.splitext(file_name)
        if ext in self.ext_filter:
            self.files[ext].append(fullpath[len(self.rootSrc)+1:])
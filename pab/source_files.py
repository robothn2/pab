# coding: utf-8

import os
import json
from .file_dispatcher import FileDispatcher


class SourceFiles:
    def __init__(self, **kwargs):
        self.dispatcher = FileDispatcher()
        self.files = {}
        for _, cat in self.dispatcher.items():
            self.files[cat] = []
        self.rootSrc = os.path.realpath(kwargs['root'])
        self.rootWorkspace = os.path.realpath(kwargs['rootBuild'])
        self.depth = kwargs.get('depth', 0)
        self.excludeFiles = kwargs.get('excludeFiles', [])
        self.rootObj = os.path.join(self.rootWorkspace, 'obj')
        ws_file = os.path.join(self.rootWorkspace, 'ws.json')
        if not os.path.exists(self.rootWorkspace):
            os.makedirs(self.rootWorkspace)
        elif not kwargs.get('rescan', False) and os.path.exists(ws_file):
            with open(ws_file, 'r', encoding='utf-8') as f:
                self.files = json.load(f)
        if not os.path.exists(self.rootObj):
            os.makedirs(self.rootObj)

        total_files = 0
        for files in self.files.values():
            total_files += len(files)
        if total_files == 0:
            self._search_folder(self.rootSrc, 1)

        total_files = 0
        for (cat, files) in self.files.items():
            cnt = len(files)
            total_files += cnt
            print('{:>10s}:{}'.format(cat, cnt))
        print('{:>10s}:{}'.format('totally', total_files))

        with open(ws_file, 'w', encoding='utf-8') as f:
            json.dump(self.files, f, indent=4)

    def _search_folder(self, fullpath, depth):
        for file_name in os.listdir(fullpath):
            if file_name in self.excludeFiles:
                continue  # ignore file by execludeFiles
            src = os.path.join(fullpath, file_name)
            if os.path.islink(src):
                continue  # no link files

            if os.path.isfile(src):
                self._add_source_file(src, file_name)
            elif os.path.isdir(src):
                if self.depth and depth >= self.depth:
                    continue  # ignore subfolder by depth
                if file_name[0] != '.':  # no tmp folders and self, parent
                    self._search_folder(src, depth+1)  # sub folder recursive

    def _add_source_file(self, fullpath, file_name):
        _, ext = os.path.splitext(file_name)
        cat = self.dispatcher.getCat(ext)
        if cat:
            self.files[cat].append(fullpath[len(self.rootSrc)+1:])

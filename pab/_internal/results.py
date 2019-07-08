# coding: utf-8


class Results:
    def __init__(self, **kwargs):
        self.skipFiles = {}
        self.errorFiles = {}
        self.succeedFiles = []
        self.unhandleFiles = []

    def reset(self, **kwargs):
        self.skipFiles = {}
        self.errorFiles = {}
        self.succeedFiles = []
        self.unhandleFiles = []
        self.kwargs = kwargs

    def unhandled(self, src):
        self.unhandleFiles.append(src)

    def skipped(self, src, reason):
        self.skipFiles[src] = reason
        print('* skipped', src, str(reason))

    def error(self, src, reason):
        self.errorFiles[src] = reason
        print('* error', src, reason)

    def succeeded(self, src):
        self.succeedFiles.append(src)

    def dump(self):
        print('=', self.kwargs.get('title', ''))
        print('- skip files:', len(self.skipFiles))
        for f, r in self.skipFiles.items():
            print('*', f, r)

        print('- error files:', len(self.errorFiles))
        for f, r in self.errorFiles.items():
            print('*', f, r)

        print('- unhandle files:', len(self.unhandleFiles))
        print('- success files:', len(self.succeedFiles))

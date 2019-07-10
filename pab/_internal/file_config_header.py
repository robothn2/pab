# coding: utf-8
import os


class HeaderFileWriter:
    def __init__(self, filepath, **kwargs):
        self.kwargs = kwargs
        path = os.path.dirname(filepath)
        if not os.path.exists(path):
            os.makedirs(path)
        head_macro = os.path.basename(filepath).replace('.', '_').upper()
        print(head_macro)
        self.file = open(filepath, 'w', encoding='utf-8')
        self.file.write('#ifndef {0}\n#define {0}\n\n'.format(head_macro))

    def writeDefine(self, macro_name, value, **kwargs):
        if value is None:
            return
        if value is False:
            if not kwargs.get('as01'):
                return
            value = 0

        if value is True:
            if kwargs.get('as01'):
                value = 1
            else:
                value = ''
        self.file.write('#define {} {}\n'.format(macro_name, value))

    def close(self):
        self.file.write('\n#endif\n')
        self.file.close()


if __name__ == '__main__':
    f = HeaderFileWriter('d:/lib/build/OgreConfig.h')
    f.writeDefine('OGRE_STATIC', True, as01=True)
    f.close()

#coding: utf-8

import os

class ConfigGenerator:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        
    def registerAll(self, toolchain):
        pass
        
        ''' Shell script for generating ffmpeg/libavutil/avconfig.h:
        cat > $TMPH <<EOF
        /* Generated by ffmpeg configure */
        #ifndef AVUTIL_AVCONFIG_H
        #define AVUTIL_AVCONFIG_H
        EOF
        
        print_config AV_HAVE_ $TMPH $HAVE_LIST_PUB
        
        echo "#endif /* AVUTIL_AVCONFIG_H */" >> $TMPH
        
        cp_if_changed $TMPH libavutil/avconfig.h
        '''
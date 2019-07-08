# coding: utf-8
import re


def output_analyze(cmdline, output):
    result = re.search(r'^(\S+:\d+:\d+): error: (.*)$',
                       output, re.RegexFlag.MULTILINE)
    if result:
        return result.groups()
    return output

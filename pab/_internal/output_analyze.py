# coding: utf-8
import re


def output_analyze(cmdline, output):
    result = re.search(r'^(\S+)\s?: (?:fatal )?error(?: [A-Z]{1,3}\d{4})?: (.*)$',
                       output, re.RegexFlag.MULTILINE)
    if result:
        return result.groups()
    return output

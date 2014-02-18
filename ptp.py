#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Copyright 2014, Peng Wan, <minexiac@gmail.com>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
"""Phylame Text Processor"""

import os
import sys
import getopt
from phylib import app_error, app_echo
import phylib


def remove_null(lines):
    """remove empty lines (default)"""

    result = []
    for line in lines:
        if line.isspace():
            continue
        result.append(line)

    return result


CHAPTER_END_SYMBOLS = tuple("""。？！：…”；’～｀¨．∶＇＂〃,.?!:";'""")


def smart_split(lines):
    """smart split paragraph"""

    result = []
    buf = ""
    for line in lines:
        s = line.rstrip()
        if s.endswith(CHAPTER_END_SYMBOLS):
            if buf:
                s = buf + s.lstrip()
                buf = ""
            result.append(s)
        else:
            if buf:    # first error line
                s = s.lstrip()
            buf += s

    return result


def para_indent(lines):
    """adjust paragraph indentation"""

    result = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        s = phylib.PARA_START + s
        result.append(s)

    return result


def split_to_lines(file, func, encoding=None):
    try:
        fp = open(file, "rb")
    except IOError as err:
        app_error(err)
        return

    data = fp.read()
    fp.close()
    if encoding:
        data = phylib.strip_bom(data)
        try:
            text = data.decode(encoding)
        except UnicodeDecodeError:
            app_error("invalid encoding: '{0}'".format(encoding))
            return
    else:
        text, encoding = phylib.decode_text(data)
        if text is None:
            err = "cannot decode text file: '{0}'"
            app_error(err.format(file))
            return

    lines = func(text.splitlines())
    if not isinstance(lines, list):
        app_error("expected 'list' returned value")
        return

    text = phylib.LN.join(lines)
    data = text.encode(encoding)
    try:
        fp = open(file, "wb")
    except IOError as err:
        app_error(err)
        return

    fp.write(data)
    fp.close()


phylib.PROG_NAME = PROG_NAME = "ptp"
OPTIONS_ARGS = "he:f:"
Commands = {
    "remove-null": remove_null,
    "smart-split": smart_split,
    "para-indent": para_indent
}


def usage():
    s = "usage: {0} [options] files...".format(PROG_NAME)
    print(s)
    print("options:")
    print(" -e <encoding>     encoding of text file")
    print(" -f <script>       customized script path")
    for k, v in Commands.items():
        print(" --{0}     {1}".format(k, v.__doc__))


def main(argv):
    argv = argv[1:]
    try:
        opts, extra = getopt.getopt(argv, OPTIONS_ARGS, Commands.keys())
    except getopt.GetoptError as err:
        app_error(err)
        usage()
        return 1

    files = phylib.expand_path(extra)

    encoding = None
    script = None
    func = remove_null
    for opt, arg in opts:
        if opt == "-e":
            encoding = arg
        elif opt == "-f":
            if not os.path.exists(arg):
                app_error("not such script: '{0}'".format(arg))
                return 1
            script = arg
        elif opt == "-h":
            usage()
            sys.exit(0)
        else:
            func = Commands.get(opt.lstrip("-"), None)

    if not files:
        app_error("no input files")
        return 1

    if script:
        path, base = os.path.split(script)
        path = path if path else "."
        sys.path.insert(0, path)
        name = os.path.splitext(base)[0]
        try:
            mod = __import__(name)
        except Exception as err:
            msg = "cannot load script '{0}': {1}"
            app_error(msg.format(script, err))
            return 1
        try:
            func = mod.do
        except AttributeError:
            msg = "not found function 'do(lines)' in script '{0}'"
            app_error(msg.format(script))
            return 1
    elif func is None:
        return 1

    for file in files:
        app_echo(file)
        split_to_lines(file, func, encoding)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

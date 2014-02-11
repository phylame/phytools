#!/usr/bin/env python3
#  Copyright 2013, Peng Wan, <minexiac@gmail.com>
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
import glob
import getopt
import codecs

try:
    import chardet
except ImportError:
    chardet = None


CHI_SPACE = "\u3000"
PARA_START = CHI_SPACE * 2
ENCODINGS = ("gb18030", "utf-8", "utf-16-le", "gbk", "gb2312")


def strip_bom(buf):
    buf = buf.replace(codecs.BOM_UTF16_LE, b'')
    buf = buf.replace(codecs.BOM_UTF16_BE, b'')
    buf = buf.replace(codecs.BOM_UTF8, b'')
    return buf


def decode_text(data):
    if isinstance(data, str):
        return data, None

    if chardet is None:
        data = strip_bom(data)
        for encoding in ENCODINGS:
            try:
                text = data.decode(encoding)
            except UnicodeDecodeError:
                continue
            else:
                return text, encoding
        return (None, None)

    result = chardet.detect(data)
    confidence = result["confidence"]
    if confidence < 0.8:
        return (None, None)

    encoding = result["encoding"]
    data = strip_bom(data)
    return data.decode(encoding), encoding


def remove_null_line(lines):
    result = []
    for line in lines:
        if line.isspace():
            continue
        result.append(line)

    return result

CHAPTER_END_SYMBOLS = "。”；！"


def smart_split(lines):
    result = []
    return lines


def split_to_lines(file, func, encoding=None):
    try:
        fp = open(file, "rb")
    except IOError as err:
        print(err, file=sys.stderr)
        return

    data = fp.read()
    fp.close()
    if encoding:
        try:
            text = data.decode(encoding)
        except UnicodeDecodeError:
            print("ptp: Invalid encoding: '{0}'".format(encoding))
            return
    else:
        text, encoding = decode_text(data)
        if text is None:
            err = "ptp: Cannot decode text file: '{0}'"
            print(err.format(file), file=sys.stderr)
            return

    lines = func(text.splitlines())
    if not isinstance(lines, list):
        print("ptp: Expected 'list' returned value", file=sys.stderr)
        return

    text = os.linesep.join(lines)
    data = text.encode(encoding)
    try:
        fp = open(file, "wb")
    except IOError as err:
        print(err, file=sys.stderr)
        return

    fp.write(data)
    fp.close()


PROG_NAME = "ptp"
OPTIONS_ARGS = "he:f:"
COMMAND_ARGS = ["remove-null", "smart-split"]


def usage():
    s = "usage: {0} [options] files...".format(PROG_NAME)
    print(s)
    print("options:")
    print(" -e                encoding of text file")
    print(" -f                customized script path")
    print(" --remove-null     remove empty lines")
    print("--smart-split      smart split chapter")


def error(msg):
    print("{0}: {1}".format(PROG_NAME, msg), file=sys.stderr)


def expand_path(files):
    if sys.platform.startswith("win"):
        items = []
        for x in files:
            ls = glob.glob(x)
            if not ls:
                error("not such file: '{0}'".format(x))
            items.extend(ls)

        return items
    else:
        return files


def main(argv):
    argv = argv[1:]
    try:
        opts, extra = getopt.getopt(argv, OPTIONS_ARGS, COMMAND_ARGS)
    except getopt.GetoptError as err:
        error(err)
        usage()
        return 1

    files = expand_path(extra)

    encoding = None
    script = None
    func = remove_null_line
    for opt, arg in opts:
        if opt == "--remove-null":
            func = remove_null_line
        elif opt == "--smart-split":
            func = smart_split
        elif opt == "-e":
            encoding = arg
        elif opt == "-f":
            if not os.path.exists(arg):
                error("not such script: '{0}'".format(arg))
                return 1
            script = arg
        elif opt == "-h":
            usage()
            sys.exit(0)

    if not files:
        error("no input files")
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
            error(msg.format(script, err))
            return 1
        try:
            func = mod.do
        except AttributeError:
            msg = "not found function 'do(lines)' in script '{0}'"
            error(msg.format(script))
            return 1
    elif func is None:
        return 1

    for file in files:
        print("{0}: {1}".format(PROG_NAME, file))
        split_to_lines(file, func, encoding)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
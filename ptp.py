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
        line = line.strip()
        if line == "":
            continue
        line = PARA_START + line
        result.append(line)

    return result


def split_to_lines(file, func=remove_null_line, encoding=None):
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


ARGS = "e:f:"


def main(argv):
    argv = argv[1:]
    try:
        opts, extra = getopt.getopt(argv, ARGS)
    except getopt.GetoptError as err:
        print("ptp:", err, file=sys.stderr)
        print("usage: ptp [-e ENCODING] [-f SCRIPTFILE] filenames...")
        sys.exit(1)

    if sys.platform.startswith("win"):
        files = []
        for x in extra:
            ls = glob.glob(x)
            if not ls:
                print("ptp: Not such file: '{0}'".format(x), file=sys.stderr)
            files.extend(ls)
    else:
        files = extra
    if not files:
        return

    encoding = None
    script = None
    for opt, arg in opts:
        if opt == "-e":
            encoding = arg
        elif opt == "-f":
            script = arg

    if not script:
        func = remove_null_line
    elif not os.path.exists(script):
        print("ptp: Not such script: '{0}'".format(script), file=sys.stderr)
        return
    else:
        path, base = os.path.split(script)
        path = path if path else "."
        sys.path.insert(0, path)
        name = os.path.splitext(base)[0]
        try:
            mod = __import__(name)
        except Exception as err:
            msg = "ptp: Cannot load script '{0}': {1}"
            print(msg.format(script, err), file=sys.stderr)
            return
        try:
            func = mod.do
        except AttributeError:
            msg = "ptp: Not found function 'do(lines)' in script '{0}'"
            print(msg.format(script), file=sys.stderr)
            return

    for file in files:
        print("ptp: {0}".format(file))
        split_to_lines(file, func, encoding)


if __name__ == "__main__":
    main(sys.argv)
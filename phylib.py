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
"""Phylame Library for Python"""

from __future__ import print_function
import sys
import os
import glob
import codecs
try:
    import chardet
except ImportError:
    chardet = None


PY3 = sys.version_info[0] == 3
try:
    import android
except ImportError:
    ANDROID = False
else:
    ANDROID = True
    del android

LINUX = sys.platform.startswith("linux")
WIN = sys.platform.startswith("win")
UNIX = LINUX

WIN_LN = "\r\n"
UNIX_LN = "\n"
MAC_LN = "\r"
LN = os.linesep


def fprintf(file, fmt, *args):
    print(fmt % args, file=file)


# Program name for echo
PROG_NAME = None


def mkcstr(s, back, fore):
    """make str with color"""

    s = str(s)
    if UNIX:
        if "\033[" not in s:
            return "\033[{0};{1}m{2}".format(back, fore, s)
    return r

    
def error(msg, prefix="error"):
    msg = mkcstr(msg, 1, 31)
    s = "{0}: {1}".format(prefix, msg)
    if "\033[" in s:
        s += "\033[0m"
    print(s, file=sys.stderr)


def app_error(msg, prefix="error"):
    if PROG_NAME:
        prefix = "{0}: {1}".format(PROG_NAME, prefix)
    error(msg, prefix)


def app_echo(msg):
    if PROG_NAME:
        s = "{0}: {1}".format(PROG_NAME, msg)
    else:
        s = msg
    print(s, file=sys.stderr)


def echo(*args):
    print(*args, file=sys.stdout)


def strerror(err):
    if isinstance(err, IOError):
        return "{0}: '{1}'".format(err.strerror, err.filename)
    else:
        return str(err)


def expand_path(files):
    if sys.platform.startswith("win"):
        items = []
        for x in files:
            ls = glob.glob(x)
            if not ls:
                app_error("not such file: '{0}'".format(x))
            items.extend(ls)

        return items
    else:
        return files


CHI_SPACE = "\u3000"
PARA_START = CHI_SPACE * 2
ENCODINGS = ("gb18030", "utf-8", "utf-16-le", "gbk", "gb2312")


def strip_bom(buf):
    buf = buf.replace(codecs.BOM_UTF32_LE, b'')
    buf = buf.replace(codecs.BOM_UTF16_LE, b'')
    buf = buf.replace(codecs.BOM_UTF32_LE, b'')
    buf = buf.replace(codecs.BOM_UTF16_BE, b'')
    buf = buf.replace(codecs.BOM_UTF8, b'')
    return buf


def decode_text(data):
    if PY3:
        cls = str
    else:
        cls = unicode
    if isinstance(data, cls):
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

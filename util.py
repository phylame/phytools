#!/usr/bin/env python
# -*- coding: utf-8 -*-
#################################################################################
##
##   Copyright 2013, Peng Wan, <minexiac@gmail.com>
##
##   Licensed under the Apache License, Version 2.0 (the "License");
##   you may not use this file except in compliance with the License.
##   You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
##   Unless required by applicable law or agreed to in writing, software
##   distributed under the License is distributed on an "AS IS" BASIS,
##   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##   See the License for the specific language governing permissions and
##   limitations under the License.
##
#################################################################################
"""constants and utilities"""

from __future__ import print_function
import os
import sys
import locale
import codecs
import struct
import datetime


# current platform
PLATFORM    = sys.platform
WINDOWS     = PLATFORM.startswith("win")
DARWIN      = PLATFORM.startswith("darwin")
SYMBIAN     = PLATFORM.startswith("symbian")        # for my old Nokia Symbian Phone, :)
UNIX        = not (WINDOWS or DARWIN or SYMBIAN)
try:
    import android    # for Android
except ImportError:
    ANDROID = False
else:
    del android
    ANDROID = True

# line separator
WIN_LN      = "\r\n"
MAC_LN      = "\r"
UNIX_LN     = "\n"
LINE_FEEDS  = WIN_LN, MAC_LN, UNIX_LN
LN          = os.linesep

# locale encoding
LOCALE_ENCODING      = locale.getpreferredencoding()
# file system encoding
FS_ENCODING          = sys.getfilesystemencoding()
if LOCALE_ENCODING is None:
    LOCALE_ENCODING = FS_ENCODING
    
# default Chinese encoding
try:
    u''.encode('gb18030')
except LookupError:
    # tested on Android
    DEF_CHI_ENCODING     = "utf-8"
else:
    DEF_CHI_ENCODING     = "gb18030"

def revdict(d):
    """Reverse key and value in dict ''d''"""
    
    return dict([(d[k], k) for k in d.iterkeys()])

BOM_UTF16_LE    = codecs.BOM_UTF16_LE
BOM_UTF16_BE    = codecs.BOM_UTF16_BE
BOM_UTF8        = codecs.BOM_UTF8
BOM_UNICODE     = BOM_UTF16_LE
ENCODING_BOM    = {
    "utf-16-le":    BOM_UTF16_LE,
    "utf-16-be":    BOM_UTF16_BE,
    "utf-8":        BOM_UTF8
}
BOM_ENCODING    = revdict(ENCODING_BOM)

ENCODINGS       = ("gb18030", "utf-8", "utf-16-le", "utf-16-be", "big5")
def _try_decode(dat):
    """Guess the encoding of ''dat'' and decode it"""

    txt = None
    for enc in ENCODINGS:
        try:
            txt = dat.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    return txt, enc

def decode_text(dat, enc=""):
    """Decode ''dat'' to unicode.
    If specified ''enc'', decode ''dat'' with ''enc'', else guess the encoding and try decode.
    Return tuple(unicode, enc) or (None, None) if failed.
    """
    
    if isinstance(dat, unicode):
        return dat, ""
    if enc:
        try:
            dat = dat.lstrip(get_bom(enc))
            txt = dat.decode(enc)
        except UnicodeDecodeError:
            txt = (None, None)
        except LookupError:
            txt = (None, None)
        return txt, enc
    if dat.startswith(BOM_UTF8):
        dat = dat.lstrip(BOM_UTF8)
        enc = "utf-8"
    elif dat.startswith(BOM_UTF16_LE):
        dat = dat.lstrip(BOM_UTF16_LE)
        enc = "utf-16-le"
    elif dat.startswith(BOM_UTF16_BE):
        dat = dat.lstrip(BOM_UTF16_BE)
        enc = "utf-16-be"
    else:
        return _try_decode(dat)
    txt = dat.decode(enc)
    return txt, enc

def read_ini(str, comm_label=u":", value_sep=u"="):
    """Read key=value data from ''str''.
    * comm_label: comment line label
    * value_sep: split key and value
    Return (dict, list), dict: keys: values, list: other lines not start with comm_label
    """
    
    vals = {}
    others = []
    for line in str.splitlines():
        s = line.lstrip()
        if s == u"" or s.startswith(comm_label):
            continue
        seq = s.split(value_sep)
        if len(seq) != 2:
            others.append(s)
        else:
            k = seq[0].strip()
            v = seq[1]
            vals[k] = v
    return vals, others

def replace_ln(txt, ln):
    txt = txt.replace('\r\n', '\n')
    txt = txt.replace('\r', '\n')
    txt = txt.replace('\n', ln)
    return txt

def encode_with_bom(str, enc):
    """Encode str and add BOM"""

    dat = str.encode(enc)
    bom = get_bom(enc)
    if bom:
        return bom + dat
    else:
        return dat

def read_all(path, mode="r"):
    """Read full data from file ''path''.
    Return str or None if failed.
    """

    try:
        fp = open(path, mode)
    except IOError:
        return None
    dat = fp.read()
    fp.close()
    return dat

def read_data(fp, fmt):
    """Read binary data from file ''fp''.
    Get value by struct.unpack, specified format ''fmt''.
    If has one value, return it instead of a tuple.
    If failed, return None.
    """
    
    sl = struct.calcsize(fmt) # size length
    dat = fp.read(sl)
    if len(dat) != sl:
        return None
    dl = struct.unpack(fmt, dat) # data length
    if len(dl) == 1:
        return dl[0]
    return dl

def read_ptext(fp, fmt, enc=""):
    """Read str from file ''fp''.
    str length specified by format ''fmt''.
    If set enc, convert to unicode by ''enc''.
    Return str or unicode or None if ''enc'' is invalid.
    """
    
    dl = read_data(fp, fmt) # data length
    dat = fp.read(dl)
    if len(dat) != dl:
        return None
    if not enc:
        return dat
    try:
        txt = dat.decode(enc)
    except UnicodeDecodeError:
        return None
    return txt

def get_bom(enc):
    enc = enc.lower()
    return ENCODING_BOM.get(enc, "")


def get_today():
    """Get today date, return datetime."""
    
    return datetime.datetime.now().date()

def get_date(str):
    """Get datetime from str.
    Return datetime or None.
    """
    
    try:
        return datetime.datetime.strptime(str, "%Y-%m-%d").date()
    except :
        return None


CHI_DIGIT_BIT = {2: u"十", 3: u"百", 0: u"千"}
CHI_NUM       = {"1": u"一", "2": u"二", "3": u"三", "4": u"四", "5": u"五", "6": u"六", "7": u"七", "8": u"八", "9": u"九"}
CHI_NUM_SEP   = {1: u"万", 2: u'亿'}
CHI_ZERO      = u"零"

# chinese number
NUM_STR = CHI_NUM.values() + [unicode(n) for n in range(10)]
NUM_STR.extend(CHI_DIGIT_BIT.values())
NUM_STR.extend(CHI_NUM_SEP.values())
NUM_STR.append(u'○')
NUM_STR.append(CHI_ZERO)
del n

def is_num_str(c):
    return c in NUM_STR


class Base(object):
    """Base class"""
    
    def __str__(self):
        """call Base.__unicode__ and encode with locale encoding"""
        
        return self.__unicode__().encode(LOCALE_ENCODING)

    def __unicode__(self):
        return unicode(repr(self))

def l2u(s):
    """locale str to unicode"""
    
    return unicode(s, LOCALE_ENCODING)

def u2l(u):
    """unicode to locale str"""
    
    if isinstance(u, unicode):
        return u.encode(LOCALE_ENCODING)
    return u

def printf(fmt, *args):
    """C style output"""
    
    s = fmt % args

    print(u2l(s), end="")

class Echo(object):
    def __init__(self):
        self.__enable = False
        self.__debug  = False
        self.__out    = sys.stdout

    def __print(self, *args):
        """print without '\n'"""

        args = map(u2l, args)
        print(*args, end="", file=self.__out)


    def printf(fmt, *args):
        """C style output"""
    
        s = fmt % args
        self.__print(u2l(s))

    def __call__(self, *args):
        if self.enable:
            self.__print(*args)
            self.__print('\n')
    
    # not append new line
    def echo(self, *args):
        if self.enable:
            self.__print(*args)

    def debug(self, *args):
        if self.__debug:
            self.__print("Debug: ")
            self.__print(*args)
            self.__print("\n")

    def error(self, *args):
        self.echo("Error: ")
        self(*args)

    @property
    def enable(self):
        return self.__enable

    @enable.setter
    def enable(self, enable):
        self.__enable = bool(enable)

    @property
    def is_debug(self):
        return self.__debug

    def set_debug(self, enable):
        self.__debug = bool(enable)

    @property
    def file(self):
        return self.__out

    @file.setter
    def file(self, fo):
        if hasattr(fo, "write"):
            self.__out = fo
        else:
            raise TypeError("file or file-like object excepted")


echo = Echo()
del Echo

def test():
    """Test the modulw"""

    echo.debug("At:", 434)
    echo.error("An error ocure")

if __name__ == "__main__":
    test()

#!/usr/bin/env python3
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
"""Modify PMAB book Information"""

import os
import sys
import glob
import getopt
import zipfile
import traceback
from phylib import app_error, app_echo
import phylib
phylib.PROG_NAME = "bookmod"

try:
    import pemx.formats.pmab as _pmab
except ImportError:
    app_error("not found 'pemx' installation")
    sys.exit(-1)

from pemx import unpack, pio, utils
try:
    import ptp
except ImportError:
    ptp = None


OUTPUT = "modified"


def get_pmab(file, book_format, parse_args):
    try:
        fp = open(file, "rb")
    except IOError as err:
        app_error(phylib.strerror(err))
        return None, None

    if not book_format:
        fmt = os.path.splitext(file)[-1].lstrip(os.extsep)
    else:
        fmt = book_format
    fmt = fmt.lower()
    book = unpack.parse_book(fp, fmt, **parse_args)
    return book, fp


def make_pmab(book, output, make_args):
    try:
        ret = _pmab.make(book, output, **make_args)
    except Exception as err:
        if _pmab.echo.is_debug():
            traceback.print_exc()
        return None

    return ret


def modify_book(book, assigned_attrs, deleted_attrs):
    for name, value in assigned_attrs.items():
        try:
            book.setinfo(name, value)
        except Exception as err:
            app_error("set attributr: {0}={1}: {1}".format(name, value, err))
            continue

    for name in deleted_attrs:
        try:
            setattr(book, name, "")
        except Exception as err:
            app_error("delete attribute: {0}".format(err))
            continue


def sec_cmp(a, b):
    trk = zip(a.split(), b.split())
    title = []
    for i, j in trk:
        if i == j:
            title.append(i)

    return title


def split_section(book):
    if book.sections:
        if _pmab.echo.is_debug():
            app_echo("debug: sections exists")
        return
    section = []
    pre = None
    title = []
    book.add_chapter("xx")  # nothing
    for i, chapter in enumerate(book):
        if not pre:
            pre = chapter.title
        else:
            section.append(i - 1)
            cur = chapter.title
            ret = sec_cmp(pre, cur)

            if not ret:
                if not title:   # single chapter
                    pass    # do nothing
                else:   # sections
                    book.add_section(title = " ".join(title), chapters=section)
                pre = cur
                title = []
                section = []
            elif not title:
                title = ret
            pre = cur

    # strip section title in the front of chapter title
    for section in book.sections:
        for i in section:
            chapter = book[i]
            title = " ".join(chapter.title.split())
            title = title.replace(section.title, "").strip()
            if title:   # title is null
                chapter.title = title

    book.pop(-1)    # remove "xx"


OPTIONS_ARGS = "hdco:f:T:r:s:P:M:"


def usage():
    print("usage: {0} [options] files...".format(phylib.PROG_NAME))
    print(" Modify PMAB book information\n")
    print("options:")
    print(" -d                 dispaly debug information")
    print(" -o <path>          place output to path")
    print(" -f <format>        specify book format")
    print(" -c                 split book sections")
    print(" -T <command>       modify book text by ptp's command")
    print(" -r <name>          remove book attribute")
    print(" -S <name=value>    set book attributes")
    print(" -P <name=value>    send value to book parser")
    print(" -M <name=value>    send value to book maker")


def parse_kargs(str):
    try:
        name, value = str.split("=")
    except ValueError:
        app_error("expected 'name=value'")
        return None, None

    return name, value


def modify_text(book, ptp_option):
    def _txtgen(sort, files):
        with open(files[sort]) as fp:
            return fp.read()

    files = []
    for i in range(len(book)):
        fn = os.path.join(pio.temp_path(), "{0}_{1}".format(id(book), i))
        try:
            fp = open(fn, "w")
        except IOError as err:
            return files
        try:
            text = book.gettext(i)
        except Exception:
            return files
        lines = text.splitlines()
        ret = ptp_option(lines)
        text = utils.LN.join(ret)
        fp.write(text)
        fp.close()
        files.append(fn)

    if files:
        book.txtgen = lambda sort: _txtgen(sort, files)
    return files


def main(argv):
    argv = argv[1:]
    try:
        opts, extra = getopt.getopt(argv, OPTIONS_ARGS)
    except getopt.GetoptError as err:
        app_error(err)
        usage()
        return -1

    files = phylib.expand_path(extra)

    output = None
    book_format = None
    deleted_attrs = []
    assigned_attrs = {}
    parse_args = {}
    make_args = {}
    command = None
    ptp_option = None
    for opt, arg in opts:
        if opt == "-o":
            if not os.path.exists(arg):
                app_error("Not such output directory: '{0}'".format(arg))
                return 1
            output = arg
        elif opt == "-c":   # split sections
            command = split_section
        elif opt == "-r":   # remove attributes
            deleted_attrs.append(arg)
        elif opt == "-s":   # set attributes
            name, value = parse_kargs(arg)
            if not name: return -1
            assigned_attrs[name] = value
        elif opt == "-T":
            arg = arg.replace("-", "_")
            if not ptp:
                app_error("not found 'ptp' module")
                return -1
            ptp_option = getattr(ptp, arg, None)
            if not ptp_option or not callable(ptp_option):
                app_error("not found option '{0}' in ptp".format(arg))
                return -1
        elif opt == "-P":   # parse arguments
            name, value = parse_kargs(arg)
            if not name: return -1
            parse_args[name] = value
        elif opt == "-M":   # make arguments
            name, value = parse_kargs(arg)
            if not name: return -1
            make_args[name] = value
        elif opt == "-f":
            book_format = arg
        elif opt == "-d":
            unpack.echo.set_debug(True)
        elif opt == "-h":
            usage()
            return 0

    if not files:
        app_error("no input files")
        return 1

    status = 0
    for file in files:
        if not output:
            out = os.path.join(os.path.dirname(file), OUTPUT)
            try:
                os.mkdir(out)
            except OSError as err:
                if err.errno != 17: # exists
                    app_error(err)
                    return 1
        else: out = output
        book, fp = get_pmab(file, book_format, parse_args)
        if book:
            modify_book(book, assigned_attrs, deleted_attrs)
            if command: command(book)
            ls = []
            if ptp_option:
                ls = modify_text(book, ptp_option)
            ret = make_pmab(book, out, make_args)
            for fn in ls:
                os.remove(fn)
            if ret: print(ret)
            else: status = -1
        else:
            status = -1
        if fp: fp.close()

    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))

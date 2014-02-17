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
"""Split book section by chapter title"""

import sys
import os
import getopt
import traceback
from phylib import app_error, app_echo
import phylib
phylib.PROG_NAME = "booksplit"

try:
    import pemx.formats.pmab as _pmab
except ImportError:
    sys.exit(1)


OPTIONS_ARG = "hdo:V:"


def usage():
    print("usage: {0} [options] files...".format(phylib.PROG_NAME))
    print(" Split book sections by chapter titles\n")
    print("options:")
    print(" -d                  display debug information")
    print(" -o <path>           place output to path")
    print(" -V <name=value>     send arguments to book parser")


def sec_cmp(a, b):
    trk = zip(a.split(), b.split())
    title = []
    for i, j in trk:
        if i == j:
            title.append(i)

    return title


def do(file, output, parser_args):
    try:
        fp = open(file, "rb")
    except IOError as err:
        msg = "{0}: '{1}'".format(err.strerror, err.filename)
        app_error(msg)
        return None

    book = _pmab.parse(fp, **parser_args)
    if book.sections:
        fp.close()
        app_echo("sections exists")
        return True

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
            chapter.title = title.replace(section.title, "").strip()

    book.pop(-1)    # remove "xx"
    try:
        ret = _pmab.make(book, output)
    except Exception as err:
        app_error("cannot make PMAB")
        if _pmab.echo.is_debug():
            traceback.print_ext()
        fp.close()
        return None

    fp.close()
    if ret:
        print(ret)
    return ret


def main(argv):
    try:
        opts, extra = getopt.getopt(argv[1:], OPTIONS_ARG)
    except getopt.GetoptError as err:
        app_error(err)
        usage()
        return -1

    files = phylib.expand_path(extra)
    output = None
    kw = {}
    for opt, arg in opts:
        if opt == "-h":
            usage()
            return 0
        elif opt == "-o":
            output = arg
        elif opt == "-d":
            _pmab.echo.set_debug(True)
        elif opt == "-V":
            try:
                name, value = arg.split("=")
            except ValueError:
                app_error("'-V' expected 'name=value'")
                sys.exit(1)
            kw[name] = value

    status = 0
    for file in files:
        if not output:
            out = os.path.join(os.path.dirname(file), "modified")
            try:
                os.mkdir(out)
            except OSError as err:
                if err.errno != 17:
                    app_error(err)
                    continue
        else:
            out = output
        if not do(file, out, kw):
            status = 1

    return status



if __name__ == "__main__":
    sys.exit(main(sys.argv))



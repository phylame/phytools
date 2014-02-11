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
"""Split PMAB's Sections to Single PMAB"""

import os
import sys
import glob
import getopt
try:
    from pemx import unpack
    from pemx.formats import pmab
except ImportError:
    print("sec2book: Not found 'pemx'", file=sys.stderr)
    sys.exit(1)


def do(path, book_format, output, kw):
    try:
        fp = open(path, "rb")
    except IOError as err:
        msg = "sec2book: {0}: '{1}'".format(err.strerror, err.filename)
        print(msg, file=sys.stderr)
        return

    if book_format:
        fmt = book_format
    else:
        fmt = os.path.splitext(path)[1].lstrip(os.extsep)
    full_book = unpack.parse_book(fp, fmt, **kw)
    if full_book is None:
        msg = "bookmod: Cannot load: '{0}'".format(path)
        print(msg, file=sys.stderr)
        fp.close()
        return

    if not full_book.sections:
        print("sec2book: No sections found in '{0}'".format(path))
        fp.close()
        return

    for section in full_book.sections:
        book = pmab.PMAB(title=section.title, author=full_book.author)
        for i in section:
            chapter = full_book[i]
            chapter.content = full_book.gettext(i)
            book.append(chapter)

        result = pmab.make(book, output)
        if result:
            print(result)

    fp.close()
    return result


def usage():
    print("usage: sec2book [-d] [-o OUTPUT] [-f FORMAT] "
        "[-V name=value] filenames...")
    print("Options:")
    print("-d                 Display debug information")
    print("-o <OUTPUT>        Output path")
    print("-f <FORMAT>        Specify book format")
    print("-V <name=value>    Send value to book parser")


ARGS = "hdo:V:f:"


def main(argv):
    argv = argv[1:]
    try:
        opts, extra = getopt.getopt(argv, ARGS)
    except getopt.GetoptError as err:
        print("sec2book:", err, file=sys.stderr)
        usage()
        sys.exit(1)

    if sys.platform.startswith("win"):
        errmsg = "sec2book: Not such file: '{0}'"
        files = []
        for x in extra:
            ls = glob.glob(x)
            if not ls:
                print(errmsg.format(x), file=sys.stderr)
            files.extend(ls)
    else:
        files = extra

    output = None
    book_format = None
    kw = {}
    for opt, arg in opts:
        if opt == "-o":
            if not os.path.exists(arg):
                msg = "sec2book: Output not exists: '{0}'"
                print(msg.format(arg), file=sys.stderr)
                sys.exit(1)

            output = arg
        elif opt == "-V":
            try:
                name, value = arg.split("=")
            except ValueError:
                print("sec2book: '-V' expected 'name=value'", file=sys.stderr)
                sys.exit(1)

            kw[name] = value
        elif opt == "-f":
            book_format = arg
        elif opt == "-d":
            pmab.echo.set_debug(True)
        elif opt == "-h":
            usage()
            sys.exit(0)

    if not files:
        print("sec2book: No input files", file=sys.stderr)
        sys.exit(1)

    status = 0
    for file in files:
        if not output:
            out = os.path.dirname(file)
        else:
            out = output
        if not do(file, book_format, out, kw):
            status = 1

    sys.exit(status)


if __name__ == "__main__":
    main(sys.argv)

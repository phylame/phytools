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
"""Modify PMAB Information"""

import os
import sys
import glob
import getopt
import zipfile
import traceback
try:
    from pemx import unpack
    from pemx.formats import pmab
except ImportError:
    print("bookmod: Not found 'pemx'", file=sys.stderr)
    sys.exit(1)


def do(path, book_format, output, assigned_attrs, deleted_attrs, kw):
    try:
        fp = open(path, "rb")
    except IOError as err:
        msg = "bookmod: {0}: '{1}'".format(err.strerror, err.filename)
        print(msg, file=sys.stderr)
        return

    if book_format:
        fmt = book_format
    else:
        fmt = os.path.splitext(path)[1].lstrip(os.extsep)
    book = unpack.parse_book(fp, fmt, **kw)
    if book is None:
        msg = "bookmod: Cannot load: '{0}'".format(path)
        print(msg, file=sys.stderr)
        fp.close()
        return

    for name, value in assigned_attrs.items():
        try:
            book.setinfo(name, value)
        except Exception as err:
            msg = "bookmod: Set attribute: {0}={1}:"
            print(msg.format(name, value), err, file=sys.stderr)
            continue

    for name in deleted_attrs:
        try:
            setattr(book, name, "")
        except Exception as err:
            msg = "bookmod: Delete attribute: {0}:"
            print(msg.format(name), err, file=sys.stderr)
            continue

    try:
        result = pmab.make(book, output)
    except Exception as err:
        msg = "bookmod: Cannot make PMAB:"
        print(msg, err, file=sys.stderr)
        if pmab.echo.is_debug():
            traceback.print_exc()
        fp.close()
        return

    if result:
        print(result)

    fp.close()
    return result


def usage():
    print("usage: bookmod [-d] [-o OUTPUT] [-r ATTRIBUTE] [-V name=value]"
        "[-f FORMAT] [-s name=value] filenames...")
    print("Options:")
    print("-d                 Dispaly debug information")
    print("-o <OUTPUT>        Output path")
    print("-r <ATTRIBUTE>     Remove PMAB attribute")
    print("-V <name=value>    Send value to book parser")
    print("-f <FORMAT>        Specify book format")
    print("-s <name=value>    Set PMAB attribute")


ARGS = "dho:r:s:V:f:"


def main(argv):
    argv = argv[1:]
    try:
        opts, extra = getopt.getopt(argv, ARGS)
    except getopt.GetoptError as err:
        print("bookmod:", err, file=sys.stderr)
        usage()
        sys.exit(1)

    if sys.platform.startswith("win"):
        msg = "bookmod: Not such file: '{0}'"
        files = []
        for x in extra:
            ls = glob.glob(x)
            if not ls:
                print(msg.format(x), file=sys.stderr)
            files.extend(ls)
    else:
        files = extra

    output = None
    book_format = None
    deleted_attrs = []
    assigned_attrs = {}
    kw = {}
    for opt, arg in opts:
        if opt == "-o":
            if not os.path.exists(arg):
                msg = "bookmod: Output not exists: '{0}'"
                print(msg.format(arg), file=sys.stderr)
                sys.exit(1)
            output = arg
        elif opt == "-r":
            deleted_attrs.append(arg)
        elif opt == "-s":
            try:
                name, value = arg.split("=")
            except ValueError:
                print("bookmod: '-s' expected 'name=value'", file=sys.stderr)
                sys.exit(1)
            assigned_attrs[name] = value
        elif opt == "-V":
            try:
                name, value = arg.split("=")
            except ValueError:
                print("bookmod: '-V' expected 'name=value'", file=sys.stderr)
                sys.exit(1)
            kw[name] = value
        elif opt == "-f":
            book_format = arg
        elif opt == "-d":
            unpack.echo.set_debug(True)
        elif opt == "-h":
            usage()
            sys.exit(0)

    if not files:
        print("bookmod: No input files", file=sys.stderr)
        sys.exit(1)

    status = 0
    for file in files:
        if not output:
            out = os.path.join(os.path.dirname(file), "modified")
            try:
                os.mkdir(out)
            except OSError as err:
                if err.errno != 17:
                    print("bookmod:", err, file=sys.stderr)
                    sys.exit(1)
        else:
            out = output
        if not do(file, book_format, out, assigned_attrs, deleted_attrs, kw):
            status = 1

    sys.exit(status)

if __name__ == "__main__":
    main(sys.argv)

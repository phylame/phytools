#!/usr/bin/env python
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
"""Phylame Music Tools"""

import sys
import os
import getopt
from phylib import echo, app_error
import phylib


phylib.PROG_NAME = PROG_NAME = "pmt"
OPTIONS = "hc:o:"


def usage():
    s = "usage: {0} [options] files...".format(PROG_NAME)
    echo(s)
    echo("options:")
    echo(" -c  <format>          convert audio format")
    echo(" -o  <path>            place output to path")


# audio and video convertor
def avconv(infile, format, output=None):
    base = os.path.basename(infile)
    name = os.extsep.join((os.path.splitext(base)[0], format))
    if not output:
        output = os.path.dirname(infile)
    outfile = os.path.join(output, name)
    # use ffmpeg
    cmd = "ffmpeg -i {0} {1}".format(infile, outfile)
    if os.system(cmd) != 0:
        app_error("cannot convert {0} to {1}")


def main(argv):
    argv = argv[1:]
    try:
        opts, extra = getopt.getopt(argv, OPTIONS)
    except getopt.GetoptError as err:
        app_error(err)
        usage()
        return 1

    files = phylib.expand_path(extra)
    func = None
    fmt = None
    output = None
    for opt, arg in opts:
        if opt == "-h":
            usage()
            return 0
        elif opt == "-c":
            func = "c"
            fmt = arg
        elif opt == "-o":
            output = arg

    if not files:
        app_error("no input files")
        return 1

    if not func:
        app_error("no options")
        return 1

    for file in files:
        if func == "c":
            avconv(file, fmt, output)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
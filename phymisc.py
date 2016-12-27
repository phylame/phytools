#  Copyright 2016 Peng Wan <phylame@163.com>
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
"""PW's Misc Library"""

import locale
import math
import sys

# line separator of current system
_platform = sys.platform
if _platform.startswith("win"):
    LINE_SEPARATOR = "\r\n"
elif _platform.startswith("mac"):
    LINE_SEPARATOR = "\r"
else:
    LINE_SEPARATOR = "\n"
del _platform

# current platform ENCODING
DEFAULT_ENCODING = locale.getpreferredencoding(False)


def non_none(o, name):
    if o is None:
        raise ValueError("'{0}' require non-none value".format(name))
    return o


def non_empty(s, name):
    if not isinstance(s, str):
        raise TypeError("'{0}' require 'str' object".format(name))
    if len(s) == 0:
        raise ValueError("'{0}' require non-empty string")
    return s


def type_name(clazz):
    if clazz is not None and not isinstance(clazz, type):
        clazz = type(clazz)
    return (clazz.__module__ + "." if clazz.__module__ != "builtins" else "") + clazz.__name__


def for_type(o, clazz, name):
    if not isinstance(o, clazz):
        raise TypeError("'{0}' require '{1}' object".format(name, type_name(clazz)))
    return o


def number_bits(n):
    return int(math.log(n) / math.log(10)) + 1


def iterable(o: object) -> bool:
    return hasattr(o, "__iter__")


app_name = ""


def app_echo(msg, *args):
    print("{0}: {1}".format(app_name, msg.format(*args)))


def app_error(msg, *args):
    print("{0}: {1}".format(app_name, msg.format(*args)), file=sys.stderr)


def app_usage(msg, *args):
    print("usage: {0} {1}".format(app_name, msg.format(*args)))

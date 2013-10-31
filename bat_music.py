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
"""Phylame Music toolkits"""

import os
import sys
import datetime
import random
import util


MUSIC_EXT = [".mp3", ".wav", ".wma", ".aac", ".ape", ".flac"]
LA_EXT = [".ape", ".flac", ".all"]

def _start(root, files, func, arg, has_done = None, not_done = None):
    def _add_has_done(fn):
        if isinstance(has_done, list):
            has_done.append(fn)
    def _add_not_done(fn):
        if isinstance(not_done, list):
            not_done.append(fn)
    
    for i, bn in enumerate(files):
        fn = os.path.join(root, bn)  # source file name
        ext = os.path.splitext(bn)[1]
        ext = ext.lower()
        if not ext or ext not in MUSIC_EXT:
            continue
        seq = bn.split(u"-")
        if len(seq) < 2:
            ar, ti = "", seq[0]
        elif len(seq) == 2:
            ar, ti = seq
        else:
            _add_not_done(fn)
            return  # we don't guess
        
        ar = ar.strip()
        ti = ti.strip()
        
        if callable(func) and func(fn, root, (ar, ti), (bn, ext), arg):
            _add_has_done(fn)
        else:
            _add_not_done(fn)

def classify_by_artist(fn, root, ar_ti, bn_ext, arg):
    ar = ar_ti[0]
    dn = os.path.join(root, ar)
    # has classified
    if root.endswith(ar):
        return True
    # not exists the directory named with artist
    elif not os.path.exists(dn):
        try:
            os.mkdir(dn)
        except OSError, msg:
            return
    bn = bn_ext[0]
    os.rename(fn, os.path.join(dn, bn))
    return True


def convert2(fn, root, ar_ti, bn_ext, arg_to = ".mp3"):
    ext = bn_ext[1]
    # not supportted
    if arg_to not in MUSIC_EXT:
        print("invalid music file")
        return
    if arg_to == ext:
        return True
    if ext not in LA_EXT and arg_to in LA_EXT:
        print("only support lossless to lossless")
        return
    
    tfn = fn.replace(ext, arg_to)
    
    # use ffmpeg
    cmd = u'ffmpeg -i "%s" "%s"' % (fn, tfn)
    cmd = util.u2l(cmd)
    return os.system(cmd) == 0
         

def split_artist(fn, root, ar_ti, bn_ext, arg):
    ar, ti = ar_ti
    if ar:
        bn = u"%s - %s" % (ar, ti)
    else:
        bn = ti
    d = os.path.join(root, bn)
    os.rename(fn, d)
    return True

def mk_m3u(pl, root, files):
    for i, bn in enumerate(files):
        fn = os.path.join(root, bn)  # source file name
        ext = os.path.splitext(bn)[1]
        if ext not in MUSIC_EXT:
            continue
        
        bn = os.path.splitext(bn)[0]
        seq = bn.split(u"-")
        if len(seq) != 2:
            ti = bn
        else:
            ti = seq[1]
        ti = ti.strip()
        s = u"#EXTINF:," + ti
        pl.append(s)
        pl.append(fn)
        
def make_playlist(src, dest = u"", shuffle = False):
    pl = []
    if not dest:
        dest = os.path.join(src, "playlist.m3u")
    for root, dirs, files in os.walk(src):
        mk_m3u(pl, root, files)
    if shuffle:
        random.shuffle(pl)
    pl.insert(0, u"#EXTM3U")
    ls = [x.encode("u8") for x in pl]
    dat = os.linesep.join(ls)
    
    fp = open(dest, "w")
    fp.write(dat)
    fp.close()

def remove_id3(fn, ar, ti, ext):
    try:
        import eyed3
    except ImportError:
        return
    
    if ext != ".mp3":
        return

    cmd = u'eyeD3 --remove-all "%s"' % fn
    cmd = cmd.encode(LOCALE_ENCODING)
    return os.system(cmd) == 0

def write_id3(fn, artist, title, ext, tags = {}, encoding = "utf-16"):
    try:
        import eyed3
    except ImportError:
        return
    
    if ext != ".mp3":
        return
    
    au = eyed3.load(fn)
    if au is None:
        return
    au.tag.artist = artist
    au.tag.title = title
    for k, v in tags.iteritems():
        setattr(au.tag, k, v)
    
    au.tag.save(version = eyed3.id3.ID3_V2_3, encoding = encoding)
    return True

def loader(src, func, arg = None):
    has_done = []
    not_done = []
    for root, dirs, files in os.walk(src):
        _start(root, files, func, arg, has_done = has_done, not_done = not_done)

    return has_done, not_done

Tools = {
    "conv": convert2,
}

def main(argv):
    for arg in argv:
        print arg

if __name__ == "__main__":
    argv = map(util.l2u, sys.argv)
    main(argv[1:])

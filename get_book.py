#!/usr/bin/env python
# -*- coding: utf-8 -*-
#################################################################################
##
##   Copyright 2013, PenG Wan, <minexiac@gmail.com>
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
"""get book from html"""

import os
import urlparse
import urllib2
import sgmllib

class JyjhParser(sgmllib.SGMLParser):
    is_title = False
    title = u''
    charset = "gb18030"
    is_a = False
    chapter_titles = []
    chapter_urls = []
    
    def start_meta(self, attr):
        for a in attr:
            k, v = a
            if k == 'charset':
                self.charset = v
            elif k == 'content':
                i = v.find('charset')
                if i != -1:
                    i = v.find('=', i)
                    v = v[i+1:]
                    self.charset = v
            
        
    def start_title(self, attr):
        self.is_title = True

    def end_title(self):
        self.is_title = False

    def start_a(self, attr):
        self.is_a = True
        v = dict(attr)
        href = v.get("href", "")
        if not href:
            return
        v = urlparse.urlparse(href)
        if v.netloc == '':
            self.chapter_urls.append(v.path)

    def end_a(self):
        self.is_a = False
    
    def handle_decl(self, data):
        txt = unicode(data, self.charset)
        print txt
        
    def handle_data(self, data):
        if self.is_title:
            title = unicode(data, self.charset)
            seq = title.split(u'-')
            self.title = seq[-1].strip()
        elif self.is_a:
            ct = unicode(data, self.charset).strip()
            print ct
            self.chapter_titles.append(ct)

def get_book(url, parser):
    """get book from www.jyjh.com.cn"""
    fp = urllib2.urlopen(url)
    dat = fp.read()
    cts = []
    cus = []
    parser.chapter_titles = cts
    parser.chapter_urls = cus
    parser.feed(dat)
    

if __name__ == "__main__":
    url = "http://www.jyjh.com.cn/jinyong/09/"
    parser = JyjhParser()
    get_book(url, parser)
    

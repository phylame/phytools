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
"""PW's HTML Utilities"""

import os
import random
import re
import zipfile
from urllib import parse, request

import bs4
import phymisc

safe_strings = ":/?& = "
default_scheme = "http://"
scheme_re = re.compile(r"(http://)|(https://)|(ftp://)")
user_agents = (
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; InfoPath.2; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; 360SE)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; TencentTraveler 4.0; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
    'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'
)


def host_of(url: (str, bs4.BeautifulSoup)) -> str:
    if isinstance(url, str):
        o = parse.urlsplit(url)
    elif isinstance(url, bs4.BeautifulSoup):
        o = parse.urlparse(url.response.url)
    else:
        raise TypeError("'url' require 'str' or 'bs4.BeautifulSoup'")
    return o.scheme + '://' + o.netloc


def make_url(url: str, encoding=phymisc.DEFAULT_ENCODING) -> str:
    return parse.quote(url, safe_strings, encoding=encoding)


def make_data(data, encoding=phymisc.DEFAULT_ENCODING):
    if data is None or isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return data.encode(encoding)
    elif isinstance(data, dict):
        return bytes(parse.urlencode(data, safe=safe_strings, encoding=encoding), "ascii")
    else:
        raise TypeError("'data' require 'None', 'bytes', 'dict' or 'str'")


def default_headers():
    return {
        "User-Agent": random.choice(user_agents),
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }


def make_request(url: (str, request.Request), data=None, headers: dict = {}, method: str = None) -> request.Request:
    _headers = default_headers()
    _headers.update(headers)
    if isinstance(url, str):
        url = request.Request(make_url(url), data=make_data(
            data), headers=_headers, method=method)
    elif isinstance(url, request.Request):
        _headers.update(url.headers)
        url.headers = _headers
        url.data = make_data(data)
        if method:
            url.method = method
    else:
        raise TypeError("'url' require 'str' or 'urllib.request.Request'.")
    return url


def open_url(url: (str, request.Request), data=None, headers: dict = {}, method: str = None):
    return request.urlopen(make_request(url, data, headers, method))


def parse_html(markup, encoding: str = None, parser: str = 'html.parser') -> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(markup, parser, from_encoding=encoding)


def fetch_html(url: (str, request.Request), data=None, headers: dict = {}, method: str = None, encoding: str = None, parser: str = 'html.parser'):
    response = open_url(url, data, headers, method)
    if response.getcode() != 200:
        return None
    if not encoding:
        encoding = response.headers.get_charsets()[0]
    soup = parse_html(response, encoding, parser)
    soup.response = response
    return soup


def fetch_file(url: (str, request.Request), data=None, headers: dict = {}, method: str = None):
    response = open_url(url, data, headers, method)
    if response.getcode() != 200:
        return None
    return response


def save_files(urls, path, for_zip=True) -> None:
    zf = zipfile.ZipFile(
        path + ".zip" if not path.endswith(".zip") else path, "w") if for_zip else None
    for i, url in enumerate(urls, 1):
        name = "{0:0%d}{1}" % phymisc.number_bits(len(urls))
        name = name.format(i, os.path.splitext(url)[-1])
        fp = open(os.path.join(path, name), "wb") if not zf else None
        with fetch_file(url) as img_in:
            print("{0}. fetching image: {1}".format(i, url))
            if zf:
                zf.writestr(name, img_in.read())
            else:
                fp.write(img_in.read())
        if not zf:
            fp.close()
    if zf:
        zf.close()


def conv_text(str):
    return str.strip().replace("\xa0", " ")


def find_tag(soup, name, clazz=None, id=None):
    attrs = {}
    if clazz:
        attrs['class'] = clazz
    if id:
        attrs['id'] = id
    return soup.find(name, attrs)


def find_tags(soup, name, clazz=None, id=None):
    attrs = {}
    if clazz:
        attrs['class'] = clazz
    if id:
        attrs['id'] = id
    return soup.find_all(name, attrs=attrs)

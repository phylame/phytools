# Utilities for HTML
#
import os
import random
import re
import zipfile
from urllib import parse, request

import bs4
import phymisc

safe_strings = ":/?&="
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


def quote_url(url: str, encoding=None) -> str:
    return parse.quote(url, safe_strings, encoding=encoding)


def prepare_url(url: str) -> str:
    return quote_url(url if scheme_re.match(url) else default_scheme + url)


def prepare_data(data, encoding=phymisc.DEFAULT_ENCODING):
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


def wrap_request(url: (str, request.Request), data, headers: dict = {}, method: str = None) -> request.Request:
    _headers = dict(default_headers())
    _headers.update(headers)
    if isinstance(url, str):
        return request.Request(prepare_url(url), data=prepare_data(data), headers=_headers, method=method)
    elif not isinstance(url, request.Request):
        raise TypeError("'url' require 'str' or 'urllib.request.Request'.")
    _headers.update(url.headers)
    url.headers = _headers
    url.data = prepare_data(data)
    if method:
        url.method = method
    return url


def open_url(url, data=None):
    if isinstance(url, str):
        response = request.urlopen(wrap_request(url, data))
    elif isinstance(url, request.Request):
        response = request.urlopen(url, data=data)
    else:
        raise TypeError("'url' require 'str' or 'urllib.request.Request'.")
    return response


def parse_html(data, encoding=None) -> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(data, "html.parser", from_encoding=encoding)


def open_soup(url: (str, request.Request), data: bytes = None, headers: dict = {}, method: str = None,
              encoding: str = None,
              parser: str = 'html.parser'):
    response = open_url(url, data)
    if response.getcode() != 200:
        return None
    if not encoding:
        encoding = response.headers.get_charsets()[0]
    soup = bs4.BeautifulSoup(response, parser, from_encoding=encoding)
    soup.response = response
    return soup


def fetch_file(url, data=None):
    response = open_url(url, data)
    if response.getcode() != 200:
        return None
    return response


def save_files(urls, path, for_zip=True) -> None:
    zip_out = zipfile.ZipFile(path + ".zip" if not path.endswith(".zip") else path, "w") if for_zip else None
    for i, url in enumerate(urls, 1):
        name = "{0:0%d}{1}" % phymisc.number_bits(len(urls))
        name = name.format(i, os.path.splitext(url)[-1])
        fp_out = open(os.path.join(path, name), "wb") if not zip_out else None
        with fetch_file(url) as img_in:
            print("{0}. fetching image: {1}".format(i, url))
            if zip_out:
                zip_out.writestr(name, img_in.read())
            else:
                fp_out.write(img_in.read())
        if not zip_out:
            fp_out.close()
    if zip_out:
        zip_out.close()


def conv_text(str):
    return str.strip().replace("\xa0", " ")


def tag_for_class(soup, name, clazz):
    return soup.find(name, {'class': clazz})


def tags_for_class(soup, name, clazz):
    return soup.find_all(name, {'class': clazz})

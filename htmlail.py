# Utilities for HTML
#

import os
import bs4
import random
from urllib.parse import urlparse
from urllib.request import urlopen, Request


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


def host_of(soup):
    o = urlparse(soup.response.url)
    return o.scheme + '://' + o.netloc


def make_request(url: (str, Request), data: bytes=None, headers: dict={}, method: str=None) -> Request:
    if isinstance(url, str):
        headers = dict(headers)
        headers['User-Agent'] = random.choice(user_agents)
        url = Request(url, data=data, headers=headers, method=method)
    return url


def open_soup(url: (str, Request), data: bytes=None, headers: dict={}, method: str=None, encoding: str=None, parser: str='html.parser'):
    response = urlopen(make_request(url, data, headers, method))
    if not encoding:
        encoding = response.headers.get_charsets()[0]
    soup = bs4.BeautifulSoup(response, parser, from_encoding=encoding)
    soup.response = response
    return soup


def tag_for_class(soup, name, clazz):
    return soup.find(name, {'class': clazz})


def tags_for_class(soup, name, clazz):
    return soup.find_all(name, {'class': clazz})


__all__ = [
    "make_request", "open_soup", "tag_for_class", "tags_for_class", "host_of"
]

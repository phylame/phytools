# PBS for www.zhuishu.com
# by PW, <phylame@163.com>
# version: 2016-12-27
#

import datetime

import re
import yem
from phyhtml import *

ENCODING = "utf-8"


def fetch_attributes(book, url):
    soup = fetch_html(url, encoding=ENCODING)
    if soup is None:
        app_error('cannot open url: {0}', url)
        return
    book.genre = find_tag(soup, 'div', 'con_top').find_all('a')[-1].string
    info = soup.find('div', id='info')
    book.title = info.h1.string.strip()
    p = info.p
    book.author = p.string.split('：')[-1].strip()
    p = p.find_next('p')
    book.state = p.next.split('：')[-1][:-1]
    book.intro = yem.LINE_SEPARATOR.join(tuple(info.find_next('div', id='intro').stripped_strings)[:-1])
    book.cover = yem.Flob.for_url(info.find_next('div', id='fmimg').next['src'])
    return soup


def fetch_contents(book, soup):
    host = host_of(soup)
    for dd in soup.find_all('dd'):
        a = dd.next
        chapter = yem.Chapter(title=re.sub(r'\s[\d]{2}-[\d]{2}', '', a.string.strip()))
        chapter.text = yem.Text.for_html(host + a['href'], fetch_text, tag=chapter)
        book.append(chapter)


def fetch_text(url, chapter):
    try:
        print('fetching text:', chapter.title)
        soup = fetch_html(url, encoding=ENCODING)
        if soup is None:
            app_error('cannot open url: {0}', url)
            return ''
        return yem.LINE_SEPARATOR.join(soup.find('div', id='content').stripped_strings)
    except:
        return ''


if __name__ == "__main__":
    url = "http://www.mangg.com/id28111/"
    book = yem.Book()
    soup = fetch_attributes(book, url)
    fetch_contents(book, soup)
    args = {
        "pmab.text.encoding": "gb18030"
    }
    yem.make_book(book, r"E:\tmp", "pmab", **args)

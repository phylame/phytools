# PBS for 234zw.com
# by PW, <phylame@163.com>
# version: 2016-12-26
#

import yem
from phyhtml import *
from phymisc import *

ENCODING = 'GBK'


def fetch_attributes(book, url):
    soup = fetch_html(url, encoding=ENCODING)
    if soup is None:
        app_error('cannot open url: {0}', url)
        return
    host = host_of(soup)
    div = find_tag(soup, 'div', 'p_box')
    book.cover = yem.Flob.for_url(host + div.img['src'])
    div = find_tag(soup, 'div', 'j_box')
    book.title = div.h2.string.strip()
    info = find_tag(div, 'div', 'info')
    for li in info.find_all('li'):
        label = li.span.string
        if label == '作者：':
            book.author = li.a.string.strip()
        elif label == '类型：':
            book.genre = li.a.string.strip()
        elif label == '总字数：':
            book.words = int(li.font.string.strip())
        elif label == '创作日期：':
            pass
        elif label == '状态：':
            book.state = li.span.next_sibling
    intro = find_tag(div, 'div', 'words')
    lines = [i.strip() for i in intro.p.text.splitlines()]
    book.intro = '\n'.join(lines)[3:]
    return soup


def fetch_contents(book, soup):
    host = host_of(soup)
    div = find_tag(soup, 'div', 'list_box')
    for a in div.find_all('a'):
        text = yem.Text.for_html(host + a['href'], fetch_text)
        book.append(yem.Chapter(text=text, title=a.string.strip()))


def fetch_text(url):
    try:
        soup = fetch_html(url, encoding=ENCODING)
        div = find_tag(soup, 'div', 'box_box')
        lines = []
        for tag in div:
            if tag.name is None:
                s = tag.string.strip()
                if len(s) != 0:
                    lines.append(s)
        lines.pop()
        return "\n".join(lines)
    except:
        return ""


if __name__ == '__main__':
    url = 'http://234zw.com/xingjiqiyuan/'
    book = yem.Book()
    soup = fetch_attributes(book, url)
    fetch_contents(book, soup)
    yem.make_book(book, r'E:\tmp')

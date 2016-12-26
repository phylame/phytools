import yem
from htmlail import *

ENCODING = 'GBK'


def fetch_attributes(book, url):
    soup = open_soup(url, encoding=ENCODING)
    host = host_of(soup)
    div = tag_for_class(soup, 'div', 'p_box')
    book.cover = yem.Flob.for_url(host + div.img['src'])
    div = tag_for_class(soup, 'div', 'j_box')
    book.title = div.h2.string.strip()
    info = tag_for_class(div, 'div', 'info')
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
    intro = tag_for_class(div, 'div', 'words')
    lines = [i.strip() for i in intro.p.text.splitlines()]
    book.intro = '\n'.join(lines)[3:]
    return soup


def fetch_contents(book, soup):
    host = host_of(soup)
    div = tag_for_class(soup, 'div', 'list_box')
    for a in div.find_all('a'):
        text = yem.Text.for_html(host + a['href'], fetch_content)
        book.append(yem.Chapter(text=text, title=a.string.strip()))


def fetch_content(url):
    try:
        soup = open_soup(url, encoding=ENCODING)
        div = tag_for_class(soup, 'div', 'box_box')
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
    url = 'http://234zw.com/yiyantongtian/'
    book = yem.Book()
    soup = fetch_attributes(book, url)
    fetch_contents(book, soup)
    yem.make_book(book, r'E:\tmp')

# PBS for www.zhuishu.com
# by PW, <phylame@163.com>
# version: 2016-4-25
#

import datetime

import yem
from phyhtml import *

encoding = "utf-8"
base_url = "http://www.zhuishu.com"
search_url = "http://www.zhuishu.com/SearchBook.aspx?keyword={0}&t={1}"
date_format = "%m/%d/%Y %I:%M:%S %p"
by_title = 1
by_author = 2


def search_books(keyword, category=by_title):
    url = search_url.format(keyword, category)
    return parse_search_results(open_soup(url, encoding=encoding))


def parse_search_results(soup):
    books = tuple(map(parse_book_item, tags_for_class(soup, "div", "book_news_style_form")))
    div = soup.find('div', attrs={"id": "UC_TopUpdate1_pnlPage"})
    fy = tag_for_class(div, "div", "fanyetxt")
    totals = div.find("b").text
    size = int(fy.text.split("：")[-1].split("/")[-1]) + 1
    pages = [soup.response.url.replace("SearchBook", "SearchBook_{0}".format(i)) for i in range(1, size)]
    return totals, pages, books


def parse_book_item(soup):
    cover = base_url + soup.find("img")["src"]
    a = soup.find("h1").find("a")
    title = conv_text(a.text)
    url = base_url + a["href"]
    author = pubdate = None
    for i, x in enumerate(soup.find("h2")):
        if i == 1:
            author = conv_text(x.text)
        elif i == 2:
            pubdate = conv_text(x)
    updates = []
    intro = None
    for i, x in enumerate(soup.find("h3")):
        if x.name == "a":
            updates.append((conv_text(x.text), base_url + x["href"]))
        elif x.name is None:
            intro = conv_text(x)
    return dict(url=url, title=title, author=author, cover=cover, pubdate=pubdate, updates=updates, intro=intro)


def fetch_attributes(book, soup):
    div = tag_for_class(soup, "div", "book_news")
    div_attr = tag_for_class(div, "div", "book_news_style")
    cover = base_url + div_attr.find("img")["src"]
    d = tag_for_class(div_attr, "div", "book_news_style_text2")
    title = d.find("h1").text
    parts = conv_text(d.find("h2").text).split("   ")
    author = parts[0].split("：")[-1]
    pubdate = parts[1].split("：")[-1]
    genre = parts[2].split("：")[-1]
    state = parts[3].split("：")[-1]
    updates = [(conv_text(a.text), base_url + a["href"]) for a in d.find("h3").find_all("a")]
    intro = "\n".join(conv_text(p.text) for p in tag_for_class(div_attr, "div", "msgarea").find_all("p"))
    book.title = title
    book.author = author
    book.cover = yem.File.for_url(cover)
    book.genre = genre
    book.state = state
    book.pubdate = datetime.datetime.strptime(pubdate, date_format)
    book.intro = yem.Text.for_string(intro)
    book.updates = updates


def fetch_contents(book, soup):
    for div in tags_for_class(soup, "div", "book_article_texttable"):
        parse_section(book, div)


def parse_section(book, soup):
    title = tag_for_class(soup, "div", "book_article_texttitle").text
    section = yem.Chapter(title=title)
    for a in soup.find_all("a"):
        section.append(yem.Chapter(yem.Text.for_html(base_url + a["href"], fetch_text), title=a.text))
    book.append(section)


def fetch_text(url):
    print(url)
    soup = open_soup(url, encoding=encoding)
    div = soup.find('div', attrs={"id": "booktext"})
    lines = [conv_text(x.string) for x in div if x.name is None]
    return yem.LINE_SEPARATOR.join(lines)


book = yem.Book()
soup = open_soup("http://www.zhuishu.com/id17271/", encoding=encoding)
fetch_attributes(book, soup)
fetch_contents(book, soup)
yem.make_book(book, r"D:\tmp", "pmab")

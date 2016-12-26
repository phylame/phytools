# PBS for k.sogou.com
# by PW, <phylame@163.com>
# version: 2016-4-25
#

import datetime

import yem
from phyhtml1 import *

encoding = "utf-8"
base_url = "http://k.sogou.com/"
search_url = "http://k.sogou.com/search?keyword={0}&v=5&gf=e-d-pidx-album&uID=8l9943vf7jR2mvZU&sgid=0"


def search_books(keyword):
    url = search_url.format(keyword)
    return parse_search_results(fetch_html(url, encoding=encoding))


def parse_search_results(soup):
    sections = soup.find_all("section")
    books = []
    if len(sections) == 2:
        books.append(parse_book_item(sections[0]))
    ul = tag_of_class(sections[-1], "ul", "booklst")
    for li in ul.find_all("li"):
        b = parse_book_item(li)
        if b:
            books.append(b)
    return books


def parse_book_item(soup):
    a = tag_of_class(soup, "a", "booklst-tab vertical-wrap")
    if not a:
        return
    url = base_url + a["href"]
    cover = a.find("img")["data-original"].replace("w/76?", "w/360?")
    title = conv_text(tag_of_class(a, "div", "booklst-tit").text)
    spans = tag_of_class(a, "div", "booklst-txt").find_all("span")
    author = spans[0].text
    genre = spans[1].text
    state = spans[2].text
    intro = conv_text(tag_of_class(a, "p", "booklst-gap").text)
    keywords = []
    for li in tag_of_class(a, "ul", "booklst-sort").find_all("li"):
        keywords.append(conv_text(li.text))
    updates = [conv_text(tag_of_class(soup, "a", "update-wrap").text.replace("\n", " "))]
    return dict(url=url, title=title, author=author, cover=cover, genre=genre, state=state, keywords=keywords,
                intro=intro, updates=updates)


def fetch_attributes(book, soup):
    div = tag_of_class(soup, "div", "book-detail-wrap")
    book.title = div.find("h2").text
    book.cover = yem.File.for_url(div.find("img")["data-original"].replace("w/97?", "w/360?"))
    for x in div.find("p"):
        if x.name is None:
            book.genre, book.author = x.split("/")
        else:
            book.state, y = x.text.strip().split("\n")[0].split("（")
            book.pubdate = datetime.datetime.strptime(y.rstrip("）"), "%Y-%m-%d")
    book.keywords = [a.text for a in tag_of_class(div, "div", "book-detail-sort").find_all("a")]
    p = tag_of_class(soup, "p", "book-read-info")
    book.intro = yem.Text.for_string(p["onclick"].lstrip("showMoreDesc('").rstrip("')"))


def fetch_contents(book, soup):
    pass


if __name__ == "__main__":
    soup = fetch_html(search_books("超品透视")[0]["url"], encoding=encoding)
    book = yem.Book()
    fetch_attributes(book, soup)
    fetch_contents(book, soup)
    print(book)

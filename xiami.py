import math
import traceback

import phyhtml
import psm

HOST_URL = 'http://www.xiami.com'
ENCODING = 'utf-8'
SEARCH_ALBUM_URL = 'http://www.xiami.com/search/album?key={0}'
SEARCH_ALBUM_URL_PAGED = 'http://www.xiami.com/search/album/page/{0}?key={1}&category=-1'
SEARCH_SONG_URL = 'http://www.xiami.com/search/artist?key={0}'
SEARCH_SONG_URL_PAGED = 'http://www.xiami.com/search/artist/page/{0}?key={1}&category=-1'
SEARCH_ARTIST_URL = 'http://www.xiami.com/search/artist/?key={0}'
SEARCH_ARTIST_URL_PAGED = 'http://www.xiami.com/search/artist/page/{0}?key={1}&category=-1'


def fetch_soup(url):
    return phyhtml.fetch_html(url, encoding=ENCODING)


def left_partition(str, sep=' '):
    parts = str.partition(sep)
    return parts[0], parts[-1]


def right_partition(str, sep=' '):
    parts = str.rpartition(sep)
    return parts[0], parts[-1]


def escape_href(href, soup):
    return phyhtml.parse.unquote(href if href.startswith('http') else soup.url + href, encoding=ENCODING)


def parse_genre(url):
    soup = fetch_soup(url)
    name, engname = left_partition(phyhtml.tag_of_class(soup, 'h3', 'bigtext').text.strip())
    lines = []
    for soup in phyhtml.tag_of_class(soup, 'div', 'content fold'):
        if soup.name is None:
            lines.append(soup.strip())
        else:
            lines.append('<br/>')
    intro = '\n'.join(lines)
    return name, engname, intro


def parse_artist(url):
    soup = fetch_soup(url)
    name = alias = None
    for tag in soup.find('h1'):
        if tag.name is None:
            name = tag.strip()
        else:
            alias = tag.text.strip().strip('“”"')
    location = profile = label = None
    genres = []
    for tag in soup.find('div', {'id': 'artist_info'}).find_all('td'):
        if label is not None:
            if label == '地区：':
                location = right_partition(tag.text.strip())
            elif label == '风格：':
                for a in tag.find_all('a'):
                    genres.append((left_partition(a.text.strip()), escape_href(a['href'], soup)))
            elif label == '档案：':
                a = phyhtml.tag_of_class(tag, 'a', 'more')
                if a:
                    profile = escape_href(a['href'], soup)
            label = None
        else:
            label = tag.text.strip()

    cover = soup.find('a', dict(id='cover_lightbox'))['href']
    intro = None
    if profile:
        soup = fetch_soup(profile)
        div = phyhtml.tag_of_class(soup, 'div', 'profile')
        lines = []
        if div:
            for tag in div.find_all('p'):
                lines.append(str(tag))
        else:
            for tag in soup.find('div', dict(id='artist-record')):
                if tag.name is None:
                    lines.append(tag.strip())
                elif tag.name == 'br':
                    lines.append('<br/>')
        intro = ''.join(lines)
    return name, alias, cover, location, genres, intro


def parse_song(url):
    soup = fetch_soup(url)
    title = alias = None
    for tag in soup.find('h1'):
        if tag.name is None:
            title = tag.strip()
        else:
            alias = tag.text.strip().strip('“”"')
    main = soup.find('div', dict(id='main'))
    label = album = lyricist = composer = arranger = None
    artists = []
    for tag in phyhtml.tag_of_class(main, 'div', 'album_relation').find_all('td'):
        text = tag.text.strip()
        if label is not None:
            if label == '所属专辑：':
                a = tag.find('a')
                album = (text, escape_href(a['href'], soup) if a else None)
            elif label == '作词：':
                lyricist = text
            elif label == '演唱者：':
                for a in tag.find_all('a'):
                    name = a.text.strip()
                    if name:
                        artists.append((name, escape_href(a['href'], soup)))
            elif label == '作曲：':
                composer = text
            elif label == '编曲：':
                arranger = text
            label = None
        else:
            label = text
    lines = []
    for tag in phyhtml.tag_of_class(main, 'div', 'lrc_main'):
        if tag.name is None:
            lines.append(tag.strip())
        else:
            lines.append('<br/>')
    lyric = ''.join(lines)
    return title, alias, album, artists, lyricist, composer, arranger, lyric


def parse_album(url):
    soup = fetch_soup(url)
    title = alias = None
    for tag in soup.find('h1'):
        if tag.name is None:
            title = tag.strip()
        else:
            alias = tag.text.strip().strip('“”"')
    main = soup.find('div', dict(id='main'))
    block = soup.find('div', dict(id='album_block'))
    label = language = publisher = pubdate = category = None
    artists = []
    genres = []
    for tag in block.find_all('td'):
        text = tag.text.strip()
        if label is not None:
            if label == '艺人：':
                for a in tag.find_all('a'):
                    artists.append((a.text.strip(), escape_href(a['href'], soup)))
            elif label == '语种：':
                language = text
            elif label == '唱片公司：':
                publisher = text
            elif label == '发行时间：':
                pubdate = text.replace('年', '-').replace('月', '-').replace('日', '')
            elif label == '专辑类别：':
                category = text
            elif label == '专辑风格：':
                for a in tag.find_all('a'):
                    genres.append((left_partition(a.text.strip()), escape_href(a['href'], soup)))
            label = None
        else:
            label = text
    cover = block.find('a', dict(id='albumCover'))['href']
    intro = None
    span = main.find('span', dict(property='v:summary'))
    if span:
        lines = []
        for tag in span:
            lines.append(str(tag))
        intro = ''.join(lines)
    return title, alias, cover, artists, language, publisher, pubdate, category, genres, intro


def fetch_albums(url, func, filter=None):
    soup = fetch_soup(url)
    for tag in phyhtml.tag_of_class(soup, 'div', 'albumBlock_list').find_all('li'):
        if not filter or filter(tag):
            func(parse_album(phyhtml.tag_of_class(tag, 'p', 'cover').next['href']))


def search_album(key, func, page=None, size=30, filter=None):
    if page is not None:
        print("fetch album in page:", page)
        fetch_albums(SEARCH_ALBUM_URL_PAGED.format(page, key), func, filter)
    soup = fetch_soup(SEARCH_ALBUM_URL.format(key))
    total = int(phyhtml.tag_of_class(soup, 'p', 'seek_counts').next.next.text)
    count = int(math.ceil(total / size))
    print("found", total, 'albums in', count, 'pages')
    for page in range(1, count + 1):
        search_album(key, func, page, size, filter)


def fetch_artists(url, func, filter=None):
    soup = fetch_soup(url)
    for tag in phyhtml.tags_of_class(soup, 'p', 'buddy'):
        if not filter or filter(tag):
            func(parse_artist(tag.next['href']))


def search_artist(key, func, page=None, size=30, filter=None):
    if page is not None:
        return fetch_artists(SEARCH_SONG_URL_PAGED.format(page, key), func, filter)
    soup = fetch_soup(SEARCH_SONG_URL.format(key))
    total = int(phyhtml.tag_of_class(soup, 'p', 'seek_counts ok').next.next.text)
    for page in range(1, int(math.ceil(total / size)) + 1):
        search_artist(key, func, page, size, filter)


def fetch_genres(helper: psm.PSMHelper, offset: int = 0):
    soup = fetch_soup('http://www.xiami.com/genre')
    seq = tuple(zip(phyhtml.tags_of_class(soup, 'dt', 'fold'), phyhtml.tags_of_class(soup, 'dd', 'fold')))
    for dt, dd in seq[offset:] if offset > 0 else seq:
        group = parse_genre(soup.url + dt.find('a')['href'])
        for a in dd.find_all('a'):
            item = parse_genre(soup.url + a['href'])


def album_artist_filter(artist):
    def do_filter(li):
        a = phyhtml.tag_of_class(li, 'a', 'singer')
        if a:
            return a.text == artist

    return lambda li: do_filter(li)


def process_artist(artist, helper: psm.PSMHelper):
    name, alias, cover, location, genres, intro = artist
    if location:
        if location[0]:
            location = location[0]
        else:
            location = location[-1]
            if location == '中国':
                location = 'China'
    helper.begin()
    try:
        genre_ids = []
        for genre in genres:
            genre_id = helper.select_genre(genre[0][0])
            if genre_id is None:
                print("not found genre:", genre[0][0])
                genre = parse_genre(genre[1])
                print("fetch genre:", genre)
                genre_ids.append(helper.insert_genre(genre[0], engname=genre[1], intro=genre[2]))
            else:
                genre_ids.append(genre_id)
        helper.insert_singer(name, alias=alias, photo=cover, location=location, intro=intro, genres=genre_ids)
        print("inserted singer:", name)
        helper.commit()
    except:
        traceback.print_exc()
        helper.rollback()


if __name__ == '__main__':
    with psm.PSMHelper.opendb() as helper:
        search_artist('古风', lambda album: process_artist(album, helper))

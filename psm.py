import traceback

import pymysql
from pymysql.cursors import Cursor


class PSMHelper:
    def __init__(self, cursor: Cursor):
        self.cursor = cursor

    @staticmethod
    def opendb(host="localhost", port=3306, user="root", password="123456", db="psm", charset="utf8"):
        return PSMHelper(
            pymysql.connect(host=host, port=port, user=user, passwd=password, db=db, charset=charset).cursor())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def begin(self):
        self.cursor.connection.begin()

    def commit(self):
        self.cursor.connection.commit()

    def rollback(self):
        self.cursor.connection.rollback()

    def close(self):
        conn = self.cursor.connection
        self.cursor.close()
        conn.close()

    def execute(self, sql: str, *args) -> int:
        return self.cursor.execute(sql, args)

    def select_id(self, table, value):
        self.execute('select id from {0} where deleted=0 and name=%s'.format(table), value)
        if self.cursor.rowcount > 0:
            return self.cursor.fetchone()[0]
        return None

    def select_insert(self, table, fields, values) -> int:
        id = self.select_id(table, values['name'])
        if id is not None:
            return id
        args = tuple(values[field] for field in fields)
        self.cursor.execute(
            'insert into {0}({1}) values({2})'.format(table, ','.join(fields), '%s,' * (len(fields) - 1) + '%s'), args)
        return self.cursor.lastrowid

    def insert_links(self, table, fields, id, links, seq_name, item_name):
        self.begin()
        try:
            for link in links:
                if not isinstance(link, int):
                    raise ValueError('{0} require sequence of {1} id'.format(seq_name, item_name))
                self.execute('insert into {0}({1}) values(%s, %s)'.format(table, ','.join(fields)), id, link)
            self.commit()
        except:
            traceback.print_exc()
            self.rollback()

    def select_tag(self, name):
        return self.select_id('tag', name)

    def insert_tag(self, name, engname=None, intro=None) -> int:
        return self.select_insert('tag', ('name', 'engname', 'intro'), locals())

    def select_genre(self, name):
        return self.select_id('genre', name)

    def insert_genre(self, name, engname=None, top_id=None, intro=None) -> int:
        return self.select_insert('genre', ('name', 'engname', 'top_id', 'intro'), locals())

    def insert_person(self, name, alias=None, engname=None, photo=None, location=None, group_id=None,
                      intro=None) -> int:
        return self.select_insert('person', ('name', 'alias', 'engname', 'photo', 'location', 'group_id', 'intro'),
                                  locals())

    def select_artist(self, type, name):
        if type == 'G':
            self.execute("""select id
            from artist t1
            left join group t2 on t2.deleted=0 and t2.id=t1.group_id and t2.name=%s
            where t1.deleted=0 and t1.type='G'""", name)
            return self.cursor.fetchone()[0] if self.cursor.rowcount > 0 else None
        else:
            self.execute("""select id
            from artist t1
            left join person t2 on t2.deleted=0 and t2.id=t1.person_id and t2.name=%s
            where t1.deleted=0 and t1.type=%s""", name, type)

    def insert_artist(self, type: str, person_id: int = None, group_id: int = None):
        if type == 'G':
            if group_id is None:
                raise ValueError('type "S" must specify group_id')
            self.execute("select id from artist where deleted=0 and type='S' and group_id=%s", group_id)
            if self.cursor.rowcount > 0:
                return self.cursor.fetchone()[0]
            else:
                self.execute("insert into artist(type, group_id) values('S', %s)", group_id)
                return self.cursor.lastrowid
        elif person_id is None:
            raise ValueError('person_id is None')
        self.execute("select id from artist where deleted=0 and type=%s and person_id=%s", type, group_id)
        if self.cursor.rowcount > 0:
            return self.cursor.fetchone()[0]
        else:
            self.execute("insert into artist(type, person_id) values(%s, %s)", type, person_id)
            return self.cursor.lastrowid

    def insert_participator(self, name, type, alias=None, engname=None, photo=None, location=None, group_id=None,
                            intro=None, tags=(), genres=()) -> int:
        artist_id = self.insert_artist(type, self.insert_person(name, alias, engname, photo, location, group_id, intro))
        self.insert_links('artist_tag', ('artist_id', 'tag_id'), artist_id, tags, 'tags', 'tag')
        self.insert_links('artist_genre', ('artist_id', 'genre_id'), artist_id, genres, 'genres', 'genre')
        return artist_id

    def insert_singer(self, name, alias=None, engname=None, photo=None, location=None, group_id=None, intro=None,
                      tags=(), genres=()) -> int:
        return self.insert_participator(name, 'S', alias, engname, photo, location, group_id, intro, tags, genres)

    def insert_composer(self, name, alias=None, engname=None, photo=None, location=None, group_id=None, intro=None,
                        tags=(), genres=()) -> int:
        return self.insert_participator(name, 'C', alias, engname, photo, location, group_id, intro, tags, genres)

    def insert_lyricist(self, name, alias=None, engname=None, photo=None, location=None, group_id=None, intro=None,
                        tags=(), genres=()) -> int:
        return self.insert_participator(name, 'L', alias, engname, photo, location, group_id, intro, tags, genres)

    def insert_arranger(self, name, alias=None, engname=None, photo=None, location=None, group_id=None, intro=None,
                        tags=(), genres=()) -> int:
        return self.insert_participator(name, 'A', alias, engname, photo, location, group_id, intro, tags, genres)

    def insert_group(self, name, engname=None, photo=None, type=None, intro=None, tags=(), genres=()) -> int:
        artist_id = self.insert_artist('G', self.select_insert('group', ('name', 'engname', 'photo', 'type', 'intro'),
                                                               locals()))
        self.insert_links('artist_tag', ('artist_id', 'tag_id'), artist_id, tags, 'tags', 'tag')
        self.insert_links('artist_genre', ('artist_id', 'genre_id'), artist_id, genres, 'genres', 'genre')
        return artist_id

    def select_album(self, name):
        return self.select_id('album', name)

    def insert_album(self, name, alias=None, engname=None, cover=None, language=None, pubdate=None, publisher=None,
                     category=None, intro=None, artists=(), tags=(), genres=()) -> int:
        album_id = self.select_insert('album', ('name', 'alias', 'engname', 'cover', 'language', 'pubdate', 'publisher',
                                                'category', 'intro'), locals())
        self.insert_links('album_artist', ('album_id', 'artist_id'), album_id, artists, 'artists', 'artist')
        self.insert_links('album_tag', ('album_id', 'tag_id'), album_id, tags, 'tags', 'tag')
        self.insert_links('album_genre', ('album_id', 'genre_id'), album_id, genres, 'genres', 'genre')

    def select_song(self, name):
        return self.select_id('song', name)

    def insert_song(self, name, alias=None, engname=None, cover=None, album_id=None, track=None, disc=None, media=None,
                    pubdate=None, publisher=None, lyric=None, intro=None, artists=(), composers=(), lyricists=(),
                    arrangers=(), tags=(), genres=()) -> int:
        song_id = self.select_insert('song', (
            'name', 'alias', 'engname', 'cover', 'album_id', 'track', 'disc', 'media', 'language', 'pubdate',
            'publisher',
            'category', 'lyric', 'intro'), locals())
        self.insert_links('song_artist', ('song_id', 'artist_id'), song_id, artists, 'artists', 'artist')
        self.insert_links('song_tag', ('song_id', 'tag_id'), song_id, tags, 'tags', 'tag')
        self.insert_links('song_genre', ('song_id', 'genre_id'), song_id, genres, 'genres', 'genre')
        self.insert_links('song_composer', ('song_id', 'composer_id'), song_id, composers, 'composers', 'composer')
        self.insert_links('song_arranger', ('song_id', 'arranger_id'), song_id, arrangers, 'arrangers', 'arranger')
        self.insert_links('song_lyricist', ('song_id', 'lyricist_id'), song_id, lyricists, 'lyricists', 'lyricist')

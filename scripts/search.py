from psycopg2 import sql
from scripts.helpers import open_postgres_connection, close_postgres_connection

def top(page, app):
    query = """SELECT p.post_id, p.title, p.url, p.published, p.username, p.approver, COALESCE(SUM(v.vote), 0) AS score,
            p.tag_all, p.tag_emk, p.tag_gpk, p.tag_epk, p.tag_vbk, p.tag_vik, p.tag_kjk, p.tag_ttk, p.tag_gtk
            FROM posts p
            LEFT JOIN votes v ON p.post_id = v.post_id
            WHERE approved IS true
            GROUP BY p.post_id
            ORDER BY score
            LIMIT 10 OFFSET (%s - 1) * 10;"""
    return to_json(search(query, (page,), app))

def fresh(page, app):
    query = """SELECT p.post_id, p.title, p.url, p.published, p.username, p.approver, COALESCE(SUM(v.vote), 0) AS score,
            p.tag_all, p.tag_emk, p.tag_gpk, p.tag_epk, p.tag_vbk, p.tag_vik, p.tag_kjk, p.tag_ttk, p.tag_gtk
            FROM posts p
            LEFT JOIN votes v ON p.post_id = v.post_id
            WHERE approved IS true
            GROUP BY p.post_id
            ORDER BY published
            LIMIT 10 OFFSET (%s - 1) * 10;"""
    return to_json(search(query, (page,), app))

def trash(page, app):
    query = """SELECT p.post_id, p.title, p.url, p.published, p.username, p.approver, COALESCE(SUM(v.vote), 0) AS score,
            p.tag_all, p.tag_emk, p.tag_gpk, p.tag_epk, p.tag_vbk, p.tag_vik, p.tag_kjk, p.tag_ttk, p.tag_gtk
            FROM posts p
            LEFT JOIN votes v ON p.post_id = v.post_id
            WHERE approved IS true
            GROUP BY p.post_id
            HAVING COALESCE(SUM(v.vote), 0) BETWEEN -30 AND -1
            ORDER BY published
            LIMIT 10 OFFSET (%s - 1) * 10;"""
    return to_json(search(query, (page,), app))

def random(page, app):
    query = """SELECT p.post_id, p.title, p.url, p.published, p.username, p.approver, COALESCE(SUM(v.vote), 0) AS score,
            p.tag_all, p.tag_emk, p.tag_gpk, p.tag_epk, p.tag_vbk, p.tag_vik, p.tag_kjk, p.tag_ttk, p.tag_gtk
            FROM posts p TABLESAMPLE SYSTEM_ROWS(10)
            LEFT JOIN votes v ON p.post_id = v.post_id
            WHERE approved IS true
            GROUP BY p.post_id
            ORDER BY random();"""
    return to_json(search(query, (page,), app))

def approve(page, app):
    query = """SELECT p.post_id, p.title, p.url, p.published, p.username, p.approver, 0 AS score,
            p.tag_all, p.tag_emk, p.tag_gpk, p.tag_epk, p.tag_vbk, p.tag_vik, p.tag_kjk, p.tag_ttk, p.tag_gtk
            FROM posts p
            WHERE approved IS NULL
            GROUP BY p.post_id
            ORDER BY published ASC
            LIMIT 10 OFFSET (%s - 1) * 10;"""
    return to_json(search(query, (page,), app))

def posts_by_user(user, page, app):
    query = """SELECT p.post_id, p.title, p.url, p.published, p.username, p.approver, COALESCE(SUM(v.vote), 0) AS score,
            p.tag_all, p.tag_emk, p.tag_gpk, p.tag_epk, p.tag_vbk, p.tag_vik, p.tag_kjk, p.tag_ttk, p.tag_gtk
            FROM posts p
            LEFT JOIN votes v ON p.post_id = v.post_id
            WHERE p.username=%s AND approved IS true
            GROUP BY p.post_id
            ORDER BY published
            LIMIT 10 OFFSET (%s - 1) * 10;"""
    return to_json(search(query, (user, page,), app))

def posts_by_title(title, page, app):
    if 50<len(title):
        return {'message': 'Search string too long'}, 400
    query = """SELECT p.post_id, p.title, p.url, p.published, p.username, p.approver, COALESCE(SUM(v.vote), 0) AS score,
            p.tag_all, p.tag_emk, p.tag_gpk, p.tag_epk, p.tag_vbk, p.tag_vik, p.tag_kjk, p.tag_ttk, p.tag_gtk
            FROM posts p
            LEFT JOIN votes v ON p.post_id = v.post_id
            WHERE p.title ILIKE %s
            GROUP BY p.post_id
            ORDER BY published
            LIMIT 10 OFFSET (%s - 1) * 10;"""
    return to_json(search(query, ('%'+title+'%', page,), app))

def posts_by_tag(tag, page, app):
    query = """SELECT p.post_id, p.title, p.url, p.published, p.username, p.approver, COALESCE(SUM(v.vote), 0) AS score,
            p.tag_all, p.tag_emk, p.tag_gpk, p.tag_epk, p.tag_vbk, p.tag_vik, p.tag_kjk, p.tag_ttk, p.tag_gtk
            FROM posts p
            LEFT JOIN votes v ON p.post_id = v.post_id
            WHERE {tag_column} IS true AND approved IS true
            GROUP BY p.post_id
            ORDER BY published
            LIMIT 10 OFFSET (%s - 1) * 10;"""
    query = sql.SQL(query).format(tag_column=sql.Identifier(tag))
    return to_json(search(query, (page,), app))

def search(query, values, app):
    try:
        connection, cursor = open_postgres_connection(app)

        cursor.execute(query, values)
        memes = cursor.fetchall()

        return memes
    except Exception as e:
        app.logger.debug(e)
        return
    finally:
        close_postgres_connection(connection, cursor, app)

def to_json(list):
    all_tags = ('tag_all', 'tag_emk', 'tag_gpk', 'tag_epk', 'tag_vbk', 'tag_vik', 'tag_kjk', 'tag_ttk', 'tag_gtk')
    out = []
    if list:
        for i in list:
            obj = {}
            obj['postid']    = i[0]
            obj['title']     = i[1]
            obj['url']       = i[2]
            obj['published'] = i[3]
            obj['username']  = i[4]
            obj['approver']  = i[5]
            obj['score']     = i[6]
            tags = []
            for k in range(len(all_tags)):
                if i[7+k]:
                    tags.append(all_tags[k])
            obj['tags']      = tags
            out.insert(0, obj)
    return out
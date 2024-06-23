import psycopg2
from psycopg2.extensions import quote_ident
from .globals import get_connection

def top(page, app):
    sql = """SELECT p, SUM(v.vote) AS Score
            FROM posts p
            JOIN votes v ON p.PostID = v.PostID
            GROUP BY p.PostID
            ORDER BY Score
            LIMIT 10 OFFSET (%s - 1) * 10;"""
    return search(sql, (page,), app)

def fresh(page, app):
    sql = """SELECT p, SUM(v.vote) AS Score
            FROM posts p
            JOIN votes v ON p.PostID = v.PostID
            GROUP BY p.PostID
            ORDER BY Published
            LIMIT 10 OFFSET (%s - 1) * 10;"""
    return search(sql, (page,), app)

def posts_by_user(user, page, app):
    sql = """SELECT p, SUM(v.vote) AS Score
            FROM posts p
            JOIN votes v ON p.PostID = v.PostID
            GROUP BY p.PostID
            ORDER BY Published
            LIMIT 10 OFFSET (%s - 1) * 10
            WHERE UserName=%s;"""
    return search(sql, (page, user,), app)

def search(sql, values, app):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        app.logger.debug("DB connection opened")

        cursor.execute(sql, values)
        memes = cursor.fetchall()

        return memes, 200
    except Exception as e:
        app.logger.debug(e)
        return 'No matching posts found', 404
    finally:
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")
    return 'Internal server error', 500
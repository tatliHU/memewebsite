import time
from scripts.helpers import open_postgres_connection, close_postgres_connection

def comment(post_id, text, username, app):
    try:
        connection, cursor = open_postgres_connection(app)
        insert_sql = "INSERT INTO comments (post_id, username, text, created) VALUES (%s, %s, %s, %s);"
        cursor.execute(insert_sql, (post_id, username, text, int(round(time.time())),))
        connection.commit()
        return {'message': 'Comment sent'}, 201
    except Exception as e:
        app.logger.debug(e)
    finally:
        close_postgres_connection(connection, cursor, app)
    return {'message': 'Internal server error'}, 500

def get_comments(post_id, app):
    try:
        connection, cursor = open_postgres_connection(app)
        get_sql = "SELECT username, text, created FROM comments WHERE post_id=%s ORDER BY created LIMIT 100;"
        cursor.execute(get_sql, (post_id,))
        comments = cursor.fetchall()
        return to_json(comments), 200
    except Exception as e:
        app.logger.debug(e)
    finally:
        close_postgres_connection(connection, cursor, app)
    return {'message': 'Internal server error'}, 500

def to_json(list):
    out = []
    if list:
        for i in list:
            obj = {}
            obj['username']  = i[0]
            obj['text']      = i[1]
            obj['created']   = i[2]
            out.append(obj)
    return out
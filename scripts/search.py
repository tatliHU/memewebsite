import psycopg2
from psycopg2.extensions import quote_ident
from .globals import get_connection

def search(order_by, page, app):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        app.logger.debug("DB connection opened")

        # Only sanitize user provided imput
        get_user_sql = "SELECT * FROM posts ORDER BY " + order_by + " LIMIT 10 OFFSET (%s - 1) * 10;"
        cursor.execute(get_user_sql, (page,))
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
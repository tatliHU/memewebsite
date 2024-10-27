import psycopg2
import bcrypt

def match_password(username, password, app):
    try:
        connection = psycopg2.connect(
            dbname   = app.config['POSTGRES_DB'],
            user     = app.config['POSTGRES_USER'],
            password = app.config['POSTGRES_PASS'],
            host     = app.config['POSTGRES_HOST'],
            port     = app.config['POSTGRES_PORT']
        )
        cursor = connection.cursor()
        app.logger.debug("DB connection opened")

        app.logger.debug("Retrieving password")
        get_user_sql = "SELECT password FROM users WHERE username=%s;"
        cursor.execute(get_user_sql, (username,))
        result = cursor.fetchone()
        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            return True
        else:
            return False
    except Exception as e:
        app.logger.debug(e)
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")
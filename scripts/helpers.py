import psycopg2

def get_password(username, app):
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
        password = cursor.fetchone()
        if password:
            return password[0]
        else:
            raise LookupError()
    except Exception as e:
        app.logger.debug(e)
        raise LookupError()
    finally:
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")
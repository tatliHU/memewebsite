import psycopg2
from .globals import get_connection

def register(username, password, app):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        app.logger.debug("DB connection opened")
        
        app.logger.debug("Checking if user exists")
        get_user_sql = "SELECT UserName FROM users WHERE UserName=%s;"
        cursor.execute(get_user_sql, (username,))
        user = cursor.fetchone()
        if user:
            return 'User already exists', 400
        
        app.logger.debug("Creating user")
        create_user_sql = '''
            INSERT INTO users (UserName, Password, EmailVerified, Score)
            VALUES (%s, %s, FALSE, 0);
        '''
        cursor.execute(create_user_sql, (username, password,))
        connection.commit()
        return 'Created', 201

    except Exception as e:
        app.logger.debug(e)
    finally:
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")
    return 'Internal server error', 500

import psycopg2
from .globals import get_connection

def change_password(username, password, app):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        app.logger.debug("DB connection opened")
        
        app.logger.debug("Changing password")
        password_change_sql = "UPDATE users SET Password=%s WHERE UserName=%s;"
        cursor.execute(password_change_sql, (password, username,))
        connection.commit()

        return 'Password updated', 200

    except Exception as e:
        app.logger.debug(e)
    finally:
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")
    return 'Internal server error', 500
import base64
import psycopg2
import flask
from .globals import get_connection

def login(authorization, app):
    try:
        base64_string = authorization.split()[1]
        decoded = base64.b64decode(base64_string).decode('utf-8')
        parts = decoded.split(":")
        username, password = parts[0], parts[1]
    except Exception as e:
        return 'Unauthorized', 401
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        app.logger.debug("DB connection opened")
        
        app.logger.debug("Authorizing")
        if get_password(username, app)==password:
            flask.session['username'] = username
            return {'message': 'Welcome '+username}, 200
        else:
            return 'Unauthorized', 401
    except LookupError:
        return 'User does not exist', 400
    except Exception as e:
        app.logger.debug(e)
    finally:
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")
    return 'Internal server error', 500

def get_password(username, app):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        app.logger.debug("DB connection opened")

        app.logger.debug("Retrieving password")
        get_user_sql = "SELECT Password FROM users WHERE UserName=%s;"
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

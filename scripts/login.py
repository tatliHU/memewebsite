import base64
import psycopg2
import flask
from scripts.helpers import match_password

def login(authorization, app):
    try:
        base64_string = authorization.split()[1]
        decoded = base64.b64decode(base64_string).decode('utf-8')
        parts = decoded.split(":")
        username, password = parts[0], parts[1]
    except Exception as e:
        return {'message': 'Unauthorized'}, 401
    
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
        
        app.logger.debug("Authorizing")
        if match_password(username, password, app):
            flask.session['username'] = username
            return '', 200
        else:
            return {'message': 'Invalid username or password'}, 401
    except Exception as e:
        app.logger.debug(e)
    finally:
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")
    return {'message': 'Internal server error'}, 500

import base64
import flask
from scripts.helpers import match_password, open_postgres_connection, close_postgres_connection

def login(authorization, app):
    try:
        base64_string = authorization.split()[1]
        decoded = base64.b64decode(base64_string).decode('utf-8')
        parts = decoded.split(":")
        username, password = parts[0], parts[1]
    except Exception as e:
        return {'message': 'Unauthorized'}, 401
    
    try:
        connection, cursor = open_postgres_connection(app)
        
        app.logger.debug("Authorizing")
        if match_password(username, password, app):
            flask.session['username'] = username
            return '', 200
        else:
            return {'message': 'Invalid username or password'}, 401
    except Exception as e:
        app.logger.debug(e)
    finally:
        close_postgres_connection(connection, cursor, app)
    return {'message': 'Internal server error'}, 500

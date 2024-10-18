import base64
import psycopg2
import flask
import hashlib

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
        password_hash = hashlib.md5((password+app.config['SALT']).encode()).hexdigest()
        if get_password(username, app)==password_hash:
            flask.session['username'] = username
            return '', 200
        else:
            return {'message': 'Unauthorized'}, 401
    except LookupError:
        return {'message': 'User does not exist'}, 400
    except Exception as e:
        app.logger.debug(e)
    finally:
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")
    return {'message': 'Internal server error'}, 500

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

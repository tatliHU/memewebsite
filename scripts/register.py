import psycopg2
from uuid import uuid4
import time
from .globals import get_connection

def register(username, password, email, app):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        app.logger.debug("DB connection opened")
        
        app.logger.debug("Checking if user exists")
        get_user_sql = "SELECT UserName FROM users WHERE UserName=%s;"
        cursor.execute(get_user_sql, (username,))
        user = cursor.fetchone()
        if user:
            app.logger.debug("User found")
            return 'User already exists', 400
        
        app.logger.debug("Deleting old registration if exists")
        delete_registration_sql = "DELETE FROM pending_registrations WHERE Email=%s;"
        cursor.execute(delete_registration_sql, (email,))
        
        uuid = uuid4().hex
        app.logger.debug("UUID for email verification is " + uuid)
        create_registration_sql = '''
            INSERT INTO pending_registrations (UserName, Password, Email, UUID, Created)
            VALUES (%s, %s, %s, %s, %s);
        '''
        cursor.execute(create_registration_sql, (username, password, email, uuid, int(round(time.time())),))

        connection.commit()
        
        app.logger.debug("Sending email for verification")
        send_email(email, uuid, app)
        return 'Created', 201

    except Exception as e:
        app.logger.debug(e)
    finally:
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")
    return 'Internal server error', 500

def verify(uuid, app):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        app.logger.debug("DB connection opened")
        
        app.logger.debug("Getting registration")
        get_user_sql = "SELECT username, password, email FROM pending_registrations WHERE UUID=%s;"
        cursor.execute(get_user_sql, (uuid,))
        user = cursor.fetchone()
        if not user:
            return 'Registration does not exist', 404
        
        app.logger.debug("Deleting registration")
        delete_registration_sql = "DELETE FROM pending_registrations WHERE UUID=%s;"
        cursor.execute(delete_registration_sql, (uuid,))

        app.logger.debug("Creating user")
        create_user_sql = "INSERT INTO users (UserName, Password, Email) VALUES (%s, %s, %s);"
        cursor.execute(create_user_sql, (user[0], user[1], user[2],))

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

def send_email(email, uuid, app):
    app.logger.debug(email+" with "+uuid)
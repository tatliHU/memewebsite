from uuid import uuid4
import bcrypt
import time
from marshmallow import Schema, fields, validate, ValidationError
from scripts.helpers import match_password, send_email, open_postgres_connection, close_postgres_connection

class UserSchema(Schema):
    password = fields.Str(required=True, validate=validate.Length(min=4, max=32), error_messages={'required': 'Password is required', 'invalid': 'Password is invalid'})
    username = fields.Str(required=True, validate=validate.Length(min=3, max=25), error_messages={'required': 'Username is required', 'invalid': 'Username is invalid'})

def change_password(username, currentPassword, newPassword, app):
    try:
        if match_password(username, currentPassword, app) == False:
            return {'message': 'Current password is invalid'}, 400
    except LookupError:
        app.logger.debug("User does not exist")
    try:
        UserSchema().load({"username": username, "password": newPassword})
    except ValidationError as err:
        return err.messages, 400
    try:
        connection, cursor = open_postgres_connection(app)
        
        app.logger.debug("Changing password")
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(newPassword.encode('utf-8'), salt).decode('utf8')
        password_change_sql = "UPDATE users SET password=%s WHERE username=%s;"
        cursor.execute(password_change_sql, (password_hash, username,))
        connection.commit()

        return {'message': 'Password updated'}, 200

    except Exception as e:
        app.logger.debug(e)
    finally:
        close_postgres_connection(connection, cursor, app)
    return {'message': 'Internal server error'}, 500

def forgot_password(email, app):
    try:
        connection, cursor = open_postgres_connection(app)
        
        get_username_sql = "SELECT username FROM users WHERE email=%s;"
        cursor.execute(get_username_sql, (email,))
        username = cursor.fetchone()
        if username:
            app.logger.debug("Creating password change request")
            uuid = uuid4().hex
            forgot_password_sql = '''
                DELETE FROM pending_passwords WHERE email=%s;
                INSERT INTO pending_passwords (username, email, uuid, created)
                VALUES (%s, %s, %s, %s);
            '''
            cursor.execute(forgot_password_sql, (email, username, email, uuid, int(round(time.time())),))
            connection.commit()
            success = send_email(
                email,
                'files/forgot_password_email.html',
                'Password reset',
                f"/api/forgot-password/{uuid}",
                app)
            if success:
                return {'message': 'Email sent'}, 200
        return {'message': 'No user found with this email'}, 404

    except Exception as e:
        app.logger.debug(e)
    finally:
        close_postgres_connection(connection, cursor, app)
    return {'message': 'Internal server error'}, 500

def reset_password(uuid, app):
    try:
        connection, cursor = open_postgres_connection(app)
        
        get_username_sql = "SELECT username FROM pending_passwords WHERE uuid=%s;"
        cursor.execute(get_username_sql, (uuid,))
        username = cursor.fetchone()
        if username:
            app.logger.debug(f"Resetting password for user {username}")
            newPassword = uuid4().hex[:32]
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(newPassword.encode('utf-8'), salt).decode('utf8')
            password_change_sql = "UPDATE users SET password=%s WHERE username=%s;"
            cursor.execute(password_change_sql, (password_hash, username,))
            cleanup_sql = "DELETE FROM pending_passwords WHERE username=%s;"
            cursor.execute(cleanup_sql, (username,))
            connection.commit()

            return {'message': f"Your new password is {newPassword}"}, 200
        return {'message': 'Link expired'}, 404

    except Exception as e:
        app.logger.debug(e)
    finally:
        close_postgres_connection(connection, cursor, app)
    return {'message': 'Internal server error'}, 500
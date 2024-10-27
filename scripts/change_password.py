import psycopg2
import bcrypt
from marshmallow import Schema, fields, validate, ValidationError
from scripts.helpers import match_password

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
        connection = psycopg2.connect(
            dbname   = app.config['POSTGRES_DB'],
            user     = app.config['POSTGRES_USER'],
            password = app.config['POSTGRES_PASS'],
            host     = app.config['POSTGRES_HOST'],
            port     = app.config['POSTGRES_PORT']
        )
        cursor = connection.cursor()
        app.logger.debug("DB connection opened")
        
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
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")
    return {'message': 'Internal server error'}, 500
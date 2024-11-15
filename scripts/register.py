from uuid import uuid4
import bcrypt
import time
from marshmallow import Schema, fields, validate, ValidationError
from scripts.helpers import send_email, open_postgres_connection, close_postgres_connection

def no_plus(email):
    if '+' in email:
        raise ValidationError("Email addresses with '+' are not allowed.")

class UserSchema(Schema):
    email = fields.Email(required=True, validate=[validate.Length(min=4, max=40), no_plus], error_messages={'required': 'Email is required', 'invalid': 'Email is invalid'})
    password = fields.Str(required=True, validate=validate.Length(min=4, max=32), error_messages={'required': 'Password is required', 'invalid': 'Password is invalid'})
    username = fields.Str(required=True, validate=validate.Length(min=3, max=25), error_messages={'required': 'Username is required', 'invalid': 'Username is invalid'})

def register(json, app):
    try:
        UserSchema().load(json)
    except ValidationError as err:
        return err.messages, 400
    try:
        username = json["username"]
        password = json["password"]
        email    = json["email"]
        connection, cursor = open_postgres_connection(app)
        
        app.logger.debug("Checking if user exists")
        get_user_sql = "SELECT username FROM users WHERE username=%s;"
        cursor.execute(get_user_sql, (username,))
        user = cursor.fetchone()
        if user:
            app.logger.debug("User found")
            return {'message': 'Please check your email to verify your user'}, 201
        
        app.logger.debug("Checking if email is already in use")
        get_user_sql = "SELECT username FROM users WHERE email=%s;"
        cursor.execute(get_user_sql, (email,))
        user = cursor.fetchone()
        if user:
            app.logger.debug("Email found")
            return {'message': 'Please check your email to verify your user'}, 201
        
        app.logger.debug("Deleting old registration if exists")
        delete_registration_sql = "DELETE FROM pending_registrations WHERE email=%s;"
        cursor.execute(delete_registration_sql, (email,))
        
        uuid = uuid4().hex
        app.logger.debug("uuid for email verification is " + uuid)
        create_registration_sql = '''
            INSERT INTO pending_registrations (username, password, email, uuid, created)
            VALUES (%s, %s, %s, %s, %s);
        '''
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf8')
        cursor.execute(create_registration_sql, (username, password_hash, email, uuid, int(round(time.time())),))
        connection.commit()
        
        app.logger.debug("Sending email for verification")
        if send_email([email], 'email_templates/verify_email.html', 'Email verification', f"/verify/{str(uuid)}", app):
            return {'message': 'Please check your email to verify your user'}, 201
        else:
            return {'message': 'An error occured while sending verification email'}, 500
    except Exception as e:
        app.logger.debug(e)
    finally:
        close_postgres_connection(connection, cursor, app)
    return {'message': 'Internal server error'}, 500

def verify(uuid, app):
    try:
        connection, cursor = open_postgres_connection(app)
        
        get_user_sql = "SELECT username, password, email FROM pending_registrations WHERE uuid=%s;"
        cursor.execute(get_user_sql, (uuid,))
        user = cursor.fetchone()
        if not user:
            return {'message': 'Registration does not exist'}, 404
        
        app.logger.debug("Deleting registration")
        delete_registration_sql = "DELETE FROM pending_registrations WHERE uuid=%s;"
        cursor.execute(delete_registration_sql, (uuid,))

        app.logger.debug("Creating user")
        create_user_sql = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s);"
        cursor.execute(create_user_sql, (user[0], user[1], user[2],))

        connection.commit()
        return {'message': 'Verification was successful. Please return to the homepage'}, 201

    except Exception as e:
        app.logger.debug(e)
    finally:
        close_postgres_connection(connection, cursor, app)
    return {'message': 'Internal server error'}, 500
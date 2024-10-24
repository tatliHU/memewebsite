import psycopg2
from uuid import uuid4
import time
import boto3
from botocore.exceptions import ClientError
import hashlib
from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(min=4, max=40), error_messages={'required': 'Email is required', 'invalid': 'Email is invalid'})
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
        connection = psycopg2.connect(
            dbname   = app.config['POSTGRES_DB'],
            user     = app.config['POSTGRES_USER'],
            password = app.config['POSTGRES_PASS'],
            host     = app.config['POSTGRES_HOST'],
            port     = app.config['POSTGRES_PORT']
        )
        cursor = connection.cursor()
        app.logger.debug("DB connection opened")
        
        app.logger.debug("Checking if user exists")
        get_user_sql = "SELECT username FROM users WHERE username=%s;"
        cursor.execute(get_user_sql, (username,))
        user = cursor.fetchone()
        if user:
            app.logger.debug("User found")
            return {'message': 'User already exists'}, 400
        
        app.logger.debug("Checking if email is already in use")
        get_user_sql = "SELECT username FROM users WHERE email=%s;"
        cursor.execute(get_user_sql, (email,))
        user = cursor.fetchone()
        if user:
            app.logger.debug("Email found")
            return {'message': 'User with this email already exists'}, 400
        
        app.logger.debug("Deleting old registration if exists")
        delete_registration_sql = "DELETE FROM pending_registrations WHERE email=%s;"
        cursor.execute(delete_registration_sql, (email,))
        
        uuid = uuid4().hex
        app.logger.debug("uuid for email verification is " + uuid)
        create_registration_sql = '''
            INSERT INTO pending_registrations (username, password, email, uuid, created)
            VALUES (%s, %s, %s, %s, %s);
        '''
        password_hash = hashlib.md5((password+app.config['SALT']).encode()).hexdigest()
        cursor.execute(create_registration_sql, (username, password_hash, email, uuid, int(round(time.time())),))
        connection.commit()
        
        app.logger.debug("Sending email for verification")
        if send_email(email, uuid, app):
            return {'message': 'Please check your email to verify your user'}, 201
        else:
            return {'message': 'An error occured while sending verification email'}, 500
    except Exception as e:
        app.logger.debug(e)
    finally:
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")
    return {'message': 'Internal server error'}, 500

def verify(uuid, app):
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
        
        app.logger.debug("Getting registration")
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
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")
    return {'message': 'Internal server error'}, 500

def send_email(email, uuid, app):
    app.logger.debug(email+" with "+uuid)
    with open('files/email.html', 'r') as file:
        body_html = file.read()
    body_html = body_html.replace('[LINK]', f"{app.config['WEBSITE_URL']}/api/verify/{str(uuid)}")
    body_html = body_html.replace('[DOMAIN]', app.config['DOMAIN'])
    ses_client = boto3.client('ses')
    try:
        response = ses_client.send_email(
            Destination={
                'ToAddresses': [email,],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': body_html,
                    },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': 'Email verification',
                },
            },
            Source=f"noreply@{app.config['DOMAIN']}",
        )
        return True
    except ClientError as e:
        app.logger.debug(e.response['Error']['Message'])
    except:
        app.logger.debug("Unknown error when sending email")
    return False
import psycopg2
import bcrypt
import boto3
from botocore.exceptions import ClientError

def open_postgres_connection(app):
    connection = psycopg2.connect(
            dbname   = app.config['POSTGRES_DB'],
            user     = app.config['POSTGRES_USER'],
            password = app.config['POSTGRES_PASS'],
            host     = app.config['POSTGRES_HOST'],
            port     = app.config['POSTGRES_PORT']
        )
    cursor = connection.cursor()
    app.logger.debug("DB connection opened")
    return connection, cursor

def close_postgres_connection(connection, cursor, app):
    if connection:
        cursor.close()
        connection.close()
        app.logger.debug("DB connection closed")

def is_admin(username, app):
    try:
        connection, cursor = open_postgres_connection(app)
        get_user_sql = "SELECT admin FROM users WHERE username=%s;"
        cursor.execute(get_user_sql, (username,))
        result = cursor.fetchone()[0]
        return result
    except Exception as e:
        app.logger.debug(e)
        return False
    finally:
        close_postgres_connection(connection, cursor, app)

def match_password(username, password, app):
    try:
        connection, cursor = open_postgres_connection(app)
        
        app.logger.debug("Retrieving password")
        get_user_sql = "SELECT password FROM users WHERE username=%s;"
        cursor.execute(get_user_sql, (username,))
        result = cursor.fetchone()
        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            return True
        else:
            return False
    except Exception as e:
        app.logger.debug(e)
        return False
    finally:
        close_postgres_connection(connection, cursor, app)

def send_email(to, file, title, urn, app):
    with open(file, 'r') as html_file:
        body_html = html_file.read()
    body_html = body_html.replace('[LINK]', f"{app.config['WEBSITE_URL']}{urn}")
    body_html = body_html.replace('[DOMAIN]', app.config['DOMAIN'])
    ses_client = boto3.client('ses')
    try:
        response = ses_client.send_email(
            Destination={
                'ToAddresses': to,
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
                    'Data': title,
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
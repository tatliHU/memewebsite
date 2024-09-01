import psycopg2
import boto3
from werkzeug.utils import secure_filename
import uuid
import time

def upload(image, title, tags, username, app):
    if image.filename == '':
        return 'No image selected', 400

    id = uuid.uuid4()
    app.logger.debug(f"Generated Id: {id}")
    file_format = secure_filename(image.filename).split(".")[-1]
    if file_format not in ["jpg", "png", "gif"]:
        return 'Invalid file format', 406
        
    # DB upload
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
        
        app.logger.debug("Uploading metadata to DB")
        create_user_sql = '''
            INSERT INTO posts (title, url, published, username)
            VALUES (%s, %s, %s, %s);
        '''
        values = (
            title,
            f"https://{app.config['AWS_REGION']}.s3.{app.config['S3_BUCKET']}.amazonaws.com/{id}.{file_format}",
            int(round(time.time())),
            username,
        )
        app.logger.debug(values)
        cursor.execute(create_user_sql, values)
        connection.commit()
    except Exception as e:
        app.logger.debug(f"DB upload failed for {id}")
        app.logger.debug(e)
        return 'File upload failed', 500
    finally:
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")
    
    # S3 upload
    try:
        app.logger.debug("Uploading file to S3")
        s3_client = boto3.client('s3')
        s3_client.upload_fileobj(image, 'bmeme-images', f"{id}.{file_format}",
                                 ExtraArgs={'ContentType': image.content_type, 'ACL': 'public-read'})
        return 'Created', 201
    except Exception as e:
        app.logger.debug(f"S3 upload failed for {id}")
        app.logger.debug(e)
        return 'File upload failed', 500
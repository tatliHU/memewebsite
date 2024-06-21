import boto3
from werkzeug.utils import secure_filename
import uuid
import time
from .globals import get_connection

def upload(image, title, tags, username, app):
    if image.filename == '':
        return 'No image selected', 400

    id = uuid.uuid4()
    app.logger.debug(f"Generated Id: {id}")
    file_format = secure_filename(image.filename).split(".")[-1]
    
    # S3 upload
    try:
        s3_client = boto3.client('s3')
        s3_client.upload_fileobj(image, 'bmeme-images', f"{id}.{file_format}",
                                 ExtraArgs={'ContentType': image.content_type, 'ACL': 'public-read'})
    except Exception as e:
        app.logger.debug(f"S3 upload failed for {id}")
        app.logger.debug(e)
        return 'File upload failed', 500
    
    # DB upload
    try:
        connection = get_connection()
        cursor = connection.cursor()
        app.logger.debug("DB connection opened")
        
        app.logger.debug("Uploading metadata to DB")
        create_user_sql = '''
            INSERT INTO posts (Title, Url, Score, Published, UserName)
            VALUES (%s, %s, %s, %s, %s);
        '''
        values = (
            title,
            f"https://bmeme-images.s3.eu-north-1.amazonaws.com/{id}",
            0,
            int(round(time.time())),
            username,
        )
        cursor.execute(create_user_sql, values)
        connection.commit()
        return 'Created', 201
    except Exception as e:
        app.logger.debug(f"DB upload failed for {id}")
        app.logger.debug(e)
        return 'File upload failed', 500
    finally:
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")

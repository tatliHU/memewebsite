import psycopg2
import boto3
from werkzeug.utils import secure_filename
import uuid
import time

def upload(image, title, tags, username, app):
    all_tags = ('tag_all', 'tag_emk', 'tag_gpk', 'tag_epk', 'tag_vbk', 'tag_vik', 'tag_kjk', 'tag_ttk', 'tag_gtk')
    tags_dict = {i : 'false' for i in all_tags}
    for i in tags:
        tags_dict[i] = 'true'
    
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
            INSERT INTO posts (
                title, url, published, username,
                tag_all, tag_emk, tag_gpk, tag_epk, tag_vbk, tag_vik, tag_kjk, tag_ttk, tag_gtk
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        '''
        values = (
            title,
            f"https://{app.config['S3_BUCKET']}.s3.{app.config['AWS_REGION']}.amazonaws.com/{id}.{file_format}",
            int(round(time.time())),
            username,
            tags_dict['tag_all'], tags_dict['tag_emk'], tags_dict['tag_gpk'],
            tags_dict['tag_epk'], tags_dict['tag_vbk'], tags_dict['tag_vik'],
            tags_dict['tag_kjk'], tags_dict['tag_ttk'], tags_dict['tag_gtk']
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
        s3_client.upload_fileobj(image, app.config['S3_BUCKET'], f"{id}.{file_format}",
                                 ExtraArgs={'ContentType': image.content_type, 'ACL': 'public-read'})
        return 'Created', 201
    except Exception as e:
        app.logger.debug(f"S3 upload failed for {id}")
        app.logger.debug(e)
        return 'File upload failed', 500
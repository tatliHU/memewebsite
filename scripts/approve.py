import psycopg2

def deny(postID, approver, app):
    return approve(postID, approver, False, app)

def accept(postID, approver, app):
    return approve(postID, approver, True, app)

def approve(postID, approver, approved, app):
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
        get_admin_sql = "SELECT admin FROM users WHERE username=%s;"
        cursor.execute(get_admin_sql, (approver,))
        admin = cursor.fetchone()
        if not len(admin):
            return 'User does not exist', 403
        app.logger.debug(admin[0])
        if not admin[0]:
            return 'Unauthorized', 403

        sql = "UPDATE posts SET approved=%s WHERE post_id=%s;"
        values = (approved, postID,)
        cursor.execute(sql, values)
        if approver:
            sql = "UPDATE posts SET approver=%s WHERE post_id=%s;"
            values = (approver, postID,)
            cursor.execute(sql, values)

        connection.commit()
        return 'Created', 201
    except Exception as e:
        app.logger.debug(f"Approval failed for {id}")
        app.logger.debug(e)
        return 'Approval failed', 500
    finally:
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")
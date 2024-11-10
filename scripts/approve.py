from scripts.helpers import open_postgres_connection, close_postgres_connection

def deny(postID, approver, app):
    return approve(postID, approver, False, app)

def accept(postID, approver, app):
    return approve(postID, approver, True, app)

def approve(postID, approver, approved, app):
    try:
        connection, cursor = open_postgres_connection(app)

        app.logger.debug("Authorizing")
        get_admin_sql = "SELECT admin FROM users WHERE username=%s;"
        cursor.execute(get_admin_sql, (approver,))
        admin = cursor.fetchone()
        if not len(admin):
            return {'message': 'User does not exist'}, 403
        app.logger.debug(admin[0])
        if not admin[0]:
            return {'message': 'You are not an administrator'}, 403

        sql = "UPDATE posts SET approved=%s WHERE post_id=%s;"
        values = (approved, postID,)
        cursor.execute(sql, values)
        if approver:
            sql = "UPDATE posts SET approver=%s WHERE post_id=%s;"
            values = (approver, postID,)
            cursor.execute(sql, values)

        connection.commit()
        return '', 201
    except Exception as e:
        app.logger.debug(f"Approval failed for {id}")
        app.logger.debug(e)
        return {'message': 'Approval failed'}, 500
    finally:
        close_postgres_connection(connection, cursor, app)
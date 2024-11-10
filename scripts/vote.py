from scripts.helpers import open_postgres_connection, close_postgres_connection

def upvote(postID, username, app):
    return vote(postID, username, 1, app)

def downvote(postID, username, app):
    return vote(postID, username, -1, app)

def vote(postID, username, score, app):
    try:
        connection, cursor = open_postgres_connection(app)
        app.logger.debug(f"Score is {score}")
        
        get_vote_sql = "SELECT vote FROM votes WHERE username=%s AND post_id=%s"
        cursor.execute(get_vote_sql, (username, postID,))
        vote = cursor.fetchone()

        if not vote:
            app.logger.debug("Registering vote")
            sql = "INSERT INTO votes (username, post_id, vote) VALUES (%s, %s, %s);"
            values = (username, postID, score,)
        elif int(vote[0])==score:
            app.logger.debug("Cancelling existing vote")
            sql = "DELETE FROM votes WHERE username=%s AND post_id=%s;"
            values = (username, postID,)
        else:
            app.logger.debug("Updating existing vote")
            sql = "UPDATE votes SET vote = %s WHERE username=%s AND post_id=%s;"
            values = (score, username, postID,)
        app.logger.debug(values)
        cursor.execute(sql, values)
        connection.commit()
        return '', 201
    except Exception as e:
        app.logger.debug(f"Vote failed for {id}")
        app.logger.debug(e)
        return {'message': 'Vote failed'}, 500
    finally:
        close_postgres_connection(connection, cursor, app)
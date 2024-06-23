from .globals import get_connection

def upvote(postID, username, app):
    return vote(postID, username, 1, app)

def downvote(postID, username, app):
    return vote(postID, username, -1, app)

def vote(postID, username, score, app):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        app.logger.debug("DB connection opened")
        app.logger.debug(f"Score is {score}")
        
        get_vote_sql = "SELECT Vote FROM VOTES WHERE UserName=%s AND PostID=%s"
        cursor.execute(get_vote_sql, (username, postID,))
        vote = cursor.fetchone()

        if not vote:
            app.logger.debug("Registering vote")
            sql = "INSERT INTO VOTES (UserName, PostID, Vote) VALUES (%s, %s, %s);"
            values = (username, postID, score,)
        elif int(vote[0])==score:
            app.logger.debug("Cancelling existing vote")
            sql = "DELETE FROM VOTES WHERE UserName=%s AND PostID=%s;"
            values = (username, postID,)
        else:
            app.logger.debug("Updating existing vote")
            sql = "UPDATE VOTES SET Vote = %s WHERE UserName=%s AND PostID=%s;"
            values = (score, username, postID,)
        app.logger.debug(values)
        cursor.execute(sql, values)
        connection.commit()
        return 'Created', 201
    except Exception as e:
        app.logger.debug(f"Vote failed for {id}")
        app.logger.debug(e)
        return 'Vote failed', 500
    finally:
        if connection:
            cursor.close()
            connection.close()
            app.logger.debug("DB connection closed")
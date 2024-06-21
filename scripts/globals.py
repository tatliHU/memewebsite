import psycopg2

def get_connection():
    db_params = {
        'dbname': 'meme',
        'user': 'atka',
        'password': 'atka',
        'host': 'localhost',
        'port': 5432
    }
    connection = psycopg2.connect(**db_params)
    return connection
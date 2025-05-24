import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        dbname="test3",
        user="postgres",
        password="1234",
        host="localhost"
    )
    return conn
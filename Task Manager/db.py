import psycopg2

def db_conn():
    return psycopg2.connect(
        database='taskmanager_db',
        host='localhost',
        user='postgres',
        password='12345',
        port='5432'
    )

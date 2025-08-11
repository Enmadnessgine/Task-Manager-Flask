import psycopg2

def db_conn():
    return psycopg2.connect(
        database='dbname',
        host='localhost',
        user='postgres',
        password='password',
        port='port'
    )

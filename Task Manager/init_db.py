import psycopg2

conn = psycopg2.connect(database='db', host='localhost', user='postgres', password='password',port='port')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS tasks (id serial PRIMARY KEY, name varchar(100), description text, duration integer);''')
cur.execute('''INSERT INTO tasks (name,description,duration) VALUES ('complete project','description text', 72)''')


conn.commit()
cur.close()
conn.close()
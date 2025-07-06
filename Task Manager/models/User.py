from flask_login import UserMixin
from db import db_conn


class User(UserMixin):
    def __init__(self, id, name, email, password_hash):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash

    @staticmethod
    def get_by_email(email):
        conn = db_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, password FROM users WHERE email = %s", (email,))
        data = cur.fetchone()
        cur.close()
        conn.close()
        if data:
            return User(*data)
        return None

    @staticmethod
    def get(user_id):
        conn = db_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, password FROM users WHERE id = %s", (user_id,))
        data = cur.fetchone()
        cur.close()
        conn.close()
        if data:
            return User(*data)
        return None

import psycopg2
from flask import Flask, request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, current_user, login_user
from datetime import timedelta
from models.User import User
from db import db_conn


# Configuration
app = Flask(__name__)
app.secret_key = 'f8Xj9qZ2mC7KsWdT3VpL'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=14)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/")
def index():
    conn = db_conn()
    cur = conn.cursor()
    cur.execute('''SELECT * FROM tasks''')
    data = cur.fetchall()
    return render_template("task manager/index.html",data=data)


@app.route('/create', methods=['POST'])
def create():
    conn = db_conn()
    cur = conn.cursor()
    name = request.form['name']
    description = request.form['description']
    duration = request.form['duration']
    cur.execute('''INSERT INTO tasks (name, description, duration) VALUES(%s,%s,%s)''', (name, description, duration))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))


@app.route("/register", methods=['POST', 'GET'])
def register():
    conn = db_conn()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if len(name) > 3 and len(email) > 4 and len(password) > 4 and password == password2:
            hash = generate_password_hash(password)
            cur.execute('''INSERT INTO users (name, email, password) VALUES(%s, %s, %s)''', (name, email, hash))
            conn.commit()
            redirect(url_for('login'))
        else:
            print('Error add to db')

    else:
        print('GET request')

    cur.close()
    conn.close()
    return render_template('auth/register.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.get_by_email(email)

        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            flash('Login success!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('auth/login.html')


@app.route("/profile", methods=['GET'])
@login_required
def profile():
    user_id = current_user.id
    conn = db_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tasks WHERE user_id = %s', (user_id,))
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('task manager/profile.html', tasks=tasks, user_name=current_user.name)


@app.route("/add_task", methods=['POST', 'GET'])
@login_required
def add_task():
    user_id = current_user.id

    conn = db_conn()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('title')
        description = request.form.get('description')
        duration = request.form.get('duration')
        deadline = request.form.get('deadline')

        cur.execute('''INSERT INTO tasks (name, description, duration, deadline, user_id) VALUES(%s, %s, %s, %s, %s)''', (name, description, duration, deadline, user_id))
        conn.commit()
        
        redirect(url_for('profile'))
    else:
        print('GET request')

    return render_template('task manager/add_task.html', user_id=user_id)


if __name__ == '__main__':
    app.run(debug=True)
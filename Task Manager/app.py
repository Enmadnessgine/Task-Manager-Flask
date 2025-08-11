import psycopg2
from flask import Flask, request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from datetime import timedelta, datetime
from models.User import User
from db import db_conn


# Configuration
app = Flask(__name__)
app.secret_key = 'secret'
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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/profile", methods=['GET'])
@login_required
def profile():
    user_id = current_user.id

    status = request.args.get('status')       # 'complete' / 'incomplete'
    priority = request.args.get('priority')   # 'high'

    conn = db_conn()
    cur = conn.cursor()
    cur.execute('SELECT id, name, description, duration, deadline, is_completed, user_id, add_date, add_time, priority FROM tasks WHERE user_id = %s', (user_id,))
    raw_tasks = cur.fetchall()
    now = datetime.now()
    tasks = []

    for task in raw_tasks:
        task = list(task)
        id, name, description, duration, deadline, is_completed, user_id, add_date, add_time, task_priority = task
        hours_left = None
        if add_date and add_time and duration:
            try:
                start_datetime = datetime.combine(add_date, add_time)
                deadline_datetime = start_datetime + timedelta(hours=duration)
                delta = deadline_datetime - now
                hours_left = round(delta.total_seconds() / 3600, 2)
            except Exception as e:
                print(f"Error computing hours_left: {e}")

        if hours_left != None and hours_left > 0:
            task.append(hours_left)
        else:
            task.append(0)

        if status == 'complete' and not is_completed:
            continue  
        if status == 'incomplete' and is_completed:
            continue
        if priority and task_priority != priority:
            continue

        tasks.append(task)

    cur.close()
    conn.close()

    return render_template('task manager/profile.html', tasks=tasks, user_name=current_user.name, selected_status=status, selected_priority=priority)


@app.route('/profile/task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def view_task(task_id):
    user_id = current_user.id
    conn = db_conn()
    cur = conn.cursor()

    cur.execute('''SELECT id, name, description, duration, add_date, add_time, is_completed, priority FROM tasks WHERE id = %s AND user_id = %s''', (task_id, user_id))

    task = cur.fetchone()


    if not task:
        cur.close()
        conn.close()
        flash("Task not found or access denied.", "danger")
        return redirect(url_for('profile'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        duration = request.form.get('duration')
        priority = request.form.get('priority')
        status_str = request.form.get('is_completed')
        status = status_str == 'true'

        cur.execute('''UPDATE tasks SET name = %s, description = %s, duration = %s, priority = %s, is_completed = %s WHERE id = %s AND user_id = %s''', (name, description, duration, priority, status, task_id, user_id))

        conn.commit()
        flash("Task updated successfully.", "success")

        cur.execute('''
            SELECT id, name, description, duration, add_date, add_time, is_completed, priority FROM tasks WHERE id = %s AND user_id = %s''', (task_id, user_id))
        task = cur.fetchone()

    cur.close()
    conn.close()

    return render_template('task manager/task_details.html', task=task)


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
        add_date = datetime.now().strftime('%Y-%m-%d')
        add_time = datetime.now().strftime('%H:%M:%S')
        cur.execute('''INSERT INTO tasks (name, description, duration, deadline, user_id, add_date, add_time) VALUES(%s, %s, %s, %s, %s, %s, %s)''', (name, description, duration, deadline, user_id, add_date, add_time))
        conn.commit()
        
        redirect(url_for('profile'))
    else:
        print('GET request')

    return render_template('task manager/add_task.html', user_id=user_id)


if __name__ == '__main__':
    app.run(debug=True)
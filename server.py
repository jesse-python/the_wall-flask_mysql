from flask import Flask, flash, redirect, request, render_template, session
from mysqlconnection import MySQLConnector
from flask_bcrypt import Bcrypt
import re
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'ThisIsSecret'
mysql = MySQLConnector('walldb')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')

@app.route('/', methods=['GET'])
def index():
    return render_template('users.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    bool = True

    if not email:
        flash('Email cannot be blank')
        bool = False
    elif not EMAIL_REGEX.match(email):
        flash('Email must be valid, try again')
        bool = False

    if not password:
        flash('Password must not be blank')
        bool = False

    if bool:
        user_query = "SELECT * FROM users WHERE email = '{}' LIMIT 1".format(email)
        user = mysql.fetch(user_query)
        if bcrypt.check_password_hash(user[0]['password'], password):
            session['curr_user'] = user[0]
            return redirect('/wall')
        else:
            flash('Wrong password, try again')
            return redirect('/')
    else:
        return redirect('/')

@app.route('/users', methods=['POST'])
def create():
    f_name = str(request.form['f_name'])
    l_name = str(request.form['l_name'])
    email = request.form['email']
    password = request.form['password']
    c_password = request.form['c_password']

    bool = True

    if not f_name:
        flash("First Name cannot be blank")
        bool = False
    elif len(f_name) < 2:
        flash("First name must be greater than 2 characters")
        bool = False
    elif not str.isalpha(f_name):
        flash("Last name must not contain non-alphabetic characters")
        bool = False

    if not l_name:
        flash("Last Name cannot be blank")
        bool = False
    elif len(l_name) < 2:
        flash("Last Name must be greater than 2 characters")
        bool = False
    elif not str.isalpha(l_name):
        flash("Last name must not contain non-alphabetic characters")
        bool = False

    if not email:
        flash("Email must not be blank")
        bool = False
    elif not EMAIL_REGEX.match(email):
        flash("Invalid email, try again")
        bool = False

    if not password:
        flash("Password must not be blank")
        bool = False
    elif len(password) < 8:
        flash("Password must be greater than 8 characters")
        bool = False

    if not c_password:
        flash("Password confirmation must not be blank")
        bool = False
    elif password != c_password:
        flash("Password must be same as password confirmation")
        bool = False

    if bool:
        pw_hash = bcrypt.generate_password_hash(password)
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', NOW(), NOW())".format(f_name, l_name, email, pw_hash)
        mysql.run_mysql_query(query)

        user_query = "SELECT * FROM users WHERE email = '{}' LIMIT 1".format(email)
        user = mysql.fetch(user_query)
        session['curr_user'] = user[0]

        return redirect('/wall')

    return redirect('/')

@app.route('/logout')
def logout():
    session.pop("curr_user")
    flash("You have logged out")
    return redirect('/')

@app.route('/wall')
def wallindex():
    messages_query = "SELECT messages.message, users.first_name, users.last_name, messages.created_at, messages.id, messages.user_id FROM users JOIN messages ON users.id = messages.user_id ORDER BY messages.created_at DESC;"
    messages = mysql.fetch(messages_query)

    comments_query = "SELECT comments.comment, users.first_name, users.last_name, comments.created_at, comments.id, comments.message_id FROM users JOIN comments ON users.id = comments.user_id ORDER BY comments.created_at ASC;"
    comments = mysql.fetch(comments_query)
    print comments
    return render_template('wall.html', messages=messages, comments=comments)

@app.route('/messages', methods=['POST'])
def create_message():
    print request.form['message']
    query = "INSERT INTO messages (message, user_id, created_at, updated_at) VALUES ('{}', '{}', NOW(), NOW())".format(request.form['message'], session['curr_user']['id'])
    mysql.run_mysql_query(query)
    return redirect('/wall')

@app.route('/messages/<id>/delete', methods=['POST'])
def delete_message(id):
    delete = "DELETE FROM walldb.messages WHERE id = {}".format(id)
    mysql.run_mysql_query(delete)
    return redirect('/wall')

@app.route('/comments', methods=['POST'])
def create_comment():
    print request.form['comment']
    print request.form['message_id']
    query = "INSERT INTO comments (comment, user_id, message_id, created_at, updated_at) VALUES ('{}','{}','{}', NOW(), NOW())".format(request.form['comment'], session['curr_user']['id'], request.form['message_id'])
    mysql.run_mysql_query(query)
    return redirect('/wall')



app.run(debug=True)

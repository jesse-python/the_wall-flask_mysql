from flask import Flask, flash, redirect, request, render_template, session
from mysqlconnection import MySQLConnector
app = Flask(__name__)
app.secret_key = 'ThisIsSecret'
mysql = MySQLConnector('walldb')

@app.route('/')
def index():
    return render_template('index.html')

app.run(debug=True)

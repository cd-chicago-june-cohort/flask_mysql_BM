from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)

app.secret_key = "8675309"

mysql = MySQLConnector(app,'emails')


@app.route('/')
def index():
    query = "SELECT * FROM emails"
    emails = mysql.query_db(query)                      
    return render_template('index.html')


@app.route('/create', methods=['POST'])
def create():
    new_email=request.form['emails']

    if_exists = "select emails from emails where emails=(:test_email)"
    new_data = {"test_email": new_email}

    the_email = mysql.query_db(if_exists, new_data)

    if len(new_email) < 1:
        flash('Email may not be blank.')
        return redirect('/')

    elif not EMAIL_REGEX.match(request.form['emails']):
        flash("Invalid Email Address")
        return redirect('/')

    elif (the_email):
        flash("That email already exists")
        return redirect('/')

    else:

        query = "INSERT INTO emails (emails, created_at) VALUES (:emails, NOW())"
  
        data = {
             'emails': request.form['emails']
           }
    
        mysql.query_db(query, data)

        final_query = "SELECT * FROM emails"
        email_list = mysql.query_db(final_query)

        return render_template("success.html", new_email=new_email, email_list=email_list)

app.run(debug=True)



from flask import Flask, redirect, request, session, flash, render_template
from mysqlconnection import MySQLConnector
import re
import md5

app = Flask(__name__)
app.secret_key = "5203945872309457"
mysql = MySQLConnector(app, "registered_users")

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route("/")
def index():
   return render_template("index.html")



@app.route("/login",methods=["POST"])
def login():

    server_email = request.form["email"]
    server_password = request.form["password"]
    hashed_password = md5.new(server_password).hexdigest()

    query = "SELECT * from users where email=:test_email"
    data = {
        'test_email': server_email
    }

    db_check = mysql.query_db(query, data)

    if len(db_check) != 1:
        flash("You are not a registered user.")
        return redirect ('/')
    
    elif db_check[0]['password'] == hashed_password:
        session['email']=server_email
        return redirect ('/success')

    else:
        flash("Incorrect Password")
        return redirect('/')

    

@app.route("/registration", methods=["POST", "GET"])
def registration():
   
    server_email = request.form["email"]
    server_first_name = request.form["first_name"]
    server_last_name = request.form["last_name"]
    server_password = request.form["password"]
    server_confirm_password = request.form["confirm_password"]

    if len(server_email) < 1 or len(server_first_name) < 1 or len(server_last_name) < 1 or len(server_password) < 1 or len(server_confirm_password) < 1:
        flash("All fields are required")
        return redirect("/")
    elif not (server_first_name.isalpha() or server_last_name.isalpha()):
        flash("First name and last name can only contain letters")
        return redirect("/")
    elif not EMAIL_REGEX.match(server_email):
        flash("Invalid Email Address!")
        return redirect("/")
    elif len(server_password) < 8:
        flash("Password must be 8 characters")
        return redirect("/")
    elif server_password != server_confirm_password:
        flash("Password confirmation must match password")
        return redirect("/")
    else:
        hashed_password = md5.new(server_password).hexdigest()
        insert = "INSERT INTO users (email, first_name, last_name, password, created_at) VALUES (:email, :first_name, :last_name, :password, NOW())"
  
        data = {
             'email': server_email,
             'first_name': server_first_name,
             'last_name': server_last_name,
             'password': hashed_password
        }
    
        mysql.query_db(insert, data)

        return redirect("/success")



@app.route('/success')
def success():

    return render_template('/accepted.html')



app.run(debug=True)
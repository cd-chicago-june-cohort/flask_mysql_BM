from flask import Flask, redirect, request, session, flash, render_template
from mysqlconnection import MySQLConnector
import re
import md5

app = Flask(__name__)
app.secret_key = "5203945872309457"
mysql = MySQLConnector(app, "the_wall")

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route("/")
def index():
   return render_template("index.html")



@app.route("/login", methods=["POST"])
def login():

    server_email = request.form["email"]
    server_password = request.form["password"]
    hashed_password = md5.new(server_password).hexdigest()

    query = "SELECT * from users where email=:test_email"
    data = {
        'test_email': server_email
    }

    db_check = mysql.query_db(query, data)
    print db_check
    username = db_check[0]['first_name'] + db_check[0]['last_name']

    if len(db_check) != 1:
        flash("You are not a registered user.")
        return redirect ('/')
    
    elif db_check[0]['password'] == hashed_password:
        session['email']=server_email
        session['username']=username
        session['id']=db_check[0]['id']
        return redirect ('/thewall')

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

        flash("You are now registered, you may now log in.")
        return redirect("/")



@app.route('/thewall')
def success():
    query_post = "SELECT first_name, last_name, messages.created_at, message, messages.id FROM messages JOIN users ON users.id=user_id ORDER BY messages.created_at DESC"
    query_comments = "SELECT first_name, last_name, comments.created_at, comment, message_id from users join comments on users.id=user_id"
    
    results_list = mysql.query_db(query_post)
    comments_list = mysql.query_db(query_comments)
    comment
    
    print "*"*50
    print comments_list
    return render_template('/wall.html', results_list=results_list, comments_list=comments_list)



@app.route('/message', methods=['POST'])
def message():

    query = "SELECT * FROM users where email = :email"
    data1 = {
        'email': session['email']
    }

    # query2 = "SELECT "
    poster_id = mysql.query_db(query, data1)
    new_message = request.form['new_message']
    insert = "INSERT INTO messages (message, created_at, user_id) VALUES (:message, NOW(), :user_id)"
    data2 = {
        'message': new_message,
        'user_id': poster_id[0]['id']
    }
    insert_msg = mysql.query_db(insert, data2)
    print new_message
    
    return redirect('/thewall')



# @app.route('/comment', methods=['POST'])
# def comment():

#     query = "SELECT * FROM users where email = :email"
#     data1 = {
#         'email': session['email']
#     }
#     commenter_id = mysql.query_db(query, data1)
#     new_comment = request.form['new_comment']
#     insert = "INSERT"

@app.route('/comment', methods=['POST'])
def comment():
    
    

    userID = session['id']
    comment = request.form['new_comment']
    messageID = request.form['messageID']
    print comment
    insert = 'INSERT into comments (message_ID, user_id, comment, created_at) value (:messageID, :userID, :comment, NOW())'
    info = {
        'messageID' : messageID,
        'userID' : userID,
        'comment' : comment
    }

    print "*"*20
    print comment
    mysql.query_db(insert, info)
    return redirect('/thewall')


@app.route('/logout', methods=['POST'])
def logout():

    session.clear()
    return redirect('/')


app.run(debug=True)
#!/usr/bin/python

import sqlite3
from flask import Flask, render_template, json, request, session, redirect, url_for, escape
import hashlib
import getopt
import sys
import os

# Command line options: -h = host; -p = port; -f = filename
myopts, args = getopt.getopt(sys.argv[1:],"p:")

PORT = 5000

for o, a in myopts:
    if  o == '-p':
        PORT=a
    else:
        print("Usage for changing the standard port from 5000: %s -p [port number]" % sys.argv[0])

print("Port number is: ",PORT)

#mysql = MySQL()
app = Flask(__name__)
app.secret_key = "my vulnerable app"

# TODO: Move the database functions and methods to a Class
exists = os.path.isfile(os.getcwd() + '/user.db')

if exists:
    print('Database exists. Moving on...')
else:
    print("Creating the database 'user.db'")
    conn = sqlite3.connect('user.db')
    print("Created database successfully")
    conn.execute('''CREATE TABLE tbl_user
         (user_id INTEGER  PRIMARY KEY   AUTOINCREMENT   NOT NULL,
         user_name           VARCHAR(45),
         user_username     VARCHAR(45),
         user_password      BLOB);
         ''')
    conn.execute('''CREATE TABLE tbl_bucketlist
         (bucket_id INTEGER PRIMARY KEY AUTOINCREMENT   NOT NULL,
         bucketname         VARCHAR(255),
         bucketdescr        TEXT,
         completed          NUMERIC
         );''')
    print("Table created successfully")
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/signUp',methods=['POST'])
def signUp():
    try:
        _name = request.form.get('inputName')
        _email = request.form.get('inputEmail')
        _password = request.form.get('inputPassword')

        print("name: ", _name)
        print("email: ", _email)

        conn = sqlite3.connect('user.db')
        cursor = conn.execute("SELECT user_username FROM tbl_user WHERE user_username='" + _email + "'")
        recordCount = 0

        for row in cursor:
            recordCount = 1

        conn.close()

        # validate the received values
        if _name and _email and _password and recordCount == 0:
            # All Good, let's call SQLite
            m = hashlib.sha256()
            m.update(_password.encode("ISO-8859-1"))
            _hashed_password = m.digest()
            print("hashed pwd: ", _hashed_password)
            sqlStmt = "INSERT INTO tbl_user (user_name,user_username,user_password) VALUES ( ?,?,?);"
            conn = sqlite3.connect('user.db')
            conn.execute(sqlStmt,[_name, _email, sqlite3.Binary(_hashed_password)])
            conn.commit()
            conn.close()
            return json.dumps({'html':'<span><b>User created successfully !</b></span>'})
        else:
            if recordCount >= 1:
                print("User already exists!")
                retMsg = "<span><b>User already exists!</b></span>"
            else:
                retMsg = "<span><b>Enter the required fields</b></span>"
                print("A required field is missing.")
            return json.dumps({'html':retMsg})
    except Exception as e:
        print("error: ",  str(e))
        return json.dumps({'error':str(e)})
        #retVal = "Error: " + str(e)
    finally:
        print("Done.")

@app.route('/login',methods = ['GET', 'POST'])
def loginUser():
    if request.method == 'POST':
        _username = request.form.get('inputName')
        _useremail = request.form.get('inputEmail')
        _userpassword = request.form.get('inputPassword')
        m = hashlib.sha256()
        m.update(_userpassword.encode("ISO-8859-1"))
        _hashed_password = m.digest()

        print("name: ", _username)
        print("email: ", _useremail)
        print("hashed pwd: ", _hashed_password)

        sqlStmt = "SELECT user_id FROM tbl_user WHERE user_username=? AND user_password=? AND user_name=?;"
        conn = sqlite3.connect('user.db')
        cursor = conn.execute(sqlStmt,[_useremail,sqlite3.Binary(_hashed_password),_username])
        recordCount = 0

        for row in cursor:
            _userId = row[0]
            print("UserID: ",_userId)
            recordCount = 1

        conn.close()

        print("Recordcount: ",recordCount)

        if(recordCount == 1):
            session['loginsuccessful'] = True
            session['username'] = _username
            session['email'] = _useremail
            session['userID'] = _userId
            return json.dumps({'redirect':'/bucketlist'})
        else:
            session['loginsuccessful'] = False
            return json.dumps({'html':'<span><b>Invalid Username or Password. Please try again.</b></span>'})

    return render_template('login.html')

@app.route('/bucketlist',methods=['POST','GET'])
def bucketList():
    if(session['loginsuccessful']):
        return render_template('bucketlist.html')
    else:
        return redirect(url_for('loginUser'))

if PORT != 5000:
    if __name__ == "__main__":
        app.run(host='0.0.0.0',port=PORT,debug=True)
else:
    if __name__ == '__main__':
        app.run(host='0.0.0.0',debug=True)



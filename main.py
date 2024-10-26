#INFORMATION
"""
Developer: Jesse Read
GitHub: JesseReadAu
Last Update: 2024/10/27
Notes:  This is a RESTful backend being developed for the company IR as a proof of concept. It is interacted with
        from a REACT front end application.
"""


from flask import Flask, abort, request, jsonify
from flask_mysqldb import MySQL
from hashlib import sha256
#from flask_cors import CORS
import MySQLdb.cursors

#GLOBAL VARIABLES


#MAIN
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ir_db'
app.secret_key = "IAmASecretKey!2KG"

mysql = MySQL(app)
#cur = mysql.connection.cursor()

if __name__ == "__name__":
    app.run()

@app.get("/test/")
def test_method():
    return "Working"


#LOGIN

# Attempt to provide a user a SessionID based on their login credentials.
@app.put("/user/login/")
def Try_To_Login():
    if(request.data):
        data = request.get_json()
        if(data.get("email") and data.get("password")):
            cur = mysql.connection.cursor()
            pass_hashed = sha256(data["password"].encode("utf-8")).hexdigest()

            #TODO: CHECK LOGIN DETAILS

            session_id = sha256(("TestSessionID_" + data["email"]).encode("utf-8")).hexdigest()
            cur.execute("UPDATE users SET session = %s WHERE email = %s AND password = %s", session_id, (data["email"]), pass_hashed)

            #This Session is a test session generated id, an update is required before live.
            #TODO: Update Session
            return session_id, 200
        else:
            return "Invalid Input", 400
    else:
        return "Empty Input", 400

#REGISTER
@app.post("/user/register/")
def Register_User():

    pass

#PROJECTS


#ASSETS


#SEARCH


#USER + USERS
@app.get("/users/")
def get_all_users():
    pass

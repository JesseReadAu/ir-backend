#INFORMATION
"""
Developer: Jesse Read
GitHub: JesseReadAu
Last Update: 2024/10/29
Notes:  This is a RESTful backend being developed for the company IR as a proof of concept. It is interacted with
        from a REACT front end application.
"""


from flask import Flask, request, session, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import json
from hashlib import sha256
from models.users import Users
from db import db
from datetime import datetime, timedelta, datetime, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root@localhost/ir_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

if __name__ == "__name__":
    with app.app_context():
        db.create_all()
    app.run()

# TODO: Incomplete
@app.get("/login")
def login():
    email    = request.args.get("login")
    found_usr = Users.query.filter_by(email=email).first()
    if found_usr:
        print("Already username with that name")
    else:
        usr = Users(login_name, "")
        db.session.add(usr)
        db.session.commit()
        print("Hello new user " + login_name)
    return "yes", 400
"""
USER
"""
# GET all of a users information, minus their password from the database.
@app.get("/user/<int:user_id>")
def get_user_by_id(user_id):
    result = Users.query.filter_by(id=user_id).first()

    if result:
        result_dict = result.to_dict()
        if "password" in result_dict:
            del result_dict["password"]

        return jsonify(result_dict), 200
    else:
        return Response("No user with that ID", 404)

#PATCH a user record in the users database. Password is deleted from return json.
@app.patch("/user/<int:user_id>")
def patch_user(user_id):
    result = Users.query.filter_by(id=user_id).first()

    if not result:
        return Response("No user found", 404)

    data = request.get_json()

    if "first_name" in data:
        result.name = data["first_name"]
    if "last_name" in data:
        result.name = data["last_name"]
    if "email" in data:
        result.email = data["email"]
    if "password" in data:
        result.password = sha256((data["password"]).encode("utf-8")).hexdigest()
    if "enabled" in data:
        result.password = data["enabled"]

    db.session.commit()

    #Prepare Json for return
    result_dict = result.to_dict()
    if "password" in result_dict:
        del result_dict["password"]


    return jsonify(result_dict), 200


"""
USERS
"""
# GET a list of all users and their details. No password is returned.
@app.get("/users")
def get_all_user():
    result = Users.query.all()
    users_dict = {row.id: {"first_name": row.first_name, "last_name": row.last_name, "email": row.email, "session": row.session, "enabled": row.enabled} for row in result}
    """
    users_list = [
        {
            "id": row.id,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "email": row.email,
            "session": row.session,
            "enabled": row.enabled
        }
        for row in result
    ]
    """
    return jsonify(users_dict), 200
#LOGIN


# Attempt to provide a user a SessionID based on their login credentials.
@app.put("/user/login")
def try_to_login():
    if(request.data):
        data = request.get_json()
        if(data.get("email") and data.get("password")):

            pass_hashed = sha256(data["password"].encode("utf-8")).hexdigest()

            #TODO: CHECK LOGIN DETAILS
            # This Session is a test session generated id, an update is required before live.
            session_id = sha256(("TestSessionID_" + data["email"]).encode("utf-8")).hexdigest()

            #Check if email and password at right
            result = Users.query.filter_by(email=data.get("email"), password=pass_hashed).first()
            if not result:
                return "Invalid Login", 400

            #TODO: ORM
            #Update database user with session
            db.session.execute(
                text("UPDATE users SET session = :session_id, last_login= :last_login WHERE email = :email AND password = :pass_hashed"),
                {"session_id": session_id, "email": data["email"], "pass_hashed": pass_hashed, "last_login": datetime.now()}
            )
            db.session.commit()

            #TODO: Update Session
            return session_id, 200
        else:
            return "Invalid Input", 400
    else:
        return "Empty Input", 400

#TODO: Make more secure, can log anyone out. Used for testing Authorisation. ORM
#Logs a user out based on the id in the users table
@app.put("/user/logout/<int:id>")
def log_user_out(id):
    if Validate_User() is True:
        db.session.execute(
            text("UPDATE users SET session = NULL WHERE id = :id"),
            {"id": id}
        )
        db.session.commit()
        return "User logged out", 200
    else:
        return "Invalid Input", 400


#REGISTER
@app.post("/user/register")
def register_user():
    pass

#PROJECTS


#ASSETS


#SEARCH

"""
OTHER METHODS
"""
# TODO: THIS NEEDS TO BE TESTED - NO TESTING DONE. ORM
#Validat
def Validate_User():
    # Check for Session
    data = request.get_json()
    if 'session' in data and data['session']:
        print("User Login Check")
        #Check session against DB
        result = Users.query.filter_by(session=data['session']).first()
        if isinstance(result.last_login, date):
            return True
        else:
            db.session.execute(
                text("UPDATE users SET session = NULL WHERE session = :session"),
                {"session": data['session']}
            )
            db.session.commit()
            return False
    else:
        return False
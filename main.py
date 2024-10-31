#INFORMATION
"""
Developer: Jesse Read
GitHub: JesseReadAu
Last Update: 2024/10/31
Notes:  This is a RESTful backend being developed for the company IR as a proof of concept. It is interacted with
        from a REACT front end application.
"""


from flask import Flask, request, session, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, delete
import json
from hashlib import sha256
from models.users import Users
from models.assets import Assets
from models.project_assets import Project_Assets
from models.projects import Projects
from db import db
from datetime import datetime, timedelta, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root@localhost/ir_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

if __name__ == "__name__":
    with app.app_context():
        db.create_all()
    app.run()



"""
ASSETS
"""
@app.get("/assets")
def get_all_assets():
    result = Assets.query.all()
    asset_dict = {
        row.id: {
            "id": row.id,
            "name": row.name,
            "category": row.category,
            "filetype": row.filetype,
            "filesize": row.filesize,
            "link": row.link,
            "screenshot": row.screenshot,
            "user_id": row.user_id
        } for row in result
    }
    return jsonify(asset_dict), 200


"""
PROJECTS
"""
@app.get("/projects")
def get_all_projects():
    result = Projects.query.all()
    project_dict = {
        row.id: {
            "id": row.id,
            "name": row.name,
            "category": row.category,
            "filetype": row.filetype,
            "filesize": row.filesize,
            "link": row.link,
            "screenshot": row.screenshot,
            "user_id": row.user_id
        } for row in result
    }
    return jsonify(project_dict), 200

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

# Delete a user from the Users database.
@app.delete("/user/<int:user_id>")
def delete_user(user_id):
    user = Users.query.get(user_id)

    if not user:
        return jsonify({"message": f"User with ID {user_id} not found"}), 404

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"User with ID {user_id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete user: {str(e)}"}), 500

# Add a new user to the Users database, requires only first_name, second_name, email and password.
@app.post("/user")
def add_new_user():
    try:
        data = request.get_json()

        first_name = data.get("first_name") or ""
        last_name = data.get("last_name") or ""
        email = data.get("email")
        password = sha256(data.get("password").encode("utf-8")).hexdigest()


        if not email and password:
            return jsonify({"message": "Email and Password are required"}), 400

        new_user = Users(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "New user added"}), 201
    except Exception as e:
        return jsonify({"message": "User not added"}), 404
    pass

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




"""
SEARCH
"""
# TODO: Create Methods
# Return all projects or assets
@app.get('/search/<search_string>')
def get_search(search_string):
    pass


"""
OTHER METHODS
"""
# TODO: THIS NEEDS TO BE TESTED - NO TESTING DONE. ORM
#Validate
def Validate_User():
    # Check for Session
    data = request.get_json()
    if 'session' in data and data['session']:
        print("User Login Check")
        #Check session against DB
        result = Users.query.filter_by(session=data['session']).first()
        #If there is a session and the date is the same return true, else destroy db session ID
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
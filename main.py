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
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root@localhost/ir_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

if __name__ == "__name__":
    with app.app_context():
        db.create_all()
    app.run()

"""""""""""""""""""""""""""""""""
DECORATORS
"""""""""""""""""""""""""""""""""
#Decorator to check session prior to function execution.
def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.get_json()
        session_id = data.get('session')

        if not session_id:
            return jsonify({"message": "User needs to login"}), 401

        # Check session against DB
        result = Users.query.filter_by(session=session_id).first()
        if not result:
            return jsonify({"message": "User needs to login"}), 401

        # Validate session date
        if str(result.last_login) == datetime.now().strftime("%Y-%m-%d") and result.enabled == 1:
            return func(*args, **kwargs)  # Proceed to the decorated function
        elif result.enabled != 1:
            return jsonify({"message": "The user has not been enabled yet"}), 403
        else:
            # Invalidate outdated session
            db.session.execute(
                text("UPDATE users SET session = NULL WHERE session = :session"),
                {"session": session_id}
            )
            db.session.commit()
            return jsonify({"message": "Session expired, please log in again"}), 401

    return wrapper

"""""""""""""""""""""""""""""""""
ASSET
"""""""""""""""""""""""""""""""""
# DELETE an asset from the asset database.
@app.delete("/asset/<int:asset_id>")
@auth_required
def delete_asset(asset_id):
    """
    # Authenticate and Authorise the request
    authenticate, response = validate_user()
    if not authenticate:
        return response
    """
    asset = Assets.query.get(asset_id)

    if not asset:
        return jsonify({"message": f"Asset with ID {asset_id} not found"}), 404

    try:
        db.session.delete(asset)
        db.session.commit()
        return jsonify({"message": f"Asset with ID {asset_id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete asset: {str(e)}"}), 500


#PATCH a record in the assets database.
@app.patch("/asset/<int:asset_id>")
@auth_required
def patch_asset(asset_id):
    result = Assets.query.filter_by(id=asset_id).first()

    if not result:
        return Response("No asset found", 404)

    data = request.get_json()

    if "name" in data:
        result.name = data["name"]
    if "category" in data:
        result.category = data["category"]
    if "filetype" in data:
        result.filetype = data["filetype"]
    if "filesize" in data:
        result.filesize = data["filesize"]
    if "link" in data:
        result.link = data["link"]
    if "screenshot" in data:
        result.screenshot = data["screenshot"]
    if "user_id" in data:
        result.user_id = data["user_id"]

    db.session.commit()

    return jsonify("Asset updated"), 200

# Add a new user to the Users database, requires only first_name, second_name, email and password.
@app.post("/asset")
@auth_required
def add_new_asset():
    try:
        data = request.get_json()

        name = data.get("name")
        category = data.get("category") or ""
        filetype = data.get("filetype") or ""
        filesize = data.get("filesize") or ""
        link = data.get("link") or ""
        screenshot = data.get("screenshot") or ""
        user_id = data.get("user_id") or ""

        if not name:
            return jsonify({"message": "Asset name required"}), 400

        new_asset = Assets(name=name, category=category, filetype=filetype, filesize=filesize, link=link, screenshot=screenshot, user_id=user_id)
        db.session.add(new_asset)
        db.session.commit()
        return jsonify({"message": "New asset added"}), 201
    except Exception as e:
        return jsonify({"message": "Asset not added - " + str(e)}), 404
    pass

"""""""""""""""""""""""""""""""""
ASSETS
"""""""""""""""""""""""""""""""""
@app.get("/assets")
@auth_required
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

"""""""""""""""""""""""""""""""""
LOGIN AND LOGOUT - USER
"""""""""""""""""""""""""""""""""
# Attempt to provide a user a SessionID based on their login credentials.
@app.put("/user/login")
def try_to_login():
    if request.data:
        data = request.get_json()
        if data.get("email") and data.get("password"):

            pass_hashed = sha256(data["password"].encode("utf-8")).hexdigest()

            #TODO: CHECK LOGIN DETAILS
            # This Session is a test session generated id, an update is required before live.
            session_id = sha256(("TestSessionID_" + data["email"]).encode("utf-8")).hexdigest()

            #Check if email and password at right
            result = Users.query.filter_by(email=data.get("email"), password=pass_hashed).first()
            if not result:
                return jsonify({"message": "Invalid Login"}), 400

            #TODO: ORM
            #Update database user with session
            db.session.execute(
                text("UPDATE users SET session = :session_id, last_login= :last_login WHERE email = :email AND password = :pass_hashed"),
                {"session_id": session_id, "email": data["email"], "pass_hashed": pass_hashed, "last_login": datetime.now()}
            )
            db.session.commit()

            #TODO: Update Session
            return jsonify({"session": session_id}), 200
        else:
            return jsonify({"message": "Invalid Input"}), 400
    else:
        return jsonify({"message": "Empty Input"}), 400

#Logs a user out based on the id in the users table
@app.put("/user/logout")
@auth_required
def log_user_out():
    if request.data:
        data = request.get_json()

        db.session.execute(
            text("UPDATE users SET session = NULL WHERE session = :session_id"),
            {"session_id": data.session}
        )
        db.session.commit()
        return jsonify({"message": "User logged out"}), 200
    else:
        return jsonify({"message": "Invalid Input"}), 400

"""""""""""""""""""""""""""""""""
PROJECT
"""""""""""""""""""""""""""""""""




"""""""""""""""""""""""""""""""""
PROJECTS
"""""""""""""""""""""""""""""""""
@app.get("/projects")
@auth_required
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


"""""""""""""""""""""""""""""""""
USER
"""""""""""""""""""""""""""""""""
# GET all of a users information, minus their password from the database.
@app.get("/user/<int:user_id>")
@auth_required
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
@auth_required
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
@auth_required
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
@auth_required
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

"""""""""""""""""""""""""""""""""
USERS
"""""""""""""""""""""""""""""""""
# GET a list of all users and their details. No password is returned.
@app.get("/users")
@auth_required
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




#REGISTER
@app.post("/user/register")
def register_user():
    pass




"""""""""""""""""""""""""""""""""
SEARCH
"""""""""""""""""""""""""""""""""
# TODO: Create Methods
# Return all projects or assets
@app.get('/search/<search_string>')
@auth_required
def get_search(search_string):
    pass


"""""""""""""""""""""""""""""""""
OTHER METHODS
"""""""""""""""""""""""""""""""""



""" 
# Old Validation method
# Validate user session
def validate_user():
    data = request.get_json()
    session_id = data.get('session')

    if not session_id:
        return False, jsonify({"message": "User needs to login"}), 404

    # Check session against DB
    result = Users.query.filter_by(session=session_id).first()
    if not result:
        return False, jsonify({"message": "User needs to login"}), 404

    # Validate session date
    if result.last_login == datetime.now().strftime("%Y-%m-%d"):
        return True, None
    else:
        # Invalidate outdated session
        db.session.execute(
            text("UPDATE users SET session = NULL WHERE session = :session"),
            {"session": session_id}
        )
        db.session.commit()
        return False, jsonify({"message": "Session expired, please log in again"}), 404
"""
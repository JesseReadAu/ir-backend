#INFORMATION
"""
Developer: Jesse Read
GitHub: JesseReadAu
Last Update: 2024/11/03
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
# DELETE an asset from the assets table.
@app.delete("/asset/<int:asset_id>")
@auth_required
def delete_asset(asset_id):
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

#PATCH a record in the assets table.
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

# Add a new asset to the assets table.
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
LOGIN, LOGOUT, REGISTER - USER
"""""""""""""""""""""""""""""""""
# Attempt to provide a user a SessionID based on their login credentials.
@app.put("/user/login")
def try_to_login():
    if request.data:
        data = request.get_json()
        if data.get("email") and data.get("password"):

            pass_hashed = sha256(data["password"].encode("utf-8")).hexdigest()

            # TODO: CHECK LOGIN DETAILS
            # This Session is a test session generated id, an update is required before live.
            session_id = sha256(("TestSessionID_" + data["email"]).encode("utf-8")).hexdigest()

            #Check if email and password at right
            result = Users.query.filter_by(email=data.get("email"), password=pass_hashed).first()
            if not result:
                return jsonify({"message": "Invalid Login"}), 400

            #TODO: ORM?
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

# Logs a user out based on the id in the users table.
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

# Register a user into the users table.
#TODO: Registrations needs to be tested.
@app.post("/user/register")
def register_user():
    if request.data:
        data = request.get_json()

        if data.get("email") and data.get("password"):
            # Hash the password
            pass_hashed = sha256(data["password"].encode("utf-8")).hexdigest()

            # Check if the email is already registered
            existing_user = Users.query.filter_by(email=data.get("email")).first()
            if existing_user:
                return jsonify({"message": "Email already registered"}), 400

            # Create a new user and add to the database
            new_user = Users(
            first_name = data.get("first_name", ""),
            last_name = data.get("last_name", ""),
            email = data["email"],
            password = pass_hashed,
            )

            db.session.add(new_user)
            db.session.commit()

            return jsonify({"message": "User registered successfully!"}), 201
        else:
            return jsonify({"message": "Invalid Input"}), 400
    else:
        return jsonify({"message": "An email and password are required"}), 400



"""""""""""""""""""""""""""""""""
PROJECT
"""""""""""""""""""""""""""""""""
# DELETE a project from the projects table.
@app.delete("/project/<int:project_id>")
@auth_required
def delete_project(project_id):

    asset = Assets.query.get(project_id)

    if not asset:
        return jsonify({"message": f"Project with ID {project_id} not found"}), 404

    try:
        db.session.delete(asset)
        db.session.commit()
        return jsonify({"message": f"Project with ID {project_id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete project: {str(e)}"}), 500

#PATCH a project in the projects table.
@app.patch("/project/<int:project_id>")
@auth_required
def patch_project(project_id):
    result = Projects.query.filter_by(id=project_id).first()

    if not result:
        return Response("No project found", 404)

    data = request.get_json()

    if "name" in data:
        result.name = data["name"]
    if "type" in data:
        result.category = data["type"]
    if "client" in data:
        result.filetype = data["filetype"]
    if "data_start" in data:
        result.filesize = data["filesize"]
    if "date_end" in data:
        result.link = data["link"]
    if "user_id" in data:
        result.user_id = data["user_id"]

    db.session.commit()

    return jsonify("Project updated"), 200

# Add a new project to the projects table.
@app.post("/project")
@auth_required
def add_new_project():
    try:
        data = request.get_json()

        name = data.get("name")
        type = data.get("type") or ""
        client = data.get("client") or ""
        data_start = data.get("data_start") or ""
        date_end = data.get("date_end") or ""
        user_id = data.get("user_id") or ""

        if not name:
            return jsonify({"message": "Project name required"}), 400

        new_project = Projects(name=name, type=type, client=client, data_start=data_start, date_end=date_end, user_id=user_id)
        db.session.add(new_project)
        db.session.commit()
        return jsonify({"message": "New project added"}), 201
    except Exception as e:
        return jsonify({"message": "Project not added - " + str(e)}), 404
    pass



"""""""""""""""""""""""""""""""""
PROJECT_ASSETS
"""""""""""""""""""""""""""""""""
# TODO: All project_assets methods have not been tested yet.
# Add a new record into the project_assets table.
@app.post("/project-assets/<int:project>/<int:asset>")
@auth_required
def add_new_project_assets(project, asset):
    try:
        project_assets = Project_Assets(project, asset)
        db.session.add(project_assets)
        db.session.commit()
        return jsonify({"message": "The project_assets data has been added to the table"})
    except Exception as e:
        return jsonify({"message": "Adding data into the project_assets table failed: " + str(e)}), 400

# Update a new record into the project_assets table using a PUT method.
@app.put("/project-assets/<int:id>")
@auth_required
def update_project_assets():
    data = request.get_json()
    result = Project_Assets.query.get(id)

    if not result:
        return jsonify({"message": "That project_asset id was not found."}), 400

    try:
        result.project = data['project']
        result.asset = data['asset']
        db.session.commit()
        return jsonify({"message": "The project_assets record with that ID has been updated"})
    except Exception as e:
        return jsonify({"message": "Updating data into the project_assets table failed: " + str(e)}), 400

# Delete a record into the project_assets table.
@app.delete("/project-assets/<int:id>")
@auth_required
def del_project_assets_record(id):
    result = Assets.query.get(id)

    if not result:
        return jsonify({"message": f"The project_assets with ID {id} not found"}), 404

    try:
        db.session.delete(result)
        db.session.commit()
        return jsonify({"message": f"The project_assets with ID {id} was deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete project_assets record: {str(e)}"}), 500



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
# GET all of a single users information, minus their password from the users table.
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

# PATCH a user record in the users table. Password is deleted from return json.
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

# Delete a user from the users table.
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

# Add a new user to the users table, requires only first_name, second_name, email and password.
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
# TODO: Add validation for the assets and projects table when they deal with project_assets.


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
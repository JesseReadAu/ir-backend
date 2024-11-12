Developer: Jesse Read

GitHub: JesseReadAu

Notes:  This is a RESTful backend being developed for the company IR as a proof of concept. It is interacted with
        from a REACT front end application.

# **Start-up Guide (Debugging, NOT FOR LIVE):**
1. Open folder in a terminal.
2. Install required packages, listed below.
3. Set up your SQL database - SQL Dump: https://github.com/JesseReadAu/ir-backend-sql
4. Enter the following command to start the application: "flask --app main run --debug"
5. Additional Information:

This application uses CORS. You will be required to change the CORS origin allowed list if you are not testing on the
current allowed list. A session header value is required for almost every http method, this is sent in the header when accessing 
an endpoint in the application. You will want to use the login endpoint to set up your session inside the database and then 
use that session in any test. The session is destroyed if used the following day, needing you to login again.

You can test if the backend is working with CORS by simply visiting the root endpoint which does not require a session.

# **Packages Required (and command for my team members):**
1. pip install flask
2. pip install mysql-connector-python
3. pip install flask_mysqlalchemy
4. pip install flask-cors

# **Relevant Terminal Commands:**
1. set FLASK_APP=main
2. flask --app main run --debug


# **Software Used:**
1. PyCharm
2. Postman
3. XAMMP - Apache, MySQL
4. FireFox (Network Tool)
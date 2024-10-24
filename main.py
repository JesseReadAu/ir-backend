#INFORMATION -- This is just confirmation that Github is working
"""
Developer: Jesse Read
GitHub: JesseReadAu
Last Update: 2024/10/25
Notes:  This is a RESTful backend being developed for the company IR as a proof of concept. It is interacted with
        from a REACT front end application.
"""


from flask import Flask, abort, request



#GLOBAL VARIABLES


#MAIN
app = Flask(__name__)

if __name__ == "__name__":
    app.run()

@app.get("/test/")
def test_method():
    return "Working"


#LOGIN


#REGISTER


#PROJECTS


#ASSETS


#SEARCH


#
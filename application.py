from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello Farts!"

@app.route("/bigfarts")
def hello():
    return "Hello BIG FARTS!"
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('timeline.html')

@app.route("/bigfarts")
def hellothere():
    return "Hello BIG FARTS!"
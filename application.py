from flask import Flask, render_template, request, jsonify
import json
import requests
import pyodbc
import pandas
import base64
import os
import datetime
import plaid
import json
import time
import jsonify

app = Flask(__name__)

@app.route("/")
def home():
  return render_template('home.html')

@app.route('/exercise')
def showform():
  return render_template('exerciseform.html')

@app.route('/exercisesubmit')
def showsetdata():
  exercise=request.args.get('exercise')
  reps=request.args.get('reps')
  date=request.args.get('date')
  weight=request.args.get('weight')
  set = {
    "Exercise": exercise,
    "Repetitions": reps,
    "Weight": weight,
    "Date": date
  }
  setjson = json.dumps(set)
  # conn = pyodbc.connect('Driver={SQL Server};'
  #                     'Server=optimizedliving.database.windows.net;'
  #                     'Database=PersonalData;'
  #                     'UID=jsandmann;'
  #                     'PWD=Ocarinaoftime0!;'
  #                     'Trusted_Connection=no;')

  # cursor = conn.cursor()
  # cursor.execute('SELECT * FROM Calls')
  # data = cursor.fetchall()
  # calls = pandas.DataFrame(data)
  # table = pandas.DataFrame.to_html(calls)
  return setjson

@app.route('/spotify')
def getlikedsongs():
  #Get authorization code
  code=request.args.get('code')
  url = "https://accounts.spotify.com/api/token"
  payload = "grant_type=authorization_code&code={}&redirect_uri=https://optimizedliving.azurewebsites.net/spotify&client_id=f703f57d46f34a7e9fffc4df3b4a9994&client_secret=1fe906d84e3e4a0db0812483390bbd8b".format(code)
  headers = {'Content-Type': "application/x-www-form-urlencoded"}
  response = requests.request("POST", url, data=payload, headers=headers)
  parsed_json=json.loads(response.text)
  access_token=parsed_json['access_token']
  url = "https://api.spotify.com/v1/me/tracks?next"
  headers = {'Authorization': "Bearer {}".format(access_token)}
  response = requests.request("GET", url, headers=headers)
  return render_template('success.html')
  #  Tracks = []
  # data = response.json()
  # Tracks = Tracks + data['items']
  # while data['next'] is not None:
  #     # print ('next page found, downloading',data['next'])
  #     response = requests.request("GET", data['next'], headers=headers)
  #     data = response.json()
  #     Tracks = Tracks + data['items']
  # print("We have", len(Tracks), "total results")

  # with open('music.json', 'w', encoding='utf-8') as f:
  #     json.dump(Tracks, f, ensure_ascii=False, indent=4)

@app.route('/fitbit')
def getfitnessdata():
  code=request.args.get('code')
  url = "https://api.fitbit.com/oauth2/token"
  querystring = {"code":code,"grant_type":"authorization_code","redirect_uri":"https://optimizedliving.azurewebsites.net/fitbit"}
  headers = {
    'Authorization': "Basic MjJCREszOjgyMGEzMmRjNzVkOGMxYWQ0OGUyYmFmNWVjMmYxN2Fk",
    'Content-Type': "application/x-www-form-urlencoded"
    }
  response = requests.request("POST", url, headers=headers, params=querystring)
  parsed_json=json.loads(response.text)
  access_token=parsed_json['access_token']
  url = "https://api.fitbit.com/1/user/-/activities/heart/date/1m/1d.json"
  headers = {'Authorization': "Bearer {}".format(access_token)}
  response = requests.request("GET", url, headers=headers)
  return 'Success', 200

@app.route('/fitbit/webhook', methods= ['GET'])
def verify():
  code = request.args.get('verify')
  if code == 'f794c3dec3d45019fee976fc44132bec58eb050bfbdd6f579363b2443a0f6bf3':
    return ('good',204)
  else: return ('bad',404)

@app.route('/timeline')
def showtimeline():
  return render_template('timeline.html')

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_PUBLIC_KEY = os.getenv('PLAID_PUBLIC_KEY')
PLAID_ENV = os.getenv('PLAID_ENV', 'development')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions')
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US,CA,GB,FR,ES')

client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, api_version='2019-05-29')


@app.route('/plaid')
def index():
  return render_template(
    'index.ejs',
    plaid_public_key=PLAID_PUBLIC_KEY,
    plaid_environment=PLAID_ENV,
    plaid_products=PLAID_PRODUCTS,
    plaid_country_codes=PLAID_COUNTRY_CODES,
  )

access_token = None
from flask import Flask, render_template, request, jsonify
import json
import requests

app = Flask(__name__)

@app.route("/")
def index():
  return render_template('home.html')

@app.route('/spotify')
def getlikedsongs():
  #Get authorization code
  code=request.args.get('code')
  url = "https://accounts.spotify.com/api/token"
  payload = "grant_type=authorization_code&code={}&redirect_uri=https://optimizedliving.azurewebsites.net/spotify&client_id=f703f57d46f34a7e9fffc4df3b4a9994&client_secret=1fe906d84e3e4a0db0812483390bbd8b".format(code)
  headers = {'Content-Type': "application/x-www-form-urlencoded"}
  response = requests.request("POST", url, data=payload, headers=headers)
  parsed_json=json.loads(response.text)
  token_type=parsed_json['token_type']
  scope=parsed_json['scope']
  expires_in=parsed_json['expires_in']
  access_token=parsed_json['access_token']
  url = "https://api.spotify.com/v1/me/tracks?next"
  headers = {'Authorization': "Bearer {}".format(access_token)}
  response = requests.request("GET", url, headers=headers)
  return render_template('success.html')
  #  Tracks = []
  # if response.status_code ==200:
  #     print('yaaaaaay success')
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
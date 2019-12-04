from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('home.html')

@app.route("/bigfarts")
def hellothere():
    return "Hello BIG FARTS!"

@app.route('/callback')
def getlikedsongs():
  #Get authorization code
  code=request.args.get('code')
  url = "https://accounts.spotify.com/api/token"
  payload = "grant_type=authorization_code&code={}&redirect_uri=https://optimizedliving.azurewebsites.net/callback&client_id=f703f57d46f34a7e9fffc4df3b4a9994&client_secret=1fe906d84e3e4a0db0812483390bbd8b".format(code)
  headers = {'Content-Type': "application/x-www-form-urlencoded"}
  response = requests.request("POST", url, data=payload, headers=headers)
  parsed_json=json.loads(response.text)
  print(parsed_json)
  token_type=parsed_json['token_type']
  scope=parsed_json['scope']
  expires_in=parsed_json['expires_in']
  access_token=parsed_json['access_token']
  return response
  #Get Tracks
#   Tracks = []
#   url = "https://api.spotify.com/v1/me/tracks?next"
#   headers = {'Authorization': "Bearer {}".format(access_token)}
#   response = requests.request("GET", url, headers=headers)
#   if response.status_code ==200:
#       print('yaaaaaay success')
#   data = response.json()
#   Tracks = Tracks + data['items']
#   while data['next'] is not None:
#       print ('next page found, downloading',data['next'])
#       response = requests.request("GET", data['next'], headers=headers)
#       data = response.json()
#       Tracks = Tracks + data['items']
#   print("We have", len(Tracks), "total results")
#   with open('music.json', 'w', encoding='utf-8') as f:
#       json.dump(Tracks, f, ensure_ascii=False, indent=4)
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
def index():
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
  conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=optimizedliving.database.windows.net;'
                      'Database=PersonalData;'
                      'UID=jsandmann;'
                      'PWD=Ocarinaoftime0!;'
                      'Trusted_Connection=no;')

  cursor = conn.cursor()
  cursor.execute('SELECT * FROM Calls')
  data = cursor.fetchall()
  calls = pandas.DataFrame(data)
  table = pandas.DataFrame.to_html(calls)
  return table

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

@app.route('/get_access_token', methods=['POST'])
def get_access_token():
  global access_token
  public_token = request.form['public_token']
  try:
    exchange_response = client.Item.public_token.exchange(public_token)
  except plaid.errors.PlaidError as e:
    return jsonify(format_error(e))

  pretty_print_response(exchange_response)
  access_token = exchange_response['access_token']
  return jsonify(exchange_response)

@app.route('/auth', methods=['GET'])
def get_auth():
  try:
    auth_response = client.Auth.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(auth_response)
  return jsonify({'error': None, 'auth': auth_response})

@app.route('/transactions', methods=['GET'])
def get_transactions():
  # Pull transactions for the last 30 days
  start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-30))
  end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
  try:
    transactions_response = client.Transactions.get(access_token, start_date, end_date)
  except plaid.errors.PlaidError as e:
    return jsonify(format_error(e))
  pretty_print_response(transactions_response)
  return jsonify({'error': None, 'transactions': transactions_response})

  @app.route('/identity', methods=['GET'])

def get_identity():
  try:
    identity_response = client.Identity.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(identity_response)
  return jsonify({'error': None, 'identity': identity_response})

@app.route('/balance', methods=['GET'])
def get_balance():
  try:
    balance_response = client.Accounts.balance.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(balance_response)
  return jsonify({'error': None, 'balance': balance_response})

@app.route('/accounts', methods=['GET'])
def get_accounts():
  try:
    accounts_response = client.Accounts.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(accounts_response)
  return jsonify({'error': None, 'accounts': accounts_response})

@app.route('/assets', methods=['GET'])
def get_assets():
  try:
    asset_report_create_response = client.AssetReport.create([access_token], 10)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(asset_report_create_response)

  asset_report_token = asset_report_create_response['asset_report_token']

  # Poll for the completion of the Asset Report.
  num_retries_remaining = 20
  asset_report_json = None
  while num_retries_remaining > 0:
    try:
      asset_report_get_response = client.AssetReport.get(asset_report_token)
      asset_report_json = asset_report_get_response['report']
      break
    except plaid.errors.PlaidError as e:
      if e.code == 'PRODUCT_NOT_READY':
        num_retries_remaining -= 1
        time.sleep(1)
        continue
      return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })

  if asset_report_json == None:
    return jsonify({'error': {'display_message': 'Timed out when polling for Asset Report', 'error_code': e.code, 'error_type': e.type } })

  asset_report_pdf = None
  try:
    asset_report_pdf = client.AssetReport.get_pdf(asset_report_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })

  return jsonify({
    'error': None,
    'json': asset_report_json,
    'pdf': base64.b64encode(asset_report_pdf),
  })

@app.route('/holdings', methods=['GET'])
def get_holdings():
  try:
    holdings_response = client.Holdings.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(holdings_response)
  return jsonify({'error': None, 'holdings': holdings_response})

@app.route('/investment_transactions', methods=['GET'])
def get_investment_transactions():
  # Pull transactions for the last 30 days
  start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-30))
  end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
  try:
    investment_transactions_response = client.InvestmentTransactions.get(access_token,
                                                                         start_date,
                                                                         end_date)
  except plaid.errors.PlaidError as e:
    return jsonify(format_error(e))
  pretty_print_response(investment_transactions_response)
  return jsonify({'error': None, 'investment_transactions': investment_transactions_response})

@app.route('/item', methods=['GET'])
def item():
  global access_token
  item_response = client.Item.get(access_token)
  institution_response = client.Institutions.get_by_id(item_response['item']['institution_id'])
  pretty_print_response(item_response)
  pretty_print_response(institution_response)
  return jsonify({'error': None, 'item': item_response['item'], 'institution': institution_response['institution']})

@app.route('/set_access_token', methods=['POST'])
def set_access_token():
  global access_token
  access_token = request.form['access_token']
  item = client.Item.get(access_token)
  return jsonify({'error': None, 'item_id': item['item']['item_id']})

def pretty_print_response(response):
  print(json.dumps(response, indent=2, sort_keys=True))

def format_error(e):
  return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type, 'error_message': e.message } }

if __name__ == '__main__':
    app.run(port=os.getenv('PORT', 5000))

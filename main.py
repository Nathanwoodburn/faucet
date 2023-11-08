from flask import Flask, make_response, redirect, request, jsonify, render_template, send_from_directory
import os
import dotenv
import requests
import gift
import json
import schedule
import time
from email_validator import validate_email, EmailNotValidError


app = Flask(__name__)
dotenv.load_dotenv()
address = 'hs1qr7d0xqsyatls47jf28gvm97twe8k606gspfpsz'

if os.getenv('address') != None:
    address = os.getenv('address')

#Assets routes
@app.route('/assets/<path:path>')
def send_report(path):
    return send_from_directory('templates/assets', path)



@app.route('/')
def index():
    params = request.args
    if 'r' in request.cookies:
        print("Referer: " + request.cookies['r'])
        return render_template('index.html', hidden=request.cookies['r'],address=address)


    if 'r' in params:
        print("Referer: " + params['r'])
        # Set cookie
        resp = make_response(render_template('index.html', hidden=params['r'],address=address))
        resp.set_cookie('r', params['r'], max_age=60*60*24)
        return resp
    return render_template('index.html',address=address)


@app.route('/', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    hidden = request.form['hi']
    ip = request.remote_addr

    if 'X-REAL-IP' in request.headers:
        ip = request.headers['X-REAL-IP']

    if 'X-Real-Ip' in request.headers:
        ip = request.headers['X-Real-Ip']

    if hidden == '':
        hidden = 'None'

    if 'r' in request.cookies:
        hidden = request.cookies['r']

    # Validate email
    try:
        emailinfo = validate_email(email, check_deliverability=False)
        email = emailinfo.normalized
    except EmailNotValidError as e:
        return render_template('error.html',error='Invalid email address',address=address)


    status = gift.gift(name, email, hidden, ip)
    print(status,flush=True)

    if status == True:
        return render_template('success.html',address=address)
    else:
        return render_template('error.html',error=status,address=address)

# Special routes
@app.route('/.well-known/wallets/<token>')
def send_wallet(token):
    address = requests.get('https://nathan.woodburn.au/.well-known/wallets/'+token).text
    return make_response(address, 200, {'Content-Type': 'text/plain'})

@app.route('/stats')
def stats():
    # Read the file
    path = '/data/gifts.json'
    if os.getenv('local') == 'true':
        path = './gifts.json'

    # Load file
    gifts = []
    if os.path.isfile(path):
        with open(path, 'r') as f:
            gifts = json.load(f)    

    # Loop through gifts
    referals = {}
    for gift_item in gifts:
        if gift_item['referer'] not in referals:
            referals[gift_item['referer']] = 1
        else:
            referals[gift_item['referer']] += 1
        
    statsHTML = 'Total gifts: ' + str(len(gifts)) + '<br><br>'
    statsHTML += 'Referals:<br>'
    for referal in referals:
        statsHTML += referal + ': ' + str(referals[referal]) + '<br>'


    statsHTML += '<br>Remaining balance: ' + str(gift.balance()) + ' HNS<br>'

    return render_template('stats.html',address=address,stats=statsHTML)

@app.route('/<path:path>')
def catch_all(path):
    # # If file exists, load it
    # if os.path.isfile('templates/' + path):
    #     return render_template(path)
    
    # # Try with .html
    # if os.path.isfile('templates/' + path + '.html'):
    #     return render_template(path + '.html')
    return redirect('/?r='+path)

# 404 catch all
@app.errorhandler(404)
def not_found(e):
    return redirect('/')

def update_address():
    global address
    payload = {
        "asset": "HNS",
        # "timestamp": 1699411892673,
        "timestamp": int(round(time.time() * 1000)),
        "receiveWindow": 10000
    }
    nbcookie = os.getenv('cookie')
    cookies = {"namebase-main": nbcookie}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    r = requests.post('https://www.namebase.io/api/v0/deposit/address', data=json.dumps(payload), headers=headers, cookies=cookies)
    address = r.json()['address']
    print("Address updated: " + address,flush=True)


update_address()

# Schedule address update every hour
schedule.every(1).hour.do(update_address)



if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')
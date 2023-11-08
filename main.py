from flask import Flask, make_response, redirect, request, jsonify, render_template, send_from_directory
import os
import dotenv
import requests
import gift
import json

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
    if 'r' in params:
        print("Referer: " + params['r'])
        return render_template('index.html', hidden=params['r'],address=address)

    return render_template('index.html',address=address)


@app.route('/', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    hidden = request.form['hi']
    ip = request.remote_addr

    if 'X-REAL-IP' in request.headers:
        print("X-REAL-IP",flush=True)
        ip = request.headers['X-REAL-IP']

    if 'X-Real-Ip' in request.headers:
        print("X-Real-Ip2",flush=True)
        ip = request.headers['X-Real-Ip']

    if hidden == '':
        hidden = 'None'

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
    for gift in gifts:
        if gift['referer'] not in referals:
            referals[gift['referer']] = 1
        else:
            referals[gift['referer']] += 1
        
    statsHTML = 'Total gifts: ' + str(len(gifts)) + '<br><br>'
    statsHTML += 'Referals:<br>'
    for referal in referals:
        statsHTML += referal + ': ' + str(referals[referal]) + '<br>'




    return render_template('stats.html',address=address,stats=statsHTML)

@app.route('/<path:path>')
def catch_all(path):
    # # If file exists, load it
    # if os.path.isfile('templates/' + path):
    #     return render_template(path)
    
    # # Try with .html
    # if os.path.isfile('templates/' + path + '.html'):
    #     return render_template(path + '.html')
    return redirect('/')

# 404 catch all
@app.errorhandler(404)
def not_found(e):
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')
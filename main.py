from flask import Flask, make_response, redirect, request, jsonify, render_template, send_from_directory
import os
import dotenv
import requests
import gift

app = Flask(__name__)
dotenv.load_dotenv()


#Assets routes
@app.route('/assets/<path:path>')
def send_report(path):
    return send_from_directory('templates/assets', path)



@app.route('/')
def index():
    params = request.args
    if 'r' in params:
        print("Referer: " + params['r'])
        return render_template('index.html', hidden=params['r'])

    return render_template('index.html')


@app.route('/', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    hidden = request.form['hi']
    ip = request.remote_addr
    if hidden == '':
        hidden = 'None'

    status = gift.gift(name, email, hidden, ip)
    print(status,flush=True)
    print(request.headers,flush=True)

    if status == True:
        return render_template('success.html')
    else:
        return render_template('error.html',error=status)

# Special routes
@app.route('/.well-known/wallets/<token>')
def send_wallet(token):
    address = requests.get('https://nathan.woodburn.au/.well-known/wallets/'+token).text
    return make_response(address, 200, {'Content-Type': 'text/plain'})


@app.route('/<path:path>')
def catch_all(path):
    # If file exists, load it
    if os.path.isfile('templates/' + path):
        return render_template(path)
    
    # Try with .html
    if os.path.isfile('templates/' + path + '.html'):
        return render_template(path + '.html')
    return redirect('/')

# 404 catch all
@app.errorhandler(404)
def not_found(e):
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')
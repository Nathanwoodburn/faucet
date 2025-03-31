import os
import dotenv
import json
import requests
import pyotp
import time


dotenv.load_dotenv()
loaded = False
gifts = []
nbcookie = os.getenv('cookie')
cookies = {"namebase-main": nbcookie}
nb_endpoint = "https://www.namebase.io/"

max_price = 5 # Max price to buy a domain at (in HNS)
previous_gifts = []
max_gifts_per_interval = 24 # Max gifts per interval
interval = 60*60*24 # 24 hours
EXPIRY_THRESHOLD = 144 * 35 # 35 days

if os.getenv('max_price') == 'true':
    max_price = int(os.getenv('max_price'))
if os.getenv('max_gifts_per_interval') == 'true':
    max_gifts_per_interval = int(os.getenv('max_gifts_per_interval'))
if os.getenv('interval') == 'true':
    interval = int(os.getenv('interval'))

def gift(name,email,referer, ip,api=False):
    global loaded
    global gifts
    global previous_gifts

    recent_gifts = 0
    for gift in previous_gifts:
        if gift['time'] > time.time() - interval:
            recent_gifts += 1

    if recent_gifts > max_gifts_per_interval and ip != os.getenv('admin_ip'):
        return "Too many gifts recently<br>Check back in a few minutes"

    print("Name: " + name,flush=True)
    print("Email: " + email,flush=True)
    print("Referer: " + referer,flush=True)
    print("IP: " + ip,flush=True)

    path = '/data/gifts.json'
    if os.getenv('local') == 'true':
        path = './gifts.json'
    
    # If the file doesn't exist, create it
    if not os.path.isfile(path):
        with open(path, 'w') as f:
            f.write('[]')
    
    # Load the file
    if not loaded:
        with open(path, 'r') as f:
            gifts = json.load(f)
        loaded = True
    
    # Check if the user has already submitted
    if ip != os.getenv('admin_ip') and not api:
        for gift in gifts:
            if gift['email'] == email:
                return "You have already submitted a gift request"
            if gift['ip'] == ip:
                return "You have already submitted a gift request"
        
    if api:
        for gift in gifts:
            if gift['email'] == email:
                return "You have already submitted a gift request"
            if gift['name'] == name:
                return "You have already submitted a gift request"

    # Add the user to the list
    gifts.append({
        'name': name,
        'email': email,
        'referer': referer,
        'ip': ip
    })

    previous_gifts.append({
        'time': time.time()
    })

    # Save the file
    with open(path, 'w') as f:
        json.dump(gifts, f)

    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    params = {"recipientEmail": email, "senderName": "Woodburn Faucet",
              "note": "Enjoy your free domain! - Woodburn Faucet"}

    names = requests.get(nb_endpoint + "/api/user/domains/owned?offset=0&sortKey=acquiredAt&sortDirection=desc&limit=100"
                         ,headers=headers, cookies=cookies)
    if names.status_code != 200:
        return "Error getting names:<br>" + names.text

    tmpnames = names.json()
    domain = None
    for name in tmpnames['domains']:
        if (name['expireBlock'] - tmpnames['currentHeight']) > EXPIRY_THRESHOLD:
            domain = name['name']
            break
    

    if domain == None:
        domains_market = requests.get(nb_endpoint + "/api/domains/marketplace?offset=0&buyNowOnly=true&sortKey=price&sortDirection=asc&exclude=%2Cnumbers%2Chyphens%2Cunderscores&maxLength=10&offersOnly=false"
                         ,headers=headers, cookies=cookies)
        if domains_market.status_code != 200:
            return "Error getting names:<br>" + domains_market.text
        
        domains_market = domains_market.json()
        if len(domains_market['domains']) == 0:
            return "No domains available to gift<br>Check back in a few minutes"
        
        listing = None
        for d in domains_market['domains']:
            if int(d['amount']) > max_price*1000000:
                continue
            data = requests.post("https://www.namebase.io/api/domains/search",headers=headers,json={"domains":[d['name']]}, cookies=cookies)
            if data.status_code != 200:
                return "Error getting names:<br>" + data.text
            data = data.json()
            if data['domains'][0]['domainInfo']['name'] != d['name']:
                return "Something weird happened<br>Check back in a few minutes"
            if (data['domains'][0]['domainInfo']['expireBlock'] - data['currentHeight']) > EXPIRY_THRESHOLD:
                domain = d['name']
                listing = d['id']
                break
        
        if domain == None:
            return "No domains available to gift<br>Check back in a few minutes"
        # Buy the domain
        print("Buying: " + domain,flush=True)

        payload = {
            "listingId": listing
        }
        buy = requests.post(nb_endpoint + "/api/v0/marketplace/"+domain+"/buynow",headers=headers,data=json.dumps(payload), cookies=cookies)
        if buy.status_code != 200:
            return "Error buying name:<br>" + buy.text
        
    
    print("Gifting: " + domain,flush=True)

    # Add this name to gifts record
    gifts[-1]['domain'] = domain

    # Save the file
    with open(path, 'w') as f:
        json.dump(gifts, f)



    send_name = requests.post(nb_endpoint + "/api/gift/" + domain.strip(),headers=headers,data=json.dumps(params), cookies=cookies)

    if send_name.status_code != 200:
        return "Error sending gift:<br>" + send_name.text

    discord(domain,email,ip,referer)

    return True

def balance():
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    user_info = requests.get(nb_endpoint + "/api/user",headers=headers, cookies=cookies)
    if user_info.status_code != 200:
        return "Error getting user info:<br>" + user_info.text
    user_info = user_info.json()
    hns_balance = user_info['hns_balance']
    hns_balance = int(hns_balance)/1000000
    return hns_balance

def discord(domain, email,ip,referer):
    url = os.getenv('discord_webhook')
    if url == None:
        return "No webhook set"
    
    payload = {
        "content": "New gift request: " + domain + "\nSent to " + email + "\nIP: " + ip + "\nReferer: " + referer
    }
    response = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

    # Check if the message was sent successfully
    if response.status_code == 204:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Status code: {response.status_code}")
        print(response.text)


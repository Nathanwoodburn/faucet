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


def gift(name,email,referer, ip):
    global loaded
    global gifts

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
    if ip != os.getenv('admin_ip'):
        for gift in gifts:
            if gift['email'] == email:
                return "You have already submitted a gift request"
            if gift['ip'] == ip:
                return "You have already submitted a gift request"
        
    # Add the user to the list
    gifts.append({
        'name': name,
        'email': email,
        'referer': referer,
        'ip': ip
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

    names = names.json()
    if len(names['domains']) == 0:
        domains_market = requests.get(nb_endpoint + "/api/domains/marketplace?offset=0&buyNowOnly=true&sortKey=price&sortDirection=asc&exclude=%2Cnumbers%2Chyphens%2Cunderscores&maxLength=10&offersOnly=false"
                         ,headers=headers, cookies=cookies)
        if domains_market.status_code != 200:
            return "Error getting names:<br>" + domains_market.text
        
        domains_market = domains_market.json()
        if len(domains_market['domains']) == 0:
            return "No domains available to gift<br>Check back in a few minutes"
        
        domain = domains_market['domains'][0]['name']
        print("Buying: " + domain,flush=True)
        price = int(domains_market['domains'][0]['ammount'])
        if price > max_price*1000000:
            return "Domain price too high<br>Check back in a few minutes"
        


        payload = {
            "listingId": domains_market['domains'][0]['id']
        }
        buy = requests.post(nb_endpoint + "/api/v0/marketplace/"+domain+"/buynow",headers=headers,data=json.dumps(payload), cookies=cookies)
        if buy.status_code != 200:
            return "Error buying name:<br>" + buy.text
        

    else:
        domain = names['domains'][0]['name']
    
    print("Gifting: " + domain,flush=True)

    # Add this name to gifts record
    gifts[-1]['domain'] = domain

    # Save the file
    with open(path, 'w') as f:
        json.dump(gifts, f)



    send_name = requests.post(nb_endpoint + "/api/gift/" + domain.strip(),headers=headers,data=json.dumps(params), cookies=cookies)

    if send_name.status_code != 200:
        return "Error sending gift:<br>" + send_name.text


    return True
import os
import dotenv
import json

dotenv.load_dotenv()
loaded = False
gifts = []

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
    for gift in gifts:
        if gift['email'] == email:
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

    return True
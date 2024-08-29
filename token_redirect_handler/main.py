import base64
import hashlib
import json
import string

from dotenv import load_dotenv
from flask import Flask, redirect, request, session
import requests
from requests import post
from spotipy.oauth2 import SpotifyOAuth
import os
import requests
app = Flask(__name__)



app = Flask(__name__)
app.config['SESSION_COOKIE_TYPE'] = 'spoti cookie'

load_dotenv()
CLIENT_ID = str(os.getenv("CLIENT_ID"))
CLIENT_SECRET = str(os.getenv("CLIENT_SECRET"))
app.secret_key = str(os.getenv("SECRET_KEY"))
bot_token = str(os.getenv("BOT_TOKEN"))

spotify_redirect_uri = 'http://bitesaitzz.pythonanywhere.com/callback'

def get_token():
    auth_str = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_str.encode("utf-8")
    encoded_str = base64.b64encode(auth_bytes)

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + str(encoded_str, "utf-8"),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.text)
    print(json_result)

    token = json_result['access_token']
    return token

def generate_random_string(length):
    possible = string.ascii_letters + string.digits
    return ''.join(possible[os.urandom(1)[0] % len(possible)] for _ in range(length))

def sha256(plain):
    return hashlib.sha256(plain.encode('utf-8')).hexdigest()
def base64encode(input):
    encoded = base64.b64encode(input.encode())
    return encoded.decode().replace('=', '').replace('+', '-').replace('/', '_')
#get_token()
key = generate_random_string(64)
hash_key = sha256(key)
key_challenge = base64encode(key)







@app.route('/')
def home():
    # Get the client_id and chat_id from the URL
    client_id = request.args.get('client_id')
    chat_id = request.args.get('chatid')
    if client_id and chat_id:
        # Store chat_id in session for later use
        session['chat_id'] = chat_id
        client_id = CLIENT_ID
        # Redirect to Spotify authorization page
        scope = "user-top-read playlist-read-private playlist-read-collaborative playlist-modify-public user-library-read user-read-recently-played user-read-playback-state"
        sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=CLIENT_SECRET, redirect_uri=spotify_redirect_uri, scope=scope, username=chat_id)
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    else:
        return 'No client_id or chat_id found in the URL'

@app.route('/callback')
def callback():
    # Get the code from the redirect URL
    code = request.args.get('code')
    if code:
        # Get chat_id from session
        chat_id = session.get('chat_id')

        # Send the code to the Telegram bot
        text = f'Code: {code}'
        send_message_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        params = {
            'chat_id': chat_id,
            'text': text
        }
        response = requests.post(send_message_url, data=params)
        if response.status_code == 200:

             return redirect('https://t.me/wrapped_stats_bot')
        else:

            return redirect('https://t.me/wrapped_stats_bot')
    else:
        return 'No code found in the URL'

if __name__ == '__main__':
    app.run(debug=True)





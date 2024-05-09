from datetime import datetime
from flask import Flask, render_template, request, redirect, jsonify, session
import json
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import urllib.parse
import requests

app = Flask(__name__)
app.secret_key = '9d4acba3-f890-c8c0-7058-300e49fd5598'

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

redirect_uri = 'http://127.0.0.1:5000/callback'

auth_url = 'https://accounts.spotify.com/authorize'
toekn_url = "https://accounts.spotify.com/api/token"
base_url =  "https://api.spotify.com/v1/"

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization" : "Basic " + auth_base64,
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    data = {"grant_type" : "client_credentials"}

    result = post(url, headers=headers, data=data)

    json_result = json.loads(result.content)

    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization" : "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"q={artist_name}&type=artist&limit=1"

    query_url = url + "?" + query

    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)  ["artists"]["items"]
    if not len(json_result):
        print("No artist")
        return None
    return json_result[0]

def get_playlist_tracks(token, playlist_id):
    url = f"{base_url}" + f"{playlist_id}/tracks"
    query = f"limit=10"
    query_url = url + "?" + query
    header = get_auth_header

    result = get(query_url, headers=header)

    json_result = json.loads(result.content) 

    return json['items']

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)  ["tracks"]
    return json_result

@app.route('/')
def index():
    return "Welcome to Discoverify <a href='/login'> Login with spotify</a>"


@app.route('/login')
def login():
    scope = 'user-read-private user-read-email playlist-read-private'

    params = {
        'client_id' : client_id,
        'response_type' : 'code',
        'scope' : scope,
        'redirect_uri' : redirect_uri,
        'show_dialog' : True
    }

    auth_urll = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(auth_urll)


@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error" : request.args['error']})
    if 'code' in request.args:
        req_body = {
            'code' : request.args['code'],
            'grant_type' : 'authorization_code',
            'redirect_uri' : redirect_uri,
            'client_id' : client_id,
            'client_secret' : client_secret
        }

        response = requests.post(toekn_url, data=req_body)

        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

        return redirect('/playlists')

@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    header = get_auth_header(session['access_token'])

    response = requests.get(base_url + 'me/playlists', headers=header)
    playlists = response.json()
    #tracks = get_playlist_tracks(session['access_token'], playlists['items'][0]['id'])
    return render_template('/playlist', playlist=playlists['items'][0]) #, songs=tracks
    return jsonify(playlists) 


@app.route('/refersh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type' : 'refresh_token',
            'refresh_token' : refresh_token,
            'client_id' : client_id,
            'client_secret' : client_secret
        }

        response = request.post(toekn_url, data=req_body)

        new_token = response.json()

        session['access_token'] = new_token['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token['expires_in']

        return redirect('/playlists')

def artist():
    token = get_token()
    result = search_for_artist(token, "Juice Wrld")
    print(result)
    artist_id = result["id"]
    song = get_songs_by_artist(token, artist_id)
    songs = set()
    for idx, son in enumerate(song):
        songs.add(son['name'])
    return render_template('testt.html', songs=songs)

"""
def search_page():
  joke_response = "LOL" #str(requests.request("GET", url + random_joke, headers=headers).json()['text'])
  return render_template('testt.html', joke=joke_response)

@app.route('/search')
def get_recipes():
  if (str(request.args['ingridients']).strip() != ""):
      # If there is a list of ingridients -> list
      querystring = {"number":"10","ranking":"1","ignorePantry":"false","ingredients":request.args['ingridients']}
      querystring1 = {"number":"1","ranking":"1","ignorePantry":"false","ingredients":request.args['ingridients']}

      response = requests.request("GET", url + find, headers=headers, params=querystring).json()
      i = 0
      while i < len(response):
        recipe_info_endpoint = "recipes/{0}/information".format(response[i]['id'])
        veg = requests.request("GET", url + recipe_info_endpoint, headers=headers).json()

        if veg['vegetarian'] == False:
          response.pop(i)
        i+=1
      if len(response) == 0:
         return render_template('error.html')
      return render_template('search.html', recipes=response)
  else:
    # Random recipes
    querystring = {"number":"5"}
    response = requests.request("GET", url + randomFind, headers=headers, params=querystring).json()
    print(response)
    return render_template('search.html')
"""
if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
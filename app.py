from flask import Flask, render_template, request
import json
from dotenv import load_dotenv
import os
import base64
from requests import post, get
app = Flask(__name__)

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

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

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)  ["tracks"]
    return json_result

@app.route('/')
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
  app.run()
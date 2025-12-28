from datetime import datetime
from flask import Flask, render_template, request, redirect, jsonify, session
import json
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import urllib.parse
import requests
import statistics

app = Flask(__name__)
load_dotenv()

app.secret_key = os.getenv("SECRET_KEY", os.urandom(24).hex())

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

redirect_uri = 'http://127.0.0.1:5000/callback'

auth_url = 'https://accounts.spotify.com/authorize'
token_url = "https://accounts.spotify.com/api/token"
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
    """Get all tracks from a playlist with pagination"""
    url = f"{base_url}playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    all_tracks = []
    offset = 0
    limit = 100
    
    while True:
        query_params = {
            'limit': limit,
            'offset': offset,
            'fields': 'items(track(id,name,artists,album,external_urls))'
        }
        query_url = url + "?" + urllib.parse.urlencode(query_params)
        
        result = get(query_url, headers=headers)
        if result.status_code != 200:
            break
            
        json_result = result.json()
        items = json_result.get('items', [])
        
        if not items:
            break
            
        all_tracks.extend([item['track'] for item in items if item.get('track')])
        offset += limit
        
        if len(items) < limit:
            break
    
    return all_tracks

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)  ["tracks"]
    return json_result

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    scope = 'user-read-private user-read-email playlist-read-private playlist-read-collaborative user-top-read'

    params = {
        'client_id' : client_id,
        'response_type' : 'code',
        'scope' : scope,
        'redirect_uri' : redirect_uri,
        'show_dialog' : True
    }

    auth_url_full = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url_full)


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

        response = requests.post(token_url, data=req_body)

        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

        return redirect('/playlists')

def is_token_expired():
    """Check if access token is expired"""
    if 'expires_at' not in session:
        return True
    return datetime.now().timestamp() >= session['expires_at']

def refresh_access_token():
    """Refresh the access token using refresh token"""
    if 'refresh_token' not in session:
        return False
    
    req_body = {
        'grant_type': 'refresh_token',
        'refresh_token': session['refresh_token'],
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(token_url, data=req_body)
    
    if response.status_code == 200:
        token_info = response.json()
        session['access_token'] = token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
        if 'refresh_token' in token_info:
            session['refresh_token'] = token_info['refresh_token']
        return True
    return False

@app.route('/playlists')
def get_playlists():
    """Display all user playlists for selection"""
    if 'access_token' not in session:
        return redirect('/login')
    
    if is_token_expired():
        if not refresh_access_token():
            return redirect('/login')

    headers = get_auth_header(session['access_token'])
    
    # Get user playlists with pagination
    all_playlists = []
    url = base_url + 'me/playlists'
    offset = 0
    limit = 50
    
    while True:
        params = {'limit': limit, 'offset': offset}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            break
            
        playlists_data = response.json()
        items = playlists_data.get('items', [])
        
        if not items:
            break
            
        all_playlists.extend(items)
        offset += limit
        
        if len(items) < limit:
            break
    
    return render_template('playlists.html', playlists=all_playlists) 


@app.route('/refresh-token')
def refresh_token_route():
    """Route to refresh token"""
    if refresh_access_token():
        return redirect('/playlists')
    return redirect('/login')

def get_audio_features(token, track_ids):
    """Get audio features for multiple tracks"""
    headers = get_auth_header(token)
    all_features = []
    
    # Spotify API allows up to 100 track IDs per request
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i+100]
        ids_param = ','.join(batch)
        url = f"{base_url}audio-features?ids={ids_param}"
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            features_data = response.json()
            all_features.extend(features_data.get('audio_features', []))
    
    return [f for f in all_features if f is not None]

def calculate_playlist_features(audio_features):
    """Calculate average audio features from playlist tracks"""
    if not audio_features:
        return None
    
    feature_keys = ['danceability', 'energy', 'key', 'loudness', 'mode', 
                   'speechiness', 'acousticness', 'instrumentalness', 
                   'liveness', 'valence', 'tempo']
    
    avg_features = {}
    for key in feature_keys:
        values = [f[key] for f in audio_features if f and key in f]
        if values:
            avg_features[key] = statistics.mean(values)
    
    return avg_features

def find_recommendations(token, seed_features, limit=20, exclude_track_ids=None):
    """Find track recommendations based on audio features"""
    if not seed_features:
        return []
    
    headers = get_auth_header(token)
    exclude_track_ids = exclude_track_ids or []
    
    # Use Spotify's recommendations API
    # Note: We need seed tracks, artists, or genres. Let's use a hybrid approach.
    url = f"{base_url}recommendations"
    
    # Build query parameters from average features
    params = {
        'limit': limit,
        'target_danceability': seed_features.get('danceability', 0.5),
        'target_energy': seed_features.get('energy', 0.5),
        'target_valence': seed_features.get('valence', 0.5),
        'target_tempo': seed_features.get('tempo', 120),
        'target_acousticness': seed_features.get('acousticness', 0.5),
        'target_instrumentalness': seed_features.get('instrumentalness', 0.5),
        'target_liveness': seed_features.get('liveness', 0.5),
        'target_speechiness': seed_features.get('speechiness', 0.5),
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        recommendations = response.json()
        tracks = recommendations.get('tracks', [])
        # Filter out tracks that are already in the playlist
        filtered_tracks = [t for t in tracks if t['id'] not in exclude_track_ids]
        return filtered_tracks
    
    return []

@app.route('/analyze/<playlist_id>')
def analyze_playlist(playlist_id):
    """Analyze a playlist and get recommendations"""
    if 'access_token' not in session:
        return redirect('/login')
    
    if is_token_expired():
        if not refresh_access_token():
            return redirect('/login')
    
    token = session['access_token']
    headers = get_auth_header(token)
    
    # Get playlist info
    playlist_url = f"{base_url}playlists/{playlist_id}"
    playlist_response = requests.get(playlist_url, headers=headers)
    
    if playlist_response.status_code != 200:
        return render_template('error.html', message="Could not fetch playlist")
    
    playlist_data = playlist_response.json()
    
    # Get all tracks from playlist
    tracks = get_playlist_tracks(token, playlist_id)
    
    if not tracks:
        return render_template('error.html', message="Playlist is empty")
    
    # Extract track IDs
    track_ids = [t['id'] for t in tracks if t and t.get('id')]
    existing_track_ids = set(track_ids)
    
    if not track_ids:
        return render_template('error.html', message="No valid tracks found in playlist")
    
    # Get audio features
    audio_features = get_audio_features(token, track_ids)
    
    if not audio_features:
        return render_template('error.html', message="Could not fetch audio features")
    
    # Calculate average features
    avg_features = calculate_playlist_features(audio_features)
    
    if not avg_features:
        return render_template('error.html', message="Could not calculate playlist features")
    
    # Get recommendations - we need seed tracks for better recommendations
    # Get recommendations using seed tracks (up to 5)
    seed_tracks = track_ids[:min(5, len(track_ids))]  # Spotify allows max 5 seed tracks
    seed_tracks_param = ','.join(seed_tracks)
    
    recommendations_url = f"{base_url}recommendations"
    rec_params = {
        'seed_tracks': seed_tracks_param,
        'limit': 30,
        'target_danceability': avg_features.get('danceability', 0.5),
        'target_energy': avg_features.get('energy', 0.5),
        'target_valence': avg_features.get('valence', 0.5),
        'target_tempo': avg_features.get('tempo', 120),
        'target_acousticness': avg_features.get('acousticness', 0.5),
    }
    
    rec_response = requests.get(recommendations_url, headers=headers, params=rec_params)
    
    recommendations = []
    if rec_response.status_code == 200:
        rec_data = rec_response.json()
        all_recs = rec_data.get('tracks', [])
        # Filter out tracks already in playlist
        recommendations = [t for t in all_recs if t['id'] not in existing_track_ids][:20]
    
    return render_template('recommendations.html', 
                         playlist=playlist_data,
                         tracks=tracks[:10],  # Show first 10 tracks from playlist
                         recommendations=recommendations,
                         features=avg_features)

@app.route('/logout')
def logout():
    """Log out user"""
    session.clear()
    return redirect('/')

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
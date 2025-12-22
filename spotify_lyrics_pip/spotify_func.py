import json, os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def load_spotify_config():
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    """config_spotify.json에서 Spotify 설정 정보를 로드"""
    with open(os.path.join(workspace_dir, 'config_spotify.json'), 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def configure_spotify():
    """Spotify API 클라이언트를 설정하고 반환"""
    config = load_spotify_config()
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=config['SPOTIFY_CLIENT_ID'],
        client_secret=config['SPOTIFY_CLIENT_SECRET'],
        redirect_uri=config['SPOTIFY_REDIRECT_URI'],
        scope='user-read-currently-playing user-read-playback-state'
    ))
    
    return sp

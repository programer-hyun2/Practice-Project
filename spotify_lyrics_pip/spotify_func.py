import json, os
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def get_auth_cache_path():
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(workspace_dir, '.cache-spotify')


def clear_auth_cache():
    cache_path = get_auth_cache_path()
    if os.path.exists(cache_path):
        os.remove(cache_path)


def is_refresh_token_revoked_error(error):
    error_text = str(error)
    return 'invalid_grant' in error_text and 'Refresh token revoked' in error_text

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
        scope='user-read-currently-playing user-read-playback-state',
        cache_path=get_auth_cache_path()
    ))
    
    return sp

def verify_spotify_login(sp):
    """Spotify 로그인 상태를 확인하고 결과를 반환"""
    if sp is None:
        return False, "Spotify 클라이언트가 초기화되지 않았습니다."

    try:
        user = sp.current_user()
        if user and user.get('id'):
            display_name = user.get('display_name') or user.get('id')
            return True, f"Spotify 로그인 성공: {display_name}"
        return False, "Spotify 로그인 정보를 가져오지 못했습니다."
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 401:
            return False, "Spotify 인증이 만료되었거나 잘못되었습니다. 다시 로그인해 주세요."
        return False, f"Spotify 로그인 확인 실패 (HTTP {e.http_status})"
    except Exception as e:
        if is_refresh_token_revoked_error(e):
            clear_auth_cache()
            return False, "리프레시 토큰이 폐기되어 인증 캐시를 초기화했습니다. 앱을 다시 실행해 Spotify 재로그인해 주세요."
        return False, f"Spotify 로그인 확인 중 오류: {type(e).__name__}: {e}"

def get_current_song(sp):
    """현재 재생 중인 곡 정보 가져오기 (오류/상태 메시지 포함)"""
    if sp is None:
        return None, None, None, None, None, None, "Spotify 연결이 초기화되지 않았습니다."

    try:
        current_track = sp.current_user_playing_track()
        if current_track is not None and current_track['item'] is not None:
            track_name = current_track['item']['name']
            artist_name = current_track['item']['artists'][0]['name']
            album_name = current_track['item']['album']['name']
            progress_ms = current_track['progress_ms']
            duration_ms = current_track['item']['duration_ms']
            return track_name, artist_name, album_name, progress_ms, duration_ms, None, None

        return None, None, None, None, None, None, "현재 재생 중인 곡이 없습니다. Spotify에서 음악을 재생해 주세요."
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 429:
            retry_after = int(e.headers.get('Retry-After', 5))
            return None, None, None, None, None, retry_after, f"Spotify 요청 제한 중입니다. {retry_after}초 후 재시도합니다."
        if e.http_status == 401:
            return None, None, None, None, None, None, "Spotify 인증이 만료되었거나 잘못되었습니다. 다시 로그인해 주세요."
        return None, None, None, None, None, None, f"Spotify API 오류 (HTTP {e.http_status})"
    except Exception as e:
        if is_refresh_token_revoked_error(e):
            clear_auth_cache()
            return None, None, None, None, None, None, "리프레시 토큰이 폐기되어 인증 캐시를 초기화했습니다. 앱을 다시 실행해 Spotify 재로그인해 주세요."
        return None, None, None, None, None, None, f"Spotify 정보 조회 오류: {type(e).__name__}: {e}"

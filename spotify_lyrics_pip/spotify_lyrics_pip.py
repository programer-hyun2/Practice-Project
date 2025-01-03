import sys, spotipy, lyricsgenius, json, re, time
from spotipy.oauth2 import SpotifyOAuth
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
# json API parsing
with open('config_spotify.json', 'r') as f:
    config_spotify = json.load(f)
    SPOTIFY_CLIENT_ID = config_spotify['SPOTIFY_CLIENT_ID']
    SPOTIFY_CLIENT_SECRET = config_spotify['SPOTIFY_CLIENT_SECRET']
    SPOTIFY_REDIRECT_URI = config_spotify['SPOTIFY_REDIRECT_URI']
    GENIUS_API_TOKEN = config_spotify['GENIUS_API_TOKEN']
# Spotify Client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT_URI, scope = "user-read-currently-playing"))
# Genius Client
genius = lyricsgenius.Genius(GENIUS_API_TOKEN)
# Get current song information
def get_current_song():
    try:
        current_track = sp.current_user_playing_track()
        if current_track is not None:
            track_name = current_track['item']['name']
            artist_name = current_track['item']['artists'][0]['name']
            progress_ms = current_track['progress_ms']
            track_duration = current_track['item']['duration_ms']
            return track_name, artist_name, progress_ms, track_duration
        return None, None, None, None
    except Exception as e:
        print(f"오류 발생: {e}")
        return None, None, None, None
# Get lyrics
def get_lyrics(track_name, artist_name, track_duration):
    if not (track_name and artist_name):
        return [("현재 재생 중인 곡이 없습니다.", 0)]
    
    try:
        song = genius.search_song(track_name, artist_name)# Serach song from Genius
        if not song:
            return [("가사를 찾을 수 없습니다.", 0)]
        lyrics_ = song.lyrics.splitlines()
        
        lyrics_lines = [line for line in lyrics_ if not re.search(r'\[', line, re.IGNORECASE)]
        filtered_lyrics = []
        timestamps = []
        
        timestamp_interval = (track_duration/1000) / len(lyrics_lines) # Calculate timestamp interval

        for i, line in enumerate(lyrics_lines):
            if line:
                filtered_lyrics.append(line)
                timestamps.append(i * timestamp_interval)
        
        return list(zip(filtered_lyrics, timestamps))
    except Exception as e:
        print(f"오류 발생: {e}")
        return [("가사를 찾을 수 없습니다.", 0)]
# PyQt5 Lyrics Widget
class LyricsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.lyrics_ = []
        self.current_song = None
        self.init_ui()
        self.drag_active = False

    def init_ui(self):
        self.setWindowTitle('Spotify Lyrics')
        self.setGeometry(100, 100, 400, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.lyrics_label = QLabel(self)
        self.lyrics_label.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.lyrics_label.setFont(QFont('Arial', 14, QFont.Bold))
        self.lyrics_label.setStyleSheet('color: white')

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(10)
        shadow_effect.setColor(Qt.black)
        shadow_effect.setOffset(2, 2)
        self.lyrics_label.setGraphicsEffect(shadow_effect)

        layout = QVBoxLayout()
        layout.addWidget(self.lyrics_label)
        self.setLayout(layout)

        self.timer_lyrics = QTimer(self)
        self.timer_lyrics.timeout.connect(self.update_lyrics)
        self.timer_lyrics.start(100)

        self.song_change_timer = QTimer(self)
        self.song_change_timer.timeout.connect(self.check_song_change)
        self.song_change_timer.start(100)

    def update_lyrics(self):
        track_name, artist_name, progress_ms, track_duration = get_current_song()
        if not self.lyrics_:
            self.lyrics_ = get_lyrics(track_name, artist_name, track_duration)
        current_time = progress_ms / 1000
        display_lyrics = []

        for line, timestamp in self.lyrics_:
            if not line.strip():
                continue
            if timestamp -12 <= current_time <= timestamp + 12:
                display_lyrics.append(line)
        if not display_lyrics:
            for i, (line, timestamp) in enumerate(self.lyrics_):
                if timestamp > current_time:
                    break
            start_index = max(0, i-12)
            end_index = min(len(self.lyrics_), i+13)
            display_lyrics = [line for line, _ in self.lyrics_[start_index:end_index]]
        self.lyrics_label.setText('\n'.join(display_lyrics))
    # Check song change
    def check_song_change(self):
        track_name, artist_name, _, _ = get_current_song()
        current_song = (track_name, artist_name)
        if current_song != self.current_song:
            self.current_song = current_song
            self.lyrics_ = []
            self.update_lyrics()

    def show_now_playing(self):
        track_name, artist_name = self.current_song
        self.timer_lyrics.stop()
        self.song_change_timer.stop()
        self.lyrics_label.setText(f"Now Playing : {track_name} - {artist_name}")
        time.sleep(3)
        self.timer_lyrics.start(100)
        self.song_change_timer.start(100)
        

    # Dragging event------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_active = True
            self.old_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_active and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.old_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_active = False
            event.accept()
    # Double click event-------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.show_now_playing()
            event.accept()    
# Main
def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    widget = LyricsWidget()
    widget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
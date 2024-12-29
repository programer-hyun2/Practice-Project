import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import lyricsgenius
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont
import re

# Spotify API 설정
SPOTIFY_CLIENT_ID = "your client id"
SPOTIFY_CLIENT_SECRET = "your client secret"
SPOTIFY_REDIRECT_URI = "http://localhost:8888/callback"

# Genius API 설정
GENIUS_API_TOKEN = "your genius api token"

# Spotify 클라이언트 생성
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-currently-playing"
))

# Genius 클라이언트 생성
genius = lyricsgenius.Genius(GENIUS_API_TOKEN)

# 현재 재생 중인 곡 정보 가져오기
def get_current_song():
    try:
        current_track = sp.current_user_playing_track()
        if current_track is not None:
            track_name = current_track['item']['name']
            artist_name = current_track['item']['artists'][0]['name']
            is_playing = current_track['is_playing']
            progress_ms = current_track['progress_ms']
            track_duration = current_track['item']['duration_ms']
            return track_name, artist_name, is_playing, progress_ms, track_duration
        return None, None, None, None, None
    except Exception as e:
        print(f"오류 발생: {e}")
        return None, None, None, None, None

def get_lyrics():
    track_name, artist_name, _, _, track_duration = get_current_song()
    if not (track_name and artist_name):
        return [("현재 재생 중인 곡이 없습니다.", 0)]

    try:
        # Genius에서 곡 검색
        song = genius.search_song(track_name, artist_name)
        if not song:
            return [("가사를 찾을 수 없습니다.", 0)]

        lyrics_lines = song.lyrics.splitlines()
        filtered_lyrics = []
        timestamps = []

        # 전체 곡 길이를 기반으로 타임스탬프 계산
        total_duration_sec = track_duration / 1000  # ms를 초로 변환
        
        # 가사 처리
        valid_lines = [line for line in lyrics_lines if not re.search(r"\[", line, re.IGNORECASE)]
        if not valid_lines:
            return [("가사 형식을 처리할 수 없습니다.", 0)]

        interval = total_duration_sec / len(valid_lines)
        
        # 가사와 타임스탬프 매칭
        for i, line in enumerate(valid_lines):
            if line.strip():  # 빈 줄 제외
                filtered_lyrics.append(line)
                timestamps.append(int(i * interval))

        return list(zip(filtered_lyrics, timestamps))

    except Exception as e:
        print(f"가사 처리 중 오류 발생: {e}")
        return [("가사를 가져오는 중 오류가 발생했습니다.", 0)]


# PyQt5 UI 설정
class LyricsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.lyrics_with_timestamps = []
        self.lyrics_ = []
        self.current_song = None  # 현재 재생 중인 곡 추가
        self.init_ui()
        self.drag_active = False
        self.update_lyrics()

    def init_ui(self):
        # 기존 UI 설정 유지
        self.setWindowTitle("Spotify Lyrics Viewer")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 기존 가사 레이블 설정 유지
        self.lyrics_label = QLabel(self)
        self.lyrics_label.setAlignment(Qt.AlignCenter)
        self.lyrics_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.lyrics_label.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
        """)

        # 그림자 효과는 유지
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(8)
        shadow_effect.setXOffset(2)
        shadow_effect.setYOffset(2)
        shadow_effect.setColor(Qt.black)
        self.lyrics_label.setGraphicsEffect(shadow_effect)
        
        layout = QVBoxLayout()
        layout.addWidget(self.lyrics_label)
        self.setLayout(layout)
        
        # 가사 업데이트 타이머 간격을 100ms로 단축
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_lyrics)
        self.timer.start(100)  # 100ms 간격으로 변경

        # 곡 변경 감지 타이머 추가
        self.song_change_timer = QTimer(self)
        self.song_change_timer.timeout.connect(self.check_for_song_change)
        self.song_change_timer.start(100)  # 100ms마다 체크

    def check_for_song_change(self):
        track_name, artist_name, _, _, _ = get_current_song()
        current_song = (track_name, artist_name)
        if current_song != self.current_song:
            self.current_song = current_song
            self.lyrics_ = []  # 가사 초기화
            self.update_lyrics()  # 새로운 곡의 가사로 업데이트

    def update_lyrics(self):
        
        track_name, artist_name, is_playing, progress_ms, _ = get_current_song()
        
        if track_name and artist_name:
            if not self.lyrics_:
                self.lyrics_ = get_lyrics()
            
            if self.lyrics_:
                current_time = progress_ms // 1000
                lyrics_to_display = []

                # 현재 시간에 맞는 가사만 표시
                for line, timestamp in self.lyrics_:
                    if not line.strip():
                        continue
                    if timestamp - 12 <= current_time < timestamp + 12:
                        lyrics_to_display.append(line)
                
                # 표시할 가사가 없으면 현재 시점 전후로 가사 표시
                if not lyrics_to_display:
                    for i, (line, timestamp) in enumerate(self.lyrics_):
                        if current_time < timestamp:
                            break
                    start_index = max(0, i - 12)
                    end_index = min(len(self.lyrics_), i + 13)
                    lyrics_to_display = [line for line, _ in self.lyrics_[start_index:end_index]]
                
                self.lyrics_label.setText("\n".join(lyrics_to_display))
                self.setWindowTitle("▶ 재생 중" if is_playing else "⏸ 일시 정지 중")
            else:
                self.lyrics_label.setText("현재 재생 중인 곡이 없습니다.")

#------------------------------------------------------------
    # 마우스 눌렀을 때 이벤트 처리
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_active = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    # 마우스 움직임 이벤트 처리
    def mouseMoveEvent(self, event):
        if self.drag_active and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    # 마우스 버튼 뗐을 때 이벤트 처리
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_active = False
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LyricsWindow()
    window.show()
    sys.exit(app.exec_())
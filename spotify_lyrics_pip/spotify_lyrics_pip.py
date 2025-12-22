import sys, time
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGraphicsDropShadowEffect, QSystemTrayIcon, QMenu, QAction, QColorDialog
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap, QPainter
from spotify_func import configure_spotify
from lrclib_func import get_lyrics_from_lrclib, lyrics_parsing_with_time
import spotipy

# Spotify Client 설정
sp = configure_spotify()

# 트레이 아이콘 생성
def create_tray_icon():
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setBrush(QColor(30, 215, 96))  # Spotify 그린
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(8, 8, 48, 48)
    painter.setPen(QColor(255, 255, 255))
    painter.setFont(QFont('Arial', 24, QFont.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, '♫')
    painter.end()
    return QIcon(pixmap)

# Get current song information with 429 handling
def get_current_song():
    try:
        current_track = sp.current_user_playing_track()
        if current_track is not None and current_track['item'] is not None:
            track_name = current_track['item']['name']
            artist_name = current_track['item']['artists'][0]['name']
            album_name = current_track['item']['album']['name']
            progress_ms = current_track['progress_ms']
            duration_ms = current_track['item']['duration_ms']
            return track_name, artist_name, album_name, progress_ms, duration_ms, None
        return None, None, None, None, None, None
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 429:
            retry_after = int(e.headers.get('Retry-After', 5))
            print(f"Rate limit 도달. {retry_after}초 후 재시도...")
            return None, None, None, None, None, retry_after
        print(f"Spotify API 오류: {e}")
        return None, None, None, None, None, None
    except Exception as e:
        print(f"오류 발생: {e}")
        return None, None, None, None, None, None

# Get lyrics from LrcLib with time-synced lyrics
def get_lyrics(track_name, artist_name, album_name, duration_ms):
    if not (track_name and artist_name):
        return [(0, "현재 재생 중인 곡이 없습니다.")], False
    
    try:
        duration_seconds = int(duration_ms / 1000)
        raw_lyrics = get_lyrics_from_lrclib(artist_name, track_name, album_name, duration_seconds)
        
        if not raw_lyrics:
            return [(0, "가사를 찾을 수 없습니다.")], False
        
        parsed_lyrics, has_timestamp = lyrics_parsing_with_time(raw_lyrics)
        
        if not parsed_lyrics:
            return [(0, "가사를 찾을 수 없습니다.")], False
        
        return parsed_lyrics, has_timestamp
    except Exception as e:
        print(f"가사 로딩 오류: {e}")
        return [(0, "가사를 찾을 수 없습니다.")], False
# PyQt5 Lyrics Widget
class LyricsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.lyrics_ = []
        self.current_song = None
        self.cached_track_info = None
        self.last_api_call_time = 0
        self.rate_limit_wait = 0
        self.has_timestamp = True
        self.showing_full_lyrics = False
        self.text_color = 'white'
        self.bg_opacity = 0  # 0-255 (기본 완전 투명)
        self.init_ui()
        self.setup_tray_icon()
        self.drag_active = False

    def init_ui(self):
        self.setWindowTitle('Spotify Lyrics')
        self.setGeometry(100, 100, 350, 150)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet('background-color: transparent;')

        self.lyrics_label = QLabel(self)
        self.lyrics_label.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.lyrics_label.setFont(QFont('Arial', 14, QFont.Bold))
        self.lyrics_label.setStyleSheet(f'color: {self.text_color}')

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(10)
        shadow_effect.setColor(Qt.black)
        shadow_effect.setOffset(2, 2)
        self.lyrics_label.setGraphicsEffect(shadow_effect)

        layout = QVBoxLayout()
        layout.addWidget(self.lyrics_label)
        self.setLayout(layout)

        self.main_timer = QTimer(self)
        self.main_timer.timeout.connect(self.update_all)
        self.main_timer.start(1000)  # 1초마다 실행

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(create_tray_icon())
        self.tray_icon.setToolTip('Spotify Lyrics')
        
        # 트레이 메뉴 생성
        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                color: black;
                border: 1px solid #ccc;
            }
            QMenu::item:selected {
                background-color: #1ED760;
                color: white;
            }
        """)
        
        # 글자 색상 메뉴
        color_menu = QMenu('글자 색상', self)
        color_menu.setStyleSheet(tray_menu.styleSheet())
        
        white_action = QAction('흰색', self)
        white_action.triggered.connect(lambda: self.change_text_color('white'))
        color_menu.addAction(white_action)
        
        black_action = QAction('검은색', self)
        black_action.triggered.connect(lambda: self.change_text_color('black'))
        color_menu.addAction(black_action)
        
        red_action = QAction('빨간색', self)
        red_action.triggered.connect(lambda: self.change_text_color('red'))
        color_menu.addAction(red_action)
        
        green_action = QAction('초록색', self)
        green_action.triggered.connect(lambda: self.change_text_color('#1ED760'))
        color_menu.addAction(green_action)
        
        custom_action = QAction('색상 선택...', self)
        custom_action.triggered.connect(self.choose_custom_color)
        color_menu.addAction(custom_action)
        
        tray_menu.addMenu(color_menu)
        
        # 배경 투명도 메뉴
        opacity_menu = QMenu('배경 투명도', self)
        opacity_menu.setStyleSheet(tray_menu.styleSheet())
        
        for opacity_percent in [0, 25, 50, 75, 100]:
            action = QAction(f'{opacity_percent}%', self)
            opacity_value = int(opacity_percent * 255 / 100)
            action.triggered.connect(lambda checked, val=opacity_value: self.change_bg_opacity(val))
            opacity_menu.addAction(action)
        
        tray_menu.addMenu(opacity_menu)
        
        tray_menu.addSeparator()
        
        # 종료 메뉴
        quit_action = QAction('종료', self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def change_text_color(self, color):
        self.text_color = color
        self.lyrics_label.setStyleSheet(f'color: {color}')
    
    def choose_custom_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.change_text_color(color.name())
    
    def change_bg_opacity(self, opacity):
        self.bg_opacity = opacity
        self.apply_background_style()
    
    def apply_background_style(self):
        """현재 bg_opacity 값에 맞춰 배경 스타일 적용"""
        if self.bg_opacity == 0:
            self.setStyleSheet('background-color: transparent;')
        else:
            self.setStyleSheet(f'background-color: rgba(50, 50, 50, {self.bg_opacity}); border-radius: 10px;')

    def update_all(self):
        # Rate limit 대기 중이면 카운트다운
        if self.rate_limit_wait > 0:
            self.rate_limit_wait -= 1
            self.lyrics_label.setText(f"Rate limit 대기 중... {self.rate_limit_wait}초")
            return
        
        # API 호출
        track_name, artist_name, album_name, progress_ms, duration_ms, retry_after = get_current_song()
        
        # 429 에러 처리
        if retry_after is not None:
            self.rate_limit_wait = retry_after
            self.main_timer.setInterval(1000)  # 1초로 재설정
            return
        
        # 트랙 정보 캐싱
        self.cached_track_info = (track_name, artist_name, album_name, progress_ms, duration_ms)
        
        # 곡 변경 체크
        current_song = (track_name, artist_name)
        if current_song != self.current_song and track_name is not None:
            self.current_song = current_song
            self.lyrics_ = []
            self.showing_full_lyrics = False
            if track_name:
                self.lyrics_, self.has_timestamp = get_lyrics(track_name, artist_name, album_name, duration_ms)
        
        # 전체 가사 표시 모드일 때는 업데이트 안 함
        if self.showing_full_lyrics:
            return
        
        # 가사 업데이트
        if not progress_ms or not self.lyrics_:
            return
            
        current_time = progress_ms / 1000
        display_lyrics = []

        # 현재 시간 기준으로 앞뒤 가사 표시 (시간 기반 동기화)
        current_index = -1
        for i, (timestamp, line) in enumerate(self.lyrics_):
            # 타입 체크: timestamp가 숫자인지 확인
            if isinstance(timestamp, (int, float)) and timestamp <= current_time:
                current_index = i
            else:
                break
        
        # 현재 줄 기준으로 앞뒤 1개씩 표시
        if current_index >= 0:
            start_index = max(0, current_index - 1)
            end_index = min(len(self.lyrics_), current_index + 2)
            display_lyrics = [line for timestamp, line in self.lyrics_[start_index:end_index]]
        else:
            # 곡 시작 부분
            display_lyrics = [line for timestamp, line in self.lyrics_[:3]]
        
        # 가사를 찾을 수 없는 경우 Now Playing 정보 추가
        if len(self.lyrics_) == 1 and self.lyrics_[0][1] == "가사를 찾을 수 없습니다.":
            if self.current_song and self.current_song[0]:
                track_name, artist_name = self.current_song
                display_lyrics = [f"Now Playing: {track_name} - {artist_name}", "", "가사를 찾을 수 없습니다."]
        # 타임스탬프가 없는 가사인 경우 안내 메시지 표시
        elif not self.has_timestamp and self.current_song and self.current_song[0]:
            track_name, artist_name = self.current_song
            display_lyrics = [f"Now Playing: {track_name} - {artist_name}", "", "더블클릭을 하면 전체 가사를 볼 수 있습니다."]
        
        self.lyrics_label.setText('\n'.join(display_lyrics))

    def show_now_playing(self):
        if self.current_song:
            track_name, artist_name = self.current_song
            self.main_timer.stop()
            self.lyrics_label.setText(f"Now Playing : {track_name} - {artist_name}")
            QTimer.singleShot(3000, lambda: self.main_timer.start(1000))
        

    # Dragging event------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_active = True
            self.old_pos = event.globalPos() - self.frameGeometry().topLeft()
            # 드래그 시작 시 반투명 회색 배경 표시
            self.setStyleSheet('background-color: rgba(128, 128, 128, 150); border-radius: 10px;')
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_active and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.old_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_active = False
            # 드래그 종료 시 설정된 배경 투명도로 복원
            self.apply_background_style()
            event.accept()
    # Double click event-------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Ctrl+Alt+더블클릭 = 프로그램 종료
            if event.modifiers() == (Qt.ControlModifier | Qt.AltModifier):
                QApplication.quit()
            # 타임스탬프가 없는 가사인 경우 전체 가사 표시/숨기기
            elif not self.has_timestamp and len(self.lyrics_) > 1:
                self.showing_full_lyrics = not self.showing_full_lyrics
                if self.showing_full_lyrics:
                    # 전체 가사 표시
                    all_lyrics = [line for _, line in self.lyrics_]
                    self.lyrics_label.setText('\n'.join(all_lyrics))
                else:
                    # 다시 기본 모드로
                    if self.current_song and self.current_song[0]:
                        track_name, artist_name = self.current_song
                        display_lyrics = [f"Now Playing: {track_name} - {artist_name}", "", "더블클릭을 하면 전체 가사를 볼 수 있습니다."]
                        self.lyrics_label.setText('\n'.join(display_lyrics))
            else:
                # 기존 기능: Now Playing 표시
                self.show_now_playing()
            event.accept()    
# Main
def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    widget = LyricsWidget()
    widget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
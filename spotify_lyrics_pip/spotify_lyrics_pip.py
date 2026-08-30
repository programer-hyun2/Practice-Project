import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QGraphicsDropShadowEffect, QSystemTrayIcon, QMenu, QAction, QColorDialog, QWidgetAction, QSlider
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap, QPainter
from spotify_func import configure_spotify, get_current_song, verify_spotify_login
from lrclib_func import get_lyrics

# Spotify Client 설정
try:
    sp = configure_spotify()
    spotify_init_error = None
except Exception as e:
    sp = None
    spotify_init_error = f"Spotify 초기화 실패: {e}"

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
        self.changing_color = False  # 색상 변경 중 플래그
        self.bg_opacity = 0  # 0-255 (기본 완전 투명)
        self.base_main_font_size = 24  # 현재 줄 기본 크기
        self.base_sub_font_size = 18   # 주변 줄 기본 크기
        self.font_scale_percent = 100
        self.main_font_size = self.base_main_font_size
        self.sub_font_size = self.base_sub_font_size
        self.font_slider = None
        self.font_scale_label_action = None
        self.color_dialog = None  # 색상 다이얼로그 인스턴스
        self.spotify_login_checked = False
        self.spotify_login_ok = False
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
        self.lyrics_label.setFont(QFont('Malgun Gothic', 14, QFont.Bold))  # 맑은 고딕 (Windows 기본 한글 폰트)
        self.lyrics_label.setStyleSheet(f'color: {self.text_color}')
        self.lyrics_label.setTextInteractionFlags(Qt.NoTextInteraction)  # 텍스트 상호작용 비활성화
        self.lyrics_label.setAttribute(Qt.WA_TransparentForMouseEvents, False)  # 마우스 이벤트가 부모로 전달되도록
        self.lyrics_label.setText('<span style="color: white;">Spotify 로그인 상태 확인 중...</span>')

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
        
        # 글자 배경 투명도 메뉴
        opacity_menu = QMenu('글자 배경 투명도', self)
        opacity_menu.setStyleSheet(tray_menu.styleSheet())
        
        for opacity_percent in [0, 25, 50, 75, 100]:
            action = QAction(f'{opacity_percent}%', self)
            opacity_value = int(opacity_percent * 255 / 100)
            action.triggered.connect(lambda checked, val=opacity_value: self.change_bg_opacity(val))
            opacity_menu.addAction(action)
        
        tray_menu.addMenu(opacity_menu)

        # 글자 크기 메뉴
        font_size_menu = QMenu('글자 크기', self)
        font_size_menu.setStyleSheet(tray_menu.styleSheet())

        self.font_scale_label_action = QAction(self.get_font_scale_text(), self)
        self.font_scale_label_action.setEnabled(False)
        font_size_menu.addAction(self.font_scale_label_action)

        slider_action = QWidgetAction(self)
        self.font_slider = QSlider(Qt.Horizontal)
        self.font_slider.setRange(70, 180)
        self.font_slider.setSingleStep(5)
        self.font_slider.setPageStep(10)
        self.font_slider.setValue(self.font_scale_percent)
        self.font_slider.valueChanged.connect(self.change_font_scale)
        slider_action.setDefaultWidget(self.font_slider)
        font_size_menu.addAction(slider_action)

        font_size_menu.addSeparator()

        font_decrease_action = QAction('작게 (-)', self)
        font_decrease_action.triggered.connect(lambda: self.adjust_font_scale(-5))
        font_size_menu.addAction(font_decrease_action)

        font_increase_action = QAction('크게 (+)', self)
        font_increase_action.triggered.connect(lambda: self.adjust_font_scale(5))
        font_size_menu.addAction(font_increase_action)

        font_reset_action = QAction('기본 크기 (100%)', self)
        font_reset_action.triggered.connect(lambda: self.change_font_scale(100))
        font_size_menu.addAction(font_reset_action)

        tray_menu.addMenu(font_size_menu)
        
        tray_menu.addSeparator()
        
        # 종료 메뉴
        quit_action = QAction('종료', self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """트레이 아이콘 클릭 이벤트"""
        if reason == QSystemTrayIcon.DoubleClick:
            # 더블클릭 시 창 표시/숨기기
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()
    
    def change_text_color(self, color):
        self.changing_color = True
        self.text_color = color
        QTimer.singleShot(500, self.finish_color_change)
    
    def finish_color_change(self):
        self.changing_color = False
    
    def choose_custom_color(self):
        if self.color_dialog is not None and self.color_dialog.isVisible():
            return
        
        current_color = QColor(self.text_color)
        if not current_color.isValid():
            current_color = QColor(255, 255, 255)
        
        self.color_dialog = QColorDialog(current_color, None)
        self.color_dialog.setWindowTitle("글자 색상 선택")
        self.color_dialog.setOption(QColorDialog.DontUseNativeDialog)
        self.color_dialog.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.color_dialog.colorSelected.connect(self.on_color_selected)
        self.color_dialog.show()
    
    def on_color_selected(self, color):
        if color.isValid():
            r, g, b = color.red(), color.green(), color.blue()
            color_hex = f"#{r:02X}{g:02X}{b:02X}"
            self.change_text_color(color_hex)
        
        if self.color_dialog is not None:
            self.color_dialog.deleteLater()
            self.color_dialog = None
    
    def change_bg_opacity(self, opacity):
        self.bg_opacity = opacity
        self.apply_background_style()

    def get_font_scale_text(self):
        return f'현재 크기: {self.font_scale_percent}%'

    def change_font_scale(self, scale_percent):
        clamped = max(70, min(180, int(scale_percent)))
        self.font_scale_percent = clamped
        self.main_font_size = max(12, int(round(self.base_main_font_size * (clamped / 100))))
        self.sub_font_size = max(10, int(round(self.base_sub_font_size * (clamped / 100))))

        if self.font_slider is not None and self.font_slider.value() != clamped:
            self.font_slider.blockSignals(True)
            self.font_slider.setValue(clamped)
            self.font_slider.blockSignals(False)

        if self.font_scale_label_action is not None:
            self.font_scale_label_action.setText(self.get_font_scale_text())

        # 즉시 반영을 위해 현재 표시 상태를 다시 계산
        self.update_all()

    def adjust_font_scale(self, delta):
        self.change_font_scale(self.font_scale_percent + delta)
    
    def apply_background_style(self):
        """항상 투명 배경 유지 (글자에 배경 적용)"""
        self.setStyleSheet('background-color: transparent;')
    
    def get_color_with_opacity(self, color, opacity):
        """색상 문자열을 rgba 형식으로 변환하여 투명도 적용"""
        if color.startswith('#'):
            color_hex = color.lstrip('#')
            if len(color_hex) == 6:
                r, g, b = int(color_hex[0:2], 16), int(color_hex[2:4], 16), int(color_hex[4:6], 16)
                return f'rgba({r}, {g}, {b}, {opacity})'
        elif color == 'white':
            return f'rgba(255, 255, 255, {opacity})'
        elif color == 'black':
            return f'rgba(0, 0, 0, {opacity})'
        elif color == 'red':
            return f'rgba(255, 0, 0, {opacity})'
        elif color == 'green':
            return f'rgba(0, 255, 0, {opacity})'
        return f'rgba(255, 255, 255, {opacity})'
    
    def get_text_bg_color(self):
        """글자 배경색 반환 (bg_opacity에 따라)"""
        if self.bg_opacity == 0:
            return ''
        opacity_value = self.bg_opacity / 255
        return f'background-color: rgba(50, 50, 50, {opacity_value}); padding: 2px 8px; border-radius: 4px;'

    def update_all(self):
        if self.changing_color:
            return

        if spotify_init_error is not None:
            self.lyrics_label.setText(f'<span style="color: {self.text_color};">{spotify_init_error}</span>')
            return

        if not self.spotify_login_checked:
            self.spotify_login_checked = True
            self.spotify_login_ok, login_message = verify_spotify_login(sp)
            self.lyrics_label.setText(f'<span style="color: {self.text_color};">{login_message}</span>')
            if not self.spotify_login_ok:
                return
        
        if self.rate_limit_wait > 0:
            self.rate_limit_wait -= 1
            self.lyrics_label.setText(f'<span style="color: {self.text_color};">Rate limit 대기 중... {self.rate_limit_wait}초</span>')
            return
        
        track_name, artist_name, album_name, progress_ms, duration_ms, retry_after, status_message = get_current_song(sp)
        
        if retry_after is not None:
            self.rate_limit_wait = retry_after
            self.main_timer.setInterval(1000)
            if status_message:
                self.lyrics_label.setText(f'<span style="color: {self.text_color};">{status_message}</span>')
            return

        if status_message is not None:
            self.lyrics_label.setText(f'<span style="color: {self.text_color};">{status_message}</span>')
            self.lyrics_ = []
            return
        
        self.cached_track_info = (track_name, artist_name, album_name, progress_ms, duration_ms)
        
        current_song = (track_name, artist_name)
        if current_song != self.current_song and track_name is not None:
            self.current_song = current_song
            self.lyrics_ = []
            self.showing_full_lyrics = False
            if track_name:
                self.lyrics_, self.has_timestamp = get_lyrics(track_name, artist_name, album_name, duration_ms)
        
        if self.showing_full_lyrics:
            return
        
        if progress_ms is None or not self.lyrics_:
            return
            
        current_time = progress_ms / 1000
        current_index = -1
        
        for i, (timestamp, line) in enumerate(self.lyrics_):
            if isinstance(timestamp, (int, float)) and timestamp <= current_time:
                current_index = i
            else:
                break
        
        if current_index >= 0:
            start_index = max(0, current_index - 1)
            end_index = min(len(self.lyrics_), current_index + 2)
            display_lyrics = [line for timestamp, line in self.lyrics_[start_index:end_index]]
            
            center_idx = 1 if current_index > 0 else 0
            if center_idx < len(display_lyrics) and not display_lyrics[center_idx].strip():
                if center_idx > 0 and display_lyrics[center_idx - 1].strip():
                    center_idx = center_idx - 1
            
            styled_lyrics = []
            for i, lyric in enumerate(display_lyrics):
                if i == center_idx:
                    bg_style = self.get_text_bg_color()
                    styled_lyrics.append(f'<span style="color: {self.text_color}; font-size: {self.main_font_size}px; {bg_style}">{lyric}</span>')
                else:
                    color_rgba = self.get_color_with_opacity(self.text_color, 0.25)
                    styled_lyrics.append(f'<span style="color: {color_rgba}; font-size: {self.sub_font_size}px;">{lyric}</span>')
            
            self.lyrics_label.setText('<br>'.join(styled_lyrics))
        else:
            if len(self.lyrics_) > 0:
                first_line = self.lyrics_[0][1]
                second_line = self.lyrics_[1][1] if len(self.lyrics_) > 1 else ""
                
                color_rgba = self.get_color_with_opacity(self.text_color, 0.25)
                bg_style = self.get_text_bg_color()
                styled_lyrics = [
                    f'<span style="font-size: {self.sub_font_size}px;"></span>',
                    f'<span style="color: {self.text_color}; font-size: {self.main_font_size}px; {bg_style}">{first_line}</span>',
                ]
                if second_line:
                    styled_lyrics.append(f'<span style="color: {color_rgba}; font-size: {self.sub_font_size}px;">{second_line}</span>')
                
                self.lyrics_label.setText('<br>'.join(styled_lyrics))
            else:
                display_lyrics = [line for timestamp, line in self.lyrics_[:3]]
                self.lyrics_label.setText('\n'.join(display_lyrics))
        
        if len(self.lyrics_) == 1 and self.lyrics_[0][1] == "가사를 찾을 수 없습니다.":
            if self.current_song and self.current_song[0]:
                track_name, artist_name = self.current_song
                styled_text = [
                    f'<span style="color: {self.text_color};">Now Playing: {track_name} - {artist_name}</span>',
                    '<br>',
                    f'<span style="color: {self.text_color};">가사를 찾을 수 없습니다.</span>'
                ]
                self.lyrics_label.setText(''.join(styled_text))
        elif not self.has_timestamp and self.current_song and self.current_song[0]:
            track_name, artist_name = self.current_song
            styled_text = [
                f'<span style="color: {self.text_color};">Now Playing: {track_name} - {artist_name}</span>',
                '<br>',
                f'<span style="color: {self.text_color};">더블클릭을 하면 전체 가사를 볼 수 있습니다.</span>'
            ]
            self.lyrics_label.setText(''.join(styled_text))

    def show_now_playing(self):
        if self.current_song:
            track_name, artist_name = self.current_song
            self.main_timer.stop()
            self.lyrics_label.setText(f'<span style="color: {self.text_color};">Now Playing : {track_name} - {artist_name}</span>')
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
                        styled_text = [
                            f'<span style="color: {self.text_color};">Now Playing: {track_name} - {artist_name}</span>',
                            '<br>',
                            f'<span style="color: {self.text_color};">더블클릭을 하면 전체 가사를 볼 수 있습니다.</span>'
                        ]
                        self.lyrics_label.setText(''.join(styled_text))
            else:
                # 기존 기능: Now Playing 표시
                self.show_now_playing()
            event.accept()    
# Main
def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    
    # 마지막 윈도우가 닫혀도 애플리케이션 종료하지 않음 (시스템 트레이 아이콘이 있으므로)
    app.setQuitOnLastWindowClosed(False)
    
    widget = LyricsWidget()
    widget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
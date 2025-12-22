from lrclib import LrcLibAPI
import time, re

lrclib = LrcLibAPI(user_agent="spotify-lyrics-pip/1.0")

def get_lyrics_from_lrclib(artist, title, album, duration):
    try:
        lyrics = lrclib.get_lyrics(track_name=title, artist_name=artist, album_name=album, duration=duration)
        
        if lyrics is None:
            return None
        
        foundlyrics = lyrics.synced_lyrics or lyrics.unsynced_lyrics
        return foundlyrics
    except Exception as e:
        print(f"LrcLib API 오류: {e}")
        return None

def lyrics_parsing_with_time(lyrics):
    if not lyrics or not isinstance(lyrics, str):
        return [], False
    
    lines = lyrics.splitlines()
    parsed_lyrics = []
    has_timestamp = False
    
    for line in lines:
        # [mm:ss.ss] lyrics 형태를 파싱
        match = re.match(r'\[(\d+):(\d+\.\d+)\]\s*(.*)', line)
        if match:
            has_timestamp = True
            minutes = int(match.group(1))
            seconds = float(match.group(2))
            lyric_text = match.group(3)
            timestamp = minutes * 60 + seconds
            parsed_lyrics.append((timestamp, lyric_text))
    
    # 타임스탬프가 없는 가사인 경우, 모든 줄을 0초 타임스탬프로 추가
    if not has_timestamp and lines:
        for i, line in enumerate(lines):
            if line.strip():  # 빈 줄이 아니면
                # 각 줄에 인덱스 기반 가상 타임스탬프 부여 (줄 단위로 구분하기 위해)
                parsed_lyrics.append((i * 0.001, line.strip()))
    
    return parsed_lyrics, has_timestamp
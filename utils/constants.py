"""
상수 및 설정 정의
"""
import sys
import os

# ==================== 앱 정보 ====================
APP_NAME = "ColdHawk_test_1.4.0"
APP_VERSION = "2.0.0"
APP_SLUG = "coldhawk_test_ver1"

# ==================== 색상 팔레트 (Apple HIG) ====================
COLORS = {
    # 배경
    'bg_primary': '#1C1C1E',      # 다크 배경
    'bg_secondary': '#2C2C2E',    # 카드 배경
    'bg_tertiary': '#3A3A3C',     # 입력 필드
    'bg_hover': '#48484A',        # Hover 상태
    
    # 텍스트
    'text_primary': '#FFFFFF',     # 흰색
    'text_secondary': '#98989D',   # 회색
    'text_tertiary': '#636366',    # 연한 회색
    'text_placeholder': '#48484A', # Placeholder
    
    # 액센트 (톡톡 튀는 색!)
    'accent_blue': '#0A84FF',      # 애플 블루
    'accent_green': '#32D74B',     # 실행 초록
    'accent_orange': '#FF9F0A',    # 경고 주황
    'accent_red': '#FF453A',       # 에러 빨강
    'accent_purple': '#BF5AF2',    # 보라
    'accent_pink': '#FF2D55',      # 핑크
    'accent_teal': '#64D2FF',      # 틸
    'accent_yellow': '#FFD60A',    # 노랑
    
    # LED 상태
    'led_running': '#32D74B',      # 실행중 (초록)
    'led_waiting': '#FF9F0A',      # 대기중 (주황)
    'led_error': '#FF453A',        # 오류 (빨강)
    'led_stopped': '#636366',      # 중지 (회색)
    'led_login': '#0A84FF',        # 로그인중 (파랑)
    
    # 그라디언트
    'gradient_purple_blue': ['#BF5AF2', '#0A84FF'],
    'gradient_pink_orange': ['#FF2D55', '#FF9F0A'],
    'gradient_green_teal': ['#32D74B', '#64D2FF'],
}

# ==================== 폰트 ====================
if sys.platform == "win32":
    FONT_FAMILY = "Malgun Gothic"     # 맑은 고딕 (이모티콘 완벽)
    FONT_MONO = "Consolas"
elif sys.platform == "darwin":
    FONT_FAMILY = "SF Pro Display"
    FONT_MONO = "SF Mono"
else:
    FONT_FAMILY = "Noto Sans CJK KR"
    FONT_MONO = "DejaVu Sans Mono"

FONT_SIZES = {
    'small': 10,      # 11 → 10
    'normal': 12,     # 13 → 12
    'large': 14,      # 15 → 14
    'title': 16,      # 18 → 16
    'huge': 20,       # 24 → 20
}

# ==================== 레이아웃 ====================
WINDOW_SIZE = (750, 750)  # 850x750 → 750x750 (더 작게)
TAB_CARD_WIDTH = 52       # 60 → 52
TAB_CARD_HEIGHT = 52      # 60 → 52
SPACING = {
    'small': 4,      # 6 → 4
    'normal': 10,    # 12 → 10
    'large': 16,     # 20 → 16
}
BORDER_RADIUS = {
    'small': 10,     # 8 → 10
    'normal': 14,    # 12 → 14
    'large': 18,     # 16 → 18
    'huge': 22,      # 20 → 22
}

# ==================== 애니메이션 ====================
ANIMATION_DURATION = {
    'fast': 150,      # 버튼 클릭
    'normal': 300,    # 카드 전환
    'slow': 500,      # 페이드인/아웃
}

# ==================== 인벤 설정 ====================
BOARD_MAP = {
    "거래게시판": "6383",
    "버스게시판": "6085",
}
BOARD_SLUG = "diablo4"

DEFAULT_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)

# ==================== 기본값 ====================
DEFAULT_TAB_COUNT = 10  # 6 → 10
DEFAULT_UPLOAD_INTERVAL = 30  # 초
DEFAULT_RUN_HOURS = 1
DEFAULT_WRITE_COUNT = 1

# ==================== 경로 ====================
def get_app_data_dir():
    """앱 데이터 저장 디렉토리"""
    if sys.platform == "win32":
        base = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        app_dir = os.path.join(base, APP_SLUG)
    elif sys.platform == "darwin":
        app_dir = os.path.expanduser(f'~/Library/Application Support/{APP_SLUG}')
    else:
        app_dir = os.path.expanduser(f'~/.{APP_SLUG}')
    
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

def get_logs_dir():
    """로그 디렉토리"""
    logs_dir = os.path.join(get_app_data_dir(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

def get_settings_file():
    """설정 파일 경로"""
    return os.path.join(get_app_data_dir(), 'settings.json')

def get_recent_posts_file():
    """최근 게시글 파일 경로"""
    return os.path.join(get_app_data_dir(), 'recent_posts.json')

# ==================== 아이콘 경로 ====================
def get_icon_path(ext='png'):
    """아이콘 파일 경로"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'resources', 'icons', f'hawk_icon.{ext}')

# ==================== 로그 레벨 아이콘 ====================
LOG_ICONS = {
    'info': '',      # 독수리 제거
    'success': '✓',  # 체크만
    'warning': '⚠',
    'error': '✗',
    'debug': '',
}

# ==================== 상태 ====================
class TabState:
    """탭 상태"""
    STOPPED = 'stopped'
    RUNNING = 'running'
    WAITING = 'waiting'
    ERROR = 'error'
    LOGIN = 'login'

# ==================== HTTP 설정 ====================
HTTP_TIMEOUT = 10
HTTP_MAX_RETRIES = 3
HTTP_RETRY_DELAY = 0.5  # 초
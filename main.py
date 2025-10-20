"""
ColdHawk_test_1.3.1 PySide6 매크로 프로그램
진입점
"""
import sys
import os
import signal
import atexit
import json
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.windows.main_window import MainWindow
from ui.windows.login_window import LoginWindow
from utils.constants import APP_NAME, APP_SLUG, FONT_FAMILY
from utils.logger import logger


# ==================== CONFIG ====================
def load_config():
    """config.json 로드 (PyInstaller onefile 지원)"""
    try:
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
        config_path = os.path.join(base_dir, "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def load_firebase_config():
    """Firebase 설정 로드 (내장 설정 우선)"""
    # 내장 Firebase 설정 (exe 파일에 포함됨)
    EMBEDDED_FIREBASE_CONFIG = {
        "disabled": False,
        "apiKey": "AIzaSyAo2-_VoDQsNjRCimzns5V6boc6-ajP8zs",
        "authDomain": "coldhawk-id.firebaseapp.com",
        "databaseURL": "https://coldhawk-id.firebaseio.com",  # IP 저장을 위해 필요
        "projectId": "coldhawk-id",
        "storageBucket": "coldhawk-id.firebasestorage.app",
        "messagingSenderId": "994254528568",
        "appId": "1:994254528568:web:6a57d9c80a230331db46cd"
    }
    
    # 환경변수에서 로드 (사용자 설정이 있으면 우선 사용)
    api_key = os.environ.get("FIREBASE_API_KEY")
    if api_key and len(api_key.strip()) > 10:
        logger.info("✅ 환경변수에서 Firebase 설정 로드")
        return {
            "disabled": False,
            "apiKey": api_key.strip(),
            "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN", "coldhawk-id.firebaseapp.com"),
            "databaseURL": os.environ.get("FIREBASE_DATABASE_URL", "https://coldhawk-id.firebaseio.com"),
            "projectId": os.environ.get("FIREBASE_PROJECT_ID", "coldhawk-id"),
            "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET", "coldhawk-id.firebasestorage.app"),
            "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID", "994254528568"),
            "appId": os.environ.get("FIREBASE_APP_ID", "1:994254528568:web:6a57d9c80a230331db46cd")
        }
    
    # 환경변수가 없으면 내장 설정 사용
    logger.info("✅ 내장 Firebase 설정 사용")
    return EMBEDDED_FIREBASE_CONFIG

def mask_sensitive_data(data):
    """민감 정보 마스킹"""
    if isinstance(data, dict):
        masked = data.copy()
        if 'apiKey' in masked and masked['apiKey']:
            # API 키는 마지막 4자리만 표시
            masked['apiKey'] = '***' + str(masked['apiKey'])[-4:] if len(str(masked['apiKey'])) > 4 else '***'
        return masked
    return data

CONFIG = load_config()
FIREBASE_CONFIG = load_firebase_config()


# ==================== 싱글 인스턴스 ====================
_lock_file = None

def acquire_single_instance():
    """싱글 인스턴스 체크"""
    global _lock_file
    
    if sys.platform == "win32":
        # Windows: Named Mutex
        try:
            import ctypes
            import ctypes.wintypes as w
            
            CreateMutex = ctypes.windll.kernel32.CreateMutexW
            GetLastError = ctypes.windll.kernel32.GetLastError
            
            mutex_name = f"Global\\{APP_SLUG}_MUTEX"
            handle = CreateMutex(None, False, mutex_name)
            
            if GetLastError() == 183:  # ERROR_ALREADY_EXISTS
                return False
            
            return True
        except Exception:
            pass
    
    # Unix/Linux/Mac: File Lock
    try:
        import fcntl
        from utils.constants import get_app_data_dir
        
        lock_path = os.path.join(get_app_data_dir(), f"{APP_SLUG}.lock")
        _lock_file = open(lock_path, 'w')
        fcntl.flock(_lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _lock_file.write(str(os.getpid()))
        _lock_file.flush()
        return True
    except (IOError, OSError):
        return False


def release_single_instance():
    """싱글 인스턴스 락 해제"""
    global _lock_file
    if _lock_file:
        try:
            if sys.platform != "win32":
                import fcntl
                fcntl.flock(_lock_file, fcntl.LOCK_UN)
            _lock_file.close()
        except Exception:
            pass


# ==================== 정리 ====================
def cleanup():
    """정리 작업"""
    logger.info("프로그램 정리 중...")
    release_single_instance()


def signal_handler(signum, frame):
    """시그널 핸들러"""
    logger.info(f"시그널 {signum} 수신 - 종료")
    cleanup()
    sys.exit(0)


# ==================== 메인 ====================
def main():
    """메인 함수"""
    logger.info("=== 프로그램 시작 ===")
    
    # 싱글 인스턴스 체크
    if not acquire_single_instance():
        logger.warning("중복 실행 감지 - 종료합니다")
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(
                    None,
                    f"{APP_NAME}이 이미 실행 중입니다.",
                    APP_NAME,
                    0x10  # MB_ICONHAND
                )
            except Exception:
                print(f"{APP_NAME}이 이미 실행 중입니다.")
        else:
            print(f"{APP_NAME}이 이미 실행 중입니다.")
        sys.exit(0)
    
    logger.info("싱글 인스턴스 체크 통과")
    
    # 정리 등록
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("시그널 핸들러 등록 완료")
    
    # 로그
    logger.info(f"{APP_NAME} 시작")
    logger.info(f"Firebase 설정: {mask_sensitive_data(FIREBASE_CONFIG)}")
    logger.debug(f"Firebase 설정 상세: {mask_sensitive_data(FIREBASE_CONFIG)}")
    
    # QApplication
    logger.info("QApplication 생성 중...")
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    
    # 기본 폰트
    app.setFont(QFont(FONT_FAMILY, 13))
    
    logger.info("QApplication 생성 완료")
    
    # 스타일시트 로드
    logger.info("스타일시트 로드 시작...")
    try:
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
        style_path = os.path.join(
            base_dir,
            'ui', 'styles', 'apple_light.qss'  # 기존 스타일로 복구
        )
        logger.debug(f"스타일시트 경로: {style_path}")
        logger.debug(f"스타일시트 파일 존재: {os.path.exists(style_path)}")
        
        if os.path.exists(style_path):
            with open(style_path, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
            app.setStyleSheet(stylesheet)
            logger.info("스타일시트 로드 완료")
        else:
            logger.warning(f"스타일시트 파일 없음: {style_path}")
    except Exception as e:
        logger.exception(f"스타일시트 로드 실패: {e}")
    
    # 로그인 창 표시
    logger.info("=== 로그인 창 시작 ===")
    logger.info(f"Firebase Config 존재: {bool(FIREBASE_CONFIG)}")
    logger.debug(f"Firebase Config 내용: {mask_sensitive_data(FIREBASE_CONFIG)}")
    
    try:
        logger.info("LoginWindow 객체 생성 중...")
        login_window = LoginWindow(firebase_config=FIREBASE_CONFIG)
        logger.info("LoginWindow 객체 생성 완료")
        
        logger.info("LoginWindow.show() 호출 중...")
        login_window.show()
        logger.info("LoginWindow.show() 호출 완료")
        
        logger.info("LoginWindow.exec() 호출 중...")
        result = login_window.exec()
        logger.info(f"LoginWindow.exec() 결과: {result}")
        logger.debug(f"Accepted 상수값: {LoginWindow.Accepted}")
        
        if result != LoginWindow.Accepted:
            # 로그인 취소 시 종료
            logger.info("로그인 취소 - 프로그램 종료")
            cleanup()
            sys.exit(0)
        
        logger.info("=== 로그인 성공 - 메인으로 진행 ===")
        
    except Exception as e:
        logger.exception(f"로그인 창 생성/실행 실패: {e}")
        
        QMessageBox.critical(
            None,
            "오류",
            f"로그인 창을 시작할 수 없습니다.\n{str(e)}"
        )
        cleanup()
        sys.exit(1)
    
    # 메인 윈도우
    logger.info("=== 메인 윈도우 생성 시작 ===")
    try:
        logger.info("MainWindow 객체 생성 중...")
        try:
            import inspect
            logger.info(f"MainWindow 정의 파일: {inspect.getsourcefile(MainWindow)}")
            logger.info(f"MainWindow 시그니처: {inspect.signature(MainWindow)}")
        except Exception as _sig_err:
            logger.warning(f"MainWindow 시그니처 확인 실패: {_sig_err}")
        user_profile = getattr(login_window, 'user_profile', None)
        window = MainWindow()
        if user_profile and hasattr(window, 'set_user_profile'):
            try:
                window.set_user_profile(user_profile)
            except Exception as _e:
                logger.warning(f"사용자 프로필 주입 실패(무시): {_e}")
        logger.info("MainWindow 객체 생성 완료")
        
        logger.info("MainWindow.show() 호출 중...")
        window.show()
        logger.info("메인 윈도우 표시 완료")
    except Exception as e:
        logger.exception(f"메인 윈도우 생성 실패: {e}")
        
        QMessageBox.critical(
            None,
            "오류",
            f"프로그램을 시작할 수 없습니다.\n{str(e)}"
        )
        cleanup()
        sys.exit(1)
    
    # 이벤트 루프 실행
    logger.info("=== Qt 이벤트 루프 시작 ===")
    exit_code = app.exec()
    
    # 정리
    cleanup()
    logger.info(f"{APP_NAME} 종료 (exit code: {exit_code})")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt - 종료")
        cleanup()
        sys.exit(0)
    except Exception as e:
        logger.exception(f"치명적 오류: {e}")
        cleanup()
        sys.exit(1)
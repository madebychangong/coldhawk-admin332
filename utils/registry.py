"""
Windows 레지스트리 유틸리티
"""
import sys
from utils.logger import logger

# Windows 전용
if sys.platform == "win32":
    try:
        import winreg
        REGISTRY_OK = True
    except ImportError:
        REGISTRY_OK = False
else:
    REGISTRY_OK = False


REGISTRY_PATH = r"Software\Coldhawk\Settings"


def get_last_email():
    """레지스트리에서 마지막 이메일 가져오기"""
    if not REGISTRY_OK:
        return ""
    
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_READ
        )
        
        value, _ = winreg.QueryValueEx(key, "LastEmail")
        winreg.CloseKey(key)
        
        logger.info(f"레지스트리에서 이메일 불러옴: {value}")
        return value
    except FileNotFoundError:
        # 키가 없음 (처음 실행)
        return ""
    except Exception as e:
        logger.error(f"레지스트리 읽기 실패: {e}")
        return ""


def save_last_email(email):
    """레지스트리에 마지막 이메일 저장"""
    if not REGISTRY_OK:
        return
    
    try:
        # 키 생성 또는 열기
        key = winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_WRITE
        )
        
        # 값 저장
        winreg.SetValueEx(key, "LastEmail", 0, winreg.REG_SZ, email)
        winreg.CloseKey(key)
        
        logger.info(f"레지스트리에 이메일 저장: {email}")
    except Exception as e:
        logger.error(f"레지스트리 쓰기 실패: {e}")
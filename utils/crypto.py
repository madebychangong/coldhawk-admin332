"""
암호화 유틸리티
"""
import hashlib
import base64
import secrets
from typing import Optional

class PasswordManager:
    """비밀번호 암호화 관리자"""
    
    def __init__(self):
        # 런타임에 키 생성 (매번 다름)
        self.key = self._generate_key()
    
    def _generate_key(self) -> bytes:
        """암호화 키 생성"""
        return hashlib.sha256(secrets.token_bytes(32)).digest()
    
    def encrypt(self, password: str) -> str:
        """비밀번호 암호화"""
        if not password:
            return ""
        
        # 간단한 XOR 암호화 (더 강력한 암호화는 필요시 구현)
        password_bytes = password.encode('utf-8')
        key_bytes = self.key[:len(password_bytes)]
        
        encrypted = bytes(a ^ b for a, b in zip(password_bytes, key_bytes))
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_password: str) -> str:
        """비밀번호 복호화"""
        if not encrypted_password:
            return ""
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_password)
            key_bytes = self.key[:len(encrypted_bytes)]
            
            decrypted = bytes(a ^ b for a, b in zip(encrypted_bytes, key_bytes))
            return decrypted.decode('utf-8')
        except Exception:
            return ""

# 전역 인스턴스
password_manager = PasswordManager()

def encrypt_password(password: str) -> str:
    """비밀번호 암호화 (편의 함수)"""
    return password_manager.encrypt(password)

def decrypt_password(encrypted_password: str) -> str:
    """비밀번호 복호화 (편의 함수)"""
    return password_manager.decrypt(encrypted_password)

def secure_clear_password(password: str) -> None:
    """비밀번호를 메모리에서 안전하게 제거 (비활성화)"""
    # 메모리 덮어쓰기는 Windows에서 안정성 문제가 있어 비활성화
    # Python의 가비지 컬렉터가 자동으로 메모리를 정리함
    pass



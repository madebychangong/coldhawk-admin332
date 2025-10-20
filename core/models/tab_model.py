"""
탭 데이터 모델 (메모리 최적화)
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
import time
from utils.constants import TabState, DEFAULT_WRITE_COUNT, DEFAULT_RUN_HOURS, DEFAULT_UPLOAD_INTERVAL
from utils.crypto import encrypt_password, decrypt_password, secure_clear_password


@dataclass
class TabModel:
    """탭 데이터 클래스"""
    
    # 기본 정보
    tab_id: int
    name: str = ""
    
    # 설정
    board_name: str = "거래게시판"
    user_id: str = ""
    _encrypted_password: str = ""  # 암호화된 비밀번호
    title: str = ""
    content: str = ""
    write_count: int = DEFAULT_WRITE_COUNT
    run_hours: int = DEFAULT_RUN_HOURS
    upload_interval: int = DEFAULT_UPLOAD_INTERVAL
    
    # 상태
    state: str = TabState.STOPPED
    
    # 통계
    total_posts: int = 0
    success_count: int = 0
    fail_count: int = 0
    last_run_time: Optional[float] = None
    
    # 최근 게시글 (idx 리스트) - 메모리 최적화
    recent_posts: list = field(default_factory=list)
    
    def __post_init__(self):
        """초기화 후 처리"""
        if not self.name:
            self.name = f"{self.tab_id}번"
    
    @property
    def password(self) -> str:
        """비밀번호 복호화하여 반환"""
        return decrypt_password(self._encrypted_password)
    
    @password.setter
    def password(self, value: str):
        """비밀번호 암호화하여 저장"""
        self._encrypted_password = encrypt_password(value)
        # 원본 비밀번호를 메모리에서 안전하게 제거
        secure_clear_password(value)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환 (저장용)"""
        data = asdict(self)
        # 암호화된 비밀번호는 저장하지 않음 (보안)
        data.pop('_encrypted_password', None)
        # 🔥 recent_posts는 저장 (자동 삭제 기능을 위해)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TabModel':
        """딕셔너리에서 생성 (불러오기용)"""
        # 없는 필드는 기본값 사용
        valid_fields = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid_fields)
    
    def update_settings(self, **kwargs):
        """설정 업데이트"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                try:
                    # 비밀번호 처리 시 특별한 안전 처리
                    if key == 'password' and value:
                        # 안전한 문자열로 변환
                        safe_password = str(value).strip()
                        setattr(self, key, safe_password)
                    else:
                        setattr(self, key, value)
                except Exception as e:
                    # 설정 업데이트 실패 시 로그만 남기고 계속 진행
                    from utils.logger import logger
                    logger.warning(f"설정 업데이트 실패 ({key}): {e}")
                    # 기본값으로 설정
                    if key == 'password':
                        setattr(self, key, "")
    
    def set_state(self, state: str):
        """상태 변경"""
        self.state = state
    
    def add_post(self, post_data: Dict[str, str]):
        """게시글 추가 (메모리 최적화)"""
        self.recent_posts.insert(0, post_data)
        # 최대 20개까지만 저장 (50 → 20)
        self.recent_posts = self.recent_posts[:20]
        self.total_posts += 1
        self.success_count += 1
    
    def clear_posts(self):
        """게시글 목록 초기화 (수동 삭제 시 사용)"""
        self.recent_posts.clear()
    
    def increment_fail(self):
        """실패 카운트 증가"""
        self.fail_count += 1
    
    def get_success_rate(self) -> float:
        """성공률 계산"""
        total = self.success_count + self.fail_count
        if total == 0:
            return 0.0
        return (self.success_count / total) * 100
    
    def reset_stats(self):
        """통계 초기화"""
        self.total_posts = 0
        self.success_count = 0
        self.fail_count = 0
        self.last_run_time = None
    
    def update_last_run(self):
        """마지막 실행 시간 업데이트"""
        self.last_run_time = time.time()
    
    def is_running(self) -> bool:
        """실행 중인지 확인"""
        return self.state in (TabState.RUNNING, TabState.WAITING, TabState.LOGIN)
    
    def can_start(self) -> bool:
        """시작 가능한지 확인 (필수 입력 체크)"""
        return all([
            self.user_id.strip(),
            self.password.strip(),
            self.title.strip(),
            self.content.strip(),
        ])
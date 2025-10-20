"""
Firebase 로그인 다이얼로그 (애플 스타일)
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QMessageBox, QWidget
)
from PySide6.QtCore import Qt, Signal, QPoint, QSize
from PySide6.QtGui import QFont, QPixmap

from ui.dialogs.success_dialog import SuccessDialog
from ui.dialogs.alert_dialog import show_warning
from ui.dialogs.confirm_dialog import show_confirm
from ui.widgets.custom_tooltip import install_custom_tooltip
from utils.constants import APP_NAME, FONT_FAMILY, get_icon_path
from utils.logger import logger
from utils.registry import get_last_email, save_last_email
import os
import time

# alert_dialog import 성공

# Firebase (선택적)
try:
    import pyrebase
    FIREBASE_OK = True
except ImportError:
    FIREBASE_OK = False

# Firebase Admin (Firestore용)
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_ADMIN_OK = True
except ImportError:
    FIREBASE_ADMIN_OK = False


class LoginWindow(QDialog):
    """Firebase 로그인 다이얼로그"""
    
    login_success = Signal()
    
    def __init__(self, firebase_config=None, parent=None):
        super().__init__(parent)
        self.firebase_config = firebase_config
        self.user_profile = None  # 로그인 후 사용자 프로필(nickname 등)
        
        # 레지스트리에서 마지막 이메일 불러오기
        self.last_email = get_last_email()
        
        # 드래그용 변수
        self.drag_position = QPoint()
        
        self._setup_window()
        self._setup_ui()
    
    def _setup_window(self):
        """윈도우 설정"""
        self.setWindowTitle(f"{APP_NAME} 로그인")
        self.setFixedSize(340, 400)  # 380 → 340, 440 → 400
        self.setModal(True)
        
        # 중앙 배치
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
        # 프레임 없는 윈도우 + 투명 배경
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
    
    def _setup_ui(self):
        """UI 초기화"""
        logger.debug("=== _setup_ui 시작 ===")
        logger.debug(f"install_custom_tooltip 함수: {install_custom_tooltip}")
        
        # 메인 컨테이너
        container = QFrame(self)
        container.setObjectName("loginContainer")
        container.setGeometry(0, 0, 340, 400)  # 크기 축소
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 타이틀바
        logger.debug("타이틀바 생성 시작...")
        titlebar = QFrame()
        titlebar.setObjectName("loginTitleBar")
        titlebar.setFixedHeight(44)
        titlebar_layout = QHBoxLayout(titlebar)
        titlebar_layout.setContentsMargins(16, 0, 16, 0)
        titlebar_layout.setSpacing(8)
        
        logger.debug("타이틀 라벨 생성...")
        # 타이틀 (왼쪽)
        title = QLabel(APP_NAME)
        title.setFont(QFont(FONT_FAMILY, 13, QFont.Bold))  # 15 → 13
        titlebar_layout.addWidget(title)
        
        titlebar_layout.addStretch()
        
        logger.debug("닫기 버튼 생성 시작...")
        # 닫기 버튼 (오른쪽)
        close_btn = QPushButton()
        close_btn.setObjectName("macCloseButton")
        close_btn.setFixedSize(12, 12)  # 원래 크기 유지
        close_btn.clicked.connect(self.on_close_clicked)
        
        # 커스텀 툴팁 적용 (iOS 스타일)
        logger.debug("커스텀 툴팁 설치 시도...")
        try:
            install_custom_tooltip(close_btn, "종료")
            logger.debug("✓ 커스텀 툴팁 설치 완료!")
        except Exception as e:
            logger.warning(f"✗ 커스텀 툴팁 설치 실패: {e}")
            close_btn.setToolTip("종료")  # 기본 툴팁으로 대체
        
        titlebar_layout.addWidget(close_btn)
        
        # 드래그 활성화
        titlebar.mousePressEvent = self._title_mouse_press
        titlebar.mouseMoveEvent = self._title_mouse_move
        
        layout.addWidget(titlebar)
        
        logger.debug("타이틀바 생성 완료!")
        
        # 컨텐츠 영역
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 16, 24, 20)  # 32-24-32-32 → 24-16-24-20
        content_layout.setSpacing(14)  # 20 → 14
        
        # 아이콘
        icon_path = get_icon_path('png')
        if os.path.exists(icon_path):
            icon_container = QWidget()
            icon_container.setFixedHeight(80)  # 100 → 80
            icon_layout = QVBoxLayout(icon_container)
            icon_layout.setContentsMargins(0, 6, 0, 6)  # 10 → 6
            icon_layout.setAlignment(Qt.AlignCenter)
            
            icon_label = QLabel()
            pixmap = QPixmap(icon_path).scaled(
                64, 64,  # 80 → 64
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_layout.addWidget(icon_label)
            
            content_layout.addWidget(icon_container)
        
        content_layout.addSpacing(6)  # 10 → 6
        
        # 이메일 입력
        email_label = QLabel("이메일")
        email_label.setFont(QFont(FONT_FAMILY, 10, QFont.Bold))  # 11 → 10
        email_label.setStyleSheet("color: rgba(28, 28, 30, 200);")
        content_layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setObjectName("loginInput")
        self.email_input.setPlaceholderText("example@email.com")
        self.email_input.setFixedHeight(38)  # 44 → 38
        if self.last_email:
            self.email_input.setText(self.last_email)
        content_layout.addWidget(self.email_input)
        
        # 비밀번호 입력
        pw_label = QLabel("비밀번호")
        pw_label.setFont(QFont(FONT_FAMILY, 10, QFont.Bold))  # 11 → 10
        pw_label.setStyleSheet("color: rgba(28, 28, 30, 200);")
        content_layout.addWidget(pw_label)
        
        self.password_input = QLineEdit()
        self.password_input.setObjectName("loginInput")
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(38)  # 44 → 38
        content_layout.addWidget(self.password_input)
        
        content_layout.addSpacing(12)  # 6 → 12로 증가
        
        # 로그인 버튼
        self.login_btn = QPushButton("로그인")
        self.login_btn.setObjectName("loginButton")
        self.login_btn.setFixedHeight(42)  # 48 → 42
        self.login_btn.clicked.connect(self.do_login)
        self.login_btn.setDefault(False)
        self.login_btn.setAutoDefault(False)
        content_layout.addWidget(self.login_btn)
        
        content_layout.addSpacing(8)  # 간격 추가
        
        # 하단 버튼들을 가로로 배치
        bottom_button_layout = QHBoxLayout()
        bottom_button_layout.setSpacing(8)
        
        # 회원가입 버튼 (왼쪽)
        self.signup_btn = QPushButton("회원가입")
        self.signup_btn.setObjectName("signupButton")
        self.signup_btn.setFixedHeight(38)
        self.signup_btn.clicked.connect(self.do_signup)
        bottom_button_layout.addWidget(self.signup_btn)
        
        # 문의 버튼 (오른쪽)
        self.inquiry_btn = QPushButton("관리자 문의")
        self.inquiry_btn.setObjectName("inquiryButton")
        self.inquiry_btn.setFixedHeight(38)
        
        self.inquiry_btn.clicked.connect(self.open_inquiry)
        bottom_button_layout.addWidget(self.inquiry_btn)
        
        content_layout.addLayout(bottom_button_layout)
        
        content_layout.addSpacing(20)  # 하단 버튼들 아래 여백 추가
        
        content_layout.addStretch()
        
        layout.addWidget(content)
        
        # Enter 키 바인딩 (do_login 직접 호출)
        self.email_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(lambda: self.do_login())
    
    def _title_mouse_press(self, event):
        """타이틀바 드래그 시작"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def _title_mouse_move(self, event):
        """타이틀바 드래그"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def on_close_clicked(self):
        """닫기 버튼 클릭"""
        self.reject()
    
    def do_login(self):
        """로그인 수행"""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        # 입력 확인
        if not email or not password:
            logger.debug("입력 오류 - show_warning 호출")
            show_warning(self, "입력 오류", "이메일과 비밀번호를 입력하세요.")
            return
        
        # 로그인 버튼 비활성화
        self.login_btn.setEnabled(False)
        self.login_btn.setText("로그인 중...")
        
        # Firebase 라이브러리 확인 (항상 필수)
        if not FIREBASE_OK:
            logger.error("pyrebase 미설치 - 로그인 불가")
            self.login_btn.setEnabled(True)
            self.login_btn.setText("로그인")
            show_warning(self, "로그인 불가", "로그인 라이브러리(pyrebase)가 설치되지 않았습니다.\n필요한 라이브러리를 설치해주세요.")
            return
        
        # Firebase 설정 확인 (내장 설정이 있으므로 항상 유효)
        if not self.firebase_config or self.firebase_config.get("disabled", False):
            logger.error("Firebase 설정이 비활성화됨 - 로그인 불가")
            self.login_btn.setEnabled(True)
            self.login_btn.setText("로그인")
            show_warning(self, "로그인 불가", "Firebase 설정이 비활성화되었습니다.")
            return
        
        # Firebase 로그인
        try:
            logger.info(f"Firebase 설정 확인: {self.firebase_config}")
            logger.info(f"API Key: {self.firebase_config.get('apiKey', 'N/A')}")
            logger.info(f"Auth Domain: {self.firebase_config.get('authDomain', 'N/A')}")
            logger.info(f"Project ID: {self.firebase_config.get('projectId', 'N/A')}")
            # logger.info(f"Database URL: {self.firebase_config.get('databaseURL', 'N/A')}")
            
            # Firebase 초기화 전에 설정 검증
            required_keys = ['apiKey', 'authDomain', 'projectId']
            for key in required_keys:
                if not self.firebase_config.get(key):
                    raise Exception(f"Firebase 설정에 {key}가 없습니다.")
            
            logger.info(f"Firebase 설정 검증 완료")
            firebase = pyrebase.initialize_app(self.firebase_config)
            auth = firebase.auth()
            
            logger.info(f"Firebase 초기화 성공")
            logger.info(f"Authentication 객체 생성 완료")
            logger.info(f"로그인 시도: {email}")
            
            # Firebase 인증 시도
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                logger.info(f"Firebase 인증 성공: {user}")
            except Exception as auth_error:
                logger.error(f"Firebase 인증 실패: {auth_error}")
                
                # Firebase 인증 실패 시 오류 메시지 표시
                error_msg = "이메일 또는 비밀번호를 확인하세요."
                if "INVALID_PASSWORD" in str(auth_error):
                    error_msg = "비밀번호가 올바르지 않습니다."
                elif "EMAIL_NOT_FOUND" in str(auth_error):
                    error_msg = "존재하지 않는 이메일입니다."
                elif "INVALID_EMAIL" in str(auth_error):
                    error_msg = "올바른 이메일 형식이 아닙니다."
                elif "NETWORK_REQUEST_FAILED" in str(auth_error):
                    error_msg = "네트워크 연결을 확인해주세요."
                
                # 버튼 복구
                self.login_btn.setEnabled(True)
                self.login_btn.setText("로그인")
                show_warning(self, "로그인 실패", error_msg)
                return
            
            logger.info(f"Firebase 로그인 성공: {email}")
            
            # 사용자 정보 저장 (IP 저장용)
            self._current_user = user
            
            # 사용자 승인 상태 확인
            approval_result = self._check_user_approval(firebase, user)
            
            if approval_result == 'suspended':
                # 비활성화 상태
                self.login_btn.setEnabled(True)
                self.login_btn.setText("로그인")
                show_warning(self, "계정 비활성화", "귀하의 계정이 비활성화되었습니다.\n관리자에게 문의해주세요.")
                return
            elif approval_result == 'expired':
                # 계정 만료
                self.login_btn.setEnabled(True)
                self.login_btn.setText("로그인")
                show_warning(self, "계정 만료", "귀하의 계정 사용 기간이 만료되었습니다.\n관리자에게 문의해주세요.")
                return
            elif not approval_result:
                # 승인 대기 상태
                self.login_btn.setEnabled(True)
                self.login_btn.setText("로그인")
                show_warning(self, "승인 대기", "관리자 승인을 기다리고 있습니다.\n승인 후 사용 가능합니다.")
                return
            
            # 최근 로그인 시간 업데이트
            try:
                import requests
                user_id = user.get('localId')
                project_id = self.firebase_config.get('projectId')
                api_key = self.firebase_config.get('apiKey')
                id_token = user.get('idToken')
                
                firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
                headers = {
                    'Authorization': f'Bearer {id_token}',
                    'Content-Type': 'application/json'
                }
                
                # lastLogin 필드 업데이트
                update_data = {
                    "fields": {
                        "lastLogin": {"integerValue": str(int(time.time() * 1000))}
                    }
                }
                
                requests.patch(f"{firestore_url}?key={api_key}&updateMask.fieldPaths=lastLogin", headers=headers, json=update_data)
                logger.info(f"최근 로그인 시간 업데이트 완료: {user_id}")
            except Exception as e:
                logger.error(f"최근 로그인 시간 업데이트 실패: {e}")
            
            # 닉네임 포함 사용자 프로필 가져오기
            try:
                profile = self._fetch_user_profile(user)
                self.user_profile = profile
                logger.info(f"사용자 프로필 로드: {profile}")
            except Exception as e:
                logger.warning(f"사용자 프로필 로드 실패(무시): {e}")
            
            # 성공 메시지 표시 후 accept
            self._show_success_and_accept(email)
            
        except Exception as e:
            logger.error(f"Firebase 로그인 실패: {e}")
            
            # 버튼 복구
            self.login_btn.setEnabled(True)
            self.login_btn.setText("로그인")
            
            # 에러 메시지 파싱
            error_msg = f"로그인 중 오류가 발생했습니다.\n\n오류 내용: {str(e)}"
            if "INVALID_PASSWORD" in str(e):
                error_msg = "비밀번호가 올바르지 않습니다."
            elif "EMAIL_NOT_FOUND" in str(e):
                error_msg = "존재하지 않는 이메일입니다."
            elif "INVALID_EMAIL" in str(e):
                error_msg = "올바른 이메일 형식이 아닙니다."
            elif "NETWORK_REQUEST_FAILED" in str(e):
                error_msg = "네트워크 연결을 확인해주세요."
            elif "TOO_MANY_ATTEMPTS_TRY_LATER" in str(e):
                error_msg = "너무 많은 시도로 인해 잠시 후 다시 시도해주세요."
            elif "INVALID_API_KEY" in str(e):
                error_msg = "Firebase API 키가 올바르지 않습니다."
            elif "PROJECT_NOT_FOUND" in str(e):
                error_msg = "Firebase 프로젝트를 찾을 수 없습니다."
            
            logger.debug("로그인 실패 - show_warning 호출")
            show_warning(self, "로그인 실패", error_msg)
    
    def do_signup(self):
        """회원가입 - 웹페이지로 연결"""
        # 확인창 표시 - 커스텀 다이얼로그 사용
        from ui.dialogs.confirm_dialog import show_confirm
        
        reply = show_confirm(
            self,
            "회원가입",
            "회원가입 페이지로 이동하시겠습니까?"
        )
        
        if reply:
            try:
                import webbrowser
                
                # 회원가입 페이지 URL
                signup_url = "https://xn--ob0by50d.store/signup"
                
                # 기본 브라우저로 열기
                webbrowser.open(signup_url)
                
                logger.info("회원가입 페이지 열기 성공")
                
            except Exception as e:
                logger.error(f"회원가입 페이지 열기 실패: {e}")
                show_warning(self, "회원가입 페이지 열기 실패", "회원가입 페이지를 열 수 없습니다.\n다시 시도해주세요.")
    
    def open_inquiry(self):
        """관리자 문의 - 홈페이지로 연결"""
        # 확인창 표시 - 커스텀 다이얼로그 사용
        from ui.dialogs.confirm_dialog import show_confirm
        
        reply = show_confirm(
            self,
            "관리자 문의",
            "홈페이지로 이동하시겠습니까?"
        )
        
        if reply:
            try:
                import webbrowser
                
                # 찬공의 스튜디오 홈페이지
                website_url = "https://xn--ob0by50d.store/"
                
                # 기본 브라우저로 열기
                webbrowser.open(website_url)
                
                logger.info("관리자 문의 홈페이지 열기 성공")
                
            except Exception as e:
                logger.error(f"홈페이지 열기 실패: {e}")
                show_warning(self, "홈페이지 열기 실패", "홈페이지를 열 수 없습니다.\n다시 시도해주세요.")
    
    def _check_user_approval(self, firebase, user):
        """사용자 승인 상태 확인"""
        try:
            logger.info(f"승인 상태 확인 시작 - 사용자: {user}")
            
            user_id = user['localId']
            user_email = user.get('email', '')
            
            # Firebase Authentication에서 기존 사용자인지 확인
            # (Firebase 인증을 통과했다면 기존 사용자로 간주)
            logger.info(f"Firebase 인증을 통과한 사용자: {user_email}")
            
            # Firebase Firestore에서 사용자 승인 상태 확인 (REST API 사용)
            try:
                import requests
                
                # Firestore REST API URL
                project_id = self.firebase_config.get('projectId')
                api_key = self.firebase_config.get('apiKey')
                firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
                
                # ID Token을 사용하여 인증
                id_token = user.get('idToken')
                headers = {
                    'Authorization': f'Bearer {id_token}',
                    'Content-Type': 'application/json'
                }
                
                # Firestore에서 사용자 데이터 조회
                response = requests.get(f"{firestore_url}?key={api_key}", headers=headers)
                
                logger.info(f"Firestore REST API 응답 코드: {response.status_code}")
                
                if response.status_code == 404:
                    # Firestore에 사용자 데이터가 없으면 승인 대기
                    logger.info(f"Firestore에 사용자 데이터 없음 - 승인 대기: {user_id}")
                    return False
                elif response.status_code != 200:
                    # 기타 오류
                    logger.error(f"Firestore REST API 오류: {response.status_code} - {response.text}")
                    logger.info(f"Firestore 연결 실패로 승인 거부: {user_id}")
                    return False
                
                # 사용자 데이터 파싱
                user_data = response.json()
                logger.info(f"Firestore 사용자 데이터: {user_data}")
                
                # fields에서 status와 expiryDate 추출
                fields = user_data.get('fields', {})
                status_field = fields.get('status', {})
                status = status_field.get('stringValue', 'pending')
                
                expiry_field = fields.get('expiryDate', {})
                expiry_date = expiry_field.get('integerValue') or expiry_field.get('timestampValue')
                
                logger.info(f"사용자 승인 상태: {status}, 만료일: {expiry_date} (사용자: {user_id})")
                
                # 만료일 체크
                if expiry_date and status == 'approved':
                    try:
                        import time
                        expiry_timestamp = int(expiry_date) if isinstance(expiry_date, str) else expiry_date
                        current_time = int(time.time() * 1000)  # 밀리초
                        
                        if current_time > expiry_timestamp:
                            logger.info(f"계정 만료: {user_email}, 만료일: {expiry_timestamp}")
                            return 'expired'
                    except Exception as exp_error:
                        logger.error(f"만료일 체크 오류: {exp_error}")
                
                # status에 따른 처리
                if status == 'approved':
                    logger.info(f"승인 완료: {user_email}")
                    return True
                elif status == 'suspended':
                    logger.info(f"일시정지 상태: {user_email}")
                    # 일시정지 메시지는 호출하는 곳에서 처리
                    return 'suspended'
                else:
                    logger.info(f"승인 대기: {user_email}")
                    return False
                
            except Exception as e:
                # Firestore 연결 오류
                logger.error(f"Firestore 연결 실패: {e}")
                # Firestore 연결 실패 시 승인되지 않은 것으로 처리
                logger.info(f"Firestore 연결 실패로 승인 거부: {user_id}")
                return False
            
        except Exception as e:
            logger.error(f"사용자 승인 상태 확인 실패: {e}")
            # 오류 발생 시 안전하게 승인되지 않은 것으로 처리
            return False

    def _fetch_user_profile(self, user) -> dict:
        """Firestore에서 사용자 닉네임 등 프로필 필드 로드"""
        import requests
        project_id = self.firebase_config.get('projectId')
        api_key = self.firebase_config.get('apiKey')
        user_id = user.get('localId')
        id_token = user.get('idToken')
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}?key={api_key}"
        headers = { 'Authorization': f'Bearer {id_token}' }
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code != 200:
            raise RuntimeError(f"프로필 조회 실패: {r.status_code}")
        doc = r.json()
        fields = doc.get('fields', {})
        nickname = (fields.get('nickname') or {}).get('stringValue')
        last_ip = (fields.get('lastLoginIP') or {}).get('stringValue')
        # 만료일(ms) 정규화
        expiry_raw = fields.get('expiryDate') or {}
        expiry_ms = None
        if 'integerValue' in expiry_raw:
            try:
                expiry_ms = int(expiry_raw.get('integerValue'))
            except Exception:
                expiry_ms = None
        elif 'timestampValue' in expiry_raw:
            # RFC3339를 ms로 변환
            from datetime import datetime, timezone
            try:
                dt = datetime.fromisoformat(expiry_raw['timestampValue'].replace('Z','+00:00'))
                expiry_ms = int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
            except Exception:
                expiry_ms = None
        email = user.get('email')
        # 닉네임 누락 시 이메일 앞부분으로 대체
        if not nickname and email:
            nickname = email.split('@')[0]
        return { 'uid': user_id, 'email': email, 'nickname': nickname, 'lastLoginIP': last_ip, 'expiryDateMs': expiry_ms }

    # 웹에서 닉네임 처리. 앱은 읽기 전용
    
    def _show_success_and_accept(self, email):
        """로그인 성공 메시지 표시 후 창 닫기"""
        # 이메일 저장
        save_last_email(email)
        
        # IP 정보 저장 (로그인 시)
        self._save_login_info(email)
        
        # 성공 다이얼로그
        dialog = SuccessDialog(self)
        dialog.exec()
        
        # 시그널 발생 및 창 닫기
        self.login_success.emit()
        self.accept()
    
    def _save_login_info(self, email):
        """로그인 정보 (IP, 시간 등) Firestore에 저장"""
        try:
            # IP 주소 가져오기
            import requests
            try:
                response = requests.get('https://api.ipify.org?format=json', timeout=3)
                ip_address = response.json().get('ip', 'unknown')
            except:
                ip_address = 'unknown'
                logger.warning("IP 주소 가져오기 실패")
            
            # pyrebase로 사용자 정보 가져오기
            if not FIREBASE_OK:
                logger.warning("pyrebase 미설치 - IP 저장 불가")
                return
            
            # 이미 로그인된 사용자 정보 사용 (중복 로그인 방지)
            # 현재 로그인된 사용자의 UID와 토큰을 사용
            if hasattr(self, '_current_user') and self._current_user:
                user_id = self._current_user.get('localId')
                id_token = self._current_user.get('idToken')
            else:
                # 대체 방법: 이메일로 사용자 찾기
                logger.warning("사용자 정보를 찾을 수 없음 - IP 저장 건너뜀")
                return
            
            # Firestore REST API로 직접 IP 정보 저장
            import json
            firestore_url = f"https://firestore.googleapis.com/v1/projects/{self.firebase_config['projectId']}/databases/(default)/documents/users/{user_id}"
            
            update_data = {
                "fields": {
                    "lastLoginAt": {"timestampValue": __import__('datetime').datetime.utcnow().isoformat() + "Z"},
                    "lastLoginIP": {"stringValue": ip_address}
                }
            }
            
            headers = {
                "Authorization": f"Bearer {id_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.patch(
                firestore_url,
                headers=headers,
                params={"updateMask.fieldPaths": "lastLoginAt", "updateMask.fieldPaths": "lastLoginIP"},
                data=json.dumps(update_data),
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"✅ 로그인 정보 저장 완료 - IP: {ip_address}")
            else:
                logger.warning(f"로그인 정보 저장 실패: {response.status_code} - {response.text}")
            
        except Exception as e:
            logger.warning(f"로그인 정보 저장 실패 (무시됨): {e}")
    
    def reject(self):
        """취소 (앱 종료) - 닫기 버튼을 눌렀을 때만 실행"""
        if show_confirm(self, "종료 확인", "로그인하지 않고 종료하시겠습니까?"):
            super().reject()
    
    def keyPressEvent(self, event):
        """키보드 이벤트 - ESC와 Enter 처리"""
        if event.key() == Qt.Key_Escape:
            # ESC만 종료 확인
            self.reject()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Enter는 이미 returnPressed에서 처리됨
            # 이벤트를 완전히 소비해서 QDialog의 기본 동작 방지
            event.accept()
        else:
            super().keyPressEvent(event)
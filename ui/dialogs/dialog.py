"""
로그인 성공 다이얼로그
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

from utils.constants import FONT_FAMILY, get_icon_path
import os


class SuccessDialog(QDialog):
    """로그인 성공 다이얼로그"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_window()
        self._setup_ui()
    
    def _setup_window(self):
        """윈도우 설정"""
        self.setWindowTitle("로그인 성공")
        self.setFixedSize(320, 280)
        self.setModal(True)
        
        # 중앙 배치
        if self.parent():
            parent_geo = self.parent().geometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            self.move(x, y)
        
        # 프레임 없는 윈도우 + 투명 배경
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
    
    def _setup_ui(self):
        """UI 초기화"""
        # 메인 컨테이너
        container = QFrame(self)
        container.setObjectName("successContainer")
        container.setGeometry(0, 0, 320, 280)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)
        
        # 로고
        icon_path = get_icon_path('png')
        if os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path).scaled(
                80, 80,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)
        
        # 성공 메시지
        message = QLabel("✓ 로그인 성공!")
        message.setAlignment(Qt.AlignCenter)
        message.setFont(QFont(FONT_FAMILY, 18, QFont.Bold))
        message.setStyleSheet("color: #34C759;")  # 초록색
        layout.addWidget(message)
        
        # 환영 메시지
        welcome = QLabel("환영합니다!")
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setFont(QFont(FONT_FAMILY, 13))
        welcome.setStyleSheet("color: rgba(28, 28, 30, 180);")
        layout.addWidget(welcome)
        
        layout.addSpacing(10)
        
        # 확인 버튼
        ok_btn = QPushButton("확인")
        ok_btn.setObjectName("successOkButton")
        ok_btn.setFixedHeight(44)
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        ok_btn.setFocus()
        layout.addWidget(ok_btn)
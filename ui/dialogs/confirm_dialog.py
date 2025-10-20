"""
iOS 스타일 확인 다이얼로그
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPainter, QColor

from utils.constants import FONT_FAMILY


class QuestionIcon(QLabel):
    """iOS 스타일 질문 아이콘"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(48, 48)
    
    def paintEvent(self, event):
        """커스텀 페인팅"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 배경 원 (파란색)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 122, 255))
        painter.drawEllipse(0, 0, 48, 48)
        
        # 물음표 (?)
        painter.setBrush(QColor(255, 255, 255))
        
        # 물음표 윗부분 (곡선 - 간단하게 원으로)
        painter.drawEllipse(18, 14, 12, 10)
        
        # 물음표 중간 부분
        painter.drawRoundedRect(21, 22, 6, 10, 3, 3)
        
        # 물음표 아래 점
        painter.drawEllipse(21, 36, 6, 6)


class ConfirmDialog(QDialog):
    """iOS 스타일 확인 다이얼로그"""
    
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.title_text = title
        self.message_text = message
        
        self._setup_window()
        self._setup_ui()
    
    def _setup_window(self):
        """윈도우 설정"""
        self.setWindowTitle(self.title_text)
        self.setFixedSize(340, 210)  # 여백 포함 크기
        self.setModal(True)
        
        # 프레임 없는 윈도우 + 투명 배경
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
    
    def _setup_ui(self):
        """UI 초기화"""
        # 메인 컨테이너
        container = QFrame(self)
        container.setObjectName("confirmContainer")
        container.setGeometry(10, 5, 320, 200)  # 중앙 배치를 위한 여백
        container.setStyleSheet("""
            QFrame#confirmContainer {
                background-color: white;
                border-radius: 18px;
                border: 1px solid rgba(0, 0, 0, 0.15);
            }
        """)
        
        # 그림자 효과 - 더 강하게!
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)  # 20 → 30
        shadow.setColor(QColor(0, 0, 0, 80))  # 40 → 80 (더 진하게)
        shadow.setOffset(0, 6)  # 4 → 6
        container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 16)  # 24-20-24-18 → 20-16-20-16
        layout.setSpacing(4)  # 6 → 4
        layout.setAlignment(Qt.AlignCenter)
        
        # 질문 아이콘 - 크기 줄임
        question_icon = QuestionIcon()
        layout.addWidget(question_icon, 0, Qt.AlignCenter)
        
        layout.addSpacing(2)  # 간격 최소화
        
        # 타이틀
        title_label = QLabel(self.title_text)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))  # 13 → 12
        title_label.setStyleSheet("color: #1C1C1E;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        layout.addSpacing(2)
        
        # 메시지
        message_label = QLabel(self.message_text)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setFont(QFont(FONT_FAMILY, 10))  # 11 → 10
        message_label.setStyleSheet("color: rgba(60, 60, 67, 0.7); padding: 0 10px;")  # 좌우 패딩 추가!
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        layout.addSpacing(6)  # 8 → 6
        
        # 버튼들
        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)  # 8 → 6
        
        # No 버튼
        no_btn = QPushButton("아니오")
        no_btn.setFixedHeight(32)  # 36 → 32
        no_btn.setCursor(Qt.PointingHandCursor)
        no_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(120, 120, 128, 0.16);
                color: #007AFF;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(120, 120, 128, 0.24);
            }
            QPushButton:pressed {
                background-color: rgba(120, 120, 128, 0.32);
            }
        """)
        no_btn.clicked.connect(self.reject)
        button_layout.addWidget(no_btn)
        
        # Yes 버튼
        yes_btn = QPushButton("예")
        yes_btn.setFixedHeight(32)  # 36 → 32
        yes_btn.setCursor(Qt.PointingHandCursor)
        yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0066CC;
            }
            QPushButton:pressed {
                background-color: #0055AA;
            }
        """)
        yes_btn.clicked.connect(self.accept)
        yes_btn.setDefault(True)
        button_layout.addWidget(yes_btn)
        
        layout.addLayout(button_layout)


def show_confirm(parent, title, message):
    """확인 다이얼로그 표시 (Yes=True, No=False)"""
    dialog = ConfirmDialog(title, message, parent)
    
    # 부모 창 중앙에 배치
    if parent:
        parent_geo = parent.geometry()
        x = parent_geo.x() + (parent_geo.width() - dialog.width()) // 2
        y = parent_geo.y() + (parent_geo.height() - dialog.height()) // 2
        dialog.move(x, y)
    
    result = dialog.exec()
    return result == QDialog.Accepted
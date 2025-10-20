"""
iOS 스타일 경고 다이얼로그
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPainter, QColor

from utils.constants import FONT_FAMILY


class WarningIcon(QLabel):
    """iOS 스타일 경고 아이콘"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(48, 48)
    
    def paintEvent(self, event):
        """커스텀 페인팅"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 배경 원 (주황색)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 149, 0))
        painter.drawEllipse(0, 0, 48, 48)
        
        # 느낌표 (!)
        painter.setBrush(QColor(255, 255, 255))
        
        # 느낌표 윗부분
        painter.drawRoundedRect(21, 14, 6, 18, 3, 3)
        
        # 느낌표 아래 점
        painter.drawEllipse(21, 36, 6, 6)


class AlertDialog(QDialog):
    """iOS 스타일 경고 다이얼로그"""
    
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.title_text = title
        self.message_text = message
        
        self._setup_window()
        self._setup_ui()
    
    def _setup_window(self):
        """윈도우 설정"""
        self.setWindowTitle(self.title_text)
        self.setFixedSize(320, 230)
        self.setModal(True)
        
        # 중앙 배치 - 듀얼모니터 지원
        if self.parent():
            parent_geo = self.parent().geometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            
            # 부모 창이 있는 모니터 찾기 (듀얼모니터 지원)
            from PySide6.QtWidgets import QApplication
            parent_screen = self.parent().screen()
            if parent_screen:
                screen_geo = parent_screen.geometry()
            else:
                # 폴백: 부모 창 위치 기준으로 모니터 찾기
                parent_center = parent_geo.center()
                parent_screen = QApplication.screenAt(parent_center)
                if parent_screen:
                    screen_geo = parent_screen.geometry()
                else:
                    # 최후 폴백: 주 모니터 사용
                    screen_geo = QApplication.primaryScreen().geometry()
            
            # 해당 모니터 경계 내에서 위치 조정
            if x < screen_geo.left():
                x = screen_geo.left() + 10
            if y < screen_geo.top():
                y = screen_geo.top() + 10
            if x + self.width() > screen_geo.right():
                x = screen_geo.right() - self.width() - 10
            if y + self.height() > screen_geo.bottom():
                y = screen_geo.bottom() - self.height() - 10
            
            self.move(x, y)
        
        # 프레임 없는 윈도우 + 투명 배경
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
    
    def _setup_ui(self):
        """UI 초기화"""
        # 메인 컨테이너
        container = QFrame(self)
        container.setObjectName("alertContainer")
        container.setGeometry(0, 0, 320, 230)
        container.setStyleSheet("""
            QFrame#alertContainer {
                background-color: white;
                border-radius: 18px;
                border: 1px solid rgba(0, 0, 0, 0.08);
            }
        """)
        
        # 그림자 효과
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)
        
        # 경고 아이콘
        warning_icon = WarningIcon()
        layout.addWidget(warning_icon, 0, Qt.AlignCenter)
        
        # 타이틀
        title_label = QLabel(self.title_text)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont(FONT_FAMILY, 11, QFont.Bold))
        title_label.setStyleSheet("color: #1C1C1E;")
        layout.addWidget(title_label)
        
        # 메시지
        message_label = QLabel(self.message_text)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setFont(QFont(FONT_FAMILY, 9))
        message_label.setStyleSheet("color: rgba(60, 60, 67, 0.6);")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        layout.addSpacing(4)
        
        # 확인 버튼
        ok_btn = QPushButton("확인")
        ok_btn.setFixedHeight(38)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0066CC;
            }
            QPushButton:pressed {
                background-color: #0055AA;
            }
        """)
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        ok_btn.setFocus()
        layout.addWidget(ok_btn)


def show_warning(parent, title, message):
    """경고 다이얼로그 표시"""
    dialog = AlertDialog(title, message, parent)
    
    # 부모 창 중앙에 배치
    if parent:
        parent_geo = parent.geometry()
        x = parent_geo.x() + (parent_geo.width() - dialog.width()) // 2
        y = parent_geo.y() + (parent_geo.height() - dialog.height()) // 2
        dialog.move(x, y)
    
    return dialog.exec()
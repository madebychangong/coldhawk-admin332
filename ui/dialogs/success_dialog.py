"""
로그인 성공 다이얼로그 (iOS 스타일)
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QPainterPath
from utils.constants import FONT_FAMILY


class CheckIcon(QLabel):
    """iOS 스타일 체크 아이콘 (원형 배경 + 부드러운 체크)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(56, 56)
    
    def paintEvent(self, event):
        """커스텀 페인팅"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 배경 원 (초록색)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(52, 199, 89))
        painter.drawEllipse(4, 4, 48, 48)
        
        # 체크 표시 (✓) - iOS 스타일로 부드럽게
        pen = QPen(QColor(255, 255, 255), 4)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        
        # 체크 경로 (더 부드러운 곡선)
        path = QPainterPath()
        path.moveTo(19, 28)
        path.lineTo(25, 34)
        path.lineTo(37, 22)
        painter.drawPath(path)


class SuccessDialog(QDialog):
    """로그인 성공 다이얼로그"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_window()
        self._setup_ui()
    
    def _setup_window(self):
        """윈도우 설정"""
        self.setWindowTitle("로그인 성공")
        self.setFixedSize(220, 180)  # 260 → 220, 200 → 180
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
        container.setObjectName("successContainer")
        container.setGeometry(0, 0, 220, 180)  # 크기 축소
        
        # 그림자 효과 추가
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 6)
        container.setGraphicsEffect(shadow)
        
        # 테두리 추가
        container.setStyleSheet("""
            QFrame#successContainer {
                background-color: white;
                border-radius: 18px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 18)  # 24-28-24-24 → 20-20-20-18
        layout.setSpacing(10)  # 14 → 10
        layout.setAlignment(Qt.AlignCenter)
        
        # 체크 아이콘
        check_icon = CheckIcon()
        layout.addWidget(check_icon, 0, Qt.AlignCenter)
        
        layout.addSpacing(2)  # 4 → 2
        
        # 성공 메시지
        message = QLabel("로그인 성공")
        message.setAlignment(Qt.AlignCenter)
        message.setFont(QFont(FONT_FAMILY, 12, QFont.DemiBold))  # 14 → 12
        message.setStyleSheet("color: #1C1C1E;")
        layout.addWidget(message)
        
        layout.addSpacing(4)  # 8 → 4
        
        # 확인 버튼
        ok_btn = QPushButton("확인")
        ok_btn.setObjectName("successOkButton")
        ok_btn.setFixedHeight(36)  # 40 → 36
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        ok_btn.setFocus()
        layout.addWidget(ok_btn)


def show_success(parent, title, message):
    """성공 다이얼로그 표시"""
    # 기본 SuccessDialog는 제목과 메시지를 받지 않으므로 간단하게 표시
    dialog = SuccessDialog(parent)
    
    # 부모 창 중앙에 배치
    if parent:
        parent_geo = parent.geometry()
        x = parent_geo.x() + (parent_geo.width() - dialog.width()) // 2
        y = parent_geo.y() + (parent_geo.height() - dialog.height()) // 2
        dialog.move(x, y)
    
    return dialog.exec()
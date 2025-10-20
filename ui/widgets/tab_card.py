"""
탭 카드 위젯 (iOS 스타일 - 숫자 없이)
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from utils.constants import FONT_FAMILY, TabState


class TabCard(QWidget):
    """탭 카드 위젯"""
    
    clicked = Signal(int)  # tab_id
    
    def __init__(self, tab_id: int, name: str = "", parent=None):
        super().__init__(parent)
        self.tab_id = tab_id
        self.tab_name = name or f"{tab_id}번"
        self.state = TabState.STOPPED
        self.is_selected = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """UI 초기화"""
        self.setFixedSize(54, 54)  # 52 → 54 (조금 더 크게)
        self.setCursor(Qt.PointingHandCursor)
        
        # 메인 프레임
        self.frame = QFrame(self)
        self.frame.setObjectName("tabCard")
        self.frame.setGeometry(0, 0, 54, 54)  # 52 → 54 (조금 더 크게)
        
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(3, 6, 3, 6)  # 원래대로 복원
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignCenter)
        
        # 상태 표시 (작은 점)
        self.status_dot = QLabel("●")
        self.status_dot.setAlignment(Qt.AlignCenter)
        self.status_dot.setFont(QFont(FONT_FAMILY, 6))  # 원래대로 복원
        self.status_dot.setStyleSheet("color: rgba(142, 142, 147, 1);")
        layout.addWidget(self.status_dot)
        
        # 탭 이름
        self.name_label = QLabel(self.tab_name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setFont(QFont(FONT_FAMILY, 9))  # 원래대로 복원
        self.name_label.setWordWrap(False)
        layout.addWidget(self.name_label)
        
        self._update_style()
    
    def set_selected(self, selected: bool):
        """선택 상태 설정"""
        self.is_selected = selected
        self.frame.setProperty("selected", selected)
        self.frame.style().unpolish(self.frame)
        self.frame.style().polish(self.frame)
        self._update_style()
    
    def set_state(self, state: str):
        """상태 설정"""
        self.state = state
        self._update_status_dot()
    
    def set_name(self, name: str):
        """이름 변경"""
        self.tab_name = name
        if len(name) > 6:
            name = name[:5] + "…"
        self.name_label.setText(name)
    
    def _update_status_dot(self):
        """상태 점 업데이트"""
        color_map = {
            TabState.STOPPED: "rgba(142, 142, 147, 1)",
            TabState.RUNNING: "rgba(52, 199, 89, 1)",
            TabState.WAITING: "rgba(255, 149, 0, 1)",
            TabState.ERROR: "rgba(255, 59, 48, 1)",
            TabState.LOGIN: "rgba(0, 122, 255, 1)",
        }
        color = color_map.get(self.state, "rgba(142, 142, 147, 1)")
        self.status_dot.setStyleSheet(f"color: {color};")
    
    def _update_style(self):
        """스타일 업데이트"""
        if self.is_selected:
            self.name_label.setStyleSheet("color: white;")
        else:
            self.name_label.setStyleSheet("color: rgba(28, 28, 30, 0.6);")
    
    def mousePressEvent(self, event):
        """클릭"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.tab_id)
        super().mousePressEvent(event)
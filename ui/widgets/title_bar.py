"""
커스텀 타이틀바 (Windows 스타일 버튼)
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QFont, QPixmap
from utils.constants import APP_NAME, FONT_FAMILY, FONT_SIZES, get_icon_path
from ui.widgets.custom_tooltip import install_custom_tooltip
import os


class TitleBar(QWidget):
    """커스텀 타이틀바"""
    
    minimize_clicked = Signal()
    hide_clicked = Signal()
    close_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.drag_position = QPoint()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """UI 초기화"""
        self.setFixedHeight(40)
        self.setObjectName("titleBar")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)
        
        # 아이콘 (실제 파일만)
        icon_path = get_icon_path('png')
        if os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            layout.addWidget(icon_label)
        
        # 앱 이름
        title = QLabel(APP_NAME)
        title.setFont(QFont(FONT_FAMILY, FONT_SIZES['large'], QFont.Bold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Windows 스타일 버튼들 (우측)
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)
        
        # 최소화 버튼 (노란색)
        self.min_btn = QPushButton()
        self.min_btn.setObjectName("macMinButton")
        self.min_btn.setFixedSize(12, 12)  # 원래 크기로 복구
        self.min_btn.clicked.connect(self.minimize_clicked.emit)
        
        # 커스텀 툴팁 적용
        install_custom_tooltip(self.min_btn, "최소화")
        
        button_layout.addWidget(self.min_btn)
        
        # 숨기기 버튼 (파란색)
        self.hide_btn = QPushButton()
        self.hide_btn.setObjectName("macHideButton")
        self.hide_btn.setFixedSize(12, 12)
        self.hide_btn.clicked.connect(self.hide_clicked.emit)
        
        # 커스텀 툴팁 적용
        install_custom_tooltip(self.hide_btn, "숨기기")
        
        button_layout.addWidget(self.hide_btn)
        
        # 닫기 버튼 (빨간색)
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("macCloseButton")
        self.close_btn.setFixedSize(12, 12)  # 원래 크기로 복구
        self.close_btn.clicked.connect(self.close_clicked.emit)
        
        # 커스텀 툴팁 적용
        install_custom_tooltip(self.close_btn, "종료")
        
        button_layout.addWidget(self.close_btn)
        
        layout.addWidget(button_container)
    
    def mousePressEvent(self, event):
        """마우스 누름"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """마우스 드래그"""
        if event.buttons() == Qt.LeftButton:
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)
        super().mouseMoveEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """더블클릭 (최대화/복원)"""
        if event.button() == Qt.LeftButton:
            if self.parent_window.isMaximized():
                self.parent_window.showNormal()
            else:
                self.parent_window.showMaximized()
        super().mouseDoubleClickEvent(event)
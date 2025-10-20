"""
로그 뷰어 위젯 (메모리 최적화)
"""
from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QTextCursor, QFont

from utils.constants import FONT_FAMILY, FONT_MONO, FONT_SIZES, LOG_ICONS, COLORS


class LogViewer(QWidget):
    """로그 뷰어 위젯"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.max_lines = 100  # 500 → 100 (메모리 최적화)
        
        # 배치 처리용 버퍼
        self.log_buffer = []
        self.batch_timer = QTimer(self)
        self.batch_timer.timeout.connect(self._flush_logs)
        self.batch_timer.start(500)  # 0.5초마다 배치 처리
        
        self._setup_ui()
    
    def _setup_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 헤더
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("실행 로그")
        title.setObjectName("logTitle")
        title.setFont(QFont(FONT_FAMILY, FONT_SIZES['large'], QFont.Bold))
        header.addWidget(title)
        
        header.addStretch()
        
        # 지우기 버튼
        clear_btn = QPushButton("🧹 지우기")
        clear_btn.setObjectName("clearLogButton")
        clear_btn.setFixedSize(100, 32)
        clear_btn.clicked.connect(self.clear_logs)
        header.addWidget(clear_btn)
        
        layout.addLayout(header)
        
        # 로그 텍스트
        self.log_text = QTextEdit()
        self.log_text.setObjectName("logText")
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont(FONT_MONO, FONT_SIZES['normal']))
        layout.addWidget(self.log_text)
    
    @Slot(str, str)
    def add_log(self, message: str, level: str = "info"):
        """로그 추가 (배치 처리)"""
        # 현재 시간
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 아이콘
        icon = LOG_ICONS.get(level, "💡")
        
        # 색상
        color_map = {
            'info': COLORS['text_secondary'],
            'success': COLORS['accent_green'],
            'warning': COLORS['accent_orange'],
            'error': COLORS['accent_red'],
            'debug': COLORS['text_tertiary'],
        }
        color = color_map.get(level, COLORS['text_primary'])
        
        # HTML 형식
        html_line = (
            f'<span style="color: {COLORS["text_tertiary"]}">[{timestamp}]</span> '
            f'<span style="color: {color}">{icon} {message}</span>'
        )
        
        # 버퍼에 추가 (즉시 표시 안 함)
        self.log_buffer.append(html_line)
        
        # 버퍼가 너무 크면 즉시 flush
        if len(self.log_buffer) >= 10:
            self._flush_logs()
    
    def _flush_logs(self):
        """버퍼의 로그를 일괄 처리"""
        if not self.log_buffer:
            return
        
        # 일괄 추가
        for html_line in self.log_buffer:
            self.log_text.append(html_line)
        
        self.log_buffer.clear()
        
        # 자동 스크롤
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
        
        # 라인 수 제한
        self._trim_logs()
    
    def _trim_logs(self):
        """로그 라인 수 제한"""
        doc = self.log_text.document()
        if doc.blockCount() > self.max_lines:
            cursor = QTextCursor(doc)
            cursor.movePosition(QTextCursor.Start)
            
            # 초과 라인 삭제
            excess = doc.blockCount() - self.max_lines
            for _ in range(excess):
                cursor.select(QTextCursor.BlockUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()  # 줄바꿈 삭제
    
    @Slot()
    def clear_logs(self):
        """로그 지우기"""
        self.log_buffer.clear()
        self.log_text.clear()
        self.add_log("로그가 지워졌습니다", "info")
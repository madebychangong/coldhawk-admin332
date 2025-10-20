"""
탭 설정 패널
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QRadioButton, QButtonGroup, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from core.models.tab_model import TabModel
from utils.constants import (
    FONT_FAMILY, FONT_SIZES, COLORS, BOARD_MAP,
    DEFAULT_WRITE_COUNT, DEFAULT_RUN_HOURS, DEFAULT_UPLOAD_INTERVAL
)


class TabSettingsPanel(QWidget):
    """탭 설정 패널"""
    
    # 시그널
    start_requested = Signal(TabModel)
    stop_requested = Signal(int)  # tab_id
    delete_requested = Signal(int)  # tab_id
    settings_changed = Signal(TabModel)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_tab: TabModel = None
        self._setup_ui()
    
    def _setup_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)  # 24 → 16
        layout.setSpacing(12)  # 20 → 12
        
        # 헤더
        header = QHBoxLayout()
        self.title_label = QLabel("탭 설정")
        self.title_label.setFont(QFont(FONT_FAMILY, 13, QFont.Bold))  # 14 → 13
        header.addWidget(self.title_label)
        header.addStretch()
        layout.addLayout(header)
        
        # 구분선
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("separator")
        layout.addWidget(line)
        
        # 설정 폼
        form = QGridLayout()
        form.setSpacing(12)  # 16 → 12
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)
        
        row = 0
        
        # 게시판 선택
        form.addWidget(self._create_label("게시판"), row, 0, Qt.AlignVCenter)
        self.board_combo = QComboBox()
        self.board_combo.addItems(list(BOARD_MAP.keys()))
        self.board_combo.setFixedWidth(200)
        self.board_combo.setFixedHeight(36)  # 높이 축소
        form.addWidget(self.board_combo, row, 1, 1, 3)
        row += 1
        
        # 아이디
        form.addWidget(self._create_label("아이디"), row, 0, Qt.AlignVCenter)
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("인벤 아이디")
        self.id_input.setFixedHeight(36)  # 높이 축소
        form.addWidget(self.id_input, row, 1)
        
        # 비밀번호
        form.addWidget(self._create_label("비밀번호"), row, 2, Qt.AlignVCenter)
        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_input.setPlaceholderText("비밀번호")
        self.pw_input.setFixedHeight(36)  # 높이 축소
        
        # 붙여넣기 이벤트 처리 (복사붙여넣기 문제 해결)
        self.pw_input.installEventFilter(self)
        
        form.addWidget(self.pw_input, row, 3)
        row += 1
        
        # 제목
        form.addWidget(self._create_label("제목"), row, 0, Qt.AlignVCenter)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("게시글 제목")
        self.title_input.setFixedHeight(36)  # 높이 축소
        form.addWidget(self.title_input, row, 1, 1, 3)
        row += 1
        
        # 내용
        form.addWidget(self._create_label("내용"), row, 0, Qt.AlignTop)
        
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(6)  # 8 → 6
        
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("게시글 내용 (HTML 지원)")
        self.content_input.setFont(QFont(FONT_FAMILY, FONT_SIZES['normal']))
        self.content_input.setMinimumHeight(100)  # 120 → 100
        self.content_input.setMaximumHeight(160)  # 200 → 160
        content_layout.addWidget(self.content_input)
        
        # 글자 수 카운터
        self.char_count_label = QLabel("0자")
        self.char_count_label.setAlignment(Qt.AlignRight)
        self.char_count_label.setFont(QFont(FONT_FAMILY, FONT_SIZES['small']))
        self.char_count_label.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        content_layout.addWidget(self.char_count_label)
        
        form.addWidget(content_container, row, 1, 1, 3)
        row += 1
        
        # 시간 설정
        form.addWidget(self._create_label("실행시간"), row, 0, Qt.AlignVCenter)
        
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setValue(DEFAULT_RUN_HOURS)
        self.hour_spin.setFixedWidth(100)
        self.hour_spin.setFixedHeight(36)  # 높이 축소
        self.hour_spin.setSuffix(" 시간")
        self.hour_spin.setSpecialValueText("무한")
        form.addWidget(self.hour_spin, row, 1)
        
        # 재업로드 간격
        form.addWidget(self._create_label("재업로드"), row, 2, Qt.AlignVCenter)
        
        interval_widget = QWidget()
        interval_layout = QHBoxLayout(interval_widget)
        interval_layout.setContentsMargins(0, 0, 0, 0)
        interval_layout.setSpacing(12)
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(2, 86400)
        self.interval_spin.setValue(DEFAULT_UPLOAD_INTERVAL)
        self.interval_spin.setSuffix(" 초")
        self.interval_spin.setFixedWidth(100)
        self.interval_spin.setFixedHeight(36)  # 높이 축소
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()
        
        form.addWidget(interval_widget, row, 3)
        row += 1
        
        layout.addLayout(form)
        
        # 구분선
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setObjectName("separator")
        layout.addWidget(line2)
        
        # 버튼들
        buttons = QHBoxLayout()
        buttons.setSpacing(10)  # 12 → 10
        
        self.start_btn = QPushButton("실행")
        self.start_btn.setObjectName("startButton")
        self.start_btn.setFixedSize(110, 40)  # 120x44 → 110x40
        self.start_btn.clicked.connect(self._on_start_clicked)
        buttons.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("중지")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setFixedSize(110, 40)  # 120x44 → 110x40
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        buttons.addWidget(self.stop_btn)
        
        self.delete_btn = QPushButton("글삭제")
        self.delete_btn.setObjectName("deleteButton")
        self.delete_btn.setFixedSize(110, 40)  # 120x44 → 110x40
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        buttons.addWidget(self.delete_btn)
        
        buttons.addStretch()
        
        layout.addLayout(buttons)
        layout.addStretch()
        
        # 시그널 연결
        self.content_input.textChanged.connect(self._update_char_count)
    
    def _create_label(self, text: str) -> QLabel:
        """레이블 생성"""
        label = QLabel(text)
        label.setFont(QFont(FONT_FAMILY, FONT_SIZES['normal'], QFont.Bold))
        return label
    
    def _update_char_count(self):
        """글자 수 업데이트"""
        count = len(self.content_input.toPlainText())
        self.char_count_label.setText(f"{count}자")
        self.char_count_label.setStyleSheet(f"color: {COLORS['text_tertiary']};")
    
    def load_tab(self, tab: TabModel):
        """탭 데이터 로드"""
        self.current_tab = tab
        
        # UI 업데이트
        self.title_label.setText(f"{tab.name} 설정")
        
        # 설정 값 로드
        board_index = list(BOARD_MAP.keys()).index(tab.board_name) if tab.board_name in BOARD_MAP else 0
        self.board_combo.setCurrentIndex(board_index)
        
        self.id_input.setText(tab.user_id)
        self.pw_input.setText(tab.password)
        self.title_input.setText(tab.title)
        self.content_input.setPlainText(tab.content)
        
        self.hour_spin.setValue(tab.run_hours)
        self.interval_spin.setValue(tab.upload_interval)
        
        self._update_char_count()
    
    def save_to_tab(self):
        """현재 입력값을 탭에 저장"""
        if not self.current_tab:
            return
        
        self.current_tab.update_settings(
            board_name=self.board_combo.currentText(),
            user_id=self.id_input.text(),
            password=self.pw_input.text(),
            title=self.title_input.text(),
            content=self.content_input.toPlainText(),
            write_count=1,
            run_hours=self.hour_spin.value(),
            upload_interval=self.interval_spin.value()
        )
        
        self.settings_changed.emit(self.current_tab)
    
    def _on_start_clicked(self):
        """실행 버튼"""
        if not self.current_tab:
            return
        
        self.save_to_tab()
        self.start_requested.emit(self.current_tab)
    
    def _on_stop_clicked(self):
        """중지 버튼"""
        if not self.current_tab:
            return
        
        self.stop_requested.emit(self.current_tab.tab_id)
    
    def _on_delete_clicked(self):
        """삭제 버튼"""
        if not self.current_tab:
            return
        
        self.save_to_tab()
        self.delete_requested.emit(self.current_tab.tab_id)
    
    def set_enabled(self, enabled: bool):
        """입력 활성/비활성"""
        self.board_combo.setEnabled(enabled)
        self.id_input.setEnabled(enabled)
        self.pw_input.setEnabled(enabled)
        self.title_input.setEnabled(enabled)
        self.content_input.setEnabled(enabled)
        self.hour_spin.setEnabled(enabled)
        self.interval_spin.setEnabled(enabled)
        self.start_btn.setEnabled(enabled)
        self.delete_btn.setEnabled(enabled)
    
    def eventFilter(self, obj, event):
        """이벤트 필터 (비밀번호 붙여넣기 처리)"""
        if obj == self.pw_input and event.type() == event.Type.KeyPress:
            # Ctrl+V (붙여넣기) 처리
            if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_V:
                try:
                    from PySide6.QtWidgets import QApplication
                    clipboard = QApplication.clipboard()
                    text = clipboard.text()
                    
                    # 특수문자 안전 처리
                    if text:
                        # 안전한 문자열로 변환
                        safe_text = str(text).strip()
                        self.pw_input.setText(safe_text)
                        return True  # 기본 이벤트 차단
                except Exception as e:
                    # 붙여넣기 실패 시 기본 동작으로 폴백
                    pass
        
        return super().eventFilter(obj, event)
"""
메인 윈도우
"""
import json
from typing import Optional, Dict
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QPushButton, QFrame, QSystemTrayIcon, QMenu,
    QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon, QAction

from ui.widgets.title_bar import TitleBar
from ui.widgets.tab_card import TabCard
from ui.widgets.tab_settings_panel import TabSettingsPanel
from ui.widgets.log_viewer import LogViewer
from ui.dialogs.confirm_dialog import show_confirm
from core.models.tab_model import TabModel
from core.controllers.macro_controller import MacroController
from utils.constants import (
    APP_NAME, WINDOW_SIZE, DEFAULT_TAB_COUNT,
    get_icon_path, get_settings_file, TabState
)
from utils.logger import logger
import os


class MainWindow(QMainWindow):
    """메인 윈도우"""
    
    def __init__(self, user_profile: Optional[Dict] = None, parent=None, **kwargs):
        super().__init__(parent)
        self.user_profile = user_profile or {}
        self._content_layout = None  # 런타임에 상단 배지 주입용
        self._user_badge = None
        
        # 데이터
        self.tabs = {}  # {tab_id: TabModel}
        self.tab_cards = {}  # {tab_id: TabCard}
        self.current_tab_id = 1
        
        # 컨트롤러
        self.macro_controller = MacroController()
        
        # 시스템 트레이
        self.tray_icon = None
        self._setup_system_tray()
        
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
        self._load_settings()
        
        # 첫 번째 탭 선택
        self._select_tab(1)
    
    def _setup_system_tray(self):
        """시스템 트레이 설정"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("시스템 트레이를 사용할 수 없습니다.")
            return
        
        # 트레이 아이콘 생성
        icon_path = get_icon_path('ico')
        if not icon_path or not os.path.exists(icon_path):
            icon_path = get_icon_path('png')
        
        if icon_path and os.path.exists(icon_path):
            self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        else:
            self.tray_icon = QSystemTrayIcon(self)
        
        # 트레이 메뉴 생성
        tray_menu = QMenu()
        
        # 보이기 액션
        show_action = QAction("보이기", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        # 종료 액션
        quit_action = QAction("종료", self)
        quit_action.triggered.connect(self._on_close_requested)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip(APP_NAME)
        
        # 더블클릭으로 창 보이기
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        # 트레이 아이콘 표시
        self.tray_icon.show()
        
        logger.info("시스템 트레이 설정 완료")
    
    def _on_tray_activated(self, reason):
        """트레이 아이콘 활성화"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()
    
    def _setup_window(self):
        """윈도우 설정"""
        self.setWindowTitle(APP_NAME)
        self.resize(*WINDOW_SIZE)
        
        # 프레임 없는 윈도우
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 투명 배경 활성화
        
        # 아이콘
        icon_path = get_icon_path('png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 중앙 위젯
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
    
    def _setup_ui(self):
        """UI 구성"""
        # 타이틀바
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        # 메인 컨텐츠
        content = QWidget()
        content.setObjectName("mainContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(12, 12, 12, 12)  # 16 → 12
        content_layout.setSpacing(12)  # 16 → 12
        self._content_layout = content_layout

        # 상단 사용자 정보(닉네임) 표시는 텍스트 라벨(welcome_label)로만 처리
        
        # 탭 카드 영역
        tabs_section = self._create_tabs_section()
        content_layout.addWidget(tabs_section)
        
        # 설정 + 로그 영역
        bottom_section = QWidget()
        bottom_layout = QHBoxLayout(bottom_section)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(12)  # 16 → 12
        
        # 설정 패널
        self.settings_panel = TabSettingsPanel()
        self.settings_panel.setObjectName("settingsPanel")
        bottom_layout.addWidget(self.settings_panel, stretch=3)
        
        # 로그 뷰어
        log_container = QWidget()
        log_container.setObjectName("logContainer")
        log_layout = QVBoxLayout(log_container)
        log_layout.setContentsMargins(12, 12, 12, 12)  # 16 → 12
        
        self.log_viewer = LogViewer()
        log_layout.addWidget(self.log_viewer)
        
        bottom_layout.addWidget(log_container, stretch=2)
        
        content_layout.addWidget(bottom_section, stretch=1)
        
        self.main_layout.addWidget(content)

    def _inject_user_badge(self, nickname: str):
        """상단 닉네임 배지를 레이아웃 최상단에 삽입"""
        try:
            bar = QHBoxLayout()
            tag = QPushButton(f"닉네임: {nickname}")
            tag.setObjectName("tagButton")
            tag.setEnabled(False)
            tag.setFixedHeight(26)
            bar.addWidget(tag)
            bar.addStretch()
            if self._content_layout:
                self._content_layout.insertLayout(0, bar)
            self._user_badge = tag
        except Exception:
            pass

    def set_user_profile(self, profile: Dict):
        """로그인 후 닉네임을 주입하기 위한 세터"""
        self.user_profile = profile or {}
        nick = self.user_profile.get('nickname')
        if hasattr(self, 'welcome_label'):
            self._update_welcome_label()
    
    def _create_tabs_section(self) -> QWidget:
        """탭 카드 섹션 생성"""
        section = QWidget()
        section.setObjectName("tabsSection")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(12, 12, 12, 12)  # 4 → 12 (다른 요소들과 일치)
        layout.setSpacing(6)  # 8 → 6
        
        # 헤더
        header = QHBoxLayout()
        
        # 전체 제어 버튼들
        self.stop_all_btn = QPushButton("전체중지")
        self.stop_all_btn.setObjectName("stopAllButton")
        self.stop_all_btn.setFixedSize(100, 32)  # 110x34 → 100x32
        header.addWidget(self.stop_all_btn)
        
        self.delete_all_btn = QPushButton("전체삭제")
        self.delete_all_btn.setObjectName("deleteAllButton")
        self.delete_all_btn.setFixedSize(100, 32)  # 110x34 → 100x32
        header.addWidget(self.delete_all_btn)
        
        header.addStretch()  # 버튼들을 왼쪽으로 밀기 위해 추가
        
        # 환영 라벨 (버튼 옆 긴 영역에 표시)
        self.welcome_label = QLabel()
        self.welcome_label.setObjectName("welcomeLabel")
        # 밝은 패널에서도 보이도록 어두운 텍스트 사용
        self.welcome_label.setStyleSheet("color: #2c2c2e; font-weight: 600; font-size: 12px;")
        self.welcome_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.welcome_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._update_welcome_label()
        header.addWidget(self.welcome_label)
        
        layout.addLayout(header)
        
        # 구분선
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("separator")
        layout.addWidget(line)
        
        # 스크롤 영역 (탭 카드들)
        scroll = QScrollArea()
        scroll.setObjectName("tabScrollArea")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFixedHeight(100)
        # scroll.setMaximumWidth(450)  # 이 줄이 탭 공간을 제한하는 원인!
        
        # 탭 카드 컨테이너
        self.tabs_container = QWidget()
        self.tabs_layout = QHBoxLayout(self.tabs_container)
        self.tabs_layout.setContentsMargins(0, 4, 0, 4)  # 2 → 0 (좌우 여백 완전 제거)
        self.tabs_layout.setSpacing(3)  # 4 → 3 (더 타이트하게)
        
        # 탭 생성 (10개)
        for i in range(1, DEFAULT_TAB_COUNT + 1):
            tab_model = TabModel(tab_id=i)
            self.tabs[i] = tab_model
            
            card = TabCard(i, tab_model.name)
            self.tab_cards[i] = card
            self.tabs_layout.addWidget(card)
        
        # + 버튼 제거됨
        
        self.tabs_layout.addStretch()
        
        scroll.setWidget(self.tabs_container)
        layout.addWidget(scroll)
        
        return section
    
    def _update_welcome_label(self):
        profile = self.user_profile or {}
        name = profile.get('nickname') or ''
        ip = profile.get('lastLoginIP') or ''
        # 남은 일수 대신 이용기한 날짜 표기
        expiry_txt = ''
        try:
            # expiryDateMs 필드명으로 수정
            expiry = profile.get('expiryDateMs')
            if expiry:
                from datetime import datetime
                # Firestore Timestamp 객체인 경우
                if hasattr(expiry, 'toDate'):
                    dt = expiry.toDate()
                # 숫자인 경우 (밀리초)
                elif isinstance(expiry, (int, float)) and expiry > 0:
                    dt = datetime.fromtimestamp(expiry / 1000.0)
                # 문자열인 경우
                elif isinstance(expiry, str):
                    dt = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
                else:
                    dt = datetime.fromtimestamp(expiry)
                expiry_txt = f"이용기한: {dt.year}년 {dt.month}월 {dt.day}일까지"
        except Exception as e:
            print(f"이용기한 파싱 오류: {e}")
            expiry_txt = ''
        parts = []
        if name:
            parts.append(f"닉네임: {name}")
        if ip:
            parts.append(f"로그인IP: {ip}")
        if expiry_txt:
            parts.append(expiry_txt)
        self.welcome_label.setText("  |  ".join(parts))
    
    def _connect_signals(self):
        """시그널 연결"""
        # 타이틀바
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.hide_clicked.connect(self._on_hide_requested)
        self.title_bar.close_clicked.connect(self._on_close_requested)
        
        # 탭 카드 클릭
        for card in self.tab_cards.values():
            card.clicked.connect(self._select_tab)
        
        # 설정 패널
        self.settings_panel.start_requested.connect(self._on_start_macro)
        self.settings_panel.stop_requested.connect(self._on_stop_macro)
        self.settings_panel.delete_requested.connect(self._on_delete_posts)
        self.settings_panel.settings_changed.connect(self._on_settings_changed)
        
        # 전체 제어
        self.stop_all_btn.clicked.connect(self._on_stop_all)
        self.delete_all_btn.clicked.connect(self._on_delete_all)
        
        # 매크로 컨트롤러
        self.macro_controller.log_message.connect(self.log_viewer.add_log)
        self.macro_controller.state_changed.connect(self._on_state_changed)
        self.macro_controller.post_created.connect(self._on_post_created)
    
    @Slot(int)
    def _select_tab(self, tab_id: int):
        """탭 선택"""
        if tab_id not in self.tabs:
            return
        
        # 🔥 중요: 현재 탭 내용 먼저 저장!
        if hasattr(self, 'settings_panel') and self.settings_panel.current_tab:
            self.settings_panel.save_to_tab()
        
        self.current_tab_id = tab_id
        
        # 카드 선택 표시
        for tid, card in self.tab_cards.items():
            card.set_selected(tid == tab_id)
        
        # 설정 패널 로드
        tab = self.tabs[tab_id]
        self.settings_panel.load_tab(tab)
        
        logger.info(f"탭 선택: {tab.name}")
    
    @Slot(TabModel)
    def _on_start_macro(self, tab: TabModel):
        """매크로 시작"""
        self.macro_controller.start_macro(tab)
        self._save_settings()
    
    @Slot(int)
    def _on_stop_macro(self, tab_id: int):
        """매크로 중지"""
        tab = self.tabs.get(tab_id)
        if tab:
            self.macro_controller.stop_macro(tab_id, tab.name)
    
    @Slot(int)
    def _on_delete_posts(self, tab_id: int):
        """게시글 삭제"""
        tab = self.tabs.get(tab_id)
        if not tab:
            return
        
        # 커스텀 확인 다이얼로그
        if show_confirm(
            self,
            "글삭제 확인",
            f"{tab.board_name}의 내 글을 모두 삭제할까요?\n⚠️ 되돌릴 수 없습니다."
        ):
            self.macro_controller.delete_posts(tab)
            self._save_settings()
    
    @Slot()
    def _on_stop_all(self):
        """전체 중지"""
        self.macro_controller.stop_all()
    
    @Slot()
    def _on_delete_all(self):
        """전체 삭제"""
        # 커스텀 확인 다이얼로그
        if show_confirm(
            self,
            "전체 글삭제",
            "모든 탭의 게시글을 삭제할까요?\n⚠️ 되돌릴 수 없습니다."
        ):
            for tab in self.tabs.values():
                if tab.user_id and tab.password:
                    self.macro_controller.delete_posts(tab)
    
    @Slot(int, str)
    def _on_state_changed(self, tab_id: int, state: str):
        """상태 변경"""
        if tab_id in self.tabs:
            self.tabs[tab_id].set_state(state)
        
        if tab_id in self.tab_cards:
            self.tab_cards[tab_id].set_state(state)
    
    @Slot(int, dict)
    def _on_post_created(self, tab_id: int, post_data: dict):
        """게시글 작성됨"""
        pass
    
    @Slot(TabModel)
    def _on_settings_changed(self, tab: TabModel):
        """설정 변경"""
        self._save_settings()
    
    def _save_settings(self):
        """설정 저장"""
        try:
            settings = {
                'tabs': {
                    str(tid): tab.to_dict()
                    for tid, tab in self.tabs.items()
                }
            }
            
            with open(get_settings_file(), 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            logger.info("설정 저장 완료")
        except Exception as e:
            logger.exception(f"설정 저장 실패: {e}")
    
    def _load_settings(self):
        """설정 불러오기"""
        try:
            settings_file = get_settings_file()
            if not os.path.exists(settings_file):
                return
            
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            tabs_data = settings.get('tabs', {})
            for tid_str, tab_data in tabs_data.items():
                tid = int(tid_str)
                if tid in self.tabs:
                    loaded_tab = TabModel.from_dict(tab_data)
                    self.tabs[tid] = loaded_tab
                    
                    # 카드 업데이트
                    if tid in self.tab_cards:
                        self.tab_cards[tid].set_name(loaded_tab.name)
            
            logger.info("설정 불러오기 완료")
        except Exception as e:
            logger.exception(f"설정 불러오기 실패: {e}")
    
    def _on_hide_requested(self):
        """숨기기 요청 (시스템 트레이로)"""
        self.hide()
        if self.tray_icon:
            self.tray_icon.showMessage(
                APP_NAME,
                "프로그램이 시스템 트레이로 숨겨졌습니다.",
                QSystemTrayIcon.Information,
                2000
            )
    
    def _on_close_requested(self):
        """닫기 요청"""
        # 커스텀 확인 다이얼로그
        if show_confirm(self, "종료 확인", "정말 종료할까요?"):
            self.close()
    
    def closeEvent(self, event):
        """종료 이벤트"""
        # 🔥 현재 탭 내용 저장
        if hasattr(self, 'settings_panel') and self.settings_panel.current_tab:
            self.settings_panel.save_to_tab()
        
        # 설정 저장
        self._save_settings()
        
        # 매크로 정리
        self.macro_controller.cleanup()
        
        # 트레이 아이콘 정리
        if self.tray_icon:
            self.tray_icon.hide()
        
        logger.info("프로그램 종료")
        event.accept()
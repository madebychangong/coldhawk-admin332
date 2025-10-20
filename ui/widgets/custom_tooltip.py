"""
iOS 스타일 커스텀 툴팁 (TranslucentBackground 완벽 지원)
"""
from PySide6.QtWidgets import QLabel, QGraphicsDropShadowEffect, QApplication
from PySide6.QtCore import Qt, QTimer, QPoint, QRect
from PySide6.QtGui import QFont, QPainter, QColor, QPainterPath
from utils.constants import FONT_FAMILY


class CustomTooltip(QLabel):
    """iOS 스타일 툴팁 - 직접 페인팅 방식"""
    
    _instance = None
    
    def __init__(self):
        # 부모 없이 생성 - 완전 독립적인 윈도우
        super().__init__(None)
        
        # 윈도우 플래그 - 최상위 툴팁
        self.setWindowFlags(
            Qt.WindowType.ToolTip |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        
        # 속성 설정
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        
        # 스타일
        self.setFont(QFont(FONT_FAMILY, 10))  # 폰트 크기 11 → 10
        self.setMargin(0)
        self.setContentsMargins(10, 6, 10, 6)  # 여백 축소
        
        # 타이머
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.hide)
        
        self.hide()
    
    @classmethod
    def instance(cls):
        """싱글톤 인스턴스"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def paintEvent(self, event):
        """커스텀 페인팅 - 직접 그리기"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 툴팁 영역
        rect = self.rect()
        
        # 그림자만 그리기 (아주 부드럽게)
        for i in range(4, 0, -1):
            alpha = int(15 - i * 3)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 0, 0, alpha))
            shadow_rect = rect.adjusted(2 - i, 2 - i, -2 + i, -2 + i)
            painter.drawRoundedRect(shadow_rect, 6, 6)
        
        # 메인 배경 (밝은 회색)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(100, 100, 100))  # 밝은 회색
        main_rect = rect.adjusted(2, 2, -2, -2)
        painter.drawRoundedRect(main_rect, 6, 6)
        
        # 텍스트 그리기
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(self.font())
        painter.drawText(main_rect, Qt.AlignmentFlag.AlignCenter, self.text())
    
    def show_tooltip(self, text, widget, delay=200):
        """툴팁 표시"""
        if not text:
            return
        
        # 툴팁 표시 시작
        
        # 텍스트 설정
        self.setText(text)
        
        # 크기 계산 (더 작게)
        metrics = self.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()
        
        # 여백 포함 (줄임)
        width = text_width + 20  # 좌우 여백 축소
        height = text_height + 14  # 상하 여백 축소
        
        self.setFixedSize(width, height)
        
        # 툴팁 크기 설정 완료
        
        # 위치 계산 (위젯 아래 중앙)
        global_pos = widget.mapToGlobal(QPoint(0, widget.height()))
        x = global_pos.x() + (widget.width() - width) // 2
        y = global_pos.y() + 6
        
        # 화면 경계 체크 - 듀얼모니터 지원
        # 위젯이 있는 모니터 찾기
        widget_screen = widget.screen()
        if widget_screen:
            screen_geo = widget_screen.geometry()
        else:
            # 폴백: 위젯 위치 기준으로 모니터 찾기
            widget_center = widget.mapToGlobal(widget.rect().center())
            widget_screen = QApplication.screenAt(widget_center)
            if widget_screen:
                screen_geo = widget_screen.geometry()
            else:
                # 최후 폴백: 주 모니터 사용
                screen_geo = QApplication.primaryScreen().geometry()
        
        if x + width > screen_geo.right():
            x = screen_geo.right() - width - 10
        if x < screen_geo.left():
            x = screen_geo.left() + 10
        if y + height > screen_geo.bottom():
            # 위젯 위쪽에 표시
            y = global_pos.y() - widget.height() - height - 6
        
        # 툴팁 위치 설정 완료
        
        self.move(x, y)
        
        # 딜레이 후 표시
        QTimer.singleShot(delay, self._do_show)
        
        # 3초 후 자동 숨김
        self.hide_timer.start(3000)
    
    def _do_show(self):
        """실제 표시"""
        self.show()
        self.raise_()
        self.update()  # 강제 리페인트
    
    def hide_tooltip(self):
        """툴팁 숨김"""
        self.hide_timer.stop()
        self.hide()


def install_custom_tooltip(widget, text):
    """위젯에 커스텀 툴팁 설치"""
    tooltip = CustomTooltip.instance()
    
    print(f"[툴팁] 설치 시작: '{text}'")
    
    def on_enter(event):
        print(f"[툴팁] 마우스 진입!")
        tooltip.show_tooltip(text, widget)
        if hasattr(widget, '_original_enter_event'):
            widget._original_enter_event(event)
    
    def on_leave(event):
        print(f"[툴팁] 마우스 이탈!")
        tooltip.hide_tooltip()
        if hasattr(widget, '_original_leave_event'):
            widget._original_leave_event(event)
    
    widget._original_enter_event = widget.enterEvent
    widget._original_leave_event = widget.leaveEvent
    widget.enterEvent = on_enter
    widget.leaveEvent = on_leave
    widget.setToolTip("")  # 기본 툴팁 비활성화
    
    print(f"[툴팁] 설치 완료: '{text}'")
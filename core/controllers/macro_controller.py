"""
매크로 실행 컨트롤러 (메모리 최적화)
"""
import time
import threading
from typing import Optional, Dict

from PySide6.QtCore import QObject, Signal

from core.models.tab_model import TabModel
from core.services.http_service import HttpService
from utils.constants import TabState
from utils.logger import logger


class MacroController(QObject):
    """매크로 실행 컨트롤러"""
    
    # 시그널 정의
    log_message = Signal(str, str)  # (message, level)
    state_changed = Signal(int, str)  # (tab_id, state)
    progress_updated = Signal(int, int, int, int)  # (tab_id, current, total, success)
    post_created = Signal(int, dict)  # (tab_id, post_data)
    
    def __init__(self):
        super().__init__()
        self.threads: Dict[int, threading.Thread] = {}
        self.stop_events: Dict[int, threading.Event] = {}
        self.http_services: Dict[int, HttpService] = {}
        
        # 탭 시작 시간 추적 (타이밍 분산용)
        self.last_start_time = 0
        self.start_delay = 0.3  # 각 탭 시작 간격 (초) - 동시 시작 과부하 완화
    
    def start_macro(self, tab: TabModel):
        """매크로 시작 (타이밍 분산)"""
        tab_id = tab.tab_id
        
        # 이미 실행 중인지 확인
        if tab_id in self.threads and self.threads[tab_id].is_alive():
            self.log_message.emit(f"[{tab.name}] 이미 실행 중입니다", "warning")
            return
        
        # 필수 입력 확인
        if not tab.can_start():
            self.log_message.emit(f"[{tab.name}] 아이디·비번·제목·내용을 입력하세요", "error")
            return
        
        # 타이밍 분산: 이전 탭 시작 후 0.1초 대기
        current_time = time.time()
        elapsed = current_time - self.last_start_time
        if elapsed < self.start_delay:
            time.sleep(self.start_delay - elapsed)
        self.last_start_time = time.time()
        
        # Stop 이벤트 생성
        self.stop_events[tab_id] = threading.Event()
        
        # 스레드 생성 및 시작
        thread = threading.Thread(
            target=self._run_macro,
            args=(tab,),
            daemon=True
        )
        self.threads[tab_id] = thread
        thread.start()
        
        self.log_message.emit(f"[{tab.name}] 매크로 시작", "success")
    
    def stop_macro(self, tab_id: int, tab_name: str = ""):
        """매크로 중지"""
        if tab_id in self.stop_events:
            self.stop_events[tab_id].set()
        
        # 즉시 스레드 정리
        self._cleanup_thread(tab_id)
    
    def stop_all(self):
        """모든 매크로 중지"""
        count = 0
        for tab_id, event in list(self.stop_events.items()):
            if not event.is_set():
                event.set()
                count += 1
        
        # 모든 스레드 정리
        for tab_id in list(self.threads.keys()):
            self._cleanup_thread(tab_id)
    
    def _cleanup_thread(self, tab_id: int):
        """스레드 즉시 정리"""
        if tab_id in self.threads:
            thread = self.threads[tab_id]
            if thread.is_alive():
                thread.join(timeout=0.5)  # 최대 0.5초 대기
            del self.threads[tab_id]
    
    def _run_macro(self, tab: TabModel):
        """매크로 실행 (스레드)"""
        tab_id = tab.tab_id
        stop_event = self.stop_events[tab_id]
        
        # HTTP 서비스 생성 (재사용)
        http = HttpService()
        self.http_services[tab_id] = http
        
        try:
            # 시작 시간
            start_time = time.time()
            max_time_sec = float('inf') if tab.run_hours == 0 else tab.run_hours * 3600
            post_count = 0
            
            # 로그인 상태
            self.state_changed.emit(tab_id, TabState.LOGIN)
            
            # 로그인
            if not http.login(tab.user_id, tab.password):
                self.log_message.emit(f"[{tab.name}] 로그인 실패", "error")
                self.state_changed.emit(tab_id, TabState.ERROR)
                return
            
            self.log_message.emit(f"[{tab.name}] 로그인 완료", "success")
            tab.update_last_run()
            
            # 이번 실행 세션에서 작성하는 글만 관리하기 위해 메모리 목록 초기화
            tab.recent_posts = []
            
            # 🔥 시작 시 검증: 저장된 글 목록과 실제 게시판 동기화 (삭제 금지, 목록 미변경)
            try:
                saved_count = len(tab.recent_posts)
                actual_posts = http.list_my_posts(tab.board_name, pages=1)
                actual_count = len(actual_posts)
                
                # 시작 시에는 절대 삭제하지 않음. 또한 최근 목록은 '우리가 작성한 글'만 유지하기 위해 변경하지 않음
                logger.info(f"[{tab.name}] 게시글 현황 확인만 수행: 서버 {actual_count}개, 로컬 최근 {saved_count}개")
                    
            except Exception as e:
                logger.warning(f"[{tab.name}] 게시글 동기화 실패 (계속 진행): {e}")
            
            # 메인 루프
            batch_number = 0
            reupload_logged = False
            has_written_in_session = False  # 첫 성공 작성 전에는 어떤 자동 삭제도 금지
            
            while not stop_event.is_set():
                # 시간 초과 확인
                if time.time() - start_time >= max_time_sec:
                    self.log_message.emit(f"[{tab.name}] 설정 시간 종료", "info")
                    break
                
                # 실행 상태
                self.state_changed.emit(tab_id, TabState.RUNNING)
                
                batch_number += 1
                
                # 재업로드시: 간격 표시 (딱 한 번만)
                if batch_number > 1 and not reupload_logged:
                    interval_text = f"{tab.upload_interval}초"
                    if tab.upload_interval >= 60:
                        minutes = tab.upload_interval // 60
                        seconds = tab.upload_interval % 60
                        if seconds == 0:
                            interval_text = f"{minutes}분"
                        else:
                            interval_text = f"{minutes}분 {seconds}초"
                    
                    self.log_message.emit(
                        f"[{tab.name}] {interval_text} 마다 재업로드 진행중",
                        "info"
                    )
                    reupload_logged = True
                
                # 글쓰기
                success_in_batch = 0
                for i in range(tab.write_count):
                    if stop_event.is_set():
                        break
                    
                    # 글 작성
                    result = http.write_post(tab.board_name, tab.title, tab.content)
                    
                    if result:
                        # 이번 세션에서 작성한 글로 표시
                        try:
                            result["owned"] = True
                        except Exception:
                            pass
                        post_count += 1
                        success_in_batch += 1
                        has_written_in_session = True
                        
                        # 탭 모델에 추가
                        tab.add_post(result)
                        
                        # 시그널 발송
                        self.post_created.emit(tab_id, result)
                        self.progress_updated.emit(tab_id, i+1, tab.write_count, success_in_batch)
                        
                        # 첫 배치에만 개별 성공 로그
                        if batch_number == 1:
                            self.log_message.emit(
                                f"[{tab.name}] 글 작성 완료",
                                "success"
                            )
                        
                        # 🔥 자동 정리: 작성 성공 직후 전체 내 글을 수집해 "최신 3개만 유지" (idx 추출 여부와 무관)
                        KEEP_LIMIT = 3  # 테스트용 유지 개수 (원하면 5로 복구/설정화 가능)
                        try:
                            my_posts = http.list_my_posts(tab.board_name, pages=50)  # 최대 50페이지 수집
                            # 정렬: 최신(idx 큰 값) → 오래된(idx 작은 값)
                            try:
                                my_posts_sorted = sorted(
                                    my_posts,
                                    key=lambda p: int(str(p.get("idx", "0")).split("?")[0]),
                                    reverse=True,
                                )
                            except Exception:
                                my_posts_sorted = my_posts
                            # 최신 KEEP_LIMIT개를 제외한 나머지(오래된 항목들) 삭제
                            if len(my_posts_sorted) > KEEP_LIMIT:
                                for post in reversed(my_posts_sorted[KEEP_LIMIT:]):
                                    idx_str = str(post.get("idx", ""))
                                    http.delete_post(post.get("slug", ""), post.get("come_idx", ""), idx_str)
                        except Exception:
                            pass
                    else:
                        # 실패 시 로그를 남기지 않고 조용히 넘어감
                        tab.increment_fail()
                
                # 배치 결과 확인: 성공 0이어도 아무 로그 없이 계속 유지
                if success_in_batch == 0:
                    pass
                
                # 대기 상태
                self.state_changed.emit(tab_id, TabState.WAITING)
                
                # 대기 (로그 없이 조용히)
                interval = max(0.2, float(getattr(tab, 'upload_interval', 0) or 0))  # 최소 인터벌 보장
                remain = interval
                while remain > 0 and not stop_event.is_set():
                    time.sleep(min(1.0, remain))
                    remain -= 1.0

                # 방어적: 인터벌이 매우 작거나 0인 경우에도 CPU 양보
                if not stop_event.is_set():
                    time.sleep(0.01)
            
            # 정상 종료
            if not stop_event.is_set():
                self.log_message.emit(
                    f"[{tab.name}] 완료 (총 {post_count}개 작성)",
                    "success"
                )
                self.state_changed.emit(tab_id, TabState.STOPPED)
            else:
                self.log_message.emit(f"[{tab.name}] 중지됨", "warning")
                self.state_changed.emit(tab_id, TabState.STOPPED)
        
        except Exception as e:
            logger.exception(f"[{tab.name}] 오류 발생")
            self.log_message.emit(f"[{tab.name}] 오류: {str(e)}", "error")
            self.state_changed.emit(tab_id, TabState.ERROR)
        
        finally:
            # 정리
            http.close()
            if tab_id in self.http_services:
                del self.http_services[tab_id]
            if tab_id in self.stop_events:
                del self.stop_events[tab_id]
            
            # 스레드 정리
            self._cleanup_thread(tab_id)
    
    def delete_posts(self, tab: TabModel, on_progress=None):
        """게시글 삭제 (별도 스레드)"""
        thread = threading.Thread(
            target=self._delete_posts_thread,
            args=(tab, on_progress),
            daemon=True
        )
        thread.start()
    
    def _delete_posts_thread(self, tab: TabModel, on_progress):
        """게시글 삭제 스레드"""
        tab_id = tab.tab_id
        
        # HTTP 서비스
        http = HttpService()
        
        try:
            self.state_changed.emit(tab_id, TabState.RUNNING)
            
            # 로그인
            if not http.login(tab.user_id, tab.password):
                self.log_message.emit(f"[{tab.name}] 로그인 실패", "error")
                self.state_changed.emit(tab_id, TabState.ERROR)
                return
            
            # 삭제 콜백
            def progress_callback(current, total, success):
                if on_progress:
                    on_progress(current, total, success)
            
            # 삭제 실행
            total, success = http.delete_all_my_posts(tab.board_name, on_progress=progress_callback)
            
            # 🔥 삭제 완료 후 recent_posts 초기화
            tab.clear_posts()
            
            # 결과 로그
            if total == 0:
                self.log_message.emit(f"[{tab.name}] 삭제할 글이 없습니다", "info")
            elif success == total:
                self.log_message.emit(f"[{tab.name}] 삭제 완료: {success}개", "success")
            else:
                self.log_message.emit(f"[{tab.name}] 일부 실패: {success}/{total}개", "warning")
            
            self.state_changed.emit(tab_id, TabState.STOPPED)
        
        except Exception as e:
            logger.exception(f"[{tab.name}] 삭제 오류")
            self.log_message.emit(f"[{tab.name}] 삭제 오류: {str(e)}", "error")
            self.state_changed.emit(tab_id, TabState.ERROR)
        
        finally:
            http.close()
    
    def cleanup(self):
        """정리"""
        # 모든 매크로 중지
        self.stop_all()
        
        # 스레드 종료 대기
        for tab_id, thread in list(self.threads.items()):
            if thread.is_alive():
                thread.join(timeout=1.0)
        
        # HTTP 서비스 정리
        for http in self.http_services.values():
            http.close()
        
        self.threads.clear()
        self.stop_events.clear()
        self.http_services.clear()
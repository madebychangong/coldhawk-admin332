"""
HTTP 매크로 엔진 (인벤 로그인/글쓰기/삭제)
"""
import time
import html
from typing import Optional, Dict, List, Tuple, Callable
from urllib.parse import urlsplit

import requests
from requests import Session
from bs4 import BeautifulSoup

from utils.constants import (
    BOARD_MAP, BOARD_SLUG, DEFAULT_USER_AGENT,
    HTTP_TIMEOUT, HTTP_MAX_RETRIES, HTTP_RETRY_DELAY
)
from utils.logger import logger


class HttpService:
    """HTTP 매크로 서비스"""
    
    def __init__(self):
        self.session: Session = requests.Session()
        self.timeout = HTTP_TIMEOUT
        self.max_retries = HTTP_MAX_RETRIES
        
        # 기본 헤더
        self.session.headers.update({
            'User-Agent': DEFAULT_USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate'
        })
    
    def close(self):
        """세션 종료"""
        try:
            self.session.close()
        except Exception:
            pass
    
    # ==================== Retry Helpers ====================
    
    def _sleep_backoff(self, attempt: int):
        """재시도 대기 (지수 백오프)"""
        delay = min(2.0, HTTP_RETRY_DELAY * (2 ** attempt))
        if delay > 0:
            time.sleep(delay)
    
    def _get(self, url: str, **kwargs):
        """GET 요청 (재시도 포함)"""
        for attempt in range(self.max_retries):
            try:
                return self.session.get(url, timeout=self.timeout, **kwargs)
            except Exception as e:
                logger.warning(f"GET 실패 ({attempt+1}/{self.max_retries}): {url} - {e}")
                if attempt < self.max_retries - 1:
                    self._sleep_backoff(attempt)
                else:
                    raise
    
    def _post(self, url: str, **kwargs):
        """POST 요청 (재시도 포함)"""
        for attempt in range(self.max_retries):
            try:
                return self.session.post(url, timeout=self.timeout, **kwargs)
            except Exception as e:
                logger.warning(f"POST 실패 ({attempt+1}/{self.max_retries}): {url} - {e}")
                if attempt < self.max_retries - 1:
                    self._sleep_backoff(attempt)
                else:
                    raise
    
    # ==================== 로그인 ====================
    
    @staticmethod
    def _encode_password(pw: str) -> str:
        """비밀번호 인코딩 (인벤 방식)"""
        return "".join(format(ord(c), "x") for c in pw)
    
    def _extract_login_form(self) -> Optional[Dict[str, any]]:
        """로그인 폼 토큰 추출"""
        try:
            # 메인 페이지 방문
            self._get("https://www.inven.co.kr/", allow_redirects=True)
            
            # 로그인 페이지
            r = self._get("https://member.inven.co.kr/user/scorpio/mlogin")
            if r.status_code != 200:
                logger.error("로그인 페이지 연결 실패")
                return None
            
            soup = BeautifulSoup(r.text, "html.parser")
            
            # CSRF 토큰
            st_input = soup.find("input", {"name": "st"})
            csrf = st_input.get("value", "") if st_input else ""
            
            # Hidden 필드들
            hidden = {}
            for inp in soup.find_all("input", {"type": "hidden"}):
                name = inp.get("name")
                value = inp.get("value", "")
                if name:
                    hidden[name] = value
            
            return {"csrf": csrf, "hidden": hidden}
            
        except Exception as e:
            logger.exception(f"로그인 폼 파싱 실패: {e}")
            return None
    
    def _bridge_www_session(self):
        """www 세션 연결"""
        try:
            self._get("https://www.inven.co.kr/", allow_redirects=True)
            self._get("https://www.inven.co.kr/board/diablo4/6025", allow_redirects=True)
        except Exception:
            pass
    
    def login(self, user_id: str, password: str) -> bool:
        """로그인 수행"""
        info = self._extract_login_form()
        if not info:
            return False
        
        # 로그인 데이터
        data = {
            "user_id": user_id,
            "password": self._encode_password(password),
            "kp": "0",
            "st": info["csrf"],
            "wsip": "",
            "surl": "https://www.inven.co.kr/"
        }
        
        headers = {
            "Host": "member.inven.co.kr",
            "User-Agent": self.session.headers["User-Agent"],
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://member.inven.co.kr",
            "Referer": "https://member.inven.co.kr/user/scorpio/mlogin",
        }
        
        try:
            r = self._post(
                "https://member.inven.co.kr/m/login/dispatch",
                data=data,
                headers=headers,
                allow_redirects=False
            )
        except Exception as e:
            logger.error(f"로그인 요청 실패: {e}")
            return False
        
        # 쿠키 확인
        cookies = {c.name: c.value for c in self.session.cookies}
        if r.status_code in (200, 302) and ("M_ID" in cookies and "M_SID" in cookies):
            self._bridge_www_session()
            logger.info(f"로그인 성공: {user_id}")
            return True
        
        logger.error("로그인 실패: 아이디/비밀번호 확인")
        return False
    
    # ==================== 글쓰기 ====================
    
    def _choose_category(self, soup, tokens: Dict[str, str]):
        """카테고리 자동 선택 (기타 우선)"""
        select = soup.select_one('select[name="CATEGORY"], select[name="category"]')
        if not select:
            return
        
        valid = []
        for option in select.find_all("option"):
            val = (option.get("value") or "").strip()
            txt = (option.text or "").strip()
            
            if not val:
                continue
            if "선택" in txt:
                continue
            if option.has_attr("disabled"):
                continue
            
            valid.append((txt, val))
        
        if not valid:
            return
        
        # 1순위: '기타' 포함 옵션
        choice = None
        for txt, val in reversed(valid):
            if "기타" in txt:
                choice = val
                break
        
        # 2순위: 마지막 옵션
        if choice is None:
            choice = valid[-1][1]
        
        tokens["CATEGORY"] = choice
        tokens["category"] = choice
    
    def _get_write_tokens(self, write_url: str) -> Optional[Dict[str, str]]:
        """글쓰기 토큰 추출"""
        try:
            r = self._get(write_url)
            if r.status_code != 200:
                logger.error("글쓰기 페이지 연결 실패")
                return None
            
            soup = BeautifulSoup(r.text, "html.parser")
            tokens = {}
            
            # Hidden 필드들
            for inp in soup.find_all("input", type="hidden"):
                name = inp.get("name")
                if name:
                    tokens[name] = inp.get("value", "")
            
            # 카테고리 자동 선택
            self._choose_category(soup, tokens)
            
            tokens["HTML"] = "html"
            
            return tokens
            
        except Exception as e:
            logger.exception(f"토큰 획득 실패: {e}")
            return None
    
    @staticmethod
    def _tokens_from_url(url: str) -> Dict[str, str]:
        """URL에서 토큰 추출"""
        path = urlsplit(url).path.strip("/")
        parts = path.split("/")
        out = {}
        if len(parts) >= 4:
            out["slug"] = parts[1]
            out["come_idx"] = parts[2]
            out["idx"] = parts[3]
        return out
    
    def _is_html_content(self, content: str) -> bool:
        """HTML 태그 포함 여부 확인"""
        html_tags = ['<p>', '<br>', '<div>', '<span>', '<b>', '<i>', '<u>', 
                     '<strong>', '<em>', '<a>', '<img>', '<h1>', '<h2>', '<h3>',
                     '<ul>', '<ol>', '<li>', '<table>', '<tr>', '<td>']
        content_lower = content.lower()
        return any(tag in content_lower for tag in html_tags)
    
    def write_post(self, board_name: str, title: str, content: str) -> Optional[Dict[str, str]]:
        """글 작성"""
        come_idx = BOARD_MAP.get(board_name, BOARD_MAP.get("거래게시판", "6383"))
        slug = BOARD_SLUG
        write_url = f"https://www.inven.co.kr/board/powerbbs.php?query=write&come_idx={come_idx}"
        
        # 토큰 획득
        tokens = self._get_write_tokens(write_url)
        if not tokens:
            return None
        
        # HTML 여부 자동 감지
        is_html = self._is_html_content(content)
        
        if is_html:
            # HTML 모드: 그대로 사용
            final_content = content
            editor_mode = "html"
        else:
            # 텍스트 모드: 그대로 전송 (인벤이 알아서 줄바꿈 처리)
            final_content = content
            editor_mode = "text"
        
        # POST 데이터
        data = {
            "SUBJECT": title,
            "subject": title,
            "memo": final_content,
            "CONTENT": final_content,
            "CONTENT2": final_content,
            "HTML": final_content,
            "content": final_content,
            "query": "write",
            "come_idx": come_idx,
            "editor_mode": editor_mode,
            "mode": editor_mode,
        }
        
        # HTML 모드일 때만 html 파라미터 추가
        if is_html:
            data["html"] = "html"
        
        data.update(tokens)
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": write_url,
            "User-Agent": self.session.headers["User-Agent"],
        }
        
        try:
            r = self._post(
                "https://www.inven.co.kr/board/bbs/include/write_data.php",
                data=data,
                headers=headers,
                allow_redirects=True
            )
        except Exception as e:
            logger.error(f"글쓰기 요청 실패: {e}")
            return None
        
        if r.status_code not in (200, 302):
            logger.error("글쓰기 실패")
            return None
        
        # 🔥 방법 1: 리다이렉트 URL에서 추출 시도
        final_url = r.url or ""
        t = self._tokens_from_url(final_url)
        
        # 제대로 된 URL인지 확인
        if all(k in t for k in ("idx", "come_idx", "slug")) and t["idx"] not in ["write_data.php", "powerbbs.php"]:
            return {
                "idx": t["idx"],
                "come_idx": t["come_idx"],
                "slug": t["slug"],
                "title": title,
                "url": final_url
            }
        
        # 🔥 방법 2: HTML에서 글 번호 찾기
        try:
            soup = BeautifulSoup(r.text, "html.parser")
            
            # 여러 패턴으로 idx 찾기
            # 1. 링크에서 찾기
            for link in soup.find_all('a', href=True):
                href = link['href']
                if f'/{slug}/{come_idx}/' in href:
                    parts = href.split('/')
                    if len(parts) >= 4:
                        idx = parts[-1].split('?')[0]  # 쿼리스트링 제거
                        if idx.isdigit():
                            return {
                                "idx": idx,
                                "come_idx": come_idx,
                                "slug": slug,
                                "title": title,
                                "url": f"https://www.inven.co.kr/board/{slug}/{come_idx}/{idx}"
                            }
            
            # 2. meta 태그에서 찾기
            meta_url = soup.find('meta', property='og:url')
            if meta_url and meta_url.get('content'):
                meta_t = self._tokens_from_url(meta_url['content'])
                if all(k in meta_t for k in ("idx", "come_idx", "slug")) and meta_t["idx"].isdigit():
                    return {
                        "idx": meta_t["idx"],
                        "come_idx": meta_t["come_idx"],
                        "slug": meta_t["slug"],
                        "title": title,
                        "url": meta_url['content']
                    }
        except Exception as e:
            logger.warning(f"HTML 파싱 실패: {e}")
        
        # 🔥 방법 3: 최근 내 글 목록에서 찾기 (가장 확실!)
        try:
            time.sleep(0.5)  # 글이 등록될 시간 대기
            my_posts = self.list_my_posts(board_name, pages=1)
            
            # 방금 쓴 글 찾기 (제목이 같은 첫 번째 글)
            for post in my_posts:
                # 실제 글 확인 (제목 매칭)
                try:
                    post_url = f"https://www.inven.co.kr/board/{post['slug']}/{post['come_idx']}/{post['idx']}"
                    check_r = self._get(post_url)
                    if title in check_r.text:
                        return {
                            "idx": post["idx"],
                            "come_idx": post["come_idx"],
                            "slug": post["slug"],
                            "title": title,
                            "url": post_url
                        }
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"최근 글 목록 조회 실패: {e}")
        
        # 모든 방법 실패
        logger.error("글 ID 추출 실패 - 모든 방법 시도했으나 실패")
        return None
    
    # ==================== 글삭제 ====================
    
    def _verify_deleted(self, slug: str, come_idx: str, idx: str) -> bool:
        """삭제 확인"""
        try:
            post_url = f"https://www.inven.co.kr/board/{slug}/{come_idx}/{idx}"
            r = self._get(post_url, allow_redirects=True)
            
            # 리다이렉트 됨
            if r.url and r.url != post_url:
                return True
            
            # 삭제 메시지 확인
            text = r.text or ""
            keywords = ["삭제된", "존재하지 않는", "없는 게시물", "잘못된 접근", "글이 없습니다"]
            if any(kw in text for kw in keywords):
                return True
            
            return False
            
        except Exception:
            return True
    
    def _delete_via_multi(self, slug: str, come_idx: str, idx: str) -> bool:
        """멀티 삭제 방식"""
        try:
            view_url = f"https://www.inven.co.kr/board/powerbbs.php?query=view&name={slug}&come_idx={come_idx}&idx={idx}&my=post"
            self._get(view_url, allow_redirects=True)
        except Exception:
            pass
        
        data = {
            "come_idx": come_idx,
            "p": "1",
            "l": idx,
            "my": "post",
            "name": slug
        }
        
        headers = {
            "Origin": "https://www.inven.co.kr",
            "Referer": view_url,
            "User-Agent": self.session.headers.get("User-Agent", ""),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        try:
            self._post(
                "https://www.inven.co.kr/board/bbs/include/multi_delete.php",
                data=data,
                headers=headers,
                allow_redirects=True
            )
        except Exception:
            pass
        
        return self._verify_deleted(slug, come_idx, idx)
    
    def delete_post(self, slug: str, come_idx: str, idx: str) -> bool:
        """게시글 삭제"""
        try:
            if self._delete_via_multi(slug, come_idx, idx):
                logger.info(f"게시글 삭제 성공: {idx}")
                return True
        except Exception as e:
            logger.error(f"게시글 삭제 실패: {e}")
        
        return False
    
    # ==================== 내 글 목록 ====================
    
    def list_my_posts(self, board_name: str, pages: int = 2) -> List[Dict[str, str]]:
        """내 글 목록 조회"""
        come_idx = BOARD_MAP.get(board_name, BOARD_MAP.get("거래게시판", "6383"))
        slug = BOARD_SLUG
        found = []
        seen = set()
        
        for page in range(1, pages + 1):
            try:
                url = f"https://www.inven.co.kr/board/{slug}/{come_idx}?my=post"
                if page > 1:
                    url += f"&p={page}"
                
                r = self._get(url)
                soup = BeautifulSoup(r.text, "html.parser")
                
                for a in soup.select('a.subject-link'):
                    href = (a.get("href") or "").strip()
                    if not href:
                        continue
                    
                    parts = urlsplit(href).path.strip("/").split("/")
                    if len(parts) >= 4 and parts[1] == slug and parts[2] == come_idx:
                        idx = parts[3]
                        if idx and idx not in seen:
                            seen.add(idx)
                            found.append({
                                "slug": slug,
                                "come_idx": come_idx,
                                "idx": idx
                            })
            except Exception:
                continue
        
        return found
    
    def delete_post_by_id(self, slug: str, come_idx: str, idx: str) -> bool:
        """글 ID로 바로 삭제 (빠른 삭제 - 자동 삭제용)"""
        try:
            if self._delete_via_multi(slug, come_idx, idx):
                logger.info(f"자동 삭제 성공: {idx}")
                return True
        except Exception as e:
            logger.error(f"자동 삭제 실패: {e}")
        
        return False
    
    def delete_oldest_post(self, board_name: str) -> bool:
        """가장 오래된 내 글 1개 삭제 (수동 삭제 버튼용)"""
        try:
            # 첫 페이지만 조회 (최신글이 위에)
            items = self.list_my_posts(board_name, pages=1)
            
            if not items:
                return False
            
            # 맨 마지막 글이 가장 오래된 글
            oldest = items[-1]
            
            # 삭제
            success = self.delete_post(oldest["slug"], oldest["come_idx"], oldest["idx"])
            
            if success:
                logger.info(f"수동 삭제 완료: {oldest['idx']}")
            
            return success
            
        except Exception as e:
            logger.error(f"수동 삭제 실패: {e}")
            return False
    
    def delete_all_my_posts(
        self,
        board_name: str,
        on_progress: Optional[Callable[[int, int, int], None]] = None
    ) -> Tuple[int, int]:
        """내 글 전체 삭제"""
        items = self.list_my_posts(board_name, pages=2)
        total = len(items)
        success = 0
        
        for i, item in enumerate(items, start=1):
            try:
                ok = self.delete_post(item["slug"], item["come_idx"], item["idx"])
            except Exception:
                ok = False
            
            if ok:
                success += 1
            
            if callable(on_progress):
                try:
                    on_progress(i, total, success)
                except Exception:
                    pass
            
            time.sleep(0.2)  # 요청 간격
        
        return total, success
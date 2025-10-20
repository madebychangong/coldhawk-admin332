# 🚀 ColdHawk_test_1.3.1 배포 가이드

## 📦 배포 방법 3가지

### 🥇 방법 1: 자동 설치 프로그램 (권장)

**장점:**
- ✅ 사용자가 설치만 하면 바로 사용 가능
- ✅ 환경변수 자동 설정
- ✅ 시작 메뉴/바탕화면 바로가기 생성
- ✅ 제거 프로그램 포함

**사용법:**
1. NSIS 설치: https://nsis.sourceforge.io/Download
2. `installer.nsi` 파일을 NSIS로 컴파일
3. 생성된 `ColdHawk_test_1.3.1_Installer.exe` 배포

**사용자 경험:**
- 설치 프로그램 실행 → 다음 클릭 → 완료
- 바탕화면에서 바로 실행 가능

---

### 🥈 방법 2: 포터블 버전

**장점:**
- ✅ 설치 없이 바로 실행 가능
- ✅ USB에 담아서 어디서든 사용
- ✅ 시스템에 영향 없음

**생성법:**
```bash
python create_portable.py
```

**배포 파일:**
- `ColdHawk_test_1.3.1_Portable.zip` (압축 해제 후 사용)

**사용자 경험:**
- 압축 해제 → `ColdHawk_test_1.3.1_실행.bat` 더블클릭

---

### 🥉 방법 3: 수동 배포

**파일 구성:**
```
ColdHawk_test_1.3.1_배포/
├── ColdHawk_test_1.3.1.exe
├── setup_environment.bat
├── 사용법.txt
└── resources/
```

**사용자 가이드:**
1. `setup_environment.bat` 실행
2. 새로운 명령 프롬프트 열기
3. `ColdHawk_test_1.3.1.exe` 실행

---

## 🎯 추천 배포 전략

### 🏢 기업/조직용
**방법 1 (자동 설치)** 권장
- 관리자가 일괄 설치 가능
- 사용자는 설치만 하면 됨
- 표준화된 배포 방식

### 👥 개인 사용자용
**방법 2 (포터블)** 권장
- 설치 없이 바로 사용
- USB로 휴대 가능
- 시스템 변경 최소화

### 🔧 개발자용
**방법 3 (수동)** 권장
- 환경변수 설정 방법 학습
- 문제 해결 능력 향상
- 유연한 설정 가능

---

## 📋 배포 체크리스트

### 공통 체크리스트
- [ ] exe 파일 정상 빌드 확인
- [ ] pyrebase 라이브러리 포함 확인
- [ ] 환경변수 설정 스크립트 포함
- [ ] 사용자 가이드 작성
- [ ] 테스트 환경에서 검증

### 방법 1 (자동 설치) 체크리스트
- [ ] NSIS 스크립트 작성 완료
- [ ] 설치 프로그램 테스트
- [ ] 제거 프로그램 동작 확인
- [ ] 환경변수 자동 설정 확인

### 방법 2 (포터블) 체크리스트
- [ ] 포터블 패키지 생성 스크립트 실행
- [ ] ZIP 파일 생성 확인
- [ ] 압축 해제 후 실행 테스트
- [ ] 환경변수 설정 스크립트 동작 확인

---

## 🛠️ 기술적 세부사항

### 환경변수 설정
```cmd
FIREBASE_API_KEY=AIzaSyAo2-_VoDQsNjRCimzns5V6boc6-ajP8zs
FIREBASE_AUTH_DOMAIN=coldhawk-id.firebaseapp.com
FIREBASE_DATABASE_URL=https://coldhawk-id.firebaseio.com
FIREBASE_STORAGE_BUCKET=coldhawk-id.appspot.com
```

### 필요한 파일
- `dist/ColdHawk_test_1.3.1.exe` (메인 프로그램)
- `resources/` (리소스 파일)
- `ui/styles/` (스타일 파일)

### 의존성
- ✅ pyrebase4 (exe에 포함됨)
- ✅ PySide6 (exe에 포함됨)
- ✅ 기타 모든 라이브러리 (exe에 포함됨)

---

## 📞 사용자 지원

### 자주 묻는 질문
**Q: 로그인 오류가 나요**
A: 환경변수 설정 스크립트를 실행하세요

**Q: 프로그램이 실행되지 않아요**
A: 관리자 권한으로 실행해보세요

**Q: 환경변수가 적용되지 않아요**
A: 컴퓨터를 재시작하거나 새로운 명령 프롬프트를 여세요

### 지원 채널
- 이메일: support@coldhawk.com
- 문서: DEPLOYMENT_GUIDE.md
- 문제 해결: QUICK_SETUP.md

















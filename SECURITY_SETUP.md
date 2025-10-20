# 🔒 보안 설정 가이드

## 환경변수 설정 방법

### 🔑 필수 설정 (프로덕션)
```bash
# Firebase 설정 (반드시 설정 필요)
FIREBASE_API_KEY="your_api_key_here"
FIREBASE_AUTH_DOMAIN="coldhawk-id.firebaseapp.com"
FIREBASE_DATABASE_URL="https://coldhawk-id.firebaseio.com"
FIREBASE_STORAGE_BUCKET="coldhawk-id.appspot.com"
```

### 🚫 개발 모드 자동 통과 제거됨
```bash
# ⚠️ 더 이상 개발 모드 자동 통과 불가
# 모든 환경에서 반드시 Firebase 로그인 필요

# 프로덕션 모드 설정 (선택사항)
APP_ENV=production
```

### Windows 설정 방법
```cmd
# 시스템 환경변수 설정 (영구)
setx FIREBASE_API_KEY "your_api_key_here"
setx FIREBASE_AUTH_DOMAIN "coldhawk-id.firebaseapp.com"
setx FIREBASE_DATABASE_URL "https://coldhawk-id.firebaseio.com"
setx FIREBASE_STORAGE_BUCKET "coldhawk-id.appspot.com"

# 현재 세션에서만 (임시)
set FIREBASE_API_KEY=your_api_key_here
```

### Linux/Mac 설정 방법
```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
export FIREBASE_API_KEY="your_api_key_here"
export FIREBASE_AUTH_DOMAIN="coldhawk-id.firebaseapp.com"
export FIREBASE_DATABASE_URL="https://coldhawk-id.firebaseio.com"
export FIREBASE_STORAGE_BUCKET="coldhawk-id.appspot.com"

# 현재 세션에서만 (임시)
export FIREBASE_API_KEY=your_api_key_here
```

## 보안 개선 사항

✅ **Firebase API 키 환경변수 이동**
- config.json에서 제거
- 환경변수로 안전하게 관리

✅ **로그 보안 강화**
- 민감 정보 마스킹
- API 키는 마지막 4자리만 표시

✅ **비밀번호 암호화**
- 메모리에서 암호화 저장
- 설정 파일에 저장하지 않음

✅ **디버그 코드 정리**
- 모든 print() 문 제거
- 로거로 통일

✅ **빌드 보안 강화**
- config.json 제거
- 민감 정보 exe에 포함되지 않음

## 🔍 로그인 동작 방식

### ✅ 정상 로그인 (모든 환경)
1. ✅ 환경변수에 `FIREBASE_API_KEY` 설정됨
2. ✅ Firebase 인증으로 실제 로그인 검증
3. ✅ 유효한 이메일/비밀번호만 통과
4. ✅ **개발 모드든 프로덕션이든 동일한 보안 수준**

### ❌ 로그인 실패 시나리오
- ❌ Firebase API 키 미설정 → "Firebase API 키가 설정되지 않았습니다"
- ❌ pyrebase 미설치 → "로그인 라이브러리(pyrebase)가 설치되지 않았습니다"
- ❌ 잘못된 인증 정보 → "이메일 또는 비밀번호를 확인하세요"
- ❌ Firebase 서버 오류 → "로그인 서비스에 문제가 있습니다"

### 🚫 제거된 기능
- ❌ 개발 모드 자동 통과 (완전 제거)
- ❌ `COLDHAWK_DEV_MODE` 환경변수 (더 이상 사용하지 않음)
- ❌ 로그인 우회 기능 (보안 강화)

## 배포 전 체크리스트

- [ ] 환경변수 `FIREBASE_API_KEY` 설정 완료
- [ ] `config.json`에서 API 키 제거 확인
- [ ] pyrebase 라이브러리 설치 확인
- [ ] exe 빌드 테스트
- [ ] 로그인 기능 정상 동작 확인 (실제 Firebase 계정으로)
- [ ] 로그에서 민감 정보 마스킹 확인
- [ ] 비밀번호 암호화 동작 확인

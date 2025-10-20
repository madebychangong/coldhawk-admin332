# 🚀 ColdHawk_test_1.3.1 빠른 보안 설정 가이드

## ⚡ 1분 설정 (자동)

### Windows 사용자
```cmd
# 1. 배치 파일 실행
setup_environment.bat

# 2. 새로운 명령 프롬프트 열기
# 3. ColdHawk_test_1.3.1 실행
```

### Linux/Mac 사용자
```bash
# 1. 스크립트 실행 권한 부여
chmod +x setup_environment.sh

# 2. 스크립트 실행
./setup_environment.sh

# 3. 셸 재시작 또는 source 명령 실행
source ~/.bashrc  # 또는 ~/.zshrc
```

### Python 사용자 (모든 OS)
```bash
# 1. Python 스크립트 실행
python setup_security.py

# 2. 새로운 터미널 열기
# 3. ColdHawk_test_1.3.1 실행
```

## 🔧 수동 설정 (고급 사용자)

### Windows
```cmd
setx FIREBASE_API_KEY "AIzaSyAo2-_VoDQsNjRCimzns5V6boc6-ajP8zs"
setx FIREBASE_AUTH_DOMAIN "coldhawk-id.firebaseapp.com"
setx FIREBASE_DATABASE_URL "https://coldhawk-id.firebaseio.com"
setx FIREBASE_STORAGE_BUCKET "coldhawk-id.appspot.com"
```

### Linux/Mac
```bash
echo 'export FIREBASE_API_KEY="AIzaSyAo2-_VoDQsNjRCimzns5V6boc6-ajP8zs"' >> ~/.bashrc
echo 'export FIREBASE_AUTH_DOMAIN="coldhawk-id.firebaseapp.com"' >> ~/.bashrc
echo 'export FIREBASE_DATABASE_URL="https://coldhawk-id.firebaseio.com"' >> ~/.bashrc
echo 'export FIREBASE_STORAGE_BUCKET="coldhawk-id.appspot.com"' >> ~/.bashrc
```

## ✅ 설정 완료 확인

환경변수가 올바르게 설정되었는지 확인:

### Windows
```cmd
echo %FIREBASE_API_KEY%
```

### Linux/Mac
```bash
echo $FIREBASE_API_KEY
```

## 🔒 보안 개선 사항

- ✅ **config.json에서 API 키 제거됨**
- ✅ **환경변수로 안전하게 관리**
- ✅ **exe 빌드 시 민감 정보 포함되지 않음**
- ✅ **자동 설정 스크립트 제공**

## 🚨 문제 해결

### 환경변수가 적용되지 않는 경우
1. **새로운 터미널/명령 프롬프트 열기**
2. **컴퓨터 재시작**
3. **관리자 권한으로 스크립트 실행**

### 로그인 실패 시
1. **pyrebase4 설치**: `pip install pyrebase4`
2. **환경변수 확인**: 위의 확인 방법 사용
3. **Firebase 계정 확인**: 이메일/비밀번호 정확한지 확인

## 📞 지원

문제가 있으면 다음을 확인하세요:
- [ ] 환경변수 설정 완료
- [ ] pyrebase4 라이브러리 설치
- [ ] 새로운 터미널에서 실행
- [ ] Firebase 계정 정보 정확성


















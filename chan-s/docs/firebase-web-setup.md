# Firebase 웹 설정 가이드

## 1. Firebase 콘솔에서 웹 앱 추가

1. [Firebase 콘솔](https://console.firebase.google.com/) 접속
2. 기존 프로젝트 선택 (현재 앱에서 사용하는 것과 동일한 프로젝트)
3. 프로젝트 설정 (⚙️) → 일반 탭
4. "내 앱" 섹션에서 "웹" 아이콘 클릭
5. 앱 닉네임 입력: "찬공스튜디오-웹"
6. "Firebase Hosting 설정" 체크하지 말고 "앱 등록" 클릭

## 2. Firebase 설정 정보 복사

앱 등록 후 나타나는 설정 정보를 복사합니다:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "your-project-id.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project-id.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdefghijklmnop"
};
```

## 3. signup.html 파일 수정

위에서 복사한 설정 정보로 `signup.html` 파일의 Firebase 설정 부분을 업데이트하세요:

```javascript
// Firebase 설정 (실제 프로젝트 설정으로 변경 필요)
const firebaseConfig = {
    apiKey: "여기에_실제_apiKey_입력",
    authDomain: "여기에_실제_authDomain_입력",
    projectId: "여기에_실제_projectId_입력",
    storageBucket: "여기에_실제_storageBucket_입력",
    messagingSenderId: "여기에_실제_messagingSenderId_입력",
    appId: "여기에_실제_appId_입력"
};
```

## 4. Firebase Authentication 설정 확인

1. Firebase 콘솔 → Authentication → Sign-in method
2. "이메일/비밀번호" 활성화 확인
3. 필요시 "이메일 링크(비밀번호 없음)" 비활성화

## 5. 도메인 승인 설정

1. Firebase 콘솔 → Authentication → Settings → Authorized domains
2. 다음 도메인 추가:
   - `xn--ob0by50d.store`
   - `madebychangong.github.io` (GitHub Pages용)

## 6. 배포 준비

GitHub Pages에 배포할 때는 HTTPS가 자동으로 적용되므로 별도 설정 불필요합니다.

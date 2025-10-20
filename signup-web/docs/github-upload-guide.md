# GitHub 저장소 업로드 가이드

## 1. GitHub 저장소 클론

```bash
git clone https://github.com/madebychangong/chan-s.git
cd chan-s
```

## 2. 파일 추가

생성된 파일들을 저장소에 추가:

```bash
# signup.html 파일을 저장소 루트에 복사
cp signup.html /path/to/chan-s/

# 또는 직접 GitHub 웹에서 업로드
```

## 3. 파일 업로드 방법

### 방법 1: GitHub 웹 인터페이스 사용 (추천)

1. [GitHub 저장소](https://github.com/madebychangong/chan-s) 접속
2. "Add file" → "Upload files" 클릭
3. `signup.html` 파일 드래그 앤 드롭
4. "Commit changes" 클릭

### 방법 2: Git 명령어 사용

```bash
cd chan-s
git add signup.html
git commit -m "Add signup page"
git push origin main
```

## 4. GitHub Pages 설정 확인

1. GitHub 저장소 → Settings
2. Pages 섹션 확인
3. Source: "Deploy from a branch" 선택
4. Branch: "main" 선택
5. Save 클릭

## 5. 접속 URL

회원가입 페이지는 다음 URL에서 접속 가능:
- `https://xn--ob0by50d.store/signup.html`

## 6. Firebase 설정 완료 후

1. Firebase 콘솔에서 웹 앱 설정 완료
2. `signup.html` 파일의 Firebase 설정 정보 업데이트
3. 다시 GitHub에 업로드

## 7. 테스트

1. 프로그램에서 회원가입 버튼 클릭
2. 웹페이지가 열리는지 확인
3. 실제 회원가입 테스트 진행

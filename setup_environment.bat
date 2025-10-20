@echo off
echo ========================================
echo Coldhawk 환경변수 설정 스크립트
echo ========================================
echo.

REM Firebase API 키 설정
set "FIREBASE_API_KEY=AIzaSyAo2-_VoDQsNjRCimzns5V6boc6-ajP8zs"
set "FIREBASE_AUTH_DOMAIN=coldhawk-id.firebaseapp.com"
set "FIREBASE_DATABASE_URL=https://coldhawk-id.firebaseio.com"
set "FIREBASE_STORAGE_BUCKET=coldhawk-id.appspot.com"

echo Firebase 환경변수를 시스템에 설정합니다...
echo.

REM 시스템 환경변수로 설정 (영구적)
setx FIREBASE_API_KEY "%FIREBASE_API_KEY%" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ FIREBASE_API_KEY 설정 완료
) else (
    echo ❌ FIREBASE_API_KEY 설정 실패
)

setx FIREBASE_AUTH_DOMAIN "%FIREBASE_AUTH_DOMAIN%" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ FIREBASE_AUTH_DOMAIN 설정 완료
) else (
    echo ❌ FIREBASE_AUTH_DOMAIN 설정 실패
)

setx FIREBASE_DATABASE_URL "%FIREBASE_DATABASE_URL%" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ FIREBASE_DATABASE_URL 설정 완료
) else (
    echo ❌ FIREBASE_DATABASE_URL 설정 실패
)

setx FIREBASE_STORAGE_BUCKET "%FIREBASE_STORAGE_BUCKET%" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ FIREBASE_STORAGE_BUCKET 설정 완료
) else (
    echo ❌ FIREBASE_STORAGE_BUCKET 설정 실패
)

echo.
echo ========================================
echo 설정 완료!
echo ========================================
echo.
echo ⚠️  새로운 명령 프롬프트를 열어야 환경변수가 적용됩니다.
echo ⚠️  또는 컴퓨터를 재시작하세요.
echo.
echo 이제 Coldhawk을 실행하면 config.json 없이도 로그인할 수 있습니다.
echo.
pause


















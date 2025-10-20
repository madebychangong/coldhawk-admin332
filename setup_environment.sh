#!/bin/bash

echo "========================================"
echo "Coldhawk 환경변수 설정 스크립트"
echo "========================================"
echo

# Firebase API 키 설정
export FIREBASE_API_KEY="AIzaSyAo2-_VoDQsNjRCimzns5V6boc6-ajP8zs"
export FIREBASE_AUTH_DOMAIN="coldhawk-id.firebaseapp.com"
export FIREBASE_DATABASE_URL="https://coldhawk-id.firebaseio.com"
export FIREBASE_STORAGE_BUCKET="coldhawk-id.appspot.com"

echo "Firebase 환경변수를 설정 파일에 추가합니다..."
echo

# 현재 셸 확인
SHELL_CONFIG=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    SHELL_CONFIG="$HOME/.profile"
fi

echo "셸 설정 파일: $SHELL_CONFIG"
echo

# 환경변수 추가
echo "" >> "$SHELL_CONFIG"
echo "# Coldhawk Firebase 설정" >> "$SHELL_CONFIG"
echo "export FIREBASE_API_KEY=\"$FIREBASE_API_KEY\"" >> "$SHELL_CONFIG"
echo "export FIREBASE_AUTH_DOMAIN=\"$FIREBASE_AUTH_DOMAIN\"" >> "$SHELL_CONFIG"
echo "export FIREBASE_DATABASE_URL=\"$FIREBASE_DATABASE_URL\"" >> "$SHELL_CONFIG"
echo "export FIREBASE_STORAGE_BUCKET=\"$FIREBASE_STORAGE_BUCKET\"" >> "$SHELL_CONFIG"

echo "✅ 환경변수 설정 완료!"
echo
echo "========================================"
echo "설정 완료!"
echo "========================================"
echo
echo "⚠️  새로운 터미널을 열거나 다음 명령을 실행하세요:"
echo "   source $SHELL_CONFIG"
echo
echo "이제 Coldhawk을 실행하면 config.json 없이도 로그인할 수 있습니다."
echo


















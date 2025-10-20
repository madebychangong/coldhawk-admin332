; Coldhawk 설치 프로그램 스크립트
!define APP_NAME "ColdHawk_test_1.4.0"
!define APP_VERSION "1.0"
!define APP_PUBLISHER "Coldhawk Team"
!define APP_EXE "ColdHawk_test_1.4.0.exe"
!define APP_ICON "resources\icons\app_icon.ico"

; 설치 프로그램 정보
Name "${APP_NAME}"
OutFile "ColdHawk_test_1.3.1_Installer.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"
InstallDirRegKey HKLM "Software\${APP_NAME}" "Install_Dir"
RequestExecutionLevel admin

; UI 설정
!include "MUI2.nsh"
!define MUI_ICON "${APP_ICON}"
!define MUI_UNICON "${APP_ICON}"

; 설치 페이지
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; 제거 페이지
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; 언어 설정
!insertmacro MUI_LANGUAGE "Korean"

; 설치 섹션
Section "Main Application" SecMain
    SetOutPath "$INSTDIR"
    
    ; 파일 복사
    File "dist\${APP_EXE}"
    File "resources\*.*"
    File "ui\styles\*.*"
    
    ; 시작 메뉴 바로가기
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\제거.lnk" "$INSTDIR\Uninstall.exe"
    
    ; 바탕화면 바로가기
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
    
    ; 환경변수 자동 설정
    WriteRegStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "FIREBASE_API_KEY" "AIzaSyAo2-_VoDQsNjRCimzns5V6boc6-ajP8zs"
    WriteRegStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "FIREBASE_AUTH_DOMAIN" "coldhawk-id.firebaseapp.com"
    WriteRegStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "FIREBASE_DATABASE_URL" "https://coldhawk-id.firebaseio.com"
    WriteRegStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "FIREBASE_STORAGE_BUCKET" "coldhawk-id.appspot.com"
    
    ; 환경변수 새로고침
    SendMessage ${HWND_BROADCAST} ${WM_WININICHANGE} 0 "STR:Environment" /TIMEOUT=5000
    
    ; 레지스트리 정보 저장
    WriteRegStr HKLM "Software\${APP_NAME}" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
    
    ; 제거 프로그램 생성
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    MessageBox MB_OK "✅ ${APP_NAME} 설치가 완료되었습니다!$\n$\n🔑 Firebase 환경변수가 자동으로 설정되었습니다.$\n🚀 바탕화면에서 바로 실행하실 수 있습니다."
SectionEnd

; 제거 섹션
Section "Uninstall"
    ; 파일 삭제
    Delete "$INSTDIR\${APP_EXE}"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir /r "$INSTDIR"
    
    ; 바로가기 삭제
    Delete "$SMPROGRAMS\${APP_NAME}\*.*"
    RMDir "$SMPROGRAMS\${APP_NAME}"
    Delete "$DESKTOP\${APP_NAME}.lnk"
    
    ; 레지스트리 정리
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    DeleteRegKey HKLM "Software\${APP_NAME}"
    
    ; 환경변수 제거
    DeleteRegValue HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "FIREBASE_API_KEY"
    DeleteRegValue HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "FIREBASE_AUTH_DOMAIN"
    DeleteRegValue HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "FIREBASE_DATABASE_URL"
    DeleteRegValue HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "FIREBASE_STORAGE_BUCKET"
    
    MessageBox MB_OK "✅ ${APP_NAME}이 완전히 제거되었습니다."
SectionEnd

















#!/usr/bin/env python3
"""
프로그램 이름 변경 도구
ColdHawk 프로그램의 이름을 동적으로 변경합니다.
"""

import re
import shutil
from pathlib import Path
import os
from utils.constants import APP_NAME, APP_SLUG

class AppRenamer:
    def __init__(self, old_name, new_name):
        self.old_name = old_name
        self.new_name = new_name
        self.old_slug = APP_SLUG
        self.new_slug = self.new_name.lower().replace(' ', '_').replace('-', '_')
        
    def update_spec_file(self):
        """spec 파일 이름 변경 및 내용 수정"""
        old_spec_file = Path(f"{self.old_name}.spec")
        new_spec_file = Path(f"{self.new_name}.spec")
        
        if old_spec_file.exists():
            # 파일 이름 변경
            old_spec_file.rename(new_spec_file)
            
            # 파일 내용 수정
            with open(new_spec_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # name 파라미터 수정
            content = re.sub(r"name='[^']*'", f"name='{self.new_name}'", content)
            
            with open(new_spec_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"spec 파일 업데이트: {old_spec_file} → {new_spec_file}")
        else:
            print(f"spec 파일을 찾을 수 없습니다: {old_spec_file}")
    
    def update_installer_nsi(self):
        """installer.nsi 파일 업데이트"""
        nsi_file = Path("installer.nsi")
        if nsi_file.exists():
            with open(nsi_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # APP_NAME과 APP_EXE 수정
            content = re.sub(r'!define APP_NAME "[^"]*"', f'!define APP_NAME "{self.new_name}"', content)
            content = re.sub(r'!define APP_EXE "[^"]*"', f'!define APP_EXE "{self.new_name}.exe"', content)
            
            with open(nsi_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"installer.nsi 업데이트 완료")
        else:
            print(f"installer.nsi 파일을 찾을 수 없습니다")
    
    def update_ui_files(self):
        """UI 파일들의 하드코딩된 이름 업데이트"""
        ui_files = [
            "ui/windows/login_window.py",
            "ui/windows/main_window.py",
            "ui/styles/apple_light.qss",
            "ui/styles/premium_modern.qss"
        ]
        
        for ui_file in ui_files:
            if Path(ui_file).exists():
                with open(ui_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 하드코딩된 이름들 교체
                content = content.replace(self.old_name, self.new_name)
                
                with open(ui_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"UI 파일 업데이트: {ui_file}")
            else:
                print(f"UI 파일을 찾을 수 없습니다: {ui_file}")
    
    def update_portable_ui_files(self):
        """포터블 UI 파일들 업데이트 (비활성화)"""
        # 포터블 자동 생성 비활성화
        print("포터블 파일 업데이트는 비활성화됨")
    
    def update_constants_file(self):
        """utils/constants.py 파일의 APP_NAME 업데이트"""
        constants_file = Path("utils/constants.py")
        if constants_file.exists():
            with open(constants_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # APP_NAME 업데이트
            content = re.sub(
                r'APP_NAME = "[^"]*"', 
                f'APP_NAME = "{self.new_name}"', 
                content
            )
            
            with open(constants_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"constants.py 업데이트: APP_NAME = {self.new_name}")
        else:
            print("utils/constants.py 파일을 찾을 수 없습니다")
    
    def rename_all(self):
        """모든 파일 이름 변경 및 내용 업데이트"""
        print(f"프로그램 이름 변경: {self.old_name} → {self.new_name}")
        print("=" * 50)
        
        # 1. spec 파일 업데이트
        self.update_spec_file()
        
        # 2. installer.nsi 업데이트
        self.update_installer_nsi()
        
        # 3. UI 파일들 업데이트
        self.update_ui_files()
        
        # 4. 포터블 UI 파일들 업데이트 (비활성화)
        self.update_portable_ui_files()
        
        # 5. constants.py 업데이트
        self.update_constants_file()
        
        print("=" * 50)
        print(f"모든 파일 업데이트 완료!")
        print(f"빌드 명령어: pyinstaller {self.new_name}.spec")
        print("=" * 50)

def main():
    """메인 함수"""
    print("프로그램 이름 변경 도구")
    print("=" * 50)
    
    try:
        from utils.constants import APP_NAME
        current_name = APP_NAME
    except ImportError:
        current_name = "Coldhawk"
    
    print(f"현재 프로그램 이름: {current_name}")
    
    # 자동으로 다음 버전으로 변경
    if "1.3.2" in current_name:
        new_name = current_name.replace("1.3.2", "1.3.3")
    elif "1.3.1" in current_name:
        new_name = current_name.replace("1.3.1", "1.3.2")
    elif "1.3.0" in current_name:
        new_name = current_name.replace("1.3.0", "1.3.1")
    else:
        # 수동 입력
        new_name = input("\n새로운 프로그램 이름을 입력하세요: ").strip()
        if not new_name:
            print("❌ 프로그램 이름을 입력해주세요.")
            return
    
    if new_name == current_name:
        print("❌ 현재 이름과 동일합니다.")
        return
    
    print(f"자동 변경: {current_name} → {new_name}")
    
    # 이름 변경 실행
    renamer = AppRenamer(current_name, new_name)
    renamer.rename_all()
    
    print(f"\n완료! 이제 빌드하세요: pyinstaller {new_name}.spec")
    input("\n아무 키나 누르면 종료됩니다...")

if __name__ == "__main__":
    main()
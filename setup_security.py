"""
ColdHawk_test_1.3.1 보안 설정 도우미
환경변수 자동 설정 및 config.json 보안 처리
"""
import os
import sys
import json
import shutil
from pathlib import Path

def setup_environment_variables():
    """환경변수 설정"""
    firebase_config = {
        "FIREBASE_API_KEY": "AIzaSyAo2-_VoDQsNjRCimzns5V6boc6-ajP8zs",
        "FIREBASE_AUTH_DOMAIN": "coldhawk-id.firebaseapp.com", 
        "FIREBASE_DATABASE_URL": "https://coldhawk-id.firebaseio.com",
        "FIREBASE_STORAGE_BUCKET": "coldhawk-id.appspot.com"
    }
    
    print("🔧 환경변수 설정 중...")
    
    # 현재 세션에 설정
    for key, value in firebase_config.items():
        os.environ[key] = value
        print(f"✅ {key} 설정 완료")
    
    # 시스템 환경변수로 영구 설정
    if sys.platform == "win32":
        print("\n🖥️  Windows 시스템 환경변수 설정...")
        try:
            import winreg
            
            # HKEY_CURRENT_USER\Environment에 설정
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                "Environment",
                0,
                winreg.KEY_SET_VALUE
            )
            
            for env_key, value in firebase_config.items():
                winreg.SetValueEx(key, env_key, 0, winreg.REG_SZ, value)
                print(f"✅ 시스템 {env_key} 설정 완료")
            
            winreg.CloseKey(key)
            print("✅ Windows 시스템 환경변수 설정 완료!")
            
        except ImportError:
            print("⚠️  winreg 모듈을 사용할 수 없습니다. 수동으로 설정해주세요.")
    else:
        print("\n🐧 Linux/Mac 환경변수 설정...")
        shell_configs = [
            os.path.expanduser("~/.bashrc"),
            os.path.expanduser("~/.zshrc"),
            os.path.expanduser("~/.profile")
        ]
        
        for config_file in shell_configs:
            if os.path.exists(config_file):
                print(f"📝 {config_file}에 환경변수 추가...")
                
                with open(config_file, "a") as f:
                    f.write("\n# ColdHawk_test_1.3.1 Firebase 설정\n")
                    for env_key, value in firebase_config.items():
                        f.write(f'export {env_key}="{value}"\n')
                
                print(f"✅ {config_file} 업데이트 완료")
                break

def secure_config_json():
    """config.json 보안 처리"""
    config_path = Path("config.json")
    
    if not config_path.exists():
        print("❌ config.json 파일을 찾을 수 없습니다.")
        return
    
    print("\n🔒 config.json 보안 처리 중...")
    
    # 백업 생성
    backup_path = config_path.with_suffix('.json.backup')
    shutil.copy2(config_path, backup_path)
    print(f"✅ 백업 생성: {backup_path}")
    
    # config.json에서 API 키 제거
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if 'firebase' in config and 'apiKey' in config['firebase']:
        # API 키 제거
        del config['firebase']['apiKey']
        config['firebase']['disabled'] = True
        config['firebase']['note'] = "API 키는 환경변수로 관리됩니다"
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("✅ config.json에서 API 키 제거 완료")
    else:
        print("ℹ️  config.json에 API 키가 없습니다.")

def verify_setup():
    """설정 검증"""
    print("\n🔍 설정 검증 중...")
    
    required_vars = [
        "FIREBASE_API_KEY",
        "FIREBASE_AUTH_DOMAIN", 
        "FIREBASE_DATABASE_URL",
        "FIREBASE_STORAGE_BUCKET"
    ]
    
    all_set = True
    for var in required_vars:
        if os.environ.get(var):
            print(f"✅ {var}: 설정됨")
        else:
            print(f"❌ {var}: 설정되지 않음")
            all_set = False
    
    if all_set:
        print("\n🎉 모든 환경변수가 올바르게 설정되었습니다!")
        print("이제 ColdHawk_test_1.3.1을 실행하면 안전하게 로그인할 수 있습니다.")
    else:
        print("\n⚠️  일부 환경변수가 설정되지 않았습니다.")
        print("새로운 터미널을 열거나 시스템을 재시작해주세요.")

def main():
    """메인 함수"""
    print("=" * 50)
    print("🔒 ColdHawk_test_1.3.1 보안 설정 도우미")
    print("=" * 50)
    
    try:
        # 1. 환경변수 설정
        setup_environment_variables()
        
        # 2. config.json 보안 처리
        secure_config_json()
        
        # 3. 설정 검증
        verify_setup()
        
        print("\n" + "=" * 50)
        print("✅ 보안 설정 완료!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())


















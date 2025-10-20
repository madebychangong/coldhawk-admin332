#!/usr/bin/env python3
"""
다른 PC 환경 시뮬레이션 테스트
환경변수를 제거하고 내장 설정으로 테스트
"""

import os
import sys

def test_other_pc_environment():
    """다른 PC 환경 시뮬레이션"""
    print("=== 다른 PC 환경 시뮬레이션 ===")
    print("=" * 50)
    
    # 환경변수 제거 (다른 PC 상태 시뮬레이션)
    env_vars_to_remove = [
        'FIREBASE_DATABASE_URL',
        'FIREBASE_API_KEY', 
        'FIREBASE_AUTH_DOMAIN',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_STORAGE_BUCKET',
        'FIREBASE_MESSAGING_SENDER_ID',
        'FIREBASE_APP_ID'
    ]
    
    removed_vars = []
    for var in env_vars_to_remove:
        if var in os.environ:
            removed_vars.append(f"{var}={os.environ[var]}")
            del os.environ[var]
    
    print(f"제거된 환경변수: {len(removed_vars)}개")
    for var in removed_vars:
        print(f"  - {var}")
    
    print("\n=== Firebase 설정 로드 테스트 ===")
    
    try:
        from main import load_firebase_config
        config = load_firebase_config()
        
        print("Firebase 설정 로드 성공")
        print(f"databaseURL: {config.get('databaseURL')}")
        print(f"projectId: {config.get('projectId')}")
        print(f"apiKey: {config.get('apiKey', '')[:20]}...")
        
        # URL 확인
        expected_url = "https://coldhawk-id.firebaseio.com"
        actual_url = config.get('databaseURL')
        
        if actual_url == expected_url:
            print(f"databaseURL 정상: {actual_url}")
        else:
            print(f"databaseURL 오류: {actual_url} (예상: {expected_url})")
            
    except Exception as e:
        print(f"Firebase 설정 로드 실패: {e}")
        return False
    
    print("\n=== IP 저장 테스트 ===")
    
    try:
        # IP 저장 로직 테스트 (실제 저장하지 않음)
        import requests
        response = requests.get('https://api.ipify.org?format=json', timeout=3)
        ip_address = response.json().get('ip', 'unknown')
        print(f"IP 주소 가져오기 성공: {ip_address}")
        
    except Exception as e:
        print(f"IP 주소 가져오기 실패: {e}")
        return False
    
    print("\n=== pyrebase 초기화 테스트 ===")
    
    try:
        import pyrebase
        firebase = pyrebase.initialize_app(config)
        print("pyrebase 초기화 성공")
        
        # databaseURL 확인
        if hasattr(firebase, 'database'):
            db = firebase.database()
            print("Realtime Database 접근 가능")
        else:
            print("Realtime Database 접근 불가")
            
    except Exception as e:
        print(f"pyrebase 초기화 실패: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("다른 PC 환경에서 정상 작동할 것으로 예상됩니다!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_other_pc_environment()
    input("\n아무 키나 누르면 종료됩니다...")

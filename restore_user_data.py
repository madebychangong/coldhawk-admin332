#!/usr/bin/env python3
"""
사용자 데이터 복구 스크립트
Firestore에서 삭제된 사용자 데이터를 복구합니다.
"""

import requests
import json
from datetime import datetime

def restore_user_data():
    """사용자 데이터 복구"""
    
    # Firebase 설정
    project_id = "coldhawk-id"
    user_id = "RzLGUQd5vbPqmDgfwJQgzukDlvp1"
    
    # 복구할 데이터
    restore_data = {
        "fields": {
            "email": {"stringValue": "ppylgr@gmail.com"},
            "status": {"stringValue": "approved"},
            "createdAt": {"timestampValue": "2025-10-19T07:37:46.377Z"},
            "approvedAt": {"integerValue": "1760881788249"},
            "approvedBy": {"stringValue": "ppylgr@gmail.com"},
            "lastLoginAt": {"timestampValue": "2025-10-19T14:46:23.000Z"},
            "lastLoginIP": {"stringValue": "218.39.102.230"}
        }
    }
    
    # Firestore REST API URL
    firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{user_id}"
    
    # 인증 토큰 필요 (Firebase Console에서 가져와야 함)
    print("Firebase Console에서 인증 토큰을 가져와주세요:")
    print("1. Firebase Console → 프로젝트 설정 → 서비스 계정")
    print("2. '새 비공개 키 생성' 클릭")
    print("3. JSON 파일 다운로드")
    print("4. 'private_key' 필드의 값을 여기에 입력하세요")
    
    # 실제로는 서비스 계정 키가 필요하지만, 
    # 여기서는 수동 복구 방법을 안내
    print("\n수동 복구 방법:")
    print("1. Firebase Console → Firestore → users 컬렉션")
    print("2. RzLGUQd5vbPqmDgfwJQgzukDlvp1 문서 클릭")
    print("3. 편집 모드에서 다음 필드들을 추가:")
    print("   - email: ppylgr@gmail.com")
    print("   - status: approved")
    print("   - createdAt: 2025-10-19T07:37:46.377Z")
    print("   - approvedAt: 1760881788249")
    print("   - approvedBy: ppylgr@gmail.com")

if __name__ == "__main__":
    restore_user_data()






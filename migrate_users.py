"""
Firebase Authentication에서 모든 사용자를 자동으로 가져와서 Firestore에 추가하는 스크립트
"""
import requests
import time
import pyrebase

# Firebase 설정
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyAo2-_VoDQsNjRCimzns5V6boc6-ajP8zs",
    "authDomain": "coldhawk-id.firebaseapp.com",
    "projectId": "coldhawk-id",
    "storageBucket": "coldhawk-id.firebasestorage.app",
    "databaseURL": "https://coldhawk-id-default-rtdb.firebaseio.com"
}

def get_all_users():
    """Firebase Authentication에서 모든 사용자 가져오기"""
    print("Firebase Authentication에서 사용자 목록 가져오는 중...")
    
    # Firebase Admin SDK를 사용해야 하지만, 여기서는 pyrebase로 로그인한 사용자 정보만 가져올 수 있음
    # 대신 사용자가 수동으로 입력한 UID 목록 사용
    print("❌ Firebase Admin SDK가 필요합니다.")
    print("대신 수동으로 UID와 이메일을 입력해주세요.")
    print()
    
    users = []
    while True:
        uid = input("UID 입력 (종료하려면 Enter): ").strip()
        if not uid:
            break
        email = input("이메일 입력: ").strip()
        users.append({"uid": uid, "email": email})
        print()
    
    return users

def migrate_users(users):
    """기존 사용자들을 Firestore에 추가"""
    project_id = FIREBASE_CONFIG["projectId"]
    api_key = FIREBASE_CONFIG["apiKey"]
    
    for user in users:
        uid = user["uid"]
        email = user["email"]
        
        print(f"사용자 추가 중: {email} ({uid})")
        
        # Firestore REST API URL
        firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/users/{uid}"
        
        # 사용자 데이터
        user_data = {
            "fields": {
                "email": {"stringValue": email},
                "status": {"stringValue": "approved"},
                "createdAt": {"integerValue": str(int(time.time() * 1000))},
                "approvedAt": {"integerValue": str(int(time.time() * 1000))},
                "approvedBy": {"stringValue": "admin"},
                "note": {"stringValue": "기존 사용자 자동 추가"}
            }
        }
        
        # Firestore에 사용자 데이터 생성
        try:
            response = requests.patch(f"{firestore_url}?key={api_key}", json=user_data)
            
            if response.status_code in [200, 201]:
                print(f"✅ 사용자 추가 완료: {email}")
            else:
                print(f"❌ 사용자 추가 실패: {email} - {response.status_code}")
                print(f"   오류: {response.text}")
        except Exception as e:
            print(f"❌ 사용자 추가 실패: {email} - {e}")
        
        print()

if __name__ == "__main__":
    print("=" * 50)
    print("기존 사용자 Firestore 자동 추가 스크립트")
    print("=" * 50)
    print()
    
    # 사용자 목록 가져오기
    users = get_all_users()
    
    if not users:
        print("추가할 사용자가 없습니다.")
        exit(0)
    
    print(f"추가할 사용자 수: {len(users)}")
    print()
    
    # 사용자에게 확인
    input("계속하려면 Enter 키를 누르세요...")
    print()
    
    # 사용자 추가
    migrate_users(users)
    
    print()
    print("=" * 50)
    print("완료!")
    print("=" * 50)


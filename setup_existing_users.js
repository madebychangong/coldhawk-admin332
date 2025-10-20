// 기존 사용자들을 자동으로 승인 상태로 설정하는 스크립트
// Firebase 콘솔의 Functions에서 실행하거나, Node.js 환경에서 실행

// 1. Firebase Admin SDK 설치 (터미널에서 실행)
// npm install firebase-admin

// 2. 이 스크립트를 실행

const admin = require('firebase-admin');

// Firebase 프로젝트 설정 (서비스 계정 키 필요)
const serviceAccount = {
  // Firebase 콘솔 → 프로젝트 설정 → 서비스 계정 → 새 비공개 키 생성
  // 생성된 JSON 파일의 내용을 여기에 붙여넣기
};

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: "https://coldhawk-id-default-rtdb.firebaseio.com"
});

async function setupExistingUsers() {
    try {
        const db = admin.database();
        const auth = admin.auth();
        
        console.log('🔍 기존 사용자 목록을 가져오는 중...');
        
        // 모든 인증된 사용자 목록 가져오기
        const listUsers = await auth.listUsers();
        console.log(`📊 총 ${listUsers.users.length}명의 사용자를 발견했습니다.`);
        
        const updates = {};
        const timestamp = Date.now();
        
        // 각 사용자에 대해 승인 데이터 생성
        for (const user of listUsers.users) {
            const uid = user.uid;
            const email = user.email;
            
            console.log(`👤 처리 중: ${email} (${uid})`);
            
            updates[`users/${uid}`] = {
                email: email,
                status: 'approved', // 기존 사용자는 자동 승인
                isApproved: true,
                createdAt: user.metadata.creationTime ? new Date(user.metadata.creationTime).getTime() : timestamp,
                approvedAt: timestamp,
                approvedBy: 'admin',
                note: '기존 사용자 자동 승인'
            };
        }
        
        console.log('💾 데이터베이스에 저장 중...');
        
        // 일괄 업데이트
        await db.ref().update(updates);
        
        console.log('✅ 완료! 모든 기존 사용자가 승인 상태로 설정되었습니다.');
        console.log(`✅ 처리된 사용자 수: ${listUsers.users.length}명`);
        
        return {
            success: true,
            processedCount: listUsers.users.length
        };
        
    } catch (error) {
        console.error('❌ 오류 발생:', error);
        throw error;
    }
}

// 실행
setupExistingUsers()
    .then(result => {
        console.log('🎉 마이그레이션 완료:', result);
        process.exit(0);
    })
    .catch(error => {
        console.error('💥 마이그레이션 실패:', error);
        process.exit(1);
    });













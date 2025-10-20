// 기존 사용자들을 승인 상태로 마이그레이션하는 스크립트
// Firebase 콘솔의 Functions에서 실행하거나, Node.js 환경에서 실행

const admin = require('firebase-admin');

// Firebase Admin SDK 초기화 (이미 초기화되어 있다면 생략)
// admin.initializeApp();

async function migrateExistingUsers() {
    try {
        const db = admin.database();
        
        // 1. Authentication에서 모든 사용자 목록 가져오기
        const auth = admin.auth();
        const listUsers = await auth.listUsers();
        
        console.log(`총 ${listUsers.users.length}명의 사용자를 처리합니다.`);
        
        const updates = {};
        const timestamp = Date.now();
        
        // 2. 각 사용자에 대해 승인 데이터 생성
        for (const user of listUsers.users) {
            const userData = {
                email: user.email,
                status: 'approved', // 기존 사용자는 자동 승인
                isApproved: true,
                createdAt: user.metadata.creationTime ? new Date(user.metadata.creationTime).getTime() : timestamp,
                approvedAt: timestamp,
                approvedBy: 'migration',
                migrationNote: '기존 사용자 자동 승인'
            };
            
            updates[`users/${user.uid}`] = userData;
        }
        
        // 3. 일괄 업데이트
        await db.ref().update(updates);
        
        console.log('✅ 기존 사용자 마이그레이션 완료!');
        console.log(`✅ ${listUsers.users.length}명의 사용자가 승인 상태로 설정되었습니다.`);
        
        return {
            success: true,
            migratedCount: listUsers.users.length
        };
        
    } catch (error) {
        console.error('❌ 마이그레이션 실패:', error);
        throw error;
    }
}

// 실행
migrateExistingUsers()
    .then(result => {
        console.log('마이그레이션 결과:', result);
        process.exit(0);
    })
    .catch(error => {
        console.error('마이그레이션 오류:', error);
        process.exit(1);
    });













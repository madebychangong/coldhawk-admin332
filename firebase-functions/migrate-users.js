// Firebase Functions - 기존 사용자 마이그레이션
const functions = require('firebase-functions');
const admin = require('firebase-admin');

exports.migrateExistingUsers = functions.https.onCall(async (data, context) => {
    // 관리자 권한 확인 (선택사항)
    // if (!context.auth || !context.auth.token.admin) {
    //     throw new functions.https.HttpsError('permission-denied', '관리자 권한이 필요합니다.');
    // }

    try {
        const db = admin.database();
        const auth = admin.auth();
        
        // 모든 인증된 사용자 목록 가져오기
        const listUsers = await auth.listUsers();
        console.log(`총 ${listUsers.users.length}명의 사용자를 처리합니다.`);
        
        const updates = {};
        const timestamp = Date.now();
        let migratedCount = 0;
        
        // 각 사용자에 대해 승인 데이터 생성
        for (const user of listUsers.users) {
            const uid = user.uid;
            const email = user.email;
            
            // 이미 users 테이블에 데이터가 있는지 확인
            const existingUser = await db.ref(`users/${uid}`).once('value');
            
            if (!existingUser.exists()) {
                // 기존 사용자 데이터가 없으면 승인 상태로 생성
                updates[`users/${uid}`] = {
                    email: email,
                    status: 'approved',
                    isApproved: true,
                    createdAt: user.metadata.creationTime ? new Date(user.metadata.creationTime).getTime() : timestamp,
                    approvedAt: timestamp,
                    approvedBy: 'migration',
                    migrationNote: '기존 사용자 자동 승인'
                };
                migratedCount++;
            }
        }
        
        // 일괄 업데이트
        if (Object.keys(updates).length > 0) {
            await db.ref().update(updates);
        }
        
        return {
            success: true,
            message: `${migratedCount}명의 기존 사용자가 승인 상태로 설정되었습니다.`,
            migratedCount: migratedCount,
            totalUsers: listUsers.users.length
        };
        
    } catch (error) {
        console.error('기존 사용자 마이그레이션 실패:', error);
        throw new functions.https.HttpsError('internal', '마이그레이션 처리 중 오류가 발생했습니다.');
    }
});













// Firebase Functions - 자동 승인 스크립트
const functions = require('firebase-functions');
const admin = require('firebase-admin');

// 모든 사용자를 자동으로 승인하는 함수
exports.autoApproveAllUsers = functions.https.onCall(async (data, context) => {
    // 관리자 권한 확인
    if (!context.auth || !context.auth.token.admin) {
        throw new functions.https.HttpsError('permission-denied', '관리자 권한이 필요합니다.');
    }

    try {
        const db = admin.database();
        const usersRef = db.ref('users');
        
        // 모든 사용자 조회
        const snapshot = await usersRef.once('value');
        const users = snapshot.val();
        
        if (!users) {
            return { message: '승인할 사용자가 없습니다.' };
        }
        
        const updates = {};
        const timestamp = Date.now();
        
        // 모든 사용자를 승인 상태로 변경
        Object.keys(users).forEach(uid => {
            updates[`users/${uid}/status`] = 'approved';
            updates[`users/${uid}/isApproved`] = true;
            updates[`users/${uid}/approvedAt`] = timestamp;
            updates[`users/${uid}/approvedBy`] = 'auto-approve';
        });
        
        // 일괄 업데이트
        await db.ref().update(updates);
        
        return { 
            message: `${Object.keys(users).length}명의 사용자가 승인되었습니다.`,
            approvedCount: Object.keys(users).length
        };
        
    } catch (error) {
        console.error('자동 승인 실패:', error);
        throw new functions.https.HttpsError('internal', '자동 승인 처리 중 오류가 발생했습니다.');
    }
});

// 특정 사용자 승인 함수
exports.approveUser = functions.https.onCall(async (data, context) => {
    const { uid } = data;
    
    if (!uid) {
        throw new functions.https.HttpsError('invalid-argument', '사용자 UID가 필요합니다.');
    }
    
    try {
        const db = admin.database();
        const userRef = db.ref(`users/${uid}`);
        
        await userRef.update({
            status: 'approved',
            isApproved: true,
            approvedAt: Date.now(),
            approvedBy: context.auth ? context.auth.uid : 'admin'
        });
        
        return { message: '사용자가 승인되었습니다.' };
        
    } catch (error) {
        console.error('사용자 승인 실패:', error);
        throw new functions.https.HttpsError('internal', '사용자 승인 처리 중 오류가 발생했습니다.');
    }
});













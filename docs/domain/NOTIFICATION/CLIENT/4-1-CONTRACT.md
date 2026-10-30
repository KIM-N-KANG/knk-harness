# 4-1 연동 계약

기준: [요구사항](2-2-REQUIREMENTS.md), [화면 흐름](3-2-INTERACTION-FLOWS.md).

<br>

### 4-1-1 클라이언트가 사용하는 API

경로 기준은 `/api/v1`이다. 요청과 응답의 정본은 [제공자 계약](../BACKEND/4-2-CONTRACT.md)이며, 아래에는 소비 조건과 사용하는 필드만 기술한다.

| 용도 | 요청과 사용 |
|---|---|
| 공지 목록과 상세 | [공지 목록과 상세](../BACKEND/4-2-CONTRACT.md#4-2-14-공지-공개-조회). 인증 없음, 목록 nextCursor, 상세 tag와 제목, publishedAt, updatedAt, body 사용 |
| 공지 본문 | 서버가 가공하지 않는 최대 5,000자 평문 |
| 회원 알림 목록 | [알림 목록](../BACKEND/4-2-CONTRACT.md#4-2-15-회원-알림함). category NEWS 또는 ACTIVITY, nextCursor 사용 |
| 안 읽은 수 | [안 읽은 수](../BACKEND/4-2-CONTRACT.md#4-2-15-회원-알림함). total과 분류별 수 사용 |
| 한 건 읽음 | [한 건 읽음](../BACKEND/4-2-CONTRACT.md#4-2-15-회원-알림함). 이미 readAt이 있으면 미호출 |
| 모두 읽음 | [모두 읽음](../BACKEND/4-2-CONTRACT.md#4-2-15-회원-알림함). category를 생략해 분류를 제한하지 않음 |
| 회원 알림 인증 | 회원 필수. 정지 403, 탈퇴 401 |
| 알림 카드 | type, 공지 noticeTag, title, body, createdAt, readAt, deepLink, noticeId와 storyId 사용 |
| 토큰 | [등록](../BACKEND/4-2-CONTRACT.md#4-2-2-토큰-등록)과 [삭제](../BACKEND/4-2-CONTRACT.md#4-2-3-토큰-삭제). WEB 또는 ANDROID 플랫폼 |
| 동의 | [조회](../BACKEND/4-2-CONTRACT.md#4-2-4-수신-동의-조회), [변경](../BACKEND/4-2-CONTRACT.md#4-2-5-수신-동의-변경). servicePush, marketingPush, marketingNightPush 전체 교체 |
| 푸시 | [제공자 데이터](../BACKEND/4-2-CONTRACT.md#4-2-10-푸시-데이터). type, recipientId, deepLink 및 시나리오 식별자 |

알림함의 이동 불가 결과는 다른 식별자로 대체하거나 읽음만 처리한다. 푸시 탭의 잘못된 링크는 플랫폼 계약에 따라 홈으로 이동한다. 두 경로를 같은 실패 처리로 합치지 않는다.

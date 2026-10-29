# NOTIFICATION 클라이언트 연동 계약

기준: [요구사항](REQUIREMENTS.md), [화면 흐름](INTERACTION-FLOWS.md).

<br>

### 클라이언트가 사용하는 API

경로 기준은 `/api/v1`이다. 공지와 알림함은 기존 클라이언트 계약의 사용 필드를 기술하며 응답 전체 스키마를 복제하지 않는다.

| 용도 | 요청과 사용 |
|---|---|
| 공지 목록과 상세 | GET /notices, GET /notices/{noticeId}. 인증 없음, 목록 nextCursor, 상세 tag와 제목, publishedAt, updatedAt, body 사용 |
| 공지 본문 | 서버가 가공하지 않는 최대 5,000자 평문 |
| 회원 알림 목록 | GET /users/me/notifications. category NEWS 또는 ACTIVITY, nextCursor 사용 |
| 안 읽은 수 | GET /users/me/notifications/unread-count. total과 분류별 수 사용 |
| 한 건 읽음 | POST /users/me/notifications/{notificationId}/read. 이미 readAt이 있으면 미호출 |
| 모두 읽음 | POST /users/me/notifications/read-all. 분류를 제한하지 않음 |
| 회원 알림 인증 | 회원 필수. 정지 403, 탈퇴 401 |
| 알림 카드 | type, 공지 tag, title, body, createdAt, readAt, deepLink, noticeId와 storyId 사용 |
| 토큰 | [등록](../BACKEND/CONTRACT.md#토큰-등록)과 [삭제](../BACKEND/CONTRACT.md#토큰-삭제). WEB 또는 ANDROID 플랫폼 |
| 동의 | [조회](../BACKEND/CONTRACT.md#수신-동의-조회), [변경](../BACKEND/CONTRACT.md#수신-동의-변경). servicePush, marketingPush, marketingNightPush 전체 교체 |
| 푸시 | [제공자 데이터](../BACKEND/CONTRACT.md#푸시-데이터). type, recipientId, deepLink 및 시나리오 식별자 |

알림함의 이동 불가 결과는 다른 식별자로 대체하거나 읽음만 처리한다. 푸시 탭의 잘못된 링크는 플랫폼 계약에 따라 홈으로 이동한다. 두 경로를 같은 실패 처리로 합치지 않는다.

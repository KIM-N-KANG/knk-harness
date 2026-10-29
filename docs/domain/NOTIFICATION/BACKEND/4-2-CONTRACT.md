# 4-2 계약

이 문서는 NOTIFICATION 도메인의 클라이언트 API, 서버와 알림 서비스 사이의 내부 API, 관리자의 캠페인과 문구 템플릿 API, 큐 메시지, 기기에 도착하는 푸시 데이터, 다른 도메인과의 경계를 정한다.

처리 순서와 판정 규칙은 처리 흐름에, 앱 코드 전체 목록과 복구는 오류 처리에, 비밀값 취급은 보안에, 관리자 토큰과 권한 판정은 관리자 계약에 있다. ([4-1 처리 흐름](4-1-PIPELINES.md), [5-3-2 앱 코드](5-3-ERROR-HANDLING.md#5-3-2-앱-코드), [5-1-7 비밀값과 개인정보](5-1-SECURITY.md#5-1-7-비밀값과-개인정보), [ADMIN 4-2-1 공통 규칙과 헤더](../../ADMIN/BACKEND/4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더))

<br>

### 4-2-1 공통 규칙과 헤더

**1. 공통 규칙**

| 항목 | 규칙 |
|---|---|
| 경로 | 회원 API와 관리자 API는 `/api/v1`을 생략해 적음<br>내부 API는 전체 경로 |
| JSON 필드 이름 | camelCase |
| 시각 | ISO 8601 UTC 문자열 |
| 식별자 | 회원, 캠페인, 공지, 알림 내역은 UUID 공개 식별자<br>토큰 행 ID와 템플릿 행 ID는 노출하지 않음 |
| 사유 | 관리자 변경 작업의 요청 본문에 `reason` 필수 |
| 푸시 데이터 값 | 모두 문자열 |
| 예시 값 | 모든 예시는 구조를 설명하기 위한 가상 값 |

<br>

**2. 인증 수준**

| 수준 | 토큰 없음 또는 무효 | 유효한 앱 접근 토큰 | 관리자 토큰 |
|---|---|---|---|
| `필수` | 거절 | 회원으로 처리 | 거절 |
| `내부` | 토큰을 읽지 않음 | 토큰을 읽지 않음<br>공유 시크릿 헤더로 인증 | 토큰을 읽지 않음 |
| `관리자` | 거절 | 거절 | 관리자 역할과 계정 상태를 다시 확인해 관리자 권한이 있는 회원으로 처리<br>권한이 없으면 403 |

<br>

**3. 요청 헤더**

| 요청 헤더 | 값 형식 | 쓰임 | 필수 |
|---|---|---|---|
| `Authorization` | `Bearer {accessToken}` 또는 `Bearer {adminToken}` | 회원 또는 관리자 식별 | 인증 수준에 따름 |
| `X-Manyak-Request-Id` | 문자열 | 로그 연결<br>없으면 생성하고 응답 헤더로 반환 | 선택 |
| `X-Manyak-Session-Id` | 문자열 | 클라이언트 분석 세션 식별 | 선택 |
| `X-Manyak-Internal-Secret` | 문자열 | 서버와 알림 서비스 사이의 인증 | 내부 API는 필수 |
| `X-Manyak-Device-Id-Hash` | 문자열 | 알림 서비스가 서버에 전달하는 기기 해시 | 선택 |

<br>

**4. 계정 상태 규칙**

| 요청 | 정지 계정 | 탈퇴 계정 |
|---|---|---|
| 토큰 등록, 토큰 삭제, 수신 동의 조회, 수신 동의 변경 | 403 | 401 |
| 알림 내역 목록, 안 읽은 알림 수, 알림 읽음, 모든 알림 읽음 | 403 | 401 |

<br>

**5. 공통 실패 응답**

실패 응답은 모두 같은 형식이다. 알림 발송의 502는 예외이며 해당 절에서 정한다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `timestamp` | `string` | 응답 생성 시각 |
| `status` | `integer` | HTTP 상태 |
| `code` | `string` | HTTP 상태 이름 또는 앱 코드 |
| `message` | `string` | 사용자 안내 문구 |
| `path` | `string` | 요청 경로 |
| `details` | `object[]` | 선언적 필드 검증과 타입 변환 실패 시 `field`와 `message` 포함<br>그 외는 빈 배열 |

| `details[].field` 규칙 | 값 |
|---|---|
| 필드 검증 | 필드명 |
| 본문 파싱 실패 | 빈 `details` |

각 절의 실패 표에는 해당 엔드포인트에서 발생하는 상태와 `code`를 적는다. 다음 공통 실패는 각 절에서 생략한다.

| 상태 | `code` | 조건 |
|---|---|---|
| 401 | `UNAUTHORIZED` | 인증 필수 경로의 토큰 누락, 만료, 위조, 주체 형식 오류, 사용자 없음<br>확인된 탈퇴 계정<br>내부 API의 시크릿 누락 또는 불일치<br>관리자 경로의 토큰 누락, 만료, 위조, 관리자 표식 없음 |
| 403 | `FORBIDDEN` | 계정 상태 규칙 표의 403<br>관리자 경로의 권한 없는 회원(역할 없음, 정지, 탈퇴, 회원 없음) |
| 403 | `CONSENT_REQUIRED` | 동의 게이트가 켜진 환경에서 미동의 회원의 허용 목록 밖 요청 |
| 404 | `NOT_FOUND` | 내부 API의 시크릿 미설정 환경 |
| 500 | `INTERNAL_SERVER_ERROR` | 예상하지 못한 오류 |

<br>

**6. 공통 응답 구조**

캠페인 목록의 항목과 상세, 예약, 취소, 재실행 응답은 같은 캠페인 구조를 쓴다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `campaignId` | `string` | 캠페인 공개 식별자 |
| `kind` | `string` | 알림 성격<br>`SERVICE`는 정보성, `MARKETING`은 광고성 |
| `title` | `string` | 광고 표기 없는 제목 |
| `body` | `string` | |
| `scheduledAt` | `string` | 예약 시각 |
| `status` | `string` | `SCHEDULED`, `SENDING`, `SENT`, `CANCELED`, `FAILED` |
| `noticeId` | `string / null` | 공지 알림이면 공지 공개 식별자 |
| `storyId` | `string / null` | 이동 대상 스토리의 공개 식별자<br>프로모션이 스토리로 이어질 때만 |
| `targetCount` | `integer / null` | 마지막 회차의 대상 수<br>회차 전은 `null` |
| `sentCount` | `integer / null` | 마지막 회차의 결과<br>원격 모드는 기록한 발송 요청 수, 로컬 모드는 발송기 호출 수<br>실제 도달 수가 아님 |
| `deliveredMembers` | `integer` | 도달 기기가 하나 이상인 회원 수<br>발송 결과 행의 집계 |
| `deliveredDevices` | `integer` | 도달 기기 수의 합 |
| `failedDevices` | `integer` | 실패 기기 수의 합 |
| `startedAt` | `string / null` | 선점 시각 |
| `finishedAt` | `string / null` | 회차 종료 시각 |
| `createdAt` | `string` | |

목록 응답은 관리자 목록 공통의 페이지 쿼리와 페이지 구조를 쓴다. ([ADMIN 4-2-1 공통 규칙과 헤더](../../ADMIN/BACKEND/4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더))

<br>

### 4-2-2 토큰 등록

| 항목 | 값 |
|---|---|
| 요청 | `PUT /users/me/push-tokens` |
| 인증 | 필수 |
| 성공 | 204, 본문 없음 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `token` | `string` | 필수 | FCM 등록 토큰, 1~512자 |
| `platform` | `string` | 필수 | `ANDROID`, `WEB` |

- 같은 토큰을 다시 보내면 갱신한다. 토큰이 바뀌면 새 값으로 다시 등록한다. 다른 회원이 등록한 토큰을 보내면 소유자가 요청자로 바뀐다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 토큰 누락, 공백, 512자 초과, 플랫폼 누락이나 미지원 값 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
PUT /api/v1/users/me/push-tokens
Authorization: Bearer {accessToken}
Content-Type: application/json

{ "token": "dEv1cE:APA91bExampleToken-0123456789", "platform": "ANDROID" }
```

**2) 204 Response**

본문 없음

**3) 400 Response body**

```json
{
  "timestamp": "2026-10-16T01:23:45.678Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "요청 값이 올바르지 않습니다.",
  "path": "/api/v1/users/me/push-tokens",
  "details": [{ "field": "platform", "message": "must not be null" }]
}
```

</details>

<br>

### 4-2-3 토큰 삭제

| 항목 | 값 |
|---|---|
| 요청 | `DELETE /users/me/push-tokens` |
| 인증 | 필수 |
| 성공 | 204, 본문 없음 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `token` | `string` | 필수 | 지울 토큰, 1~512자 |

- 토큰은 경로가 아니라 본문으로 받는다. 요청자 소유가 아니거나 없으면 삭제 없이 성공으로 응답한다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 토큰 누락, 공백, 512자 초과 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
DELETE /api/v1/users/me/push-tokens
Authorization: Bearer {accessToken}
Content-Type: application/json

{ "token": "dEv1cE:APA91bExampleToken-0123456789" }
```

**2) 204 Response**

본문 없음

**3) 400 Response body**

```json
{
  "timestamp": "2026-10-16T01:23:45.678Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "요청 값이 올바르지 않습니다.",
  "path": "/api/v1/users/me/push-tokens",
  "details": [{ "field": "token", "message": "must not be blank" }]
}
```

</details>

<br>

### 4-2-4 수신 동의 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /users/me/push-settings` |
| 인증 | 필수 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `servicePush` | `boolean` | 서비스 알림 수신 여부 |
| `marketingPush` | `boolean` | 광고 알림 동의 여부 |
| `marketingNightPush` | `boolean` | 야간 광고 알림 동의 여부 |

<br>

**2. 실패 응답**

공통 실패만 있다.

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/users/me/push-settings
Authorization: Bearer {accessToken}
```

**2) 200 Response body**

```json
{ "servicePush": true, "marketingPush": true, "marketingNightPush": false }
```

</details>

<br>

### 4-2-5 수신 동의 변경

| 항목 | 값 |
|---|---|
| 요청 | `PUT /users/me/push-settings` |
| 인증 | 필수 |
| 성공 | 200, 수신 동의 조회와 같은 응답 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `servicePush` | `boolean` | 필수 | 서비스 알림 수신 여부 |
| `marketingPush` | `boolean` | 필수 | 광고 알림 동의<br>`false`면 야간도 함께 철회 |
| `marketingNightPush` | `boolean` | 필수 | 야간 광고 알림 동의<br>`marketingPush`가 `false`면 `true`일 수 없음 |

- 세 설정값을 모두 교체한다. 누락과 `null`은 거절해 보내지 않은 설정이 꺼지지 않게 한다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 필드 누락, `null`, 형식 오류 |
| 400 | `NIGHT_PUSH_REQUIRES_MARKETING` | 광고 동의 없이 야간만 켬 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
PUT /api/v1/users/me/push-settings
Authorization: Bearer {accessToken}
Content-Type: application/json

{ "servicePush": true, "marketingPush": true, "marketingNightPush": true }
```

**2) 200 Response body**

```json
{ "servicePush": true, "marketingPush": true, "marketingNightPush": true }
```

**3) 400 Response body**

```json
{
  "timestamp": "2026-10-16T01:23:45.678Z",
  "status": 400,
  "code": "NIGHT_PUSH_REQUIRES_MARKETING",
  "message": "야간 광고 알림은 광고 알림 수신에 동의해야 켤 수 있습니다.",
  "path": "/api/v1/users/me/push-settings",
  "details": []
}
```

</details>

<br>

### 4-2-6 발송 자격 조회

서버가 제공하고 알림 서비스가 호출한다.

| 항목 | 값 |
|---|---|
| 요청 | `GET /internal/users/{publicId}/push-eligibility` |
| 인증 | 내부 |
| 성공 | 200 |

**1. 경로와 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `publicId` | `string` | 필수 | 경로 변수, 회원 공개 식별자 |
| `kind` | `string` | 필수 | `SERVICE`, `MARKETING` |
| `at` | `string` | 필수 | 판정 시각<br>발송 직전의 현재 시각 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `allowed` | `boolean` | 발송 가능 여부 |
| `reason` | `string` | `OK`, `USER_NOT_FOUND`, `NOT_ACTIVE`, `SERVICE_PUSH_DISABLED`, `MARKETING_NOT_AGREED`, `NO_TOKENS` |
| `tokens` | `object[]` | 허용일 때만, 최근 갱신 순 최대 10개<br>거절이면 빈 배열 |
| `tokens[].token` | `string` | FCM 등록 토큰 |
| `tokens[].platform` | `string` | `ANDROID`, `WEB` |

| `reason` | 의미 |
|---|---|
| `OK` | 발송 가능 |
| `USER_NOT_FOUND` | 없는 회원 |
| `NOT_ACTIVE` | 정지 또는 탈퇴 계정 |
| `SERVICE_PUSH_DISABLED` | 서비스 알림 꺼짐 |
| `MARKETING_NOT_AGREED` | 광고 알림 미동의<br>야간 시각이면 야간 광고 알림 미동의 포함 |
| `NO_TOKENS` | 등록된 토큰 없음 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `kind` 또는 `at` 누락, 형식 오류 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /internal/users/3f2504e0-4f89-41d3-9a0c-0305e82c3301/push-eligibility?kind=MARKETING&at=2026-10-16T00:00:00Z
X-Manyak-Internal-Secret: {sharedSecret}
```

**2) 200 Response body, 허용**

```json
{
  "allowed": true,
  "reason": "OK",
  "tokens": [{ "token": "dEv1cE:APA91bExampleToken-0123456789", "platform": "ANDROID" }]
}
```

**3) 200 Response body, 거절**

```json
{ "allowed": false, "reason": "MARKETING_NOT_AGREED", "tokens": [] }
```

**4) 400 Response body**

```json
{
  "timestamp": "2026-10-16T01:23:45.678Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "kind는 필수입니다.",
  "path": "/internal/users/3f2504e0-4f89-41d3-9a0c-0305e82c3301/push-eligibility",
  "details": []
}
```

</details>

<br>

### 4-2-7 무효 토큰 삭제

서버가 제공하고 알림 서비스가 호출한다.

| 항목 | 값 |
|---|---|
| 요청 | `DELETE /internal/push-tokens` |
| 인증 | 내부 |
| 성공 | 204, 본문 없음 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `token` | `string` | 필수 | FCM이 무효라고 알린 토큰, 1~512자 |

- 소유자 조건 없이 토큰으로 지운다. 없어도 성공으로 응답한다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 토큰 누락, 공백, 512자 초과 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
DELETE /internal/push-tokens
X-Manyak-Internal-Secret: {sharedSecret}
Content-Type: application/json

{ "token": "dEv1cE:APA91bExampleToken-0123456789" }
```

**2) 204 Response**

본문 없음

**3) 400 Response body**

```json
{
  "timestamp": "2026-10-16T01:23:45.678Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "요청 값이 올바르지 않습니다.",
  "path": "/internal/push-tokens",
  "details": [{ "field": "token", "message": "must not be blank" }]
}
```

</details>

<br>

### 4-2-8 알림 발송

알림 서비스가 제공한다. 메시지 큐를 거치지 않는 수동 검증용 경로이며 서비스 경로에서는 호출하지 않는다.

| 항목 | 값 |
|---|---|
| 요청 | `POST /internal/notifications` |
| 인증 | 내부 |
| 성공 | 200 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `recipientId` | `string` | 필수 | 수신 회원 공개 식별자 |
| `kind` | `string` | 필수 | `SERVICE`, `MARKETING` |
| `type` | `string` | 필수 | 시나리오 식별자 |
| `data` | `object` | 필수 | 푸시 데이터 |
| `expiresAt` | `string` | 선택 | 발송 가능 기한<br>생략하면 만료 없음 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `outcome` | `string` | `SENT`, `SKIPPED`, `EXPIRED`, `FAILED` |
| `reason` | `string` | `OK`, `PARTIAL_FAILURE`, `NO_DELIVERIES`, `EXPIRED`, `FCM_DISABLED`, `ELIGIBILITY_UNAVAILABLE`, 또는 자격 거절 사유 |
| `sent` | `integer` | 발송 성공 기기 수 |
| `unregistered` | `integer` | 무효로 정리한 기기 수 |
| `failed` | `integer` | 실패 기기 수 |

| `outcome` | `reason` | 의미 |
|---|---|---|
| `SENT` | `OK` | 모든 기기 성공 |
| `SENT` | `PARTIAL_FAILURE` | 일부 성공 |
| `SKIPPED` | 자격 거절 사유 | 동의, 상태, 토큰 조건 미충족 |
| `SKIPPED` | `FCM_DISABLED` | FCM 자격 증명 미설정 |
| `EXPIRED` | `EXPIRED` | 기한 경과 |
| `FAILED` | `NO_DELIVERIES` | 성공 0건 |
| `FAILED` | `ELIGIBILITY_UNAVAILABLE` | 자격 조회 실패, 발송 없음 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 필수 필드 누락, 형식 오류 |
| 502 | 없음 | 자격 조회 실패<br>본문은 공통 실패 형식이 아니라 응답과 같은 구조이며 `outcome`은 `FAILED`, `reason`은 `ELIGIBILITY_UNAVAILABLE` |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /internal/notifications
X-Manyak-Internal-Secret: {sharedSecret}
Content-Type: application/json

{
  "recipientId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "kind": "SERVICE",
  "type": "STORY_COMPLETED",
  "data": {
    "type": "STORY_COMPLETED",
    "storyId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "title": "달빛 아래의 약속",
    "deepLink": "https://manyak.app/stories/7c9e6679-7425-40de-944b-e07fc1f90ae7?utm_source=push&utm_medium=push&utm_campaign=story_completed&utm_content=story_completed"
  }
}
```

**2) 200 Response body**

```json
{ "outcome": "SENT", "reason": "OK", "sent": 2, "unregistered": 0, "failed": 0 }
```

**3) 502 Response body**

```json
{ "outcome": "FAILED", "reason": "ELIGIBILITY_UNAVAILABLE", "sent": 0, "unregistered": 0, "failed": 0 }
```

</details>

<br>

### 4-2-9 큐 메시지

서버가 발행하고 알림 서비스가 소비한다. 아웃박스 본문과 큐 메시지 본문이 같다.

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `messageId` | `string` | 필수 | 시나리오별 메시지 식별자<br>재발행과 재전달에도 바뀌지 않음 |
| `recipientId` | `string` | 필수 | 수신 회원 공개 식별자 |
| `kind` | `string` | 필수 | `SERVICE`, `MARKETING` |
| `type` | `string` | 필수 | `STORY_COMPLETED`, `STORY_MODERATION_COMPLETED`, `STORY_TAKEN_DOWN`, `NOTICE`, `ATTENDANCE_REMINDER`, `CREDIT_EXPIRY_REMINDER`, `PROMOTION`<br>`data.type`과 같아야 함 |
| `data` | `object` | 필수 | 푸시 데이터<br>동의와 토큰을 담지 않음 |
| `expiresAt` | `string` | 선택 | 발송 가능 기한<br>출석 리마인드는 당일 KST 자정<br>이프 만료 예정 알림은 회원의 창 안 로트 중 가장 늦은 만료 시각<br>생략하면 만료 없음 |
| `requestId` | `string` | 필수 | 발행 원인의 요청 ID<br>없으면 `unknown` |
| `sessionId` | `string` | 필수 | 발행 원인의 세션 ID<br>없으면 `unknown` |
| `schemaVersion` | `integer` | 필수 | `1` |

| `type` | `kind` | `messageId` |
|---|---|---|
| `STORY_COMPLETED` | `SERVICE` | `story-completed:{완성 요청 ID}` |
| `STORY_MODERATION_COMPLETED` | `SERVICE` | `story-moderation:{제출본 ID}:{회차}` |
| `STORY_TAKEN_DOWN` | `SERVICE` | `story-taken-down:{스토리 공개 식별자}:{공개 중단 시각의 epoch 밀리초}` |
| `NOTICE` | `SERVICE` | `notice:{캠페인 공개 식별자}:{회원 공개 식별자}` |
| `ATTENDANCE_REMINDER` | `MARKETING` | `attendance:{회원 공개 식별자}:{KST 날짜}` |
| `CREDIT_EXPIRY_REMINDER` | `SERVICE` | `credit-expiry:{회원 공개 식별자}:{KST 날짜}` |
| `PROMOTION` | `MARKETING` | `promotion:{캠페인 공개 식별자}:{회원 공개 식별자}` |

- 추적 헤더 `traceparent`, `tracestate`는 본문이 아니라 메시지 큐의 메시지 속성에 싣는다.
- 출석 리마인드, 이프 만료 예정 알림, 캠페인은 스케줄러가 회원마다 메시지를 기록한다. `requestId`와 `sessionId`는 `unknown`이다.

<details>
<summary><b>메시지 예시</b></summary>

<br>

**1) `STORY_COMPLETED` 메시지**

```json
{
  "messageId": "story-completed:9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "recipientId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "kind": "SERVICE",
  "type": "STORY_COMPLETED",
  "data": {
    "type": "STORY_COMPLETED",
    "storyId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "title": "달빛 아래의 약속",
    "deepLink": "https://manyak.app/stories/7c9e6679-7425-40de-944b-e07fc1f90ae7?utm_source=push&utm_medium=push&utm_campaign=story_completed&utm_content=story_completed"
  },
  "requestId": "req_0f1e2d3c4b5a69788796a5b4c3d2e1f0",
  "sessionId": "unknown",
  "schemaVersion": 1
}
```

</details>

<br>

### 4-2-10 푸시 데이터

기기에 도착하는 FCM 메시지의 데이터다. 클라이언트는 `type`으로 시나리오를 판정하고 `recipientId`를 현재 회원과 대조한다.

**1. 공통 필드**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `type` | `string` | 시나리오 식별자 |
| `recipientId` | `string` | 수신 회원 공개 식별자<br>발송기가 항상 덧붙이며 시나리오 값보다 우선 |
| `deepLink` | `string` | 알림을 눌렀을 때 열 절대 URL<br>운영 웹 주소에 경로와 UTM 쿼리를 붙임<br>없는 시나리오도 있음 |

<br>

**2. 시나리오별 필드**

| `type` | 필드명 | 타입 | 의미 |
|---|---|---|---|
| `STORY_COMPLETED` | `storyId` | `string` | 스토리 공개 식별자 |
| `STORY_COMPLETED` | `title` | `string` | 스토리 제목 |
| `STORY_COMPLETED` | `deepLink` | `string` | `/stories/{storyId}` |
| `STORY_MODERATION_COMPLETED` | `submissionId` | `string` | 제출본 식별자 |
| `STORY_MODERATION_COMPLETED` | `status` | `string` | `APPROVED`, `REJECTED`, `FAILED` |
| `STORY_MODERATION_COMPLETED` | `storyId` | `string` | 스토리 공개 식별자<br>있을 때만 |
| `STORY_MODERATION_COMPLETED` | `deepLink` | `string` | `/studio` |
| `STORY_MODERATION_COMPLETED` | `title` | `string` | 결과별 제목 |
| `STORY_MODERATION_COMPLETED` | `body` | `string` | 결과별 본문 |
| `STORY_TAKEN_DOWN` | `storyId` | `string` | 스토리 공개 식별자 |
| `STORY_TAKEN_DOWN` | `deepLink` | `string` | `/studio` |
| `STORY_TAKEN_DOWN` | `title` | `string` | 고정 제목 |
| `STORY_TAKEN_DOWN` | `body` | `string` | 스토리 제목과 사유가 들어간 본문 |
| `NOTICE` | `campaignId` | `string` | 캠페인 공개 식별자 |
| `NOTICE` | `noticeId` | `string` | 공지 공개 식별자 |
| `NOTICE` | `noticeTag` | `string` | 공지 태그<br>`SERVICE`, `UPDATE`, `MAINTENANCE` |
| `NOTICE` | `title` | `string` | 공지의 알림 제목<br>광고 표기 없음 |
| `NOTICE` | `body` | `string` | 공지의 알림 본문 |
| `NOTICE` | `deepLink` | `string` | `/notices/{noticeId}` |
| `ATTENDANCE_REMINDER` | `date` | `string` | KST 날짜 |
| `ATTENDANCE_REMINDER` | `title` | `string` | 광고 표기가 붙은 템플릿 제목 |
| `ATTENDANCE_REMINDER` | `body` | `string` | 수신거부 안내가 붙은 템플릿 본문<br>원문 최대 300자에 줄바꿈과 안내를 더해 최대 317자 |
| `ATTENDANCE_REMINDER` | `deepLink` | `string` | `/my/credits?tab=free` |
| `CREDIT_EXPIRY_REMINDER` | `title` | `string` | 템플릿 제목<br>광고 표기 없음 |
| `CREDIT_EXPIRY_REMINDER` | `body` | `string` | 템플릿 본문 |
| `CREDIT_EXPIRY_REMINDER` | `deepLink` | `string` | `/my/credits?tab=history` |
| `PROMOTION` | `campaignId` | `string` | 캠페인 공개 식별자 |
| `PROMOTION` | `title` | `string` | 광고 표기가 붙은 제목 |
| `PROMOTION` | `body` | `string` | 수신거부 안내가 붙은 본문<br>원문 최대 300자에 줄바꿈과 안내를 더해 최대 317자 |
| `PROMOTION` | `noticeId` | `string` | 광고성 공지일 때만<br>공지 공개 식별자 |
| `PROMOTION` | `noticeTag` | `string` | 광고성 공지일 때만<br>`EVENT`, `PROMOTION` |
| `PROMOTION` | `storyId` | `string` | 이동 대상 스토리가 있을 때만<br>스토리 공개 식별자 |
| `PROMOTION` | `deepLink` | `string` | 광고성 공지는 `/notices/{noticeId}`<br>이동 대상 스토리는 `/stories/{storyId}`<br>둘 다 없으면 필드 없음 |

| `status` | `title` | `body` |
|---|---|---|
| `APPROVED` | 검수를 통과했어요 | 「{스토리 제목}」의 등록이 완료됐어요. 지금 확인해 보세요. |
| `REJECTED` | 검수에서 반려됐어요 | 「{스토리 제목}」의 내용을 수정해 다시 제출해 주세요. |
| `FAILED` | 검수를 진행하지 못했어요 | 「{스토리 제목}」의 검수 중 문제가 생겼어요. 잠시 후 다시 제출해 주세요. |

| `type` | `title` | `body` |
|---|---|---|
| `STORY_TAKEN_DOWN` | 스토리 공개가 제한됐어요 | 「{스토리 제목}」{은/는} {사유} 사유로 공개할 수 없어요. 내용을 수정해 검수를 통과하면 공개할 수 있어요. |

| 자리 | 값 |
|---|---|
| `{스토리 제목}` | 이름 토큰을 기본 주인공 이름으로 치환한 공개 중단 시점의 제목<br>치환한 제목이 100자를 넘으면 앞 99자 뒤에 `…`(U+2026) 한 글자를 붙여 100자로 줄임<br>글자 수는 코드포인트 기준이고 서로게이트 쌍을 쪼개지 않음<br>저장된 스토리 제목은 바꾸지 않음 |
| `{은/는}` | 본문에 넣은 제목의 마지막 글자가 한글 음절이면 받침이 있을 때 `은`, 없을 때 `는`<br>그 밖의 글자(숫자, 영문, 기호)면 `은(는)`<br>줄인 제목은 `…`로 끝나 `은(는)` |
| `{사유}` | 사유 분류의 표시 이름(선정성, 저작권 침해, 혐오 표현)<br>사유 분류가 `ETC`면 관리자가 입력한 사유이며 표시 이름 기타는 쓰지 않음 ([MODERATION 4-2-10 공개 중단](../../MODERATION/BACKEND/4-2-CONTRACT.md#4-2-10-공개-중단)) |

- 알림 내역 본문과 푸시 본문은 같은 문자열이다. 제목을 줄이면 본문은 입력 사유 100자를 넣어도 250자 이하라 알림 내역 본문 상한 300자를 넘지 않는다.
- 이미 비공개였던 스토리도 같은 문구다. 사용자 화면에서는 관리자 용어 "공개 중단" 대신 "공개 제한"으로 부른다.
- `CREDIT_EXPIRY_REMINDER`에는 금액, 수량, 만료 시각 필드가 없다. 회원이 이프 내역 탭에서 만료 예정일을 확인한다. 알림 내역의 제목, 본문, 딥링크도 이 데이터와 같다.
- `tab` 값은 `purchase`, `free`, `history`다. 모르는 값을 받은 클라이언트는 이프 화면의 기본 탭을 연다.

<br>

**3. 딥링크 UTM 쿼리**

딥링크가 있는 모든 시나리오는 경로 뒤에 팀 UTM 규격의 네 필드를 붙인다. 경로에 이미 쿼리가 있으면 `&`로 잇고 없으면 `?`로 시작한다. 값은 URL 인코딩하고 순서는 `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`다.

| `type` | `utm_source` | `utm_medium` | `utm_campaign` | `utm_content` |
|---|---|---|---|---|
| `STORY_COMPLETED` | `push` | `push` | `story_completed` | `story_completed` |
| `STORY_MODERATION_COMPLETED` | `push` | `push` | `story_moderation_completed` | `story_moderation_completed` |
| `STORY_TAKEN_DOWN` | `push` | `push` | `story_taken_down` | `story_taken_down` |
| `ATTENDANCE_REMINDER` | `push` | `push` | `attendance_reminder` | `attendance_reminder` |
| `CREDIT_EXPIRY_REMINDER` | `push` | `push` | `credit_expiry_reminder` | `credit_expiry_reminder` |
| `NOTICE` | `push` | `push` | 캠페인 공개 식별자 | `notice` |
| `PROMOTION` | `push` | `push` | 캠페인 공개 식별자 | `promotion` |

- 관리자 캠페인으로 보내는 공지와 프로모션은 캠페인 공개 식별자, 캠페인이 없는 서비스 알림과 출석 리마인드는 `type`을 소문자로 바꾼 종류 코드를 캠페인 값으로 쓴다.
- 딥링크가 없는 프로모션은 UTM도 없다.
- 예: 출석 리마인드는 `https://manyak.app/my/credits?tab=free&utm_source=push&utm_medium=push&utm_campaign=attendance_reminder&utm_content=attendance_reminder`, 공지 알림은 `https://manyak.app/notices/{noticeId}?utm_source=push&utm_medium=push&utm_campaign={campaignId}&utm_content=notice`다.

<br>

**4. 플랫폼별 구성**

| 플랫폼 | 구성 |
|---|---|
| Android | 데이터만<br>서비스 알림은 높은 우선순위, 광고 알림은 보통<br>유효 기한이 있는 시나리오는 유효 기한까지의 TTL |
| 웹 | 데이터와 함께 제목, 본문, 아이콘, 클릭 링크의 알림 구성<br>스토리 완성은 제목 `스토리가 완성됐어요`, 본문은 스토리 제목<br>그 외는 데이터의 `title`과 `body`<br>클릭 링크는 `deepLink`, 없으면 운영 웹 주소 |

<details>
<summary><b>푸시 데이터 예시</b></summary>

<br>

**1) `ATTENDANCE_REMINDER` 푸시 데이터**

```json
{
  "type": "ATTENDANCE_REMINDER",
  "recipientId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "date": "2026-10-16",
  "title": "(광고) 이프 250이 도착했어요 🍃",
  "body": "출석하고 받아 가세요. 오늘은 어떤 스토리를 시작해 볼까요?\n수신거부: 마이 > 알림 설정",
  "deepLink": "https://manyak.app/my/credits?tab=free&utm_source=push&utm_medium=push&utm_campaign=attendance_reminder&utm_content=attendance_reminder"
}
```

**2) `STORY_TAKEN_DOWN` 푸시 데이터**

```json
{
  "type": "STORY_TAKEN_DOWN",
  "recipientId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "storyId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "title": "스토리 공개가 제한됐어요",
  "body": "「달빛 아래의 약속」은 저작권 침해 사유로 공개할 수 없어요. 내용을 수정해 검수를 통과하면 공개할 수 있어요.",
  "deepLink": "https://manyak.app/studio?utm_source=push&utm_medium=push&utm_campaign=story_taken_down&utm_content=story_taken_down"
}
```

**3) 기타 사유의 `STORY_TAKEN_DOWN` 본문**

입력 사유가 "실존 인물 비방"이고 제목이 받침 없이 끝나는 경우다.

```json
{ "body": "「푸른 바다」는 실존 인물 비방 사유로 공개할 수 없어요. 내용을 수정해 검수를 통과하면 공개할 수 있어요." }
```

**4) `CREDIT_EXPIRY_REMINDER` 푸시 데이터**

```json
{
  "type": "CREDIT_EXPIRY_REMINDER",
  "recipientId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "title": "이프 만료 예정 안내",
  "body": "곧 만료되는 이프가 있어요",
  "deepLink": "https://manyak.app/my/credits?tab=history&utm_source=push&utm_medium=push&utm_campaign=credit_expiry_reminder&utm_content=credit_expiry_reminder"
}
```

</details>

<br>

### 4-2-11 발송 결과 보고

서버가 제공하고 알림 서비스가 메시지 처리를 마친 뒤 호출한다. 로컬 모드 발송기는 같은 내용을 직접 기록한다.

| 항목 | 값 |
|---|---|
| 요청 | `POST /internal/push-deliveries` |
| 인증 | 내부 |
| 성공 | 204, 본문 없음 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `messageId` | `string` | 필수 | 메시지 식별자, 1~255자 |
| `type` | `string` | 필수 | `STORY_COMPLETED`, `STORY_MODERATION_COMPLETED`, `STORY_TAKEN_DOWN`, `NOTICE`, `ATTENDANCE_REMINDER`, `CREDIT_EXPIRY_REMINDER`, `PROMOTION`<br>큐 메시지의 `type` |
| `kind` | `string` | 필수 | `SERVICE`, `MARKETING` |
| `recipientId` | `string` | 필수 | 수신 회원 공개 식별자 |
| `campaignId` | `string` | 선택 | 캠페인 공개 식별자<br>캠페인 발송만 |
| `outcome` | `string` | 필수 | `DELIVERED`, `UNDELIVERED`, `DISCARDED` |
| `reason` | `string` | 필수 | 알림 발송 응답의 `reason` 값, 1~40자 |
| `deliveredDevices` | `integer` | 필수 | 0 이상<br>`DELIVERED`일 때만 1 이상 |
| `failedDevices` | `integer` | 필수 | 0 이상 |
| `completedAt` | `string` | 필수 | 처리 완료 시각 |

- 같은 메시지 식별자의 두 번째 보고는 기록하지 않고 성공으로 응답한다. 저장된 행은 바꾸지 않는다.
- 보고에 실패해도 알림 서비스는 소비를 되돌리지 않는다. `type`에 없는 시나리오를 보고하면 거절되므로 새 시나리오는 이 목록을 함께 확장한다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 필수 필드 누락, 형식 오류, 목록에 없는 `type`, `outcome`과 `deliveredDevices`의 불일치, 없는 캠페인 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /internal/push-deliveries
X-Manyak-Internal-Secret: {sharedSecret}
Content-Type: application/json

{
  "messageId": "credit-expiry:3f2504e0-4f89-41d3-9a0c-0305e82c3301:2026-10-26",
  "type": "CREDIT_EXPIRY_REMINDER",
  "kind": "SERVICE",
  "recipientId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "outcome": "DELIVERED",
  "reason": "OK",
  "deliveredDevices": 1,
  "failedDevices": 0,
  "completedAt": "2026-10-26T01:00:12Z"
}
```

**2) 204 Response**

본문 없음

**3) 400 Response body**

```json
{
  "timestamp": "2026-10-26T01:00:12.345Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "도달 결과와 도달 기기 수가 일치하지 않습니다.",
  "path": "/internal/push-deliveries",
  "details": []
}
```

</details>

<br>

### 4-2-12 문구 템플릿 관리

관리자가 키별 문구 오버라이드를 조회, 변경, 기본값으로 복귀한다. 허용하는 `templateKey`는 `attendance_reminder`, `credit_expiry_reminder`다. 광고 표기는 저장하지 않으며 발송 시 서버가 붙인다.

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/push/templates/{templateKey}`<br>`PUT /admin/push/templates/{templateKey}`<br>`DELETE /admin/push/templates/{templateKey}` |
| 인증 | 관리자 |
| 성공 | 200, 세 요청 모두 같은 응답 |

**1. 본문**

| 요청 | 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|---|
| `PUT` | `title` | `string` | 필수 | 1~100자<br>광고 표기 없이 |
| `PUT` | `body` | `string` | 필수 | 1~300자 |
| `PUT` | `effectiveFrom` | `string` | 선택 | 적용 시작<br>생략하면 현재 시각<br>현재 이전이면 거절 |
| `PUT` | `effectiveUntil` | `string` | 선택 | 적용 종료<br>생략하면 상시 적용<br>시작 이전이면 거절 |
| `PUT` | `reason` | `string` | 필수 | 변경 사유, 1~500자<br>감사 기록에 남음 |
| `DELETE` | `reason` | `string` | 필수 | 복귀 사유, 1~500자 |

- `PUT`은 오버라이드 행을 추가한다. 기존 행을 고치지 않으므로 예약 교체가 가능하다. 같은 시점에 유효한 행이 여럿이면 적용 시작이 가장 늦은 행, 그것도 같으면 나중에 추가된 행을 쓴다.
- `DELETE`는 유효한 행과 예약된 행의 종료 시각을 지금 또는 그 행의 시작 시각으로 당겨 기본 문구로 돌린다. 행을 지우지 않으며 종료할 행이 없어도 성공이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `templateKey` | `string` | |
| `effective` | `object` | 지금 발송하면 쓰는 문구<br>저장소의 현재 행으로 계산하며 발송기는 스냅샷을 읽으므로 갱신 주기 안에 같아짐 |
| `effective.title` | `string` | 광고 표기 없는 제목 |
| `effective.body` | `string` | |
| `effective.isDefault` | `boolean` | 기본 문구인지 여부 |
| `overrides` | `object[]` | 키의 모든 오버라이드 행, 시작 시각 내림차순 |
| `overrides[].title` | `string` | |
| `overrides[].body` | `string` | |
| `overrides[].effectiveFrom` | `string` | |
| `overrides[].effectiveUntil` | `string / null` | `null`은 상시 |
| `overrides[].active` | `boolean` | 지금 유효한지 여부 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 필드 누락, 길이 초과, 시각 형식 오류, 시작이 현재 이전, 종료가 시작 이전 |
| 404 | `NOT_FOUND` | 허용 목록에 없는 `templateKey` |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
PUT /api/v1/admin/push/templates/credit_expiry_reminder
Authorization: Bearer {adminToken}
Content-Type: application/json

{ "title": "이프 만료 예정 안내", "body": "내일이면 사라지는 이프가 있어요", "reason": "문구 다듬기" }
```

**2) 200 Response body**

```json
{
  "templateKey": "credit_expiry_reminder",
  "effective": { "title": "이프 만료 예정 안내", "body": "내일이면 사라지는 이프가 있어요", "isDefault": false },
  "overrides": [
    { "title": "이프 만료 예정 안내", "body": "내일이면 사라지는 이프가 있어요", "effectiveFrom": "2026-10-26T01:00:00Z", "effectiveUntil": null, "active": true }
  ]
}
```

**3) 404 Response body**

```json
{
  "timestamp": "2026-10-26T01:00:12.345Z",
  "status": 404,
  "code": "NOT_FOUND",
  "message": "문구 템플릿이 없습니다.",
  "path": "/api/v1/admin/push/templates/unknown_key",
  "details": []
}
```

</details>

<br>

### 4-2-13 캠페인 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/push/campaigns` |
| 인증 | 관리자 |
| 성공 | 200<br>페이지 구조의 캠페인 구조 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `q` | `string` | 선택 | 제목과 본문 부분 일치<br>캠페인 공개 식별자 정확 일치<br>규칙은 관리자 목록 공통의 검색어 규칙 |
| `status` | `string` | 선택 | 캠페인 상태 값 중 하나<br>생략하면 전체 |
| `kind` | `string` | 선택 | 알림 성격<br>`SERVICE`, `MARKETING`<br>생략하면 전체 |
| `sort` | `string` | 선택 | `createdAt`, `scheduledAt`, `title`, `kind`, `status`, `targetCount`, `sentCount`, `deliveredMembers`, `deliveredDevices`, `failedDevices`<br>기본 `createdAt` |
| 페이지 쿼리 | | 선택 | 공통 페이지 쿼리 |

- 프로모션과 공지 알림을 함께 보여 준다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 지원하지 않는 `status`와 `kind`<br>검색어와 공통 페이지 쿼리 오류 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/push/campaigns?status=SCHEDULED&size=1
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "items": [
    {
      "campaignId": "6f1d2c3b-4a5e-4f60-9b7c-8d9e0f1a2b3c",
      "kind": "MARKETING",
      "title": "주말 한정 이프 2배 이벤트",
      "body": "이번 주말 충전하면 이프를 두 배로 드려요.",
      "scheduledAt": "2026-10-24T01:00:00Z",
      "status": "SCHEDULED",
      "noticeId": null,
      "storyId": null,
      "targetCount": null,
      "sentCount": null,
      "deliveredMembers": 0,
      "deliveredDevices": 0,
      "failedDevices": 0,
      "startedAt": null,
      "finishedAt": null,
      "createdAt": "2026-10-21T03:00:00Z"
    }
  ],
  "page": 1,
  "size": 1,
  "totalElements": 1,
  "totalPages": 1
}
```

</details>

<br>

### 4-2-14 캠페인 예약

| 항목 | 값 |
|---|---|
| 요청 | `POST /admin/push/campaigns` |
| 인증 | 관리자 |
| 성공 | 201<br>캠페인 구조 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `title` | `string` | 필수 | 1~100자<br>광고 표기 없이 |
| `body` | `string` | 필수 | 1~300자 |
| `scheduledAt` | `string` | 선택 | 예약 시각<br>생략하면 현재 시각으로 즉시 발송 |
| `storyId` | `string` | 선택 | 알림을 누르면 열 스토리의 공개 식별자<br>발행 상태이고 공개이며 삭제되지 않은 스토리만 |
| `reason` | `string` | 필수 | 사유<br>1~500자 |

- 알림 성격은 항상 `MARKETING`이다. 공지 알림 캠페인은 공지 게시가 만든다.
- `storyId`가 있으면 푸시 데이터의 딥링크는 `/stories/{storyId}`다.
- 확정 전에 대상 수 미리보기로 대상 규모를 확인한다. ([4-2-17 대상 수 미리보기](#4-2-17-대상-수-미리보기))

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 필드 누락, 길이 초과, 과거 시각, 시각 형식 오류<br>`storyId`가 UUID 형식이 아니거나 공개 스토리가 아님 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/admin/push/campaigns
Authorization: Bearer {adminToken}
Content-Type: application/json

{
  "title": "주말 한정 이프 2배 이벤트",
  "body": "이번 주말 충전하면 이프를 두 배로 드려요.",
  "scheduledAt": "2026-10-24T01:00:00Z",
  "reason": "주말 프로모션"
}
```

**2) 201 Response body**

캠페인 목록의 항목과 같다.

**3) 400 Response body**

```json
{
  "timestamp": "2026-10-21T03:00:00.000Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "예약 시각은 현재 이후여야 합니다.",
  "path": "/api/v1/admin/push/campaigns",
  "details": []
}
```

</details>

<br>

### 4-2-15 캠페인 취소

| 항목 | 값 |
|---|---|
| 요청 | `POST /admin/push/campaigns/{campaignId}/cancel` |
| 인증 | 관리자 |
| 성공 | 200<br>캠페인 구조 |

**1. 경로와 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `campaignId` | 경로 | 필수 | 캠페인 공개 식별자 |
| `reason` | `string` | 필수 | 사유<br>1~500자 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `reason` 누락 또는 `campaignId` 형식 오류 |
| 404 | `NOT_FOUND` | 없는 캠페인 |
| 409 | `CONFLICT` | 예약 상태가 아님<br>이미 선점됐거나 끝났거나 취소됨 |

<br>

### 4-2-16 캠페인 재실행

| 항목 | 값 |
|---|---|
| 요청 | `POST /admin/push/campaigns/{campaignId}/retry` |
| 인증 | 관리자 |
| 성공 | 200<br>캠페인 구조 |

**1. 경로와 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `campaignId` | 경로 | 필수 | 캠페인 공개 식별자 |
| `reason` | `string` | 필수 | 사유<br>1~500자 |

- 예약 상태로 돌아가 다음 폴링에서 다시 실행된다. 원격 모드에서는 이미 기록된 회원의 요청이 중복 기록되지 않는다. 로컬 모드에는 회원별 기록이 없어 이미 받은 회원에게 다시 갈 수 있다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `reason` 누락 또는 `campaignId` 형식 오류 |
| 404 | `NOT_FOUND` | 없는 캠페인 |
| 409 | `CONFLICT` | 실패 상태가 아님 |

<br>

### 4-2-17 대상 수 미리보기

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/push/campaigns/target-count` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `kind` | `string` | 필수 | `SERVICE`와 `MARKETING` |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `kind` | `string` | 요청한 알림 성격 |
| `targetCount` | `integer` | 현재 조건으로 대상이 되는 회원 수 |
| `nightEligibleCount` | `integer / null` | 알림 성격이 `MARKETING`일 때 야간 광고 알림 동의까지 있는 회원 수<br>`SERVICE`면 `null` |
| `nightNow` | `boolean` | 현재 시각이 KST 야간이면 `true` |
| `asOf` | `string` | 집계 시각 |

- 실제 발송 대상은 회차가 다시 조회하므로 미리보기와 다를 수 있다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `kind` 누락이나 지원하지 않는 값 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/push/campaigns/target-count?kind=MARKETING
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{ "kind": "MARKETING", "targetCount": 412, "nightEligibleCount": 180, "nightNow": false, "asOf": "2026-10-21T03:00:00Z" }
```

</details>

<br>

### 4-2-18 캠페인 상세

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/push/campaigns/{campaignId}` |
| 인증 | 관리자 |
| 성공 | 200<br>캠페인 구조 |

**1. 경로**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `campaignId` | 경로 | 필수 | 캠페인 공개 식별자 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `campaignId` 형식 오류 |
| 404 | `NOT_FOUND` | 없는 캠페인 |

<br>

### 4-2-19 알림 통계

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/push/delivery-stats` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from` | `string` | 선택 | 시작 KST 날짜 `YYYY-MM-DD`<br>생략하면 `to`의 6일 전 |
| `to` | `string` | 선택 | 끝 KST 날짜 `YYYY-MM-DD`<br>생략하면 오늘 |
| `type` | `string` | 선택 | 큐 메시지의 `type` 값 중 하나<br>생략하면 전체 |
| `kind` | `string` | 선택 | 알림 성격<br>`SERVICE`, `MARKETING`<br>생략하면 전체<br>알림 종류 `type`과 함께 지정하면 둘 다 만족하는 행 |

- 시작과 끝을 포함한 기간은 최대 366일이다. 기간을 바꿔 가며 조회하고 주 단위나 월 단위 합계는 관리자 페이지가 날짜 행을 더해 만든다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `from` | `string` | 적용된 시작 날짜 |
| `to` | `string` | 적용된 끝 날짜 |
| `items` | `object[]` | 날짜 내림차순이며 같은 날은 `type` 오름차순<br>결과 행이 없는 날과 시나리오는 없음 |
| `items[].date` | `string` | 완료 시각의 KST 날짜 |
| `items[].type` | `string` | 시나리오 식별자 |
| `items[].kind` | `string` | 알림 성격<br>`SERVICE`와 `MARKETING` |
| `items[].requested` | `integer` | 처리가 끝난 메시지 수 |
| `items[].deliveredMembers` | `integer` | 도달 메시지 수(건)<br>도달 기기가 하나 이상인 메시지 수이며 고유 회원 수가 아님 |
| `items[].deliveredDevices` | `integer` | 도달 기기 수의 합 |
| `items[].failedDevices` | `integer` | 실패 기기 수의 합 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 날짜 형식 오류, `from`이 `to`보다 늦음, 366일 초과, 지원하지 않는 `type`과 `kind` |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/push/delivery-stats?from=2026-10-20&to=2026-10-21
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "from": "2026-10-20",
  "to": "2026-10-21",
  "items": [
    { "date": "2026-10-21", "type": "ATTENDANCE_REMINDER", "kind": "MARKETING", "requested": 412, "deliveredMembers": 380, "deliveredDevices": 455, "failedDevices": 9 },
    { "date": "2026-10-21", "type": "STORY_COMPLETED", "kind": "SERVICE", "requested": 64, "deliveredMembers": 61, "deliveredDevices": 70, "failedDevices": 2 },
    { "date": "2026-10-20", "type": "NOTICE", "kind": "SERVICE", "requested": 1180, "deliveredMembers": 1102, "deliveredDevices": 1301, "failedDevices": 15 }
  ]
}
```

**3) 400 Response body**

```json
{
  "timestamp": "2026-10-21T03:00:00.000Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "통계 기간은 최대 366일입니다.",
  "path": "/api/v1/admin/push/delivery-stats",
  "details": []
}
```

</details>

<br>

### 4-2-20 알림 내역 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /users/me/notifications` |
| 인증 | 필수 |
| 성공 | 200 |

**1. 쿼리**

| 쿼리 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `category` | `string` | 선택 | `NEWS` 또는 `ACTIVITY`<br>생략하면 전체 |
| `limit` | `integer` | 선택 | 기본값 20, 1~50으로 보정 |
| `cursor` | `string` | 선택 | 이전 응답의 `nextCursor`<br>같은 `category`를 함께 보냄 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items` | `object[]` | 알림 내역<br>생성 시각 내림차순 |
| `nextCursor` | `string / null` | 다음 페이지 커서<br>마지막 페이지는 `null` |

| `items[]` 필드명 | 타입 | 의미 |
|---|---|---|
| `notificationId` | `string` | 알림 식별자 |
| `category` | `string` | `NEWS`, `ACTIVITY` |
| `type` | `string` | `STORY_COMPLETED`, `STORY_MODERATION_COMPLETED`, `STORY_TAKEN_DOWN`, `NOTICE`, `ATTENDANCE_REMINDER`, `CREDIT_EXPIRY_REMINDER`, `PROMOTION`<br>모르는 값은 클라이언트가 기본 표시로 처리 |
| `title` | `string` | 표시 제목<br>광고 알림도 광고 표기 없는 원문 |
| `body` | `string` | 표시 본문 |
| `deepLink` | `string / null` | 눌렀을 때 열 절대 URL<br>딥링크가 없는 프로모션은 `null` |
| `storyId` | `string / null` | 관련 스토리 공개 식별자 |
| `noticeId` | `string / null` | 관련 공지 공개 식별자 |
| `noticeTag` | `string / null` | 공지 알림이면 공지 태그<br>`SERVICE`, `UPDATE`, `MAINTENANCE`, `EVENT`, `PROMOTION`<br>그 외 `null` |
| `createdAt` | `string` | 기록 시각 |
| `readAt` | `string / null` | 읽은 시각<br>`null`이면 안 읽음 |

- 종류와 분류의 대응은 처리 흐름이 정한다. ([4-1-19 알림 내역 기록](4-1-PIPELINES.md#4-1-19-알림-내역-기록))
- 보관 기간이 없어 커서로 가장 오래된 내역까지 내려 볼 수 있다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 모르는 `category`, `limit`이 숫자가 아님<br>UUID가 아닌 커서, 없거나 다른 회원의 알림 식별자인 커서 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/users/me/notifications?category=ACTIVITY&limit=2
Authorization: Bearer {accessToken}
```

**2) 200 Response body**

```json
{
  "items": [
    {
      "notificationId": "5d8e2f10-6b3a-4c1e-9f7a-2a1b3c4d5e6f",
      "category": "ACTIVITY",
      "type": "STORY_MODERATION_COMPLETED",
      "title": "검수를 통과했어요",
      "body": "「달빛 아래의 약속」의 등록이 완료됐어요. 지금 확인해 보세요.",
      "deepLink": "https://manyak.app/studio?utm_source=inbox&utm_medium=inbox&utm_campaign=story_moderation_completed&utm_content=story_moderation_completed",
      "storyId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "noticeId": null,
      "noticeTag": null,
      "createdAt": "2026-10-24T09:12:30Z",
      "readAt": null
    },
    {
      "notificationId": "0a7c4e21-93d5-4b8f-a6e2-71c0d9b8f3a4",
      "category": "ACTIVITY",
      "type": "ATTENDANCE_REMINDER",
      "title": "이프 250이 도착했어요 🍃",
      "body": "출석하고 받아 가세요. 오늘은 어떤 스토리를 시작해 볼까요?",
      "deepLink": "https://manyak.app/my/credits?tab=free&utm_source=inbox&utm_medium=inbox&utm_campaign=attendance_reminder&utm_content=attendance_reminder",
      "storyId": null,
      "noticeId": null,
      "noticeTag": null,
      "createdAt": "2026-10-24T00:00:05Z",
      "readAt": "2026-10-24T01:03:11Z"
    }
  ],
  "nextCursor": "0a7c4e21-93d5-4b8f-a6e2-71c0d9b8f3a4"
}
```

**3) 400 Response body**

다른 회원의 알림 식별자를 커서로 보낸 경우다.

```json
{
  "timestamp": "2026-10-24T09:20:00.000Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "커서 형식이 올바르지 않습니다.",
  "path": "/api/v1/users/me/notifications",
  "details": []
}
```

</details>

<br>

### 4-2-21 안 읽은 알림 수

| 항목 | 값 |
|---|---|
| 요청 | `GET /users/me/notifications/unread-count` |
| 인증 | 필수 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `total` | `integer` | 안 읽은 내역 전체 수 |
| `news` | `integer` | `NEWS` 분류의 안 읽은 수 |
| `activity` | `integer` | `ACTIVITY` 분류의 안 읽은 수 |

- `total`은 분류별 수의 합이다. 상한 없이 실제 수를 준다. 표시 상한은 클라이언트가 정한다.

<br>

**2. 실패 응답**

공통 실패만 있다.

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/users/me/notifications/unread-count
Authorization: Bearer {accessToken}
```

**2) 200 Response body**

```json
{ "total": 3, "news": 1, "activity": 2 }
```

</details>

<br>

### 4-2-22 알림 읽음

| 항목 | 값 |
|---|---|
| 요청 | `POST /users/me/notifications/{notificationId}/read` |
| 인증 | 필수 |
| 성공 | 204, 본문 없음 |

**1. 경로**

| 경로값 | 타입 | 의미 |
|---|---|---|
| `notificationId` | `string` | 알림 식별자 |

- 이미 읽은 알림도 204이며 처음 읽은 시각을 유지한다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | UUID가 아닌 식별자 |
| 404 | `NOT_FOUND` | 없거나 다른 회원의 알림<br>두 경우를 구분하지 않음 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/users/me/notifications/5d8e2f10-6b3a-4c1e-9f7a-2a1b3c4d5e6f/read
Authorization: Bearer {accessToken}
```

**2) 204 Response**

본문 없음

**3) 404 Response body**

```json
{
  "timestamp": "2026-10-24T09:21:00.000Z",
  "status": 404,
  "code": "NOT_FOUND",
  "message": "알림을 찾을 수 없습니다.",
  "path": "/api/v1/users/me/notifications/5d8e2f10-6b3a-4c1e-9f7a-2a1b3c4d5e6f/read",
  "details": []
}
```

</details>

<br>

### 4-2-23 모든 알림 읽음

| 항목 | 값 |
|---|---|
| 요청 | `POST /users/me/notifications/read-all` |
| 인증 | 필수 |
| 성공 | 204, 본문 없음 |

**1. 쿼리**

| 쿼리 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `category` | `string` | 선택 | `NEWS` 또는 `ACTIVITY`<br>생략하면 전체 |

- 요청 시점에 안 읽은 내역을 읽음으로 바꾼다. 이미 읽은 내역의 시각은 바꾸지 않는다.
- 안 읽은 내역이 없어도 204다. 반복해도 결과가 같다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 모르는 `category` |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/users/me/notifications/read-all?category=NEWS
Authorization: Bearer {accessToken}
```

**2) 204 Response**

본문 없음

</details>

<br>

### 4-2-24 다른 도메인과의 경계

| 도메인 | NOTIFICATION이 제공하는 것 | NOTIFICATION이 사용하는 것 |
|---|---|---|
| STORY | 완성 이벤트의 발송 경로 | 완성 요청 행의 완료 기록 트랜잭션, 완성 이벤트, 캠페인 이동 대상 스토리의 공개 판정 |
| MODERATION | 검수 완료 이벤트의 발송 경로와 결과별 문구<br>공개 중단 이벤트의 알림 내역 기록, 발송 경로와 문구 | 제출본 종료 기록 트랜잭션, 검수 완료 이벤트<br>공개 중단 트랜잭션, 공개 중단 이벤트 |
| NOTICE | 공지 발송 요청 연산 | 공지 공개 식별자 |
| ACCOUNT | 회원의 토큰 전부 삭제 연산<br>회원의 알림 내역 전부 삭제 연산 | 계정 상태, 공개 식별자, 보상 신원, 사용자 행 잠금 |
| PAYMENT | 없음 | 출석 보상 멱등 키의 존재, 만료 창 안에 잔여 있는 로트를 가진 회원 조회 |
| ADMIN | 캠페인과 문구 템플릿 관리<br>기간의 캠페인 도달 요약 연산<br>종류별 날짜별 도달 회원 수 연산 | 관리자 권한 판정과 요청자, 변경 감사 기록 |
| 모든 도메인 | 없음 | 인증 필터, 탈퇴 거부, 동의 게이트, 관리자 판정 필터 |

다른 도메인이 호출하거나 발행하는 연산의 입력과 결과는 다음과 같다.

| 연산 | 입력 | 결과 |
|---|---|---|
| 완성 이벤트 발행 | 회원 내부 ID, 완성 요청 ID, 스토리 공개 식별자, 제목 | 원격 모드는 아웃박스 행, 로컬 모드는 커밋 후 발송 |
| 검수 완료 이벤트 발행 | 회원 내부 ID, 제출본 식별자, 스토리 공개 식별자, 결과, 회차, 제목 | 원격 모드는 아웃박스 행, 로컬 모드는 커밋 후 발송 |
| 공개 중단 이벤트 발행 | 회원 내부 ID, 스토리 공개 식별자, 이름 토큰을 치환한 제목, 사유 분류, 기타의 입력 사유, 공개 중단 시각 | 알림 내역 행<br>원격 모드는 아웃박스 행, 로컬 모드는 커밋 후 발송<br>호출자의 트랜잭션에 참여 |
| 공지 발송 요청 | 공지 공개 식별자, 알림 제목 100자 이내, 알림 본문 300자 이내, 종류, 공지 태그, 딥링크 | 예약 시각이 현재인 캠페인 1건<br>호출자의 트랜잭션에 참여하고 같은 공지의 두 번째 요청은 유니크 위반 |
| 회원 토큰 전부 삭제 | 회원 내부 ID | 삭제 행 수 |
| 기간의 캠페인 도달 요약 | KST 날짜 범위 | 마지막 회차의 선점 시각이 범위 안인 캠페인마다 공개 식별자, 종류, 제목, 공지 공개 식별자, 선점 시각, 딥링크 포함 여부(`null` 가능), 도달 회원 수<br>도달 회원 수는 캠페인 구조의 `deliveredMembers`와 같은 집계 |
| 종류별 날짜별 도달 회원 수 | KST 날짜 범위, 시나리오 목록 | 시나리오와 KST 날짜마다 도달 기기가 하나 이상인 발송 결과의 회원을 중복 없이 센 수<br>날짜는 처리가 끝난 시각 기준이며 회원 참조가 없는 행은 세지 않음 |
| 회원 알림 내역 전부 삭제 | 회원 내부 ID | 삭제 행 수<br>탈퇴 트랜잭션에 참여 |

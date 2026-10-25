# 4-2 계약

이 문서는 NOTIFICATION 도메인의 클라이언트 API, 서버와 알림 서비스 사이의 내부 API, 운영자의 문구 템플릿 API, 큐 메시지, 기기에 도착하는 푸시 데이터, 다른 도메인과의 경계를 정한다.

처리 순서와 판정 규칙은 처리 흐름에, 앱 코드 전체 목록과 복구는 오류 처리에, 비밀값 취급은 보안에 있다. ([4-1 처리 흐름](4-1-PIPELINES.md), [5-3-2 앱 코드](5-3-ERROR-HANDLING.md#5-3-2-앱-코드), [5-1-7 비밀값과 개인정보](5-1-SECURITY.md#5-1-7-비밀값과-개인정보))

<br>

### 4-2-1 공통 규칙과 헤더

**1. 공통 규칙**

| 항목 | 규칙 |
|---|---|
| 경로 | 회원 API는 `/api/v1`을 생략해 적음<br>내부 API는 전체 경로 |
| JSON 필드 이름 | camelCase |
| 시각 | ISO 8601 UTC 문자열 |
| 식별자 | 회원과 캠페인은 UUID 공개 식별자<br>토큰 행 ID는 노출하지 않음 |
| 푸시 데이터 값 | 모두 문자열 |
| 예시 값 | 모든 예시는 구조를 설명하기 위한 가상 값 |

<br>

**2. 인증 수준**

| 수준 | 토큰 없음 또는 무효 | 유효한 토큰 |
|---|---|---|
| `필수` | 거절 | 회원으로 처리 |
| `내부` | 토큰을 읽지 않음 | 토큰을 읽지 않음<br>공유 시크릿 헤더로 인증 |
| `관리자` | 거절 | 관리자 권한이 있는 회원으로 처리<br>권한이 없으면 403 |

<br>

**3. 요청 헤더**

| 요청 헤더 | 값 형식 | 쓰임 | 필수 |
|---|---|---|---|
| `Authorization` | `Bearer {accessToken}` | 회원 식별 | 인증 수준에 따름 |
| `X-Manyak-Request-Id` | 문자열 | 로그 연결<br>없으면 생성하고 응답 헤더로 반환 | 선택 |
| `X-Manyak-Session-Id` | 문자열 | 클라이언트 분석 세션 식별 | 선택 |
| `X-Manyak-Internal-Secret` | 문자열 | 서버와 알림 서비스 사이의 인증 | 내부 API는 필수 |
| `X-Manyak-Device-Id-Hash` | 문자열 | 알림 서비스가 서버에 전달하는 기기 해시 | 선택 |

<br>

**4. 계정 상태 규칙**

| 요청 | 정지 계정 | 탈퇴 계정 |
|---|---|---|
| 토큰 등록, 토큰 삭제, 수신 동의 조회, 수신 동의 변경 | 403 | 401 |

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
| 401 | `UNAUTHORIZED` | 인증 필수 경로의 토큰 누락, 만료, 위조, 주체 형식 오류, 사용자 없음<br>확인된 탈퇴 계정<br>내부 API의 시크릿 누락 또는 불일치 |
| 403 | `FORBIDDEN` | 계정 상태 규칙 표의 403<br>관리자 경로의 권한 없는 회원 |
| 403 | `CONSENT_REQUIRED` | 동의 게이트가 켜진 환경에서 미동의 회원의 허용 목록 밖 요청 |
| 404 | `NOT_FOUND` | 내부 API의 시크릿 미설정 환경 |
| 500 | `INTERNAL_SERVER_ERROR` | 예상하지 못한 오류 |

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
    "deepLink": "https://manyak.app/stories/7c9e6679-7425-40de-944b-e07fc1f90ae7"
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
| `type` | `string` | 필수 | `STORY_COMPLETED`, `STORY_MODERATION_COMPLETED`, `ATTENDANCE_REMINDER`, `CREDIT_EXPIRY_REMINDER`, `PROMOTION`<br>`data.type`과 같아야 함 |
| `data` | `object` | 필수 | 푸시 데이터<br>동의와 토큰을 담지 않음 |
| `expiresAt` | `string` | 선택 | 발송 가능 기한<br>출석 리마인드는 당일 KST 자정<br>이프 만료 예정 알림은 회원의 창 안 로트 중 가장 늦은 만료 시각<br>생략하면 만료 없음 |
| `requestId` | `string` | 필수 | 발행 원인의 요청 ID<br>없으면 `unknown` |
| `sessionId` | `string` | 필수 | 발행 원인의 세션 ID<br>없으면 `unknown` |
| `schemaVersion` | `integer` | 필수 | `1` |

| `type` | `kind` | `messageId` |
|---|---|---|
| `STORY_COMPLETED` | `SERVICE` | `story-completed:{완성 요청 ID}` |
| `STORY_MODERATION_COMPLETED` | `SERVICE` | `story-moderation:{제출본 ID}:{회차}` |
| `ATTENDANCE_REMINDER` | `MARKETING` | `attendance:{회원 공개 식별자}:{KST 날짜}` |
| `CREDIT_EXPIRY_REMINDER` | `SERVICE` | `credit-expiry:{회원 공개 식별자}:{KST 날짜}` |
| `PROMOTION` | `MARKETING` | `promotion:{캠페인 공개 식별자}:{회원 공개 식별자}` |

- 추적 헤더 `traceparent`, `tracestate`는 본문이 아니라 메시지 큐의 메시지 속성에 싣는다.
- 출석 리마인드, 이프 만료 예정 알림, 프로모션은 스케줄러가 회원마다 메시지를 기록한다. `requestId`와 `sessionId`는 `unknown`이다.

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
    "deepLink": "https://manyak.app/stories/7c9e6679-7425-40de-944b-e07fc1f90ae7"
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
| `deepLink` | `string` | 알림을 눌렀을 때 열 절대 URL<br>운영 웹 주소에 경로를 붙임<br>없는 시나리오도 있음 |

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
| `ATTENDANCE_REMINDER` | `date` | `string` | KST 날짜 |
| `ATTENDANCE_REMINDER` | `title` | `string` | 광고 표기가 붙은 템플릿 제목 |
| `ATTENDANCE_REMINDER` | `body` | `string` | 템플릿 본문 |
| `ATTENDANCE_REMINDER` | `deepLink` | `string` | `/my/credits?tab=free` |
| `CREDIT_EXPIRY_REMINDER` | `title` | `string` | 템플릿 제목<br>광고 표기 없음 |
| `CREDIT_EXPIRY_REMINDER` | `body` | `string` | 템플릿 본문 |
| `CREDIT_EXPIRY_REMINDER` | `deepLink` | `string` | `/my/credits?tab=free` |
| `PROMOTION` | `campaignId` | `string` | 캠페인 공개 식별자 |
| `PROMOTION` | `title` | `string` | 광고 표기가 붙은 제목 |
| `PROMOTION` | `body` | `string` | 본문 |

| `status` | `title` | `body` |
|---|---|---|
| `APPROVED` | 검수를 통과했어요 | 「{스토리 제목}」의 등록이 완료됐어요. 지금 확인해 보세요. |
| `REJECTED` | 검수에서 반려됐어요 | 「{스토리 제목}」의 내용을 수정해 다시 제출해 주세요. |
| `FAILED` | 검수를 진행하지 못했어요 | 「{스토리 제목}」의 검수 중 문제가 생겼어요. 잠시 후 다시 제출해 주세요. |

- `CREDIT_EXPIRY_REMINDER`에는 금액, 수량, 만료 시각 필드가 없다. 회원이 이프 화면에서 확인한다. 알림 내역의 제목, 본문, 딥링크도 이 데이터와 같다.

<br>

**3. 플랫폼별 구성**

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
  "body": "출석하고 받아 가세요. 오늘은 어떤 스토리를 시작해 볼까요?",
  "deepLink": "https://manyak.app/my/credits?tab=free"
}
```

**2) `CREDIT_EXPIRY_REMINDER` 푸시 데이터**

```json
{
  "type": "CREDIT_EXPIRY_REMINDER",
  "recipientId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "title": "이프 만료 예정 안내",
  "body": "곧 만료되는 이프가 있어요",
  "deepLink": "https://manyak.app/my/credits?tab=free"
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
| `type` | `string` | 필수 | `STORY_COMPLETED`, `STORY_MODERATION_COMPLETED`, `NOTICE`, `ATTENDANCE_REMINDER`, `CREDIT_EXPIRY_REMINDER`, `PROMOTION` |
| `kind` | `string` | 필수 | `SERVICE`, `MARKETING` |
| `recipientId` | `string` | 필수 | 수신 회원 공개 식별자 |
| `campaignId` | `string` | 선택 | 캠페인 공개 식별자<br>캠페인 발송만 |
| `outcome` | `string` | 필수 | `DELIVERED`, `UNDELIVERED`, `DISCARDED` |
| `reason` | `string` | 필수 | 알림 발송 응답의 `reason` 값, 1~40자 |
| `deliveredDevices` | `integer` | 필수 | 0 이상<br>`DELIVERED`일 때만 1 이상 |
| `failedDevices` | `integer` | 필수 | 0 이상 |
| `completedAt` | `string` | 필수 | 처리 완료 시각 |

- 같은 메시지 식별자의 두 번째 보고는 기록하지 않고 성공으로 응답한다.
- 보고에 실패해도 알림 서비스는 소비를 되돌리지 않는다. `type`에 없는 시나리오를 보고하면 거절되므로 새 시나리오는 이 목록을 함께 확장한다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 필수 필드 누락, 목록에 없는 `type`, `outcome`과 `deliveredDevices`의 불일치, 없는 캠페인 |

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

운영자가 키별 문구 오버라이드를 조회, 변경, 기본값으로 복귀한다. 허용하는 `templateKey`는 `attendance_reminder`, `credit_expiry_reminder`다. 광고 표기는 저장하지 않으며 발송 시 서버가 붙인다.

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/push/templates/{templateKey}`<br>`PUT /admin/push/templates/{templateKey}`<br>`DELETE /admin/push/templates/{templateKey}` |
| 인증 | 관리자 |
| 성공 | 200, 세 요청 모두 같은 응답 |

**1. 본문**

| 요청 | 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|---|
| `PUT` | `title` | `string` | 필수 | 1~100자 |
| `PUT` | `body` | `string` | 필수 | 1~300자 |
| `PUT` | `effectiveFrom` | `string` | 선택 | 적용 시작<br>생략하면 현재 시각<br>현재 이전이면 거절 |
| `PUT` | `effectiveUntil` | `string` | 선택 | 적용 종료<br>생략하면 상시 적용<br>시작 이전이면 거절 |
| `PUT` | `reason` | `string` | 필수 | 변경 사유, 1~500자<br>감사 기록에 남음 |
| `DELETE` | `reason` | `string` | 필수 | 복귀 사유, 1~500자 |

- `PUT`은 오버라이드 행을 추가한다. 기존 행을 고치지 않으므로 예약 교체가 가능하다.
- `DELETE`는 유효한 행과 예약된 행의 종료 시각을 지금 또는 그 행의 시작 시각으로 당겨 기본 문구로 돌린다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `templateKey` | `string` | |
| `effective` | `object` | 지금 발송하면 쓰는 문구 |
| `effective.title` | `string` | |
| `effective.body` | `string` | |
| `effective.isDefault` | `boolean` | 기본 문구인지 여부 |
| `overrides` | `object[]` | 키의 모든 오버라이드 행, 시작 시각 내림차순 |
| `overrides[].title` | `string` | |
| `overrides[].body` | `string` | |
| `overrides[].effectiveFrom` | `string` | |
| `overrides[].effectiveUntil` | `string / null` | |
| `overrides[].active` | `boolean` | 지금 유효한지 여부 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 필드 누락, 길이 초과, 시작이 현재 이전, 종료가 시작 이전 |
| 404 | `NOT_FOUND` | 허용 목록에 없는 `templateKey` |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
PUT /api/v1/admin/push/templates/credit_expiry_reminder
Authorization: Bearer {accessToken}
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

### 4-2-13 다른 도메인과의 경계

| 도메인 | NOTIFICATION이 제공하는 것 | NOTIFICATION이 사용하는 것 |
|---|---|---|
| STORY | 완성 이벤트의 발송 경로 | 완성 요청 행의 완료 기록 트랜잭션, 완성 이벤트 |
| MODERATION | 검수 완료 이벤트의 발송 경로와 결과별 문구 | 제출본 종료 기록 트랜잭션, 검수 완료 이벤트 |
| ACCOUNT | 회원의 토큰 전부 삭제 연산 | 계정 상태, 공개 식별자, 보상 신원, 사용자 행 잠금 |
| PAYMENT | 없음 | 출석 보상 멱등 키의 존재, 만료 창 안에 잔여 있는 로트를 가진 회원 조회 |
| ADMIN | 문구 템플릿 관리 | 관리자 권한 판정, 변경 감사 기록 |
| 모든 도메인 | 없음 | 인증 필터, 탈퇴 거부, 동의 게이트 |

다른 도메인이 호출하거나 발행하는 연산의 입력과 결과는 다음과 같다.

| 연산 | 입력 | 결과 |
|---|---|---|
| 완성 이벤트 발행 | 회원 내부 ID, 완성 요청 ID, 스토리 공개 식별자, 제목 | 원격 모드는 아웃박스 행, 로컬 모드는 커밋 후 발송 |
| 검수 완료 이벤트 발행 | 회원 내부 ID, 제출본 식별자, 스토리 공개 식별자, 결과, 회차, 제목 | 원격 모드는 아웃박스 행, 로컬 모드는 커밋 후 발송 |
| 회원 토큰 전부 삭제 | 회원 내부 ID | 삭제 행 수 |

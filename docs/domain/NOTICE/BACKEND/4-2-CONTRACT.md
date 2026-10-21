# 4-2 계약

이 문서는 NOTICE 도메인 백엔드와 클라이언트, 관리자 페이지, 다른 도메인 사이의 계약을 정한다. 엔드포인트별 요청 필드, 성공과 실패 응답의 필드와 예시, 도메인 경계를 다룬다.

처리 순서와 판정 규칙은 처리 흐름에, 앱 코드 전체 목록과 복구는 오류 처리에, 관리자 인증 수준과 토큰은 관리자 계약에 있다. ([4-1 처리 흐름](4-1-PIPELINES.md), [5-3-2 앱 코드](5-3-ERROR-HANDLING.md#5-3-2-앱-코드), [ADMIN 4-2-1 공통 규칙과 헤더](../../ADMIN/BACKEND/4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더))

<br>

### 4-2-1 공통 규칙과 헤더

**1. 공통 규칙**

| 항목 | 규칙 |
|---|---|
| 경로 | `/api/v1`을 생략해 적음 |
| JSON 필드 이름 | camelCase |
| 시각 | ISO 8601 UTC 문자열 |
| 식별자 | 공지와 회원은 UUID 공개 식별자 |
| 상태와 유형 | 대문자 enum 문자열 |
| 본문 | 줄바꿈이 있는 평문 |
| 예시 값 | 모든 예시는 구조를 설명하기 위한 가상 값 |

<br>

**2. 인증 수준**

| 수준 | 토큰 없음 또는 무효 | 앱 접근 토큰 | 관리자 토큰 |
|---|---|---|---|
| `불필요` | 처리 | 처리<br>토큰을 읽지 않음 | 처리<br>토큰을 읽지 않음 |
| `관리자` | 거절 | 거절 | 관리자 역할과 계정 상태를 다시 확인해 통과 |

<br>

**3. 요청 헤더**

| 요청 헤더 | 값 형식 | 쓰임 | 필수 |
|---|---|---|---|
| `Authorization` | `Bearer {adminToken}` | 관리자 식별 | 관리자 경로는 필수 |
| `X-Manyak-Request-Id` | 문자열 | 로그 연결<br>없으면 서버가 생성하고 응답 헤더로 항상 반환 | 선택 |
| `X-Manyak-Session-Id` | 문자열 | 클라이언트 분석 세션 식별 | 선택 |

<br>

**4. 계정 상태 규칙**

공개 조회는 토큰을 읽지 않아 계정 상태를 판정하지 않는다. 관리자 경로는 관리자의 정지와 탈퇴를 거절한다.

<br>

**5. 공통 실패 응답**

실패 응답은 모두 같은 형식이다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `timestamp` | `string` | 응답 생성 시각 |
| `status` | `integer` | HTTP 상태 |
| `code` | `string` | HTTP 상태 이름 또는 앱 코드 |
| `message` | `string` | 안내 문구 |
| `path` | `string` | 요청 경로 |
| `details` | `object[]` | 선언적 필드 검증, 쿼리와 경로 변수의 타입 변환 실패 시 `field`와 `message` 포함<br>그 외는 빈 배열 |

| `details[].field` 규칙 | 값 |
|---|---|
| 필드 검증 | 필드명 |
| 본문 파싱 실패 | 빈 `details` |

각 절의 실패 표에는 해당 엔드포인트에서 발생하는 상태와 `code`를 적는다. 다음 공통 실패는 각 절에서 생략한다.

| 상태 | `code` | 조건 |
|---|---|---|
| 401 | `UNAUTHORIZED` | 관리자 경로의 토큰 누락, 만료, 위조, 관리자 표식 없음 |
| 403 | `FORBIDDEN` | 관리자 역할 없음, 정지, 탈퇴 |
| 500 | `INTERNAL_SERVER_ERROR` | 예상하지 못한 오류 |

<br>

**6. 공통 응답 구조**

관리자 목록 항목, 관리자 상세, 작성과 수정과 게시와 게시 해제의 응답은 같은 관리자 공지 구조를 쓴다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `noticeId` | `string` | 공지 공개 식별자 |
| `title` | `string` | |
| `body` | `string` | 목록에서는 생략 |
| `status` | `string` | `DRAFT`, `PUBLISHED` |
| `publishedAt` | `string / null` | 마지막 게시 시각<br>게시한 적 없으면 `null` |
| `notifiedAt` | `string / null` | 알림 요청 시각<br>요청한 적 없으면 `null` |
| `createdBy` | `object` | 작성 관리자 |
| `createdBy.memberId` | `string` | 회원 공개 식별자 |
| `createdBy.nickname` | `string` | |
| `createdAt` | `string` | |
| `updatedAt` | `string` | |

목록 응답은 같은 페이지 구조를 쓴다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items` | `object[]` | 최신순 |
| `nextCursor` | `string / null` | 다음 페이지 커서<br>더 없으면 `null` |

<br>

### 4-2-2 공개 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /notices` |
| 인증 | 불필요 |
| 성공 | 200, 페이지 구조 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `limit` | `integer` | 선택 | 페이지 크기<br>1~50으로 보정, 기본 20 |
| `cursor` | `string` | 선택 | 이전 응답의 `nextCursor` 그대로 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items[].noticeId` | `string` | 공지 공개 식별자 |
| `items[].title` | `string` | |
| `items[].publishedAt` | `string` | 게시 시각 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 형식 오류인 `cursor`, `limit` 타입 오류 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/notices?limit=2
```

**2) 200 Response body**

```json
{
  "items": [
    { "noticeId": "2d5a9c1e-7b3f-4e8a-9c0d-1f2e3a4b5c6d", "title": "10월 25일 새벽 점검 안내", "publishedAt": "2026-10-21T02:00:00Z" },
    { "noticeId": "8e1f2a3b-4c5d-4e6f-8a9b-0c1d2e3f4a5b", "title": "이프 충전 상품 변경 안내", "publishedAt": "2026-10-18T09:00:00Z" }
  ],
  "nextCursor": "MjAyNi0xMC0xOFQwOTowMDowMFp8MTI"
}
```

</details>

<br>

### 4-2-3 공개 상세

| 항목 | 값 |
|---|---|
| 요청 | `GET /notices/{noticeId}` |
| 인증 | 불필요 |
| 성공 | 200 |

**1. 경로**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `noticeId` | 경로 | 필수 | 공지 공개 식별자 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `noticeId` | `string` | 공지 공개 식별자 |
| `title` | `string` | |
| `body` | `string` | |
| `publishedAt` | `string` | 게시 시각 |
| `updatedAt` | `string` | 마지막 수정 시각 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 404 | `NOT_FOUND` | 없는 공지, 초안, 형식 오류 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/notices/2d5a9c1e-7b3f-4e8a-9c0d-1f2e3a4b5c6d
```

**2) 200 Response body**

```json
{
  "noticeId": "2d5a9c1e-7b3f-4e8a-9c0d-1f2e3a4b5c6d",
  "title": "10월 25일 새벽 점검 안내",
  "body": "10월 25일 02:00부터 04:00까지 서버 점검이 있습니다.\n점검 중에는 채팅과 제작을 이용할 수 없습니다.",
  "publishedAt": "2026-10-21T02:00:00Z",
  "updatedAt": "2026-10-21T02:00:00Z"
}
```

**3) 404 Response body**

```json
{
  "timestamp": "2026-10-21T01:23:45.678Z",
  "status": 404,
  "code": "NOT_FOUND",
  "message": "공지를 찾을 수 없습니다.",
  "path": "/api/v1/notices/00000000-0000-0000-0000-000000000000",
  "details": []
}
```

</details>

<br>

### 4-2-4 관리자 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/notices` |
| 인증 | 관리자 |
| 성공 | 200, 페이지 구조의 관리자 공지 구조 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `status` | `string` | 선택 | `DRAFT`, `PUBLISHED`<br>생략하면 전체 |
| `limit` | `integer` | 선택 | 페이지 크기<br>1~50으로 보정, 기본 20 |
| `cursor` | `string` | 선택 | 이전 응답의 `nextCursor` 그대로 |

- 생성 시각 내림차순이다. 항목에 `body`는 없다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 지원하지 않는 `status`, 형식 오류인 `cursor`, `limit` 타입 오류 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/notices?status=DRAFT&limit=1
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "items": [
    {
      "noticeId": "5c6d7e8f-9a0b-4c1d-8e2f-3a4b5c6d7e8f",
      "title": "할로윈 이벤트 안내",
      "status": "DRAFT",
      "publishedAt": null,
      "notifiedAt": null,
      "createdBy": { "memberId": "9a8b7c6d-5e4f-4a3b-9c2d-1e0f9a8b7c6d", "nickname": "고요한 서고" },
      "createdAt": "2026-10-21T01:00:00Z",
      "updatedAt": "2026-10-21T01:10:00Z"
    }
  ],
  "nextCursor": null
}
```

</details>

<br>

### 4-2-5 관리자 상세

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/notices/{noticeId}` |
| 인증 | 관리자 |
| 성공 | 200, 관리자 공지 구조 |

**1. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `noticeId`가 UUID 형식이 아님 |
| 404 | `NOT_FOUND` | 없는 공지 |

<br>

### 4-2-6 공지 작성

| 항목 | 값 |
|---|---|
| 요청 | `POST /admin/notices` |
| 인증 | 관리자 |
| 성공 | 201, 관리자 공지 구조 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `title` | `string` | 필수 | 1~100자 |
| `body` | `string` | 필수 | 1~5,000자 |
| `reason` | `string` | 필수 | 사유, 1~500자 |

- 생성된 공지는 초안이다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 필드 누락, 공백만, 길이 초과 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/admin/notices
Authorization: Bearer {adminToken}
Content-Type: application/json

{
  "title": "10월 25일 새벽 점검 안내",
  "body": "10월 25일 02:00부터 04:00까지 서버 점검이 있습니다.\n점검 중에는 채팅과 제작을 이용할 수 없습니다.",
  "reason": "정기 점검 공지"
}
```

**2) 201 Response body**

```json
{
  "noticeId": "2d5a9c1e-7b3f-4e8a-9c0d-1f2e3a4b5c6d",
  "title": "10월 25일 새벽 점검 안내",
  "body": "10월 25일 02:00부터 04:00까지 서버 점검이 있습니다.\n점검 중에는 채팅과 제작을 이용할 수 없습니다.",
  "status": "DRAFT",
  "publishedAt": null,
  "notifiedAt": null,
  "createdBy": { "memberId": "9a8b7c6d-5e4f-4a3b-9c2d-1e0f9a8b7c6d", "nickname": "고요한 서고" },
  "createdAt": "2026-10-21T01:00:00Z",
  "updatedAt": "2026-10-21T01:00:00Z"
}
```

</details>

<br>

### 4-2-7 공지 수정

| 항목 | 값 |
|---|---|
| 요청 | `PATCH /admin/notices/{noticeId}` |
| 인증 | 관리자 |
| 성공 | 200, 관리자 공지 구조 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `title` | `string` | 선택 | 1~100자<br>생략하면 유지 |
| `body` | `string` | 선택 | 1~5,000자<br>생략하면 유지 |
| `reason` | `string` | 필수 | 사유, 1~500자 |

- `title`과 `body` 중 하나는 있어야 한다. `null`은 생략과 같다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 둘 다 없음, 공백만, 길이 초과, `reason` 누락, `noticeId` 형식 오류 |
| 404 | `NOT_FOUND` | 없는 공지 |

<br>

### 4-2-8 게시

| 항목 | 값 |
|---|---|
| 요청 | `POST /admin/notices/{noticeId}/publish` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `notify` | `boolean` | 필수 | 알림을 함께 요청할지 |
| `notificationKind` | `string` | `notify`가 `true`면 필수 | `SERVICE`는 정보성, `MARKETING`은 광고성 |
| `reason` | `string` | 필수 | 사유, 1~500자 |

<br>

**2. 응답**

관리자 공지 구조에 다음 필드를 더한다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `notified` | `boolean` | 이번 게시로 알림을 요청했는지<br>이미 요청한 적 있거나 `notify`가 `false`면 `false` |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `notify` 누락, `notify`가 `true`인데 `notificationKind` 없음, 지원하지 않는 유형, `reason` 누락 |
| 404 | `NOT_FOUND` | 없는 공지 |
| 409 | `CONFLICT` | 이미 게시된 공지 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/admin/notices/2d5a9c1e-7b3f-4e8a-9c0d-1f2e3a4b5c6d/publish
Authorization: Bearer {adminToken}
Content-Type: application/json

{ "notify": true, "notificationKind": "SERVICE", "reason": "점검 공지 게시" }
```

**2) 200 Response body**

```json
{
  "noticeId": "2d5a9c1e-7b3f-4e8a-9c0d-1f2e3a4b5c6d",
  "title": "10월 25일 새벽 점검 안내",
  "body": "10월 25일 02:00부터 04:00까지 서버 점검이 있습니다.\n점검 중에는 채팅과 제작을 이용할 수 없습니다.",
  "status": "PUBLISHED",
  "publishedAt": "2026-10-21T02:00:00Z",
  "notifiedAt": "2026-10-21T02:00:00Z",
  "createdBy": { "memberId": "9a8b7c6d-5e4f-4a3b-9c2d-1e0f9a8b7c6d", "nickname": "고요한 서고" },
  "createdAt": "2026-10-21T01:00:00Z",
  "updatedAt": "2026-10-21T02:00:00Z",
  "notified": true
}
```

**3) 409 Response body**

```json
{
  "timestamp": "2026-10-21T02:05:00.000Z",
  "status": 409,
  "code": "CONFLICT",
  "message": "이미 게시된 공지입니다.",
  "path": "/api/v1/admin/notices/2d5a9c1e-7b3f-4e8a-9c0d-1f2e3a4b5c6d/publish",
  "details": []
}
```

</details>

<br>

### 4-2-9 게시 해제

| 항목 | 값 |
|---|---|
| 요청 | `POST /admin/notices/{noticeId}/unpublish` |
| 인증 | 관리자 |
| 성공 | 200, 관리자 공지 구조 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `reason` | `string` | 필수 | 사유, 1~500자 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `reason` 누락, `noticeId` 형식 오류 |
| 404 | `NOT_FOUND` | 없는 공지 |
| 409 | `CONFLICT` | 게시되지 않은 공지 |

<br>

### 4-2-10 초안 삭제

| 항목 | 값 |
|---|---|
| 요청 | `DELETE /admin/notices/{noticeId}` |
| 인증 | 관리자 |
| 성공 | 204, 본문 없음 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `reason` | `string` | 필수 | 사유, 1~500자 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `reason` 누락, `noticeId` 형식 오류 |
| 404 | `NOT_FOUND` | 없는 공지 |
| 409 | `CONFLICT` | 게시된 공지, 알림을 요청한 적 있는 공지 |

<br>

### 4-2-11 다른 도메인과의 경계

| 도메인 | NOTICE가 제공하는 것 | NOTICE가 사용하는 것 |
|---|---|---|
| NOTIFICATION | 없음 | 공지 발송 요청 연산 |
| ADMIN | 없음 | 관리자 요청자, 변경 감사 기록 |
| ACCOUNT | 없음 | 작성 관리자의 닉네임과 공개 식별자 |
| 모든 도메인 | 없음 | 상관관계 필터, 관리자 판정 필터 |

다른 도메인의 연산을 호출할 때의 입력과 결과는 다음과 같다.

| 연산 | 입력 | 결과 |
|---|---|---|
| 공지 발송 요청 | 공지 공개 식별자, 제목, 알림 본문, 유형, 딥링크 | 캠페인 1건<br>호출자의 트랜잭션에 참여 |
| 변경 감사 기록 | 관리자, 작업 이름, 대상 종류 `NOTICE`, 공지 공개 식별자, 사유, 변경 전후 값 | 감사 로그 행 |

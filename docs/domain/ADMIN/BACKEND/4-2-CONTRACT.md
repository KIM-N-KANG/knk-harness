# 4-2 계약

이 문서는 ADMIN 도메인 백엔드와 관리자 페이지, 다른 도메인 사이의 계약을 정한다. 관리자 API 공통 규칙, 엔드포인트별 요청 필드, 성공과 실패 응답의 필드와 예시, 도메인 경계를 다룬다.

처리 순서와 판정 규칙은 처리 흐름에, 앱 코드 전체 목록과 복구는 오류 처리에, 토큰과 개인정보 취급은 보안에 있다. ([4-1 처리 흐름](4-1-PIPELINES.md), [5-3-2 앱 코드](5-3-ERROR-HANDLING.md#5-3-2-앱-코드), [5-1-6 비밀값과 개인정보](5-1-SECURITY.md#5-1-6-비밀값과-개인정보))

<br>

### 4-2-1 공통 규칙과 헤더

이 절의 인증 수준, 헤더, 공통 실패 응답은 다른 도메인의 관리자 API에도 그대로 적용된다.

**1. 공통 규칙**

| 항목 | 규칙 |
|---|---|
| 경로 | `/api/v1`을 생략해 적음<br>관리자 API는 모두 `/admin/` 아래 |
| JSON 필드 이름 | camelCase |
| 시각 | ISO 8601 UTC 문자열 |
| 식별자 | 회원, 감사 로그, 주문은 UUID 공개 식별자<br>내부 PK는 노출하지 않음 |
| 호출 주체 | 관리자 페이지의 서버 측 처리기<br>브라우저가 직접 호출하지 않으므로 관리자 페이지 주소는 CORS 허용 목록에 없음 |
| 사유 | 변경 작업의 요청 본문에 `reason` 필수 |
| 예시 값 | 모든 예시는 구조를 설명하기 위한 가상 값 |

<br>

**2. 인증 수준**

| 수준 | 토큰 없음 또는 무효 | 앱 접근 토큰 | 관리자 토큰 |
|---|---|---|---|
| `불필요` | 처리 | 처리 | 처리 |
| `관리자` | 거절 | 거절 | 역할과 계정 상태를 다시 확인해 통과<br>역할 없음, 정지, 탈퇴는 거절 |

<br>

**3. 요청 헤더**

| 요청 헤더 | 값 형식 | 쓰임 | 필수 |
|---|---|---|---|
| `Authorization` | `Bearer {adminToken}` | 관리자 식별 | 인증 수준에 따름 |
| `X-Manyak-Request-Id` | 문자열 | 로그 연결과 감사 로그의 요청 ID<br>없으면 서버가 생성하고 응답 헤더로 항상 반환 | 선택 |

<br>

**4. 관리자 토큰**

| 항목 | 값 |
|---|---|
| 형식 | HS256 JWT<br>앱 접근 토큰과 같은 대칭키 |
| 클레임 | 발급자 `manyak`, 주체는 회원 공개 식별자, 대상 `manyak-admin`, 발급 시각, 만료 |
| 수명 | 2시간<br>갱신 없음 |
| 구분 | 대상 클레임이 `manyak-admin`을 포함하면 관리자 토큰<br>앱 경로는 대상 클레임이 있는 토큰을 거절 |

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
| `details` | `object[]` | 선언적 필드 검증 실패나 쿼리와 경로 변수의 타입 변환 실패 시 `field`와 `message` 포함<br>그 외는 빈 배열 |

| `details[].field` 규칙 | 값 |
|---|---|
| 필드 검증 | 필드명 |
| 본문 파싱 실패 | 빈 `details` |

각 절의 실패 표에는 해당 엔드포인트에서 발생하는 상태와 `code`를 적는다. 다음 공통 실패는 각 절에서 생략한다.

| 상태 | `code` | 조건 |
|---|---|---|
| 401 | `UNAUTHORIZED` | 관리자 경로의 토큰 누락, 만료, 위조, 주체 형식 오류, 관리자 표식 없음 |
| 403 | `FORBIDDEN` | 관리자 표식이 있는 토큰이지만 역할 없음, 정지, 탈퇴, 회원 없음 |
| 500 | `INTERNAL_SERVER_ERROR` | 예상하지 못한 오류 |

<br>

**6. 공통 응답 구조**

회원 검색 항목, 회원 상세, 감사 로그의 처리자는 같은 회원 요약 구조를 쓴다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `memberId` | `string` | 회원 공개 식별자 |
| `nickname` | `string` | 탈퇴 계정은 익명화된 이름 |
| `status` | `string` | `ACTIVE`, `SUSPENDED`, `DELETED` |
| `isAdmin` | `boolean` | 관리자 역할 보유 여부 |
| `createdAt` | `string` | 가입 시각 |

목록 응답은 같은 페이지 구조를 쓴다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items` | `object[]` | 최신순 |
| `nextCursor` | `string / null` | 다음 페이지 커서<br>더 없으면 `null` |

<br>

### 4-2-2 관리자 로그인

| 항목 | 값 |
|---|---|
| 요청 | `POST /admin/auth/login/google` |
| 인증 | 불필요 |
| 성공 | 200 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `idToken` | `string` | 필수 | Google이 발급한 OIDC ID 토큰 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `accessToken` | `string` | 관리자 토큰 |
| `expiresIn` | `integer` | 만료까지 남은 초 |
| `tokenType` | `string` | 항상 `Bearer` |
| `admin` | `object` | 회원 요약 구조 |

- 갱신 토큰은 없다. 만료되면 다시 로그인한다. 로그아웃 엔드포인트는 없으며 관리자 페이지가 쿠키를 지운다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `idToken` 누락 |
| 401 | `UNAUTHORIZED` | 신원 증명 검증 실패 |
| 403 | `FORBIDDEN` | 회원 없음, 관리자 역할 없음, 정지, 탈퇴<br>사유를 구분하지 않음 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/admin/auth/login/google
Content-Type: application/json

{ "idToken": "{googleIdToken}" }
```

**2) 200 Response body**

```json
{
  "accessToken": "{adminToken}",
  "expiresIn": 7200,
  "tokenType": "Bearer",
  "admin": {
    "memberId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
    "nickname": "차분한 등대",
    "status": "ACTIVE",
    "isAdmin": true,
    "createdAt": "2026-07-01T09:00:00Z"
  }
}
```

**3) 403 Response body**

```json
{
  "timestamp": "2026-10-21T01:23:45.678Z",
  "status": 403,
  "code": "FORBIDDEN",
  "message": "관리자 권한이 없습니다.",
  "path": "/api/v1/admin/auth/login/google",
  "details": []
}
```

</details>

<br>

### 4-2-3 대시보드 요약

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/dashboard/summary` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string` | 집계 기준 시각 |
| `todayStartsAt` | `string` | 오늘 범위의 시작인 KST 자정 |
| `members` | `object` | 회원 |
| `members.total` | `integer` | 탈퇴하지 않은 회원 수 |
| `members.joinedToday` | `integer` | 오늘 가입 |
| `members.withdrawnTotal` | `integer` | 탈퇴 누적 |
| `members.withdrawnToday` | `integer` | 오늘 탈퇴 |
| `chats` | `object` | 채팅 |
| `chats.startedTotal` | `integer` | 채팅 시작 누적 |
| `chats.startedToday` | `integer` | 오늘 채팅 시작 |
| `chats.turnsTotal` | `integer` | 턴 누적 |
| `chats.turnsToday` | `integer` | 오늘 턴 |
| `stories` | `object` | 스토리 |
| `stories.total` | `integer` | 스토리 누적 |
| `stories.createdToday` | `integer` | 오늘 생성 |
| `credits` | `object` | 이프 |
| `credits.grantedTotal` | `integer` | 지급 누적 |
| `credits.grantedToday` | `integer` | 오늘 지급 |
| `credits.spentTotal` | `integer` | 소진 누적 |
| `credits.spentToday` | `integer` | 오늘 소진 |
| `payments` | `object` | 결제 |
| `payments.completedTotal` | `integer` | 결제 건수 누적 |
| `payments.completedToday` | `integer` | 오늘 결제 건수 |
| `payments.amountKrwTotal` | `integer` | 결제 금액 누적 |
| `payments.amountKrwToday` | `integer` | 오늘 결제 금액 |
| `payments.refundedTotal` | `integer` | 환불 건수 누적 |
| `payments.refundedToday` | `integer` | 오늘 환불 건수 |
| `moderation` | `object` | 검수 |
| `moderation.heldSubmissions` | `integer` | 현재 보류 중인 제출본 수 |

<br>

**2. 실패 응답**

공통 실패만 있다.

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/dashboard/summary
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "asOf": "2026-10-21T05:12:00Z",
  "todayStartsAt": "2026-10-20T15:00:00Z",
  "members": { "total": 1240, "joinedToday": 12, "withdrawnTotal": 38, "withdrawnToday": 0 },
  "chats": { "startedTotal": 8210, "startedToday": 64, "turnsTotal": 96320, "turnsToday": 710 },
  "stories": { "total": 1530, "createdToday": 9 },
  "credits": { "grantedTotal": 2480000, "grantedToday": 6250, "spentTotal": 1902400, "spentToday": 14200 },
  "payments": { "completedTotal": 41, "completedToday": 1, "amountKrwTotal": 312800, "amountKrwToday": 4800, "refundedTotal": 2, "refundedToday": 0 },
  "moderation": { "heldSubmissions": 1 }
}
```

</details>

<br>

### 4-2-4 결제 내역

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/payments/orders` |
| 인증 | 관리자 |
| 성공 | 200<br>페이지 구조 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `limit` | `integer` | 선택 | 페이지 크기<br>1~100으로 보정<br>기본 50 |
| `cursor` | `string` | 선택 | 이전 응답의 `nextCursor` 그대로 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items[].orderId` | `string` | 주문 공개 식별자 |
| `items[].member` | `object` | 회원 요약 구조 |
| `items[].productId` | `string` | 상품 ID |
| `items[].status` | `string` | `COMPLETED`<br>`REFUNDED` |
| `items[].priceKrw` | `integer` | 결제 금액 |
| `items[].creditAmount` | `integer` | 적립 총량 |
| `items[].completedAt` | `string` | 완료 시각 |
| `items[].refundedAt` | `string / null` | 환불 시각 |
| `items[].reversalShortfall` | `integer / null` | 회수 때 돌려받지 못한 수량<br>환불 전은 `null` |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 형식 오류인 `cursor` 또는 `limit` 타입 오류 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/payments/orders?limit=1
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "items": [
    {
      "orderId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "member": { "memberId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301", "nickname": "차분한 등대", "status": "ACTIVE", "isAdmin": false, "createdAt": "2026-07-01T09:00:00Z" },
      "productId": "if_5000",
      "status": "COMPLETED",
      "priceKrw": 4800,
      "creditAmount": 5000,
      "completedAt": "2026-10-21T01:22:03Z",
      "refundedAt": null,
      "reversalShortfall": null
    }
  ],
  "nextCursor": "MjAyNi0xMC0yMVQwMToyMjowM1p8NDE"
}
```

</details>

<br>

### 4-2-5 회원 검색

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/members` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `query` | `string` | 필수 | 1~50자<br>UUID 형식이면 공개 식별자로 검색하고 아니면 닉네임 부분 일치로 검색 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items` | `object[]` | 회원 요약 구조<br>최대 20건<br>가입 시각 내림차순 |

- 검색은 접속 기록으로 감사 로그에 남는다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `query` 누락, 공백, 50자 초과 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/members?query=등대
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "items": [
    { "memberId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301", "nickname": "차분한 등대", "status": "ACTIVE", "isAdmin": false, "createdAt": "2026-07-01T09:00:00Z" }
  ]
}
```

</details>

<br>

### 4-2-6 회원 상세

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/members/{memberId}` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 경로**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `memberId` | 경로 | 필수 | 회원 공개 식별자 |

<br>

**2. 응답**

회원 요약 구조에 다음 필드를 더한다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `creditBalance` | `integer` | 만료되지 않은 이프 잔액 |
| `storyCount` | `integer` | 삭제되지 않은 소유 스토리 수 |
| `chatCount` | `integer` | 삭제되지 않은 소유 채팅 수 |
| `deletedAt` | `string / null` | 탈퇴 시각 |

- 상세 조회는 접속 기록으로 감사 로그에 남는다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `memberId`가 UUID 형식이 아님<br>`details[].field`는 `memberId` |
| 404 | `NOT_FOUND` | 없는 회원 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/members/3f2504e0-4f89-41d3-9a0c-0305e82c3301
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "memberId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "nickname": "차분한 등대",
  "status": "ACTIVE",
  "isAdmin": false,
  "createdAt": "2026-07-01T09:00:00Z",
  "creditBalance": 1230,
  "storyCount": 4,
  "chatCount": 17,
  "deletedAt": null
}
```

</details>

<br>

### 4-2-7 감사 로그 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/audit-logs` |
| 인증 | 관리자 |
| 성공 | 200<br>페이지 구조 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `adminId` | `string` | 선택 | 처리자의 회원 공개 식별자 |
| `action` | `string` | 선택 | 작업 이름 |
| `targetType` | `string` | 선택 | 대상 종류 |
| `targetId` | `string` | 선택 | 대상 식별자<br>`targetType`과 함께 지정 |
| `limit` | `integer` | 선택 | 페이지 크기<br>1~100으로 보정<br>기본 50 |
| `cursor` | `string` | 선택 | 이전 응답의 `nextCursor` 그대로 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items[].auditLogId` | `string` | 감사 로그 공개 식별자 |
| `items[].admin` | `object` | 처리자의 회원 요약 구조 |
| `items[].category` | `string` | `CHANGE`<br>`ACCESS` |
| `items[].action` | `string` | 작업 이름 |
| `items[].targetType` | `string` | 대상 종류 |
| `items[].targetId` | `string` | 대상 식별자 |
| `items[].reason` | `string / null` | 사유<br>조회 기록은 `null` |
| `items[].before` | `object / null` | 변경 전 값 |
| `items[].after` | `object / null` | 변경 후 값 |
| `items[].requestId` | `string` | 요청 ID |
| `items[].createdAt` | `string` | 기록 시각 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 형식 오류인 `cursor`, `adminId`가 UUID 형식이 아님, `targetId`만 지정, `limit` 타입 오류 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/audit-logs?action=CREDIT_GRANTED&limit=1
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "items": [
    {
      "auditLogId": "0b7f6b1a-2c3d-4e5f-8a9b-0c1d2e3f4a5b",
      "admin": { "memberId": "9a8b7c6d-5e4f-4a3b-9c2d-1e0f9a8b7c6d", "nickname": "고요한 서고", "status": "ACTIVE", "isAdmin": true, "createdAt": "2026-07-01T09:00:00Z" },
      "category": "CHANGE",
      "action": "CREDIT_GRANTED",
      "targetType": "MEMBER",
      "targetId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
      "reason": "결제 오류 보상",
      "before": { "balance": 1230 },
      "after": { "balance": 6230, "amount": 5000 },
      "requestId": "req_0f1e2d3c4b5a69788796a5b4c3d2e1f0",
      "createdAt": "2026-10-21T01:23:45.678Z"
    }
  ],
  "nextCursor": null
}
```

</details>

<br>

### 4-2-8 다른 도메인과의 경계

| 도메인 | ADMIN이 제공하는 것 | ADMIN이 사용하는 것 |
|---|---|---|
| ACCOUNT | 관리자 요청자 식별과 감사 기록 연산 | 신원 검증기, 회원 조회와 검색, 계정 상태, 회원 수 집계 |
| PAYMENT | 관리자 요청자 식별과 감사 기록 연산 | 잔액, 완료와 환불 주문 조회, 지급과 소진 집계 |
| NOTIFICATION, NOTICE, MODERATION | 관리자 요청자 식별과 감사 기록 연산 | 보류 제출본 수 |
| STORY<br>CHAT | 없음 | 스토리 수, 채팅 시작 수, 턴 수, 회원별 소유 수 |
| 모든 도메인 | 관리자 판정 필터와 앱 토큰 검증 보강 | 인증 필터와 상관관계 필터 |

다른 도메인이 호출하는 연산의 입력과 결과는 다음과 같다.

| 연산 | 입력 | 결과 |
|---|---|---|
| 관리자 요청자 | 현재 요청 | 관리자의 회원 내부 ID<br>필터가 확정한 값 |
| 변경 감사 기록 | 관리자, 작업 이름, 대상 종류, 대상 식별자, 사유, 변경 전 값, 변경 후 값 | 감사 로그 행<br>호출자의 트랜잭션에 참여하고 트랜잭션이 없으면 거부 |
| 접속 기록 | 관리자, 작업 이름, 대상 종류, 대상 식별자 | 감사 로그 행<br>독립 트랜잭션 |

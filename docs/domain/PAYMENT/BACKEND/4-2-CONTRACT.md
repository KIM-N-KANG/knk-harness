# 4-2 계약

이 문서는 PAYMENT 도메인 백엔드와 클라이언트, 결제 제공자, 관리자 페이지, 다른 도메인 사이의 계약을 정한다. 엔드포인트별 요청 필드, 성공과 실패 응답의 필드와 예시, 도메인 경계를 다룬다.

처리 순서와 판정 규칙은 처리 흐름에, 앱 코드 전체 목록과 복구는 오류 처리에, 비밀값 취급은 보안에, 관리자 토큰과 권한 판정은 관리자 계약에 있다. ([4-1 처리 흐름](4-1-PIPELINES.md), [5-3-2 앱 코드](5-3-ERROR-HANDLING.md#5-3-2-앱-코드), [5-1-7 비밀값과 개인정보](5-1-SECURITY.md#5-1-7-비밀값과-개인정보), [ADMIN 4-2-1 공통 규칙과 헤더](../../ADMIN/BACKEND/4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더))

<br>

### 4-2-1 공통 규칙과 헤더

**1. 공통 규칙**

| 항목 | 규칙 |
|---|---|
| 경로 | `/api/v1`을 생략해 적음 |
| JSON 필드 이름 | camelCase |
| 시각 | ISO 8601 UTC 문자열 |
| 금액 | 정수<br>이프는 단위 없는 수량, 가격은 원 |
| 식별자 | 주문과 회원은 UUID 공개 식별자<br>원장과 로트의 식별자는 노출하지 않음 |
| 사유와 상태 | 대문자 enum 문자열 |
| 사유 문장 | 관리자 변경 작업의 요청 본문에 `reason` 필수 |
| 예시 값 | 모든 예시는 구조를 설명하기 위한 가상 값 |

<br>

**2. 인증 수준**

| 수준 | 토큰 없음 또는 무효 | 유효한 앱 접근 토큰 | 관리자 토큰 |
|---|---|---|---|
| `불필요` | 익명으로 처리 | 회원으로 처리<br>탈퇴 계정은 거절 | 거절 |
| `필수` | 거절 | 회원으로 처리 | 거절 |
| `서명` | 토큰을 읽지 않음 | 토큰을 읽지 않음<br>웹훅 서명으로 인증 | 토큰을 읽지 않음 |
| `관리자` | 거절 | 거절 | 관리자 역할과 계정 상태를 다시 확인해 통과 |

<br>

**3. 요청 헤더**

| 요청 헤더 | 값 형식 | 쓰임 | 필수 |
|---|---|---|---|
| `Authorization` | `Bearer {accessToken}` 또는 `Bearer {adminToken}` | 회원 또는 관리자 식별 | 인증 수준에 따름 |
| `X-Manyak-Request-Id` | 문자열 | 로그 연결<br>없으면 서버가 생성하고 응답 헤더로 항상 반환 | 선택 |
| `X-Manyak-Session-Id` | 문자열 | 클라이언트 분석 세션 식별 | 선택 |
| `X-Manyak-Device-Id` | 문자열 | 게스트의 체험 카운터 식별 | 게스트의 체험 조회는 필수 |
| `X-Groble-Timestamp` | 초 단위 Unix 시각 | 웹훅 서명 대상과 재전송 방지 | 웹훅은 필수 |
| `X-Groble-Signature` | 16진수 64자 | 웹훅 서명 | 웹훅은 필수 |
| `X-Groble-Signature-Previous` | 16진수 64자 | 시크릿 교체 기간의 이전 서명 | 선택 |
| `X-Groble-Idempotency-Key` | 문자열 | 로그 기록용<br>멱등 판정에 쓰지 않음 | 선택 |

<br>

**4. 계정 상태 규칙**

| 요청 | 정지 계정 | 탈퇴 계정 |
|---|---|---|
| 상품 목록, 정책값 조회, 체험 조회 | 처리 | 유효한 토큰은 401<br>만료되거나 위조된 토큰은 익명 처리 |
| 잔액 조회, 이용내역 조회, 주문 조회 | 처리 | 401 |
| 출석 보상, 충전 주문 생성 | 403 | 401 |

<br>

**5. 공통 실패 응답**

실패 응답은 모두 같은 형식이다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `timestamp` | `string` | 응답 생성 시각 |
| `status` | `integer` | HTTP 상태 |
| `code` | `string` | HTTP 상태 이름 또는 앱 코드 |
| `message` | `string` | 사용자 안내 문구 |
| `path` | `string` | 요청 경로 |
| `details` | `object[]` | 선언적 필드 검증, 쿼리와 경로 변수의 타입 변환 실패 시 `field`와 `message` 포함<br>그 외는 빈 배열 |

| `details[].field` 규칙 | 값 |
|---|---|
| 필드 검증 | 필드명 |
| 본문 파싱 실패 | 빈 `details` |

각 절의 실패 표에는 해당 엔드포인트에서 발생하는 상태와 `code`를 적는다. 다음 공통 실패는 각 절에서 생략한다.

| 상태 | `code` | 조건 |
|---|---|---|
| 401 | `UNAUTHORIZED` | 인증 필수 경로의 토큰 누락, 만료, 위조, 주체 형식 오류, 사용자 없음<br>확인된 탈퇴 계정<br>관리자 경로의 토큰 누락, 만료, 위조, 관리자 표식 없음 |
| 403 | `FORBIDDEN` | 계정 상태 규칙 표의 403<br>관리자 경로의 역할 없음, 정지, 탈퇴 |
| 403 | `CONSENT_REQUIRED` | 동의 게이트가 켜진 환경에서 미동의 회원의 허용 목록 밖 요청 |
| 500 | `INTERNAL_SERVER_ERROR` | 예상하지 못한 오류 |

<br>

### 4-2-2 상품 목록 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /credits/products` |
| 인증 | 불필요 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items` | `object[]` | 설정 순서의 상품 6종 |
| `items[].productId` | `string` | 상품 ID |
| `items[].baseCredits` | `integer` | 기본 이프 |
| `items[].bonusCredits` | `integer` | 보너스 이프 |
| `items[].totalCredits` | `integer` | 적립 총량 |
| `items[].webPriceKrw` | `integer` | 웹 가격 |

<br>

**2. 실패 응답**

공통 실패만 있다.

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

1) Request

```http
GET /api/v1/credits/products
```

2) 200 Response body

```json
{
  "items": [
    { "productId": "if_2000", "baseCredits": 2000, "bonusCredits": 0, "totalCredits": 2000, "webPriceKrw": 2000 },
    { "productId": "if_5000", "baseCredits": 4800, "bonusCredits": 200, "totalCredits": 5000, "webPriceKrw": 4800 }
  ]
}
```

</details>

<br>

### 4-2-3 정책값 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /credits/policies` |
| 인증 | 불필요 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `signupReward` | `integer` | 가입 보상 이프 |
| `inviteReward` | `integer` | 초대 보상 이프<br>초대자와 제출자가 각각 받음 |
| `inviteMonthlyCap` | `integer` | 초대자 보상의 KST 월 횟수 상한<br>제출자 몫에는 적용하지 않음 |
| `attendanceReward` | `integer` | 출석 보상 이프 |
| `storyCreationCost` | `integer` | 간편 제작 소모 이프<br>회원 체험을 소진한 뒤 적용 |
| `chatTurnCost` | `integer` | 채팅 턴 소모 이프, 재생성 포함<br>회원 체험을 소진한 뒤 적용 |
| `chatImageCost` | `integer` | 채팅 이미지 소모 이프<br>0이면 체험 소진 뒤에도 무료 |

- 한 응답의 값은 같은 시점의 정책 스냅샷이다. 오버라이드 변경은 갱신 주기 안에 반영된다. 클라이언트는 이 값을 표시하고 하드코딩하지 않는다.

<br>

**2. 실패 응답**

공통 실패만 있다.

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

1) Request

```http
GET /api/v1/credits/policies
```

2) 200 Response body

```json
{
  "signupReward": 1000,
  "inviteReward": 2000,
  "inviteMonthlyCap": 10,
  "attendanceReward": 250,
  "storyCreationCost": 250,
  "chatTurnCost": 20,
  "chatImageCost": 0
}
```

</details>

<br>

### 4-2-4 체험 사용량 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /users/me/trials` |
| 인증 | 불필요<br>게스트는 `X-Manyak-Device-Id` 필수 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `chatTurn` | `object` | 채팅 턴 |
| `chatImage` | `object` | 채팅 이미지 |
| `storyCreation` | `object` | 간편 제작 |
| `storylineGeneration` | `object` | 스토리라인 생성 |
| `*.used` | `integer` | 사용 횟수 |
| `*.limit` | `integer / null` | 한도<br>회원의 스토리라인 생성은 `null`이고 사용 횟수는 0 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 게스트 요청에 기기 헤더가 없거나 공백 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

1) Request

```http
GET /api/v1/users/me/trials
X-Manyak-Device-Id: 9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

2) 200 Response body

```json
{
  "chatTurn": { "used": 2, "limit": 5 },
  "chatImage": { "used": 0, "limit": 5 },
  "storyCreation": { "used": 1, "limit": 1 },
  "storylineGeneration": { "used": 3, "limit": 5 }
}
```

3) 400 Response body

```json
{
  "timestamp": "2026-10-16T01:23:45.678Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "게스트의 체험 한도 대상 요청은 X-Manyak-Device-Id 헤더가 필요합니다.",
  "path": "/api/v1/users/me/trials",
  "details": []
}
```

</details>

<br>

### 4-2-5 잔액 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /users/me/credits` |
| 인증 | 필수 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `balance` | `integer` | 만료되지 않은 잔액<br>지갑이 없으면 0 |

<br>

**2. 실패 응답**

공통 실패만 있다.

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

1) Request

```http
GET /api/v1/users/me/credits
Authorization: Bearer {accessToken}
```

2) 200 Response body

```json
{ "balance": 1230 }
```

</details>

<br>

### 4-2-6 출석 보상

| 항목 | 값 |
|---|---|
| 요청 | `POST /users/me/credits/attendance` |
| 인증 | 필수 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `rewarded` | `boolean` | 이번 요청으로 적립했는지<br>오늘 이미 받았으면 `false` |
| `amount` | `integer` | 이번 요청으로 적립한 이프<br>이미 받았으면 0 |
| `balance` | `integer` | 적립 뒤 잔액 |

- 하루의 기준은 KST 자정이다. 같은 날 다시 호출해도 200으로 응답한다. 추가로 적립하지 않는다.

<br>

**2. 실패 응답**

공통 실패만 있다.

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

1) Request

```http
POST /api/v1/users/me/credits/attendance
Authorization: Bearer {accessToken}
```

2) 200 Response body, 첫 호출

```json
{ "rewarded": true, "amount": 250, "balance": 1480 }
```

3) 200 Response body, 같은 날 재호출

```json
{ "rewarded": false, "amount": 0, "balance": 1480 }
```

</details>

<br>

### 4-2-7 이용내역 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /users/me/credits/transactions` |
| 인증 | 필수 |
| 성공 | 200 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `type` | `string` | 선택 | `ALL`, `SPEND`, `EARN`, `EXPIRE`<br>대소문자 무시, 기본 `ALL` |
| `limit` | `integer` | 선택 | 페이지 크기<br>1~100으로 보정, 기본 50 |
| `cursor` | `string` | 선택 | 이전 응답의 `nextCursor` 그대로 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items` | `object[]` | 최신순 |
| `items[].type` | `string` | `SPEND`, `EARN`, `EXPIRE` |
| `items[].reason` | `string` | 원장 사유<br>한국어 라벨은 클라이언트가 붙임 |
| `items[].amount` | `integer` | 부호 있는 증감<br>소모, 만료, 회수는 음수 |
| `items[].title` | `string / null` | 관련 스토리 제목<br>채팅 참조는 읽을 수 없거나 삭제된 스토리면 마지막 공개 스냅샷의 제목이고 스냅샷이 없으면 `null`<br>간편 제작 참조는 삭제된 스토리면 `null`<br>보상, 만료, 회수 행은 `null` |
| `items[].expiresAt` | `string / null` | 획득 행은 그 적립분의 만료 예정 시각, 만료 행은 실제 만료 시각<br>소모와 회수 행은 `null` |
| `items[].createdAt` | `string` | 원장 기록 시각<br>만료 행은 만료 시각이 아니라 회수가 기록된 시각 |
| `nextCursor` | `string / null` | 다음 페이지 커서<br>더 없으면 `null` |

| `type` | 포함하는 `reason` |
|---|---|
| `SPEND` | `STORY_CREATION`, `CHAT_TURN`, `CHAT_IMAGE` |
| `EARN` | `SIGNUP_REWARD`, `ATTENDANCE_REWARD`, `INVITE_REWARD`, `REFUND`, `PURCHASE`, `ADMIN_GRANT` |
| `EXPIRE` | `EXPIRE`, `PURCHASE_REVERSAL`, `ADMIN_REVOKE` |

- 커서는 불투명 문자열이다. 같은 위치를 가리켜도 발급할 때마다 값이 다르다. 클라이언트는 커서를 해석하거나 조립하지 않는다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 지원하지 않는 `type`, 형식 오류이거나 변조된 `cursor`, `limit` 타입 오류 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

1) Request

```http
GET /api/v1/users/me/credits/transactions?type=ALL&limit=2
Authorization: Bearer {accessToken}
```

2) 200 Response body

```json
{
  "items": [
    {
      "type": "SPEND",
      "reason": "CHAT_TURN",
      "amount": -20,
      "title": "달빛 아래의 약속",
      "expiresAt": null,
      "createdAt": "2026-10-16T01:20:11.482913Z"
    },
    {
      "type": "EARN",
      "reason": "ATTENDANCE_REWARD",
      "amount": 250,
      "title": null,
      "expiresAt": "2026-11-15T00:03:27.104552Z",
      "createdAt": "2026-10-16T00:03:27.104552Z"
    }
  ],
  "nextCursor": "Zj1oV3pYcVhQbU1TM1Z0X2V4YW1wbGVfY3Vyc29y"
}
```

3) 400 Response body

```json
{
  "timestamp": "2026-10-16T01:23:45.678Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "커서가 올바르지 않습니다.",
  "path": "/api/v1/users/me/credits/transactions",
  "details": []
}
```

</details>

<br>

### 4-2-8 웹 충전 주문 생성

| 항목 | 값 |
|---|---|
| 요청 | `POST /users/me/credits/orders` |
| 인증 | 필수 |
| 성공 | 201 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `productId` | `string` | 필수 | 상품 ID, 1~32자 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `orderId` | `string` | 주문 공개 식별자 |
| `paymentUrl` | `string` | 상품의 그로블 결제창 주소에 `ref={orderId}`를 붙인 값 |

- 주문은 대기 상태다. 결제 복귀 뒤 주문 조회로 완료를 확인하기 전에는 적립을 단정하지 않는다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 필드 검증 실패, 설정에 없는 상품 |
| 503 | `SERVICE_UNAVAILABLE` | 상품의 결제창 주소 또는 웹훅 시크릿 미설정 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

1) Request

```http
POST /api/v1/users/me/credits/orders
Authorization: Bearer {accessToken}
Content-Type: application/json

{ "productId": "if_5000" }
```

2) 201 Response body

```json
{
  "orderId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "paymentUrl": "https://www.groble.im/payment/nSGNPJ?ref=7c9e6679-7425-40de-944b-e07fc1f90ae7"
}
```

3) 400 Response body

```json
{
  "timestamp": "2026-10-16T01:23:45.678Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "지원하지 않는 이프 상품입니다.",
  "path": "/api/v1/users/me/credits/orders",
  "details": []
}
```

</details>

<br>

### 4-2-9 주문 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /users/me/credits/orders/{orderId}` |
| 인증 | 필수 |
| 성공 | 200 |

**1. 경로**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `orderId` | 경로 | 필수 | 주문 공개 식별자 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `orderId` | `string` | 주문 공개 식별자 |
| `productId` | `string` | 상품 ID |
| `status` | `string` | `PENDING`, `COMPLETED`, `REFUNDED` |
| `totalCredits` | `integer` | 주문 생성 시점의 적립 총량 |
| `createdAt` | `string` | |
| `completedAt` | `string / null` | 완료 시각<br>적립 없이 환불 상태가 된 주문도 채움 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `orderId`가 UUID 형식이 아님<br>`details[].field`는 `orderId` |
| 404 | `NOT_FOUND` | 없는 주문, 타인의 주문 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

1) Request

```http
GET /api/v1/users/me/credits/orders/7c9e6679-7425-40de-944b-e07fc1f90ae7
Authorization: Bearer {accessToken}
```

2) 200 Response body

```json
{
  "orderId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "productId": "if_5000",
  "status": "COMPLETED",
  "totalCredits": 5000,
  "createdAt": "2026-10-16T01:20:11.482913Z",
  "completedAt": "2026-10-16T01:22:03.917204Z"
}
```

3) 404 Response body

```json
{
  "timestamp": "2026-10-16T01:23:45.678Z",
  "status": 404,
  "code": "NOT_FOUND",
  "message": "주문을 찾을 수 없습니다.",
  "path": "/api/v1/users/me/credits/orders/7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "details": []
}
```

</details>

<br>

### 4-2-10 그로블 웹훅 수신

| 항목 | 값 |
|---|---|
| 요청 | `POST /webhooks/groble` |
| 인증 | 서명 |
| 성공 | 200, 본문 없음 |

**1. 본문**

그로블이 보내는 이벤트 JSON이다. 서버가 읽는 필드만 적는다.

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `id` | `string` | 완료는 필수 | 이벤트 ID, 248자 이내<br>구매 적립의 멱등 키 |
| `type` | `string` | 필수 | `payment.completed`, `payment.refunded`<br>그 외는 무시 |
| `data.object.merchantUid` | `string` | 필수 | 그로블 거래 식별자, 255자 이내 |
| `data.object.sellerReference` | `string` | 완료는 필수 | 주문 공개 식별자 |
| `data.object.pricing.finalAmount` | `integer` | 완료는 필수 | 결제 금액<br>주문 가격과 같아야 적립 |
| `data.object.refund.partialRefund` | `boolean` | 환불은 필수 | `true`면 무시 |
| `data.object.refund.amount` | `integer` | 환불은 필수 | 환불 금액<br>주문 가격과 같아야 회수 |

<br>

**2. 응답**

처리하거나 무시한 요청은 모두 200으로 응답한다. 응답 본문은 없다. 무시한 사유는 응답에 담지 않는다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 서명은 유효하나 본문이 JSON 객체가 아님 |
| 401 | `UNAUTHORIZED` | 타임스탬프 누락, 형식 오류, 허용 범위 밖<br>서명 불일치 |
| 503 | `SERVICE_UNAVAILABLE` | 웹훅 시크릿 미설정 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

1) Request

```http
POST /api/v1/webhooks/groble
X-Groble-Timestamp: 1792700000
X-Groble-Signature: {hmacSha256Hex}
Content-Type: application/json

{
  "id": "evt_01JABCDEF",
  "type": "payment.completed",
  "data": {
    "object": {
      "merchantUid": "mu_20261016_000123",
      "sellerReference": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "pricing": { "finalAmount": 4800 }
    }
  }
}
```

2) 200 Response

본문 없음

3) 401 Response body

```json
{
  "timestamp": "2026-10-16T01:23:45.678Z",
  "status": 401,
  "code": "UNAUTHORIZED",
  "message": "그로블 웹훅 검증 실패",
  "path": "/api/v1/webhooks/groble",
  "details": []
}
```

</details>

<br>

### 4-2-11 이프 조정

| 항목 | 값 |
|---|---|
| 요청 | `POST /admin/credits/adjustments` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `memberId` | `string` | 필수 | 회원 공개 식별자 |
| `type` | `string` | 필수 | `GRANT`는 지급<br>`REVOKE`는 회수 |
| `amount` | `integer` | 필수 | 1~100,000 |
| `expiresInDays` | `integer` | 선택 | 지급 로트의 유효기간 일수<br>1~365, 생략하면 30<br>회수에서는 무시 |
| `idempotencyKey` | `string` | 필수 | 1~64자<br>영문, 숫자, 하이픈<br>관리자 페이지가 요청마다 새로 만들고 재시도에는 같은 값 |
| `reason` | `string` | 필수 | 사유<br>1~500자 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `memberId` | `string` | 회원 공개 식별자 |
| `type` | `string` | 적용된 종류 |
| `requestedAmount` | `integer` | 요청 금액 |
| `appliedAmount` | `integer` | 실제 적립 또는 회수한 금액<br>회수에서 잔액이 모자라면 잔액 |
| `shortfall` | `integer` | 회수에서 돌려받지 못한 금액<br>지급은 0 |
| `balance` | `integer` | 적용 뒤 잔액 |
| `duplicated` | `boolean` | 같은 멱등 키의 재요청이라 적용하지 않았으면 `true` |
| `expiresAt` | `string / null` | 지급 로트의 만료 시각<br>적립 시각에 유효기간 일수를 더한 값<br>회수는 `null` |

- 같은 멱등 키의 재요청은 종류와 금액이 달라도 적용하지 않고 처음 결과를 `duplicated` `true`로 돌려준다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 필드 누락, 범위 밖 금액, 범위 밖 `expiresInDays`, 멱등 키 형식 오류, 지원하지 않는 `type`, `memberId` 형식 오류 |
| 404 | `NOT_FOUND` | 없는 회원 |
| 409 | `CONFLICT` | 탈퇴 계정 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/admin/credits/adjustments
Authorization: Bearer {adminToken}
Content-Type: application/json

{
  "memberId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "type": "GRANT",
  "amount": 5000,
  "expiresInDays": 90,
  "idempotencyKey": "7f3c2a1e-9b8d-4c6f-a5e4-d3c2b1a09f8e",
  "reason": "결제 오류 보상"
}
```

**2) 200 Response body**

```json
{
  "memberId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "type": "GRANT",
  "requestedAmount": 5000,
  "appliedAmount": 5000,
  "shortfall": 0,
  "balance": 6230,
  "duplicated": false,
  "expiresAt": "2027-01-19T01:23:45.678Z"
}
```

**3) 200 Response body, 잔액보다 큰 회수**

```json
{
  "memberId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "type": "REVOKE",
  "requestedAmount": 10000,
  "appliedAmount": 6230,
  "shortfall": 3770,
  "balance": 0,
  "duplicated": false,
  "expiresAt": null
}
```

</details>

<br>

### 4-2-12 정책 오버라이드 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/credits/policies` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items` | `object[]` | 정책 키 7종<br>저장 키 순서 |
| `items[].policyKey` | `string` | 저장 키<br>snake_case |
| `items[].defaultAmount` | `integer` | 기본값 |
| `items[].effectiveAmount` | `integer` | 현재 적용 중인 값<br>스냅샷 기준 |
| `items[].minimum` | `integer` | 키별 최솟값 |
| `items[].override` | `object / null` | 오버라이드 행<br>없으면 `null` |
| `items[].override.amount` | `integer` | |
| `items[].override.effectiveUntil` | `string / null` | `null`은 상시 |
| `items[].override.updatedAt` | `string` | |

<br>

**2. 실패 응답**

공통 실패만 있다.

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/credits/policies
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "items": [
    { "policyKey": "signup_reward", "defaultAmount": 1000, "effectiveAmount": 1000, "minimum": 1, "override": null },
    { "policyKey": "attendance_reward", "defaultAmount": 250, "effectiveAmount": 500, "minimum": 1, "override": { "amount": 500, "effectiveUntil": "2026-10-31T15:00:00Z", "updatedAt": "2026-10-21T01:00:00Z" } }
  ]
}
```

</details>

<br>

### 4-2-13 정책 오버라이드 기록

| 항목 | 값 |
|---|---|
| 요청 | `PUT /admin/credits/policies/{policyKey}` |
| 인증 | 관리자 |
| 성공 | 200<br>정책 오버라이드 조회의 항목 구조 |

**1. 경로와 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `policyKey` | 경로 | 필수 | 저장 키 7종 중 하나 |
| `amount` | `integer` | 필수 | 키별 최솟값 이상 10,000 이하 |
| `effectiveUntil` | `string` | 선택 | 종료 시각<br>현재 이후<br>생략하면 상시 |
| `reason` | `string` | 필수 | 사유<br>1~500자 |

- 키당 한 행이며 이미 있으면 덮어쓴다. 응답의 `effectiveAmount`는 갱신 전 스냅샷 값일 수 있다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 범위 밖 `amount`, 과거 `effectiveUntil`, `reason` 누락 |
| 404 | `NOT_FOUND` | 없는 정책 키 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
PUT /api/v1/admin/credits/policies/attendance_reward
Authorization: Bearer {adminToken}
Content-Type: application/json

{ "amount": 500, "effectiveUntil": "2026-10-31T15:00:00Z", "reason": "할로윈 출석 이벤트" }
```

**2) 400 Response body**

```json
{
  "timestamp": "2026-10-21T01:23:45.678Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "attendance_reward는 1 이상 10000 이하여야 합니다.",
  "path": "/api/v1/admin/credits/policies/attendance_reward",
  "details": []
}
```

</details>

<br>

### 4-2-14 정책 오버라이드 삭제

| 항목 | 값 |
|---|---|
| 요청 | `DELETE /admin/credits/policies/{policyKey}` |
| 인증 | 관리자 |
| 성공 | 200<br>정책 오버라이드 조회의 항목 구조 |

**1. 경로와 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `policyKey` | 경로 | 필수 | 저장 키 7종 중 하나 |
| `reason` | `string` | 필수 | 사유<br>1~500자 |

- 삭제 뒤 갱신 주기 안에 기본값으로 돌아간다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `reason` 누락 |
| 404 | `NOT_FOUND` | 없는 정책 키<br>오버라이드 행 없음 |

<br>

### 4-2-15 다른 도메인과의 경계

| 도메인 | PAYMENT가 제공하는 것 | PAYMENT가 사용하는 것 |
|---|---|---|
| ACCOUNT | 멱등 키 기반 적립과 월 상한 판정, 체험 스냅샷, 잔액과 당일 출석 여부, 기간별 보상 횟수, 정책값 `signup_reward`, `invite_reward`, `invite_monthly_cap` | 보상 신원, 계정 상태 검사, 체험 스냅샷 완료 시각 기록, 회원 조회 |
| STORY | 체험 예약과 복원, 선차감, 환불, 정책값 `story_creation_cost`, 잔액 부족과 한도 소진 예외 | 간편 제작 진행의 상태와 스토리 참조, 스토리 제목과 읽기 판정 |
| CHAT | 체험 예약과 복원, 항목 합산 선차감, 환불, 정책값 `chat_turn_cost`, `chat_image_cost`, 잔액 부족과 한도 소진 예외 | 채팅의 턴 수, 재생성 수, 스토리 참조 |
| NOTIFICATION | 출석 보상 멱등 키의 존재 | 없음 |
| ADMIN | 잔액, 완료와 환불 주문 조회, 지급과 소진 집계 | 관리자 요청자와 변경 감사 기록 |
| 모든 도메인 | 없음 | 인증 필터, 탈퇴 거부, 동의 게이트, 관리자 판정 필터 |

다른 도메인이 호출하는 연산의 입력과 결과는 다음과 같다. 상태 코드 변환은 호출 도메인이 한다.

| 연산 | 입력 | 결과 |
|---|---|---|
| 적립 | 회원, 양수 금액, 사유, 멱등 키, 참조, 월 상한 조건 | 적립 여부, 잔액, 상한 도달 여부 |
| 차감 | 회원, 항목 목록(양수 금액, 사유, 참조) | 잔액, 항목별 소모 행<br>부족하면 잔액 부족 예외 |
| 잔액 | 회원 | 만료되지 않은 잔액 |
| 멱등 키 존재 | 멱등 키 | 존재 여부 |
| 기간별 보상 횟수 | 회원, 사유, 기간, 키 패턴 | 횟수 |
| 게스트 예약 | 회원 여부, 기기 식별자, 카운터 | 복원에 쓸 기기 식별자<br>헤더가 없으면 거절, 한도를 소진했으면 한도 소진 예외 |
| 회원 예약 | 회원, 카운터 | 예약 여부<br>장애는 미예약 |
| 복원 | 기기 식별자 또는 회원, 카운터 | 회원 복원은 성공 여부 |
| 체험 스냅샷 | 회원, 기기 식별자 | 완료 여부 |
| 정책값 | 정책 키 | 현재 유효값 |
| 완료와 환불 주문 조회 | 커서<br>페이지 크기 | 완료 시각 내림차순의 주문과 다음 커서 |
| 지급과 소진 집계 | 시각 범위 | 지급 사유 합계와 소모 사유 합계의 절댓값 |

| 예외 | 앱 코드 | 의미 |
|---|---|---|
| 잔액 부족 | `INSUFFICIENT_CREDIT` | 회원의 활성 잔액이 소모액 미만 |
| 한도 소진 | `GUEST_TRIAL_LIMIT_EXCEEDED` | 게스트 카운터가 한도에 도달 |

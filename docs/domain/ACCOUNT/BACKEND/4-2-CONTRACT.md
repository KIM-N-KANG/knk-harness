# 4-2 계약

이 문서는 ACCOUNT 도메인 백엔드와 클라이언트, 다른 도메인 사이의 계약을 정한다. 엔드포인트별 요청 필드, 성공과 실패 응답의 필드와 예시, 도메인 경계를 다룬다.

처리 순서와 판정 규칙은 처리 흐름에, 앱 코드 전체 목록과 복구는 오류 처리에, 토큰과 코드의 취급은 보안에 있다. ([4-1 처리 흐름](4-1-PIPELINES.md), [5-3-2 앱 코드](5-3-ERROR-HANDLING.md#5-3-2-앱-코드), [5-1-6 비밀값과 코드 취급](5-1-SECURITY.md#5-1-6-비밀값과-코드-취급))

<br>

### 4-2-1 공통 규칙과 헤더

**1. 공통 규칙**

| 항목 | 규칙 |
|---|---|
| 경로 | `/api/v1`을 생략해 적음 |
| JSON 필드 이름 | camelCase |
| 시각 | ISO 8601 UTC 문자열 |
| 문자 수 | UTF-16 코드 유닛 기준 |
| 식별자 | 회원, 페르소나, 스토리, 채팅은 UUID 공개 식별자 |
| 제공자 | 경로값과 응답은 소문자 `google`, `kakao`<br>재인증 요청 본문만 대문자 enum |
| 예시 값 | 모든 예시는 구조를 설명하기 위한 가상 값 |

<br>

**2. 인증 수준**

| 수준 | 토큰 없음 또는 무효 | 유효한 토큰 |
|---|---|---|
| `불필요` | 검사하지 않음 | 검사하지 않음<br>자동 첨부된 만료 토큰으로 막히지 않음 |
| `필수` | 거절 | 회원으로 처리 |

<br>

**3. 요청 헤더**

| 요청 헤더 | 값 형식 | 쓰임 | 필수 |
|---|---|---|---|
| `Authorization` | `Bearer {accessToken}` | 회원 식별 | 인증 수준에 따름 |
| `X-Manyak-Request-Id` | 문자열 | 로그 연결<br>없으면 서버가 생성하고 응답 헤더로 항상 반환 | 선택 |
| `X-Manyak-Session-Id` | 문자열 | 클라이언트 분석 세션 식별 | 선택 |
| `X-Manyak-Device-Id` | 문자열 | 회원 체험 스냅샷의 기기 사용량 조회, 게스트 동의의 기기 식별 | 핸드오프 생성과 게스트 동의는 필수 |
| `X-Manyak-Consent-Token` | 문자열 | 동의 완료 전용 대기 코드 | 동의 완료는 필수 |
| `X-Manyak-Handoff-Code` | 문자열 | 핸드오프 확인과 상태 조회 | 해당 요청은 필수 |
| `X-Manyak-Link-Code` | 문자열 | 계정 연동 | 연동은 필수 |

<br>

**4. 계정 상태 규칙**

| 요청 | 정지 계정 | 탈퇴 계정 |
|---|---|---|
| 소셜 인증, 동의 완료 | 처리<br>동의가 없으면 동의 대기 | 재가입으로 처리 |
| 호환 로그인 | 처리 | 재가입으로 처리 |
| 세션 조회, 탈퇴, 내 콘텐츠 목록 | 처리 | 401 |
| 토큰 회전 | 세션 폐기와 403 | 세션 폐기와 401 |
| 이관, 연동 재인증, 연동, 프로필 수정, 페르소나 생성, 수정, 삭제, 회원 동의 조회와 기록, 초대 조회와 제출 | 403 | 401 |

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
| `details` | `object[]` | 선언적 필드 검증과 쿼리 타입 변환 실패 시 `field`와 `message` 포함<br>그 외는 빈 배열 |

| `details[].field` 규칙 | 값 |
|---|---|
| 필드 검증 | 필드명 |
| 본문 파싱 실패 | 빈 `details` |

각 절의 실패 표에는 해당 엔드포인트에서 발생하는 상태와 `code`를 적는다. 다음 공통 실패는 각 절에서 생략한다.

| 상태 | `code` | 조건 |
|---|---|---|
| 401 | `UNAUTHORIZED` | 인증 필수 경로의 토큰 누락, 만료, 위조, 주체 형식 오류, 사용자 없음<br>확인된 탈퇴 계정 |
| 403 | `FORBIDDEN` | 정지 계정의 쓰기 요청<br>계정 상태 규칙 표의 403 |
| 403 | `CONSENT_REQUIRED` | 동의 게이트가 켜진 환경에서 미동의 회원의 허용 목록 밖 요청 |
| 500 | `INTERNAL_SERVER_ERROR` | 예상하지 못한 오류 |

<br>

**6. 공통 응답 구조**

소셜 인증 완료, 동의 완료, 호환 로그인, 토큰 회전은 같은 토큰 응답 구조를 쓴다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `accessToken` | `string` | 접근 토큰, `Authorization` 헤더에 실음 |
| `refreshToken` | `string` | 갱신 토큰, 1회용 |
| `expiresIn` | `integer` | 접근 토큰 만료까지 남은 초 |
| `tokenType` | `string` | 항상 `Bearer` |
| `isNewUser` | `boolean` | 이번 요청으로 계정이 새로 생성됐는지<br>기존 계정 로그인과 회전은 항상 `false` |

세션 조회와 프로필 수정은 같은 세션 응답 구조를 쓴다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `id` | `string` | 회원 공개 식별자 |
| `nickname` | `string` | |
| `profileImageUrl` | `string / null` | 프리셋 원본 이미지 URL |
| `profileThumbnailBase64` | `string / null` | 48×48 인라인 썸네일 |
| `status` | `string` | `ACTIVE`, `SUSPENDED` |
| `creditBalance` | `integer` | 이프 잔액, 지갑이 없으면 0 |
| `attendedToday` | `boolean` | KST 자정 기준 당일 출석 보상 적립 여부 |
| `linkedProviders` | `string[]` | 연동된 제공자, `google`, `kakao` 순 |

소셜 인증 대기 응답, 회원 동의, 게스트 동의는 같은 동의 상태 구조를 쓴다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `requiredVersion` | `string` | 현행 버전 |
| `needsConsent` | `boolean` | 현행 버전의 동의 기록이 없으면 `true` |

<br>

### 4-2-2 소셜 인증

| 항목 | 값 |
|---|---|
| 요청 | `POST /auth/social/{provider}` |
| 인증 | 불필요 |
| 성공 | 200 |

**1. 경로와 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `provider` | 경로 | 필수 | `google`, `kakao` |
| `idToken` | `string` | 필수 | 제공자가 발급한 OIDC ID 토큰 |
| `handoffCode` | `string` | 선택 | 핸드오프 코드<br>유효하지 않으면 무시하고 로그인 진행 |

<br>

**2. 응답**

`status`에 따라 실리는 필드가 다르다. 없는 필드는 응답에서 생략한다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `status` | `string` | `COMPLETED`, `CONSENT_REQUIRED` |
| `token` | `object` | `COMPLETED`일 때 토큰 응답 |
| `consentToken` | `string` | `CONSENT_REQUIRED`일 때 동의 완료 전용 코드<br>다른 API의 인증 수단이 아님 |
| `expiresAt` | `string` | 대기 코드 만료 시각 |
| `isNewUser` | `boolean` | 조회 시점에 계정이 없었는지<br>신규와 재가입은 `true` |
| `consents` | `object` | `terms`, `privacy`, `age14`의 동의 상태<br>신규와 재가입은 셋 다 `needsConsent` `true` |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 지원하지 않는 제공자, `idToken` 누락, 본문 파싱 실패 |
| 401 | `UNAUTHORIZED` | ID 토큰 검증 실패<br>서명, 만료, 발급자, 대상, 공개 키 조회 실패를 구분하지 않음 |
| 500 | `INTERNAL_SERVER_ERROR` | 계정 저장 중 DB 오류<br>원인을 싣지 않은 고정 문구 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/auth/social/google
Content-Type: application/json
X-Manyak-Device-Id: 2b7e1c4a-5d6f-4a8b-9c0d-1e2f3a4b5c6d

{
  "idToken": "<provider-id-token>",
  "handoffCode": "<optional-handoff-code>"
}
```

**2) 200 Response body, 동의 대기**

```json
{
  "status": "CONSENT_REQUIRED",
  "consentToken": "<opaque-code>",
  "expiresAt": "2026-10-16T00:10:00Z",
  "isNewUser": true,
  "consents": {
    "terms": { "requiredVersion": "v1.4", "needsConsent": true },
    "privacy": { "requiredVersion": "v1.7", "needsConsent": true },
    "age14": { "requiredVersion": "1", "needsConsent": true }
  }
}
```

**3) 200 Response body, 완료**

```json
{
  "status": "COMPLETED",
  "token": {
    "accessToken": "<access>",
    "refreshToken": "<refresh>",
    "expiresIn": 1800,
    "tokenType": "Bearer",
    "isNewUser": false
  }
}
```

**4) 401 Response body**

```json
{
  "timestamp": "2026-10-16T00:00:00Z",
  "status": 401,
  "code": "UNAUTHORIZED",
  "message": "유효하지 않은 ID 토큰입니다.",
  "path": "/api/v1/auth/social/google",
  "details": []
}
```

</details>

<br>

### 4-2-3 동의 완료

| 항목 | 값 |
|---|---|
| 요청 | `POST /auth/social/complete` |
| 인증 | 불필요, `X-Manyak-Consent-Token` 헤더 필수 |
| 성공 | 200, 토큰 응답 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `terms` | `string` | 조건부 | 동의한 이용약관 버전 |
| `privacy` | `string` | 조건부 | 동의한 개인정보 처리방침 버전 |
| `age14` | `string` | 조건부 | 만 14세 이상 확인 버전, `1` |

완료 시점에 현행 동의가 없는 항목이 필수다. 대기 응답 이후 다른 요청이 같은 계정에 동의를 기록했으면 그 항목은 생략할 수 있다. 보낸 값은 모두 현행 버전이어야 한다. `null`은 생략과 같다. 대기 중에 계정이 탈퇴했거나 문서가 개정되면 필요한 항목과 버전이 달라지므로 항목 누락이나 버전 불일치로 거절되고, 클라이언트는 소셜 인증부터 다시 시작해 현행 항목을 받는다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `CONSENT_VERSION_MISMATCH` | 보낸 값이 현행 버전과 다름<br>코드는 소비하지 않음 |
| 400 | `CONSENT_REQUIRED_MISSING` | 필요한 항목이 빠짐<br>코드는 소비하지 않음 |
| 400 | `BAD_REQUEST` | 본문 파싱 실패 |
| 401 | `CONSENT_TOKEN_INVALID` | 헤더 누락, 코드 없음, 만료, 소비됨<br>소셜 인증부터 다시 시작 |
| 500 | `INTERNAL_SERVER_ERROR` | 재조회로도 계정을 확정하지 못함, DB 오류 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/auth/social/complete
Content-Type: application/json
X-Manyak-Consent-Token: <opaque-code>

{
  "terms": "v1.4",
  "privacy": "v1.7",
  "age14": "1"
}
```

**2) 200 Response body**

```json
{
  "accessToken": "<access>",
  "refreshToken": "<refresh>",
  "expiresIn": 1800,
  "tokenType": "Bearer",
  "isNewUser": true
}
```

**3) 400 Response body**

```json
{
  "timestamp": "2026-10-16T00:00:00Z",
  "status": 400,
  "code": "CONSENT_VERSION_MISMATCH",
  "message": "현행 문서 버전을 확인하고 다시 동의해 주세요.",
  "path": "/api/v1/auth/social/complete",
  "details": []
}
```

</details>

<br>

### 4-2-4 호환 로그인

웹과 구버전 Android가 쓰는 경로다. 동의를 확인하지 않고 계정을 만든다.

| 항목 | 값 |
|---|---|
| 요청 | `POST /auth/login/{provider}` |
| 인증 | 불필요 |
| 성공 | 200, 토큰 응답 |

**1. 경로와 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `provider` | 경로 | 필수 | `google`, `kakao` |
| `idToken` | `string` | 필수 | 제공자가 발급한 OIDC ID 토큰 |
| `handoffCode` | `string` | 선택 | 핸드오프 코드<br>무효이면 무시 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `idToken` 누락, 본문 파싱 실패 |
| 401 | `UNAUTHORIZED` | ID 토큰 검증 실패 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/auth/login/kakao
Content-Type: application/json

{
  "idToken": "<provider-id-token>"
}
```

**2) 200 Response body**

```json
{
  "accessToken": "<access>",
  "refreshToken": "<refresh>",
  "expiresIn": 1800,
  "tokenType": "Bearer",
  "isNewUser": false
}
```

</details>

<br>

### 4-2-5 세션 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /auth/me` |
| 인증 | 필수 |
| 성공 | 200, 세션 응답 |

실패는 공통 실패뿐이다.

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) 200 Response body**

```json
{
  "id": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "nickname": "몽환적인이야기꾼",
  "profileImageUrl": "https://api.manyak.app/profile-presets/%EC%9D%B4%EC%95%BC%EA%B8%B0%EA%BE%BC.png",
  "profileThumbnailBase64": "iVBORw0KGgo...",
  "status": "ACTIVE",
  "creditBalance": 1000,
  "attendedToday": false,
  "linkedProviders": ["google"]
}
```

</details>

<br>

### 4-2-6 토큰 회전

| 항목 | 값 |
|---|---|
| 요청 | `POST /auth/token/refresh` |
| 인증 | 불필요 |
| 성공 | 200, 토큰 응답 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `refreshToken` | `string` | 필수 | 발급받은 갱신 토큰 |

<br>

**2. 응답**

정상 회전 시 새 접근 토큰과 새 갱신 토큰을 반환한다. 유예 조건을 만족하는 과거 토큰을 다시 제출하면 직전 회전에서 발급한 갱신 토큰과 새 접근 토큰을 반환한다. 유예 시간 안이라도 그 갱신 토큰으로 이미 다시 회전했으면 재사용으로 보고 세션을 폐기한다. `isNewUser`는 항상 `false`다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `refreshToken` 누락 |
| 401 | `UNAUTHORIZED` | 무효, 만료, 유예 조건 밖의 재사용, 사용자 없음, 탈퇴<br>재사용과 탈퇴는 세션 폐기 |
| 403 | `FORBIDDEN` | 정지 계정<br>세션 폐기 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/auth/token/refresh
Content-Type: application/json

{
  "refreshToken": "<refresh>"
}
```

**2) 401 Response body**

```json
{
  "timestamp": "2026-10-16T00:00:00Z",
  "status": 401,
  "code": "UNAUTHORIZED",
  "message": "유효하지 않은 refresh 토큰입니다.",
  "path": "/api/v1/auth/token/refresh",
  "details": []
}
```

</details>

<br>

### 4-2-7 로그아웃

| 항목 | 값 |
|---|---|
| 요청 | `POST /auth/logout` |
| 인증 | 불필요 |
| 성공 | 204, 본문 없음 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `refreshToken` | `string` | 필수 | 폐기할 갱신 토큰<br>그 토큰이 속한 세션 전체를 폐기 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `refreshToken` 누락 |

이미 폐기됐거나 발급된 적 없는 토큰도 204다. 접근 토큰은 폐기하지 않으므로 만료까지 유효하다.

<br>

### 4-2-8 핸드오프 생성

핸드오프 3종은 이미 발급된 외부 브라우저 전환 링크를 복구하는 데 쓴다. 현재 클라이언트는 새 핸드오프를 만들지 않는다.

| 항목 | 값 |
|---|---|
| 요청 | `POST /auth/handoffs` |
| 인증 | 불필요, `X-Manyak-Device-Id` 헤더 필수 |
| 성공 | 201 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `storyIds` | `string[]` | 선택 | 이관할 스토리 공개 식별자, 최대 100개, 기본값 빈 배열 |
| `chatIds` | `string[]` | 선택 | 이관할 채팅 공개 식별자, 최대 100개, 기본값 빈 배열 |
| `callbackPath` | `string` | 필수 | 로그인 후 복귀할 앱 내 상대 경로<br>`/`로 시작하고 `//`와 `/\`로 시작하지 않으며 ASCII 제어 문자 없이 512자 이내 |
| `sourceApp` | `string` | 필수 | `kakaotalk`, `instagram`, `threads` |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `handoffCode` | `string` | 1회용 코드<br>이 응답에서만 노출 |
| `handoffId` | `string` | 분석 전용 식별자, 비밀값 아님 |
| `expiresAt` | `string` | 만료 시각 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 디바이스 헤더 누락이나 공백, 배열 100개 초과, 식별자 형식 오류, 복귀 경로 규칙 위반, 출처 앱 허용값 밖 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/auth/handoffs
Content-Type: application/json
X-Manyak-Device-Id: 2b7e1c4a-5d6f-4a8b-9c0d-1e2f3a4b5c6d

{
  "storyIds": ["3f2504e0-4f89-41d3-9a0c-0305e82c3301"],
  "chatIds": ["7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d"],
  "callbackPath": "/chats/7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d",
  "sourceApp": "kakaotalk"
}
```

**2) 201 Response body**

```json
{
  "handoffCode": "<opaque-code>",
  "handoffId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
  "expiresAt": "2026-10-16T00:30:00Z"
}
```

</details>

<br>

### 4-2-9 핸드오프 확인

| 항목 | 값 |
|---|---|
| 요청 | `GET /auth/handoffs` |
| 인증 | 불필요, `X-Manyak-Handoff-Code` 헤더 필수 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `storyCount` | `integer` | 옮길 스토리 건수 |
| `chatCount` | `integer` | 옮길 채팅 건수 |
| `callbackPath` | `string` | 생성 시 저장한 복귀 경로 |
| `expiresAt` | `string` | 만료 시각 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 헤더 누락 |
| 404 | `NOT_FOUND` | 코드 없음, 만료<br>둘을 구분하지 않음 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) 200 Response body**

```json
{
  "storyCount": 1,
  "chatCount": 1,
  "callbackPath": "/chats/7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d",
  "expiresAt": "2026-10-16T00:30:00Z"
}
```

</details>

<br>

### 4-2-10 핸드오프 상태 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /auth/handoffs/status` |
| 인증 | 불필요, `X-Manyak-Handoff-Code` 헤더 필수 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `status` | `string` | `PENDING`, `LANDED`, `MIGRATED`, `MIGRATION_CLOSED` |
| `migratedStoryIds` | `string[]` | 이번 핸드오프에서 실제로 이관한 스토리 공개 식별자 |
| `migratedChatIds` | `string[]` | 이번 핸드오프에서 실제로 이관한 채팅 공개 식별자 |

| `status` | 의미 |
|---|---|
| `PENDING` | 생성됨, 외부 브라우저가 아직 받지 않음 |
| `LANDED` | 외부 랜딩이 코드를 확인함 |
| `MIGRATED` | 로그인 처리 중 핸드오프를 소비하고 결과를 저장함<br>실제로 이관된 항목이 없어도 이 상태 |
| `MIGRATION_CLOSED` | 로그인이 소비했으나 계정의 이관이 닫혀 이관하지 않음 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 헤더 누락 |
| 404 | `NOT_FOUND` | 코드 없음, 만료 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) 200 Response body**

```json
{
  "status": "MIGRATED",
  "migratedStoryIds": ["3f2504e0-4f89-41d3-9a0c-0305e82c3301"],
  "migratedChatIds": []
}
```

</details>

<br>

### 4-2-11 연동 재인증

| 항목 | 값 |
|---|---|
| 요청 | `POST /auth/links/reauth` |
| 인증 | 필수 |
| 성공 | 201 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `provider` | `string` | 필수 | `GOOGLE`, `KAKAO`<br>요청자에게 이미 연동된 제공자 |
| `idToken` | `string` | 필수 | 방금 발급받은 ID 토큰 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `linkCode` | `string` | 연동 요청의 `X-Manyak-Link-Code`에 실을 1회용 코드 |
| `expiresAt` | `string` | 만료 시각 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 로그인 경로가 없는 제공자, `idToken` 누락 |
| 403 | `REAUTH_FAILED` | ID 토큰 검증 실패, 발급 시각이 없거나 오래됨, 연동되지 않은 제공자, 제공자 쪽 식별자 불일치<br>사유를 구분하지 않음 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/auth/links/reauth
Authorization: Bearer <access>
Content-Type: application/json

{
  "provider": "GOOGLE",
  "idToken": "<fresh-provider-id-token>"
}
```

**2) 201 Response body**

```json
{
  "linkCode": "<opaque-code>",
  "expiresAt": "2026-10-16T00:05:00Z"
}
```

</details>

<br>

### 4-2-12 계정 연동

| 항목 | 값 |
|---|---|
| 요청 | `POST /auth/links/{provider}` |
| 인증 | 필수, `X-Manyak-Link-Code` 헤더 필수 |
| 성공 | 201, 본문 없음 |

**1. 경로와 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `provider` | 경로 | 필수 | 연동할 제공자 `google`, `kakao`<br>대소문자는 구분하지 않음 |
| `idToken` | `string` | 필수 | 연동할 제공자가 발급한 ID 토큰 |

연동 후 상태는 세션 조회의 `linkedProviders`로 확인한다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 알 수 없거나 로그인 경로가 없는 제공자, `idToken` 누락 |
| 403 | `REAUTH_FAILED` | 링크 코드 누락, 무효, 만료, 소비됨, 다른 회원이 발급받은 코드 |
| 403 | `SOCIAL_TOKEN_INVALID` | 연동할 ID 토큰 검증 실패 |
| 409 | `SOCIAL_ACCOUNT_WITHDRAWN` | 탈퇴한 계정에 연결됐던 소셜 계정<br>그 계정으로 로그인은 가능 |
| 409 | `PROVIDER_ALREADY_LINKED` | 이미 내게 연동된 소셜 계정이거나 그 제공자가 이미 연동됨 |
| 409 | `SOCIAL_ACCOUNT_LINKED_TO_OTHER_USER` | 다른 회원에게 연동된 소셜 계정 |

403과 409는 링크 코드를 소비하지 않는다.

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/auth/links/kakao
Authorization: Bearer <access>
X-Manyak-Link-Code: <opaque-code>
Content-Type: application/json

{
  "idToken": "<kakao-id-token>"
}
```

**2) 409 Response body**

```json
{
  "timestamp": "2026-10-16T00:00:00Z",
  "status": 409,
  "code": "SOCIAL_ACCOUNT_LINKED_TO_OTHER_USER",
  "message": "이미 다른 계정에 연동된 소셜 계정입니다.",
  "path": "/api/v1/auth/links/kakao",
  "details": []
}
```

</details>

<br>

### 4-2-13 게스트 이관

| 항목 | 값 |
|---|---|
| 요청 | `POST /auth/migrate` |
| 인증 | 필수 |
| 성공 | 200 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `storyIds` | `string[]` | 선택 | 스토리 공개 식별자, 최대 100개, 기본값 빈 배열 |
| `chatIds` | `string[]` | 선택 | 채팅 공개 식별자, 최대 100개, 기본값 빈 배열 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `migrationClosed` | `boolean` | `true`면 이관이 닫힌 계정이므로 항목을 평가하지 않음. 두 배열은 빈 배열<br>한 건이라도 `MIGRATED`가 나오면 이후 요청은 닫힘<br>빈 배열 요청을 포함해 계정당 5회까지만 평가하고 그 뒤는 닫힘 |
| `stories` | `object[]` | 항목별 결과 |
| `chats` | `object[]` | 항목별 결과 |
| `[].id` | `string` | 요청한 공개 식별자 |
| `[].status` | `string` | `MIGRATED`, `ALREADY_OWNED`, `CONFLICT`, `NOT_FOUND` |

| `status` | 의미 |
|---|---|
| `MIGRATED` | 이번 요청으로 소유권이 설정됨 |
| `ALREADY_OWNED` | 이미 요청자 소유 |
| `CONFLICT` | 다른 회원 소유 |
| `NOT_FOUND` | 없거나 삭제됨 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 식별자 형식 오류, 배열 100개 초과 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/auth/migrate
Authorization: Bearer <access>
Content-Type: application/json

{
  "storyIds": ["3f2504e0-4f89-41d3-9a0c-0305e82c3301"],
  "chatIds": ["7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d", "0d1e2f3a-4b5c-4d6e-8f7a-8b9c0d1e2f3a"]
}
```

**2) 200 Response body**

```json
{
  "migrationClosed": false,
  "stories": [
    { "id": "3f2504e0-4f89-41d3-9a0c-0305e82c3301", "status": "MIGRATED" }
  ],
  "chats": [
    { "id": "7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d", "status": "MIGRATED" },
    { "id": "0d1e2f3a-4b5c-4d6e-8f7a-8b9c0d1e2f3a", "status": "CONFLICT" }
  ]
}
```

**3) 200 Response body, 닫힌 계정**

```json
{
  "migrationClosed": true,
  "stories": [],
  "chats": []
}
```

</details>

<br>

### 4-2-14 프로필 수정

| 항목 | 값 |
|---|---|
| 요청 | `PATCH /users/me` |
| 인증 | 필수 |
| 성공 | 200, 세션 응답 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `nickname` | `string` | 조건부 | 새 닉네임<br>2~20자, 완성형 한글과 영문과 숫자만, 공백 불가<br>중복 판정은 소문자 변환과 공백 제거 기준 |
| `profileImagePreset` | `string` | 조건부 | 프리셋 키 |

둘 중 하나는 있어야 한다. 보낸 필드만 반영한다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 바꿀 항목 없음, 닉네임 규칙 위반, 없는 프리셋 키 |
| 409 | `NICKNAME_TAKEN` | 다른 회원이 정규화 기준으로 같은 닉네임을 사용 중 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
PATCH /api/v1/users/me
Authorization: Bearer <access>
Content-Type: application/json

{
  "nickname": "달빛작가",
  "profileImagePreset": "작가"
}
```

**2) 409 Response body**

```json
{
  "timestamp": "2026-10-16T00:00:00Z",
  "status": 409,
  "code": "NICKNAME_TAKEN",
  "message": "이미 사용 중인 닉네임입니다.",
  "path": "/api/v1/users/me",
  "details": []
}
```

</details>

<br>

### 4-2-15 프리셋 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /profile-presets` |
| 인증 | 필수 |
| 성공 | 200, 배열 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `[].key` | `string` | 프리셋 키, 프로필 수정의 `profileImagePreset` 값 |
| `[].imageUrl` | `string` | 원본 이미지 URL, 256×256 |
| `[].thumbnailBase64` | `string / null` | 48×48 인라인 썸네일 |

순서는 고정이다. 실패는 공통 실패뿐이다.

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) 200 Response body**

```json
[
  {
    "key": "이야기꾼",
    "imageUrl": "https://api.manyak.app/profile-presets/%EC%9D%B4%EC%95%BC%EA%B8%B0%EA%BE%BC.png",
    "thumbnailBase64": "iVBORw0KGgo..."
  }
]
```

</details>

<br>

### 4-2-16 페르소나 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /users/me/personas` |
| 인증 | 필수 |
| 성공 | 200, 배열 |

**1. 응답**

페르소나 생성과 수정도 같은 응답 구조를 쓴다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `id` | `string` | 공개 식별자 |
| `name` | `string` | |
| `description` | `string` | |
| `createdAt` | `string` | |
| `updatedAt` | `string` | |

페르소나가 없으면 빈 배열을 반환한다. 생성 최신순으로 정렬한다. 실패는 공통 실패뿐이다.

<br>

### 4-2-17 페르소나 생성

| 항목 | 값 |
|---|---|
| 요청 | `POST /users/me/personas` |
| 인증 | 필수 |
| 성공 | 201, 페르소나 응답 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `name` | `string` | 필수 | 앞뒤 공백 제거 후 1~20자 |
| `description` | `string` | 필수 | 앞뒤 공백 제거 후 1~1,000자 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 누락, 공백뿐, 길이 위반<br>`details[].field`에 필드명 |
| 409 | `CONFLICT` | 삭제되지 않은 페르소나가 10개 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/users/me/personas
Authorization: Bearer <access>
Content-Type: application/json

{
  "name": "은하",
  "description": "별을 쫓는 떠돌이 천문학자"
}
```

**2) 201 Response body**

```json
{
  "id": "5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b",
  "name": "은하",
  "description": "별을 쫓는 떠돌이 천문학자",
  "createdAt": "2026-10-16T00:00:00Z",
  "updatedAt": "2026-10-16T00:00:00Z"
}
```

**3) 400 Response body**

```json
{
  "timestamp": "2026-10-16T00:00:00Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "페르소나 입력이 올바르지 않습니다.",
  "path": "/api/v1/users/me/personas",
  "details": [
    { "field": "name", "message": "앞뒤 공백을 제외하고 1~20자여야 합니다." }
  ]
}
```

</details>

<br>

### 4-2-18 페르소나 수정

| 항목 | 값 |
|---|---|
| 요청 | `PATCH /users/me/personas/{personaId}` |
| 인증 | 필수 |
| 성공 | 200, 페르소나 응답 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `name` | `string` | 조건부 | 앞뒤 공백 제거 후 1~20자 |
| `description` | `string` | 조건부 | 앞뒤 공백 제거 후 1~1,000자 |

둘 중 하나는 있어야 한다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 바꿀 항목 없음, 공백뿐, 길이 위반 |
| 404 | `NOT_FOUND` | 식별자 형식 오류, 없음, 삭제됨, 타인 소유 |

<br>

### 4-2-19 페르소나 삭제

| 항목 | 값 |
|---|---|
| 요청 | `DELETE /users/me/personas/{personaId}` |
| 인증 | 필수 |
| 성공 | 204, 본문 없음 |

**1. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 404 | `NOT_FOUND` | 식별자 형식 오류, 없음, 이미 삭제됨, 타인 소유 |

<br>

### 4-2-20 회원 동의 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /users/me/consents` |
| 인증 | 필수 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `terms` | `object` | 이용약관 동의 상태 |
| `privacy` | `object` | 개인정보 처리방침 동의 상태 |
| `age14` | `object` | 만 14세 이상 확인 동의 상태, `requiredVersion`은 `1` |

실패는 공통 실패뿐이다.

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) 200 Response body**

```json
{
  "terms": { "requiredVersion": "v1.4", "needsConsent": false },
  "privacy": { "requiredVersion": "v1.7", "needsConsent": true },
  "age14": { "requiredVersion": "1", "needsConsent": false }
}
```

</details>

<br>

### 4-2-21 회원 동의 기록

| 항목 | 값 |
|---|---|
| 요청 | `POST /users/me/consents` |
| 인증 | 필수 |
| 성공 | 200, 회원 동의 조회와 같은 응답 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `terms` | `string` | 조건부 | 동의한 버전 |
| `privacy` | `string` | 조건부 | 동의한 버전 |
| `age14` | `string` | 조건부 | `1` |

하나 이상 있어야 한다. 누락과 `null`은 미제출이며 철회가 아니다. 같은 버전의 재제출은 최초 동의 시각을 유지한다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 전부 미제출, 본문 파싱 실패 |
| 400 | `CONSENT_VERSION_MISMATCH` | 보낸 값이 현행 버전과 다름<br>클라이언트는 현행 문서를 다시 표시해 동의를 받아 재제출하고, 동의 없이 버전 값만 바꿔 자동 재전송하지 않음 |

<br>

### 4-2-22 게스트 동의 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /guests/consents` |
| 인증 | 불필요, `X-Manyak-Device-Id` 헤더 필수 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `guestPrivacy` | `object` | 게스트 개인정보 수집 동의 상태 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 디바이스 헤더 누락이나 공백 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) 200 Response body**

```json
{
  "guestPrivacy": { "requiredVersion": "v1.0", "needsConsent": true }
}
```

</details>

<br>

### 4-2-23 게스트 동의 기록

| 항목 | 값 |
|---|---|
| 요청 | `POST /guests/consents` |
| 인증 | 불필요, `X-Manyak-Device-Id` 헤더 필수 |
| 성공 | 200, 게스트 동의 조회와 같은 응답 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `guestPrivacy` | `string` | 필수 | 동의한 현행 버전 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 디바이스 헤더 누락이나 공백, 미제출, 본문 파싱 실패 |
| 400 | `CONSENT_VERSION_MISMATCH` | 보낸 값이 현행 버전과 다름 |

<br>

### 4-2-24 회원 탈퇴

| 항목 | 값 |
|---|---|
| 요청 | `DELETE /users/me` |
| 인증 | 필수 |
| 성공 | 204, 본문 없음 |

실패는 공통 실패뿐이다.

<br>

### 4-2-25 내 스토리 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /users/me/stories` |
| 인증 | 필수 |
| 성공 | 200, 스토리 카드 배열 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `limit` | `integer` | 선택 | 최대 개수, 기본값 100<br>1 미만은 1, 100 초과는 100으로 보정 |

<br>

**2. 응답**

스토리 카드 구조는 STORY 도메인의 일괄 조회와 같다. ([STORY 4-2-7 일괄 조회](../../STORY/BACKEND/4-2-CONTRACT.md#4-2-7-일괄-조회)) 생성 최신순으로 정렬한다. 삭제된 스토리는 제외한다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `limit`이 정수가 아님 |

<br>

### 4-2-26 내 채팅 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /users/me/chats` |
| 인증 | 필수 |
| 성공 | 200, 채팅 카드 배열 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `limit` | `integer` | 선택 | 최대 개수, 기본값 100<br>1 미만은 1, 100 초과는 100으로 보정 |

<br>

**2. 응답**

채팅 카드 구조는 CHAT 도메인의 일괄 조회와 같다. ([CHAT 4-2-3 일괄 조회](../../CHAT/BACKEND/4-2-CONTRACT.md#4-2-3-일괄-조회)) 최근 활동순으로 정렬한다. 삭제된 채팅은 제외한다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `limit`이 정수가 아님 |

<br>

### 4-2-27 초대 코드 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /users/me/invite` |
| 인증 | 필수 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `inviteCode` | `string` | 내 초대 코드, 대문자와 숫자 8자<br>처음 조회 때 발급하고 이후 같은 값 |
| `monthlyRewardCount` | `integer` | 이번 KST 월에 초대자로서 받은 보상 횟수 |
| `monthlyRewardLimit` | `integer` | 초대자 보상 월 상한, 이프 정책값 |

실패는 공통 실패뿐이다.

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) 200 Response body**

```json
{
  "inviteCode": "AB3XK9QZ",
  "monthlyRewardCount": 3,
  "monthlyRewardLimit": 10
}
```

</details>

<br>

### 4-2-28 초대 코드 제출

| 항목 | 값 |
|---|---|
| 요청 | `POST /users/me/invite/redeem` |
| 인증 | 필수 |
| 성공 | 200 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `code` | `string` | 필수 | 다른 회원의 초대 코드<br>앞뒤 공백과 소문자 허용 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `amount` | `integer` | 이번 요청으로 제출자에게 적립된 이프<br>이프 정책값 |
| `balance` | `integer` | 적립 후 제출자 잔액 |

초대자가 월 상한이면 초대자 적립만 건너뛰고 응답은 그대로 200이다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 빈 값, 정규화 후 대문자와 숫자 8자가 아님 |
| 404 | `NOT_FOUND` | 일치하는 코드 없음 |
| 409 | `INVITE_ALREADY_REDEEMED` | 이미 초대 코드를 제출한 계정 |
| 409 | `INVITE_SELF_CODE` | 자기 코드 |
| 409 | `INVITE_INVITER_WITHDRAWN` | 초대자가 탈퇴 |
| 409 | `INVITE_INVITER_UNAVAILABLE` | 초대자가 정지 |
| 409 | `INVITE_INVITER_NEWER` | 초대자가 제출자보다 나중에 가입 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
POST /api/v1/users/me/invite/redeem
Authorization: Bearer <access>
Content-Type: application/json

{
  "code": " ab3xk9qz "
}
```

**2) 200 Response body**

```json
{
  "amount": 2000,
  "balance": 3000
}
```

**3) 409 Response body**

```json
{
  "timestamp": "2026-10-16T00:00:00Z",
  "status": 409,
  "code": "INVITE_ALREADY_REDEEMED",
  "message": "이미 초대 코드를 입력한 계정입니다.",
  "path": "/api/v1/users/me/invite/redeem",
  "details": []
}
```

</details>

<br>

### 4-2-29 다른 도메인과의 경계

| 도메인 | ACCOUNT가 제공하는 것 | ACCOUNT가 사용하는 것 |
|---|---|---|
| STORY | 요청자 식별, 계정 상태 검사, 소유자 프로필, 이관 시 소유권 설정, 닉네임 변경 시 재색인 요청 이벤트, 탈퇴 시 초안과 제출본 삭제 호출 | 내 스토리 목록 조회 메서드와 카드 구조, 스토리와 간편 제작 진행의 조건부 소유권 설정 |
| CHAT | 요청자 식별, 계정 상태 검사, 페르소나 스냅샷, 이관 시 소유권 설정과 도달 집계 보정 | 내 채팅 목록 조회 메서드와 카드 구조, 채팅의 조건부 소유권 설정 |
| PAYMENT | 보상 신원, 가입과 초대 보상의 멱등 키와 월 상한 조건 | 보상 적립, 체험 사용량 스냅샷, 잔액과 당일 출석 조회, 초대자 월 보상 횟수, 정책값 `signup_reward`, `invite_reward`, `invite_monthly_cap` |
| NOTIFICATION | 탈퇴 시 푸시 토큰 삭제 호출 | 없음 |
| MODERATION | 탈퇴 시 제출본 삭제 호출 | 없음 |
| 모든 도메인 | 인증 필터, 탈퇴 거부, 동의 게이트와 허용 목록 | 없음 |

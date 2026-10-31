# 4-2 계약

이 문서는 CHAT 도메인 백엔드와 클라이언트, 다른 도메인 사이의 계약을 정한다. 엔드포인트별 요청 필드, 성공과 실패 응답의 필드와 예시, SSE 이벤트, 도메인 경계를 다룬다.

AI 서버로 보내는 값과 받은 값의 처리는 처리 흐름에, 앱 코드 전체 목록과 복구는 오류 처리에, 소유 판정의 보안 관점은 보안에 있다. ([4-1-6 이어쓰기](4-1-PIPELINES.md#4-1-6-이어쓰기), [4-1-8 선택지 생성](4-1-PIPELINES.md#4-1-8-선택지-생성), [5-3-2 앱 코드](5-3-ERROR-HANDLING.md#5-3-2-앱-코드), [5-1-2 소유권 판정](5-1-SECURITY.md#5-1-2-소유권-판정))

<br>

### 4-2-1 공통 규칙과 헤더

**1. 공통 규칙**

| 항목 | 규칙 |
|---|---|
| 경로 | `/api/v1`을 생략해 적음 |
| JSON 필드 이름 | camelCase |
| 시각 | ISO 8601 UTC 문자열 |
| 문자 수 | UTF-16 코드 유닛 기준 |
| 식별자 | 채팅, 스토리, 시작 설정, 페르소나, 공유는 UUID 공개 식별자<br>턴은 정수 ID |
| SSE | `Content-Type: text/event-stream;charset=UTF-8`<br>프레임은 `event: 이름`, `data: JSON`, 빈 줄<br>heartbeat 없음<br>처음 연결과 재연결 모두 생성 이벤트를 처음부터 수신 |
| 이미지 마커 | AI 응답 본문의 대사 줄 위 별도 줄에 `[[URL]]`과 빈 줄<br>클라이언트는 마커 줄 대신 해당 위치에 이미지를 표시 |
| 예시 값 | 모든 예시는 구조를 설명하기 위한 가상 값 |

<br>

**2. 인증 수준**

관리자 경로(`/admin/**`)를 제외한 엔드포인트의 인증 수준은 `선택`이다. 관리자 경로의 판정은 ADMIN 세트의 관리자 판정 필터가 맡는다. ([4-2-1 공통 규칙과 헤더](../../ADMIN/BACKEND/4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더))

| 수준 | 토큰 없음 또는 무효 | 유효한 앱 토큰 | 관리자 토큰 |
|---|---|---|---|
| `선택` | 익명으로 처리 | 회원으로 처리 | 익명으로 처리 |
| `관리자` | 거절 | 거절 | 관리자 역할과 계정 상태를 다시 확인해 통과 |

<br>

**3. 요청 헤더**

| 요청 헤더 | 값 형식 | 쓰임 | 필수 |
|---|---|---|---|
| `Authorization` | `Bearer {accessToken}` | 회원 식별 | 인증 수준에 따름 |
| `X-Manyak-Request-Id` | 문자열 | 로그와 AI 호출 연결<br>없으면 서버가 생성하고 응답 헤더로 항상 반환 | 선택 |
| `X-Manyak-Session-Id` | 문자열 | 클라이언트 분석 세션 식별<br>Amplitude 연결에는 정수 문자열이어야 함 | 선택 |
| `X-Manyak-Device-Id` | 문자열 | 게스트의 턴과 이미지 체험 한도 집계<br>AI 서버에는 해시로 전달<br>서버 분석 이벤트의 `device_id` | 게스트 이어쓰기와 재생성은 필수 |
| `User-Agent` | 문자열 | 피드백에 함께 저장 | 선택 |

<br>

**4. 소유 규칙**

| 요청 | 허용 |
|---|---|
| 채팅 생성 | 읽을 수 있는 스토리<br>소유자 없는 스토리는 익명 요청만 |
| 상세, 생성 스트림 재연결, 삭제, 이어쓰기, 재생성, 선택지, 공유 발급, 채팅 설정 변경 | 회원 소유 채팅은 소유자만<br>소유자 없는 채팅은 익명 요청만<br>위반은 403 |
| 모델 목록 | 누구나<br>프로모션 정보는 회원에게만 |
| 모델 프로모션 조회, 설정, 해제 | 관리자 |
| 일괄 조회 | 열람할 수 없는 채팅은 제외 |
| 공유 열람 | 토큰을 아는 누구나<br>회원이면 스토리 읽기 권한 판정에만 회원 정보 사용 |
| 페르소나 지정 | 회원만<br>본인 페르소나만 |

<br>

**5. 공통 실패 응답**

실패 응답은 모두 같은 형식이다. SSE 엔드포인트도 스트림을 열기 전의 실패는 이 형식의 JSON이다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `timestamp` | `string` | 응답 생성 시각 |
| `status` | `integer` | HTTP 상태 |
| `code` | `string` | HTTP 상태 이름 또는 앱 코드 |
| `message` | `string` | 사용자 안내 문구 |
| `path` | `string` | 요청 경로 |
| `details` | `object[]` | 필드 검증 실패 시 `field`와 `message` 포함<br>그 외는 빈 배열 |

| `details[].field` 규칙 | 값 |
|---|---|
| 필드 검증 | 필드명 |
| 객체 수준 검증 | 객체명 |
| 본문 파싱 실패 | 빈 `details` |

각 절의 실패 표에는 해당 엔드포인트에서 발생하는 상태와 `code`를 적는다. 다음 공통 실패는 각 절에서 생략한다.

| 상태 | `code` | 조건 |
|---|---|---|
| 401 | `UNAUTHORIZED` | 인증 선택 경로에서 확인된 탈퇴 계정 |
| 403 | `CONSENT_REQUIRED` | 동의 게이트가 켜진 환경에서 미동의 회원의 허용 목록 밖 요청 |
| 500 | `INTERNAL_SERVER_ERROR` | 예상하지 못한 오류 |

<details>
<summary><b>공통 실패 응답 예시</b></summary>

<br>

**1) 500 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 500,
  "code": "INTERNAL_SERVER_ERROR",
  "message": "서버 오류가 발생했습니다.",
  "path": "/api/v1/chats",
  "details": []
}
```

</details>

<br>

### 4-2-2 채팅 생성

| 항목 | 값 |
|---|---|
| 요청 | `POST /chats` |
| 인증 | 선택 |
| 성공 | 201 |

**1. 요청 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `storyId` | `string` | 필수 | 스토리 공개 식별자 |
| `startSettingId` | `string` | 선택 | 시작 설정 공개 식별자<br>생략하면 스토리의 첫 시작 설정 |
| `personaId` | `string` | 선택 | 내 페르소나 공개 식별자<br>생략하거나 `null`이면 기본 주인공 사용 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `id` | `string` | 채팅 공개 식별자<br>클라이언트가 보관해 목록 조회에 사용 |
| `storyId` | `string` | |
| `persona` | `object / null` | 선택한 페르소나 스냅샷<br>기본 주인공이면 `null` |
| `persona.name` | `string` | 페르소나 이름 |
| `model` | `string` | 저장한 모델 코드<br>새 채팅은 기본 모델 |
| `longResponse` | `boolean` | 출력 분량<br>새 채팅은 `false`(짧은 응답) |
| `prologue` | `string` | 플레이 이름으로 치환한 프롤로그<br>시작 설정이 없으면 빈 문자열 |
| `suggestedInputs` | `string[]` | 시작 화면의 추천 입력<br>없으면 빈 배열 |
| `createdAt` | `string` | |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `storyId` 누락 |
| 401 | `UNAUTHORIZED` | 게스트가 `personaId` 지정 |
| 403 | `FORBIDDEN` | 정지 계정<br>소유자 없는 스토리에 회원 요청 |
| 404 | `NOT_FOUND` | 스토리가 없거나 삭제됐거나 읽을 수 없음<br>시작 설정이 없거나 이 스토리에 속하지 않음<br>페르소나가 없거나 삭제됐거나 타인의 것<br>식별자 형식 오류 |

<details>
<summary><b>채팅 생성 요청, 응답 예시</b></summary>

<br>

**1) Request body**

```json
{
  "storyId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "startSettingId": "0b7c9d1e-3f4a-4b5c-8d6e-7f8091a2b3c4",
  "personaId": "9c5b94b1-35ad-49bb-b118-8e8fc24abf80"
}
```

<br>

**2) 201 Response body**

```json
{
  "id": "7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d",
  "storyId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "persona": { "name": "민우" },
  "model": "AURORA",
  "longResponse": false,
  "prologue": "마법 세계에서 민우는 호아킨 아카데미의 1학년으로 입학했다. 입학식 전 수행되는 적성 검사. 묘한 긴장감이 검사장을 감싼다.",
  "suggestedInputs": ["검사장을 둘러본다.", "마법수정에 손을 올린다.", "주변 학생들에게 말을 건다."],
  "createdAt": "2026-06-12T12:00:00Z"
}
```

<br>

**3) 404 Response body**

```json
{
  "timestamp": "2026-06-12T12:00:00Z",
  "status": 404,
  "code": "NOT_FOUND",
  "message": "스토리를 찾을 수 없습니다.",
  "path": "/api/v1/chats",
  "details": []
}
```

</details>

<br>

### 4-2-3 일괄 조회

| 항목 | 값 |
|---|---|
| 요청 | `POST /chats/batch` |
| 인증 | 선택 |
| 성공 | 200 |

**1. 요청 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `chatIds` | `string[]` | 필수 | 채팅 공개 식별자 1~100개<br>UUID 형식이 아닌 값과 없는 값은 제외 |

<br>

**2. 응답**

응답은 카드 배열이다. 갱신 시각 내림차순으로 정렬한다. 클라이언트는 이 순서를 유지한다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `[].id` | `string` | 채팅 공개 식별자 |
| `[].storyId` | `string` | |
| `[].storyTitle` | `string` | 읽을 수 있으면 현재 제목, 아니면 마지막 공개본의 제목 |
| `[].thumbnailUrlSm` | `string / null` | 스토리 표지의 축소 변형 URL<br>생성하거나 업로드한 표지는 원본 URL<br>표지가 없으면 `null` |
| `[].lastStoryPreview` | `string` | 마지막 AI 응답 전문<br>서버가 자르지 않음<br>턴이 없으면 빈 문자열 |
| `[].turnCount` | `integer` | 완료된 턴 수 |
| `[].reachedEndings` | `string[]` | 도달한 엔딩 이름<br>채팅당 최대 1개, 도달 전 빈 배열<br>기본 주인공 이름으로 치환해 상세와 완료 이벤트의 플레이 이름 표기와 다를 수 있음 |
| `[].updatedAt` | `string` | 마지막 진행 시각 |
| `[].persona` | `object / null` | 채팅 시작 시 페르소나 스냅샷 `{name}` |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 빈 배열, 101개 이상 |

<details>
<summary><b>일괄 조회 요청, 응답 예시</b></summary>

<br>

**1) Request body**

```json
{ "chatIds": ["7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d", "9c5b94b1-35ad-49bb-b118-8e8fc24abf80"] }
```

<br>

**2) 200 Response body**

```json
[
  {
    "id": "7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d",
    "storyId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
    "storyTitle": "호아킨 아카데미의 무속성 신입생",
    "thumbnailUrlSm": "https://cdn.example.com/thumbnails/thumb_0012_sm.png",
    "lastStoryPreview": "검사장은 한순간 숨소리조차 사라진 듯 조용해졌다.",
    "turnCount": 2,
    "reachedEndings": [],
    "updatedAt": "2026-06-12T12:10:00Z",
    "persona": { "name": "민우" }
  }
]
```

</details>

<br>

### 4-2-4 상세

| 항목 | 값 |
|---|---|
| 요청 | `GET /chats/{chatId}` |
| 인증 | 선택 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `id` | `string` | |
| `storyId` | `string` | |
| `storyTitle` | `string` | 읽을 수 있으면 현재 제목, 아니면 마지막 공개본의 제목 |
| `persona` | `object / null` | 생성 응답과 같은 스냅샷 |
| `model` | `string` | 유효 모델 코드<br>보관한 모델이 노출 중이면 그 코드, 아니면 기본 모델 코드<br>게스트 채팅도 보관한 값을 반환하며 턴은 라이트(`LITE`)로 처리 |
| `longResponse` | `boolean` | 채팅에 보관한 출력 분량<br>`false`는 짧은 응답, `true`는 긴 응답<br>게스트 채팅의 턴에도 그대로 적용 |
| `prologue` | `string` | 플레이 이름으로 치환 |
| `turns` | `object[]` | 완료된 턴을 순서대로 제공 |
| `turns[].id` | `integer` | 턴 ID |
| `turns[].userInput` | `string` | |
| `turns[].aiOutput` | `string` | 활성본 전문<br>이미지 마커 포함 |
| `turns[].choices` | `string[]` | 저장된 선택지<br>아직 생성하지 않았으면 빈 배열 |
| `turns[].reachedEnding` | `string / null` | 이 턴이 도달 턴이면 엔딩 이름 |
| `turns[].createdAt` | `string` | |
| `generatingTurn` | `object / null` | 생성 중 키가 있을 때만 객체<br>키 부재, Redis 읽기 오류, 저장된 값 해석 실패 시 `null`<br>오류 처리는 [5-3 오류 처리](5-3-ERROR-HANDLING.md#5-3-3-오류-분류) 참조 |
| `generatingTurn.type` | `string` | `CONTINUE`(이어쓰기) 또는 `REGENERATE`(재생성) |
| `generatingTurn.userInput` | `string` | 생성 중인 사용자 입력 |
| `generatingTurn.startedAt` | `string` | 요청 접수 시각<br>ISO 8601 UTC 문자열 |
| `generatingTurn.targetTurnId` | `integer / null` | 재생성 대상의 `turns[].id`<br>이어쓰기는 `null`로 항상 포함 |
| `generatingTurn.generationId` | `string` | 생성 ID<br>UUID 문자열 |
| `suggestedInputs` | `string[]` | 턴이 없을 때만 추천 입력<br>턴이 있으면 빈 배열 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 403 | `FORBIDDEN` | 소유자가 아님<br>회원이 소유자 없는 채팅을 조회 |
| 404 | `NOT_FOUND` | 없거나 삭제됨, 형식 오류 |

<details>
<summary><b>상세 응답 예시</b></summary>

<br>

**1) 200 Response body: 생성 중인 턴 없음**

```json
{
  "id": "7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d",
  "storyId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "storyTitle": "호아킨 아카데미의 무속성 신입생",
  "persona": null,
  "model": "AURORA",
  "longResponse": false,
  "prologue": "마법 세계에서 당신은 호아킨 아카데미의 1학년으로 입학했다.",
  "turns": [
    {
      "id": 1201,
      "userInput": "검사장을 둘러본다.",
      "aiOutput": "*검사장은 한순간 숨소리조차 사라진 듯 조용해졌다.*\n[[https://cdn.example.com/characters/generated/3f2504e0/9b1c.webp]]\n\n교관: 다음, 앞으로.",
      "choices": ["단상 앞으로 나선다.", "주변 학생들의 반응을 살핀다.", "조용히 자리를 벗어난다."],
      "reachedEnding": null,
      "createdAt": "2026-06-12T12:05:00Z"
    }
  ],
  "suggestedInputs": [],
  "generatingTurn": null
}
```

<br>

**2) 200 Response body: 이어쓰기 생성 중**

```json
{
  "id": "7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d",
  "storyId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "storyTitle": "호아킨 아카데미의 무속성 신입생",
  "persona": null,
  "model": "LITE",
  "longResponse": true,
  "prologue": "마법 세계에서 당신은 호아킨 아카데미의 1학년으로 입학했다.",
  "turns": [
    {
      "id": 1201,
      "userInput": "검사장을 둘러본다.",
      "aiOutput": "*검사장은 한순간 숨소리조차 사라진 듯 조용해졌다.*\n[[https://cdn.example.com/characters/generated/3f2504e0/9b1c.webp]]\n\n교관: 다음, 앞으로.",
      "choices": [
        "단상 앞으로 나선다.",
        "주변 학생들의 반응을 살핀다.",
        "조용히 자리를 벗어난다."
      ],
      "reachedEnding": null,
      "createdAt": "2026-06-12T12:05:00Z"
    }
  ],
  "suggestedInputs": [],
  "generatingTurn": {
    "type": "CONTINUE",
    "userInput": "단상 앞으로 나선다.",
    "startedAt": "2026-06-12T12:06:00Z",
    "targetTurnId": null,
    "generationId": "5e7b9a10-2c34-4d56-8e90-123456789abc"
  }
}
```

<br>

**3) 403 Response body**

```json
{
  "timestamp": "2026-06-12T12:00:00Z",
  "status": 403,
  "code": "FORBIDDEN",
  "message": "채팅을 조회할 권한이 없습니다.",
  "path": "/api/v1/chats/7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d",
  "details": []
}
```

</details>

<br>

### 4-2-5 삭제

| 항목 | 값 |
|---|---|
| 요청 | `DELETE /chats/{chatId}` |
| 인증 | 선택 |
| 성공 | 204, 본문 없음 |

**1. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 403 | `FORBIDDEN` | 소유자가 아님 |
| 404 | `NOT_FOUND` | 없거나 이미 삭제됨, 형식 오류 |

<br>

### 4-2-6 이어쓰기

| 항목 | 값 |
|---|---|
| 요청 | `POST /chats/{chatId}/turns/stream` |
| 인증 | 선택 |
| 성공 | 200, SSE |

회원 턴은 채팅의 유효 모델로 생성하고 그 모델의 적용 가격을 매긴다. 적용 가격이 0이면 체험을 쓰지 않고 무료다. 적용 가격이 0보다 크면 유효 모델이 라이트(`LITE`)일 때 턴 체험 잔여를 먼저 써서 무료이고 잔여가 없으면 적용 가격을 선차감한다. 다른 모델은 체험 잔여와 무관하게 적용 가격을 선차감한다. 게스트 턴은 선택한 모델과 무관하게 라이트(`LITE`)로 생성하고 체험 횟수를 예약한다. 모델별 가격은 모델 목록이 기준이다. 잔액 부족과 한도 소진은 스트림을 열기 전에 JSON으로 거절한다. 생성 중 재전송은 거절한다. 생성이 끝난 뒤 같은 입력을 다시 보내면 마지막 턴 검사를 거쳐 새 턴으로 과금한다. 연결이 끊겨도 생성과 저장을 계속한다. 엔딩에 도달한 채팅도 이어쓰기와 선택지 생성은 할 수 있다.

**1. 요청 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `userInput` | `string` | 필수 | 공백만 있으면 안 되고 3,000자 이하 |
| `lastTurnId` | `integer / null` | 선택 | 클라이언트가 본 마지막 턴의 `turns[].id`<br>첫 턴은 명시적 `null`<br>생략하면 마지막 턴 비교를 건너뛰어 구버전 앱 허용<br>명시적 `null`은 서버에도 완료된 턴이 없을 때만 일치<br>선택 기록용 `sourceTurnId`와 별개 |
| `userSource` | `string` | 선택 | `choice`, `edited_choice`, `typed`<br>AI에 그대로 전달하고 생략하면 전달하지 않음 |
| `sourceTurnId` | `integer` | 선택 | 고른 선택지가 속한 직전 턴의 ID<br>현재 마지막 턴이 아니거나 다른 채팅의 턴이면 기록만 생략 |
| `choiceOrder` | `integer` | 선택 | 고른 선택지의 순번, 1부터<br>`turns[].choices` 인덱스 + 1<br>범위 밖은 기록만 생략 |
| `realtimeImage` | `boolean` | 선택 | 실시간 이미지 생성 여부, 기본값 `true`<br>`true`라도 저장소 미설정이나 게스트의 이미지 체험 소진이면 생성 없이 진행<br>회원은 이미지 체험을 다 쓰면 이미지 비용을 턴 비용과 합산해 차감 |

<br>

**2. 이벤트**

순서는 `started`, `token` 반복, `completed` 또는 `error`다. `character_image`는 `token` 사이에 전송될 수 있다.

| 이벤트 | 필드명 | 타입 | 의미 |
|---|---|---|---|
| `started` | `chatId` | `string` | 스트림 시작 |
| `started` | `generationId` | `string` | 생성 ID<br>UUID 문자열<br>같은 화면에서 연결 종료 후 재연결할 때 사용 |
| `token` | `text` | `string` | AI 본문 조각 |
| `character_image` | `name` | `string` | 인물 이름 |
| `character_image` | `imageUrl` | `string` | 인물 이미지 URL<br>한 턴에서 인물마다 첫 대사 앞에 한 번 |
| `completed` | `chatId` | `string` | |
| `completed` | `turnId` | `integer` | 저장된 턴 ID |
| `completed` | `aiOutput` | `string` | 저장된 본문 전체<br>이미지 마커 포함<br>검증으로 토큰 누적분과 달라질 수 있어 클라이언트는 이 값으로 교체 |
| `completed` | `choices` | `string[]` | 항상 빈 배열<br>선택지는 별도 요청으로 생성 |
| `completed` | `reachedEnding` | `string / null` | 이번 턴이 도달 턴이면 엔딩 이름 |
| `error` | `code` | `string` | AI 서버가 보낸 코드 또는 `AI_STREAM_FAILED`<br>저장 시 마지막 턴 불일치는 `CHAT_TURN_STALE` |
| `error` | `message` | `string` | AI 서버가 보낸 문구 또는 고정 문구 |

처음 연결인 이어쓰기와 재생성 POST는 자기 생성의 스트림을 기다리며 404로 판정하지 않는다. 큐 대기 중 아직 이벤트가 없어도 기다린다. 생성 작업이 기록한 이벤트를 Redis Streams에서 처음부터 읽고 이후 이벤트를 이어서 받는다. 재연결도 같은 이벤트 순서와 본문을 사용한다. 클라이언트는 누적 본문을 비운 뒤 처음부터 다시 구성하고 `completed.aiOutput`으로 확정한다. 재연결은 생성이나 과금을 다시 시작하지 않는다.

`started.generationId`를 받은 클라이언트는 같은 화면에서 연결이 끊겨도 해당 생성으로 바로 재연결한다. 재진입한 클라이언트는 상세의 `generatingTurn.generationId`로 재연결한다. `completed`와 `error` 없이 스트림이 끝나면 상세를 다시 조회한다. 이어쓰기는 생성 중 키가 사라졌는데 새 턴이 없으면 실패로 안내한다. 재생성은 턴 ID와 턴 수가 유지된다. 1단계(KNK-1677)에서는 이탈 중 재생성의 성공과 실패를 상세만으로 구분하지 못한다. 2단계는 클라이언트가 생성 ID를 받아 보관한 경우(`started` 또는 생성 중 상세에서 수신)에만 보관된 스트림의 `completed` 또는 `error`로 재생성의 성공과 실패를 구분한다. `started` 전에 이탈하고 생성이 끝난 뒤 돌아와 생성 ID를 모르면 1단계와 같은 한계가 남는다. `error`를 받아도 저장된 턴이 있을 수 있으므로 다시 보내기 전에 상세를 확인한다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `userInput` 공백이나 3,001자 이상, `userSource` 허용값 밖<br>게스트의 `X-Manyak-Device-Id` 누락 |
| 402 | `INSUFFICIENT_CREDIT` | 회원의 이프 부족 |
| 402 | `GUEST_TRIAL_LIMIT_EXCEEDED` | 게스트의 턴 체험 소진 |
| 403 | `FORBIDDEN` | 정지 계정<br>소유자가 아님 |
| 404 | `NOT_FOUND` | 채팅이 없거나 삭제됨, 형식 오류 |
| 409 | `CHAT_TURN_IN_PROGRESS` | 같은 채팅의 이어쓰기나 재생성이 생성 중 |
| 503 | `SERVICE_UNAVAILABLE` | Redis 오류로 생성 중 키를 획득하지 못함<br>과금 없음 |
| 409 | `CHAT_TURN_STALE` | 제공한 `lastTurnId`가 서버의 마지막 턴과 불일치 |

<details>
<summary><b>이어쓰기 요청, 응답 예시</b></summary>

<br>

**1) Request body**

```json
{
  "userInput": "단상 앞으로 나선다.",
  "userSource": "choice",
  "sourceTurnId": 1201,
  "lastTurnId": 1201,
  "choiceOrder": 1,
  "realtimeImage": true
}
```

<br>

**2) 200 Response stream**

```text
event: started
data: {"chatId":"7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d","generationId":"5e7b9a10-2c34-4d56-8e90-123456789abc"}

event: token
data: {"text":"*단상 위 "}

event: character_image
data: {"name":"교관","imageUrl":"https://cdn.example.com/chat-images/7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d/2-4c9e2b7a-1d3f-4a5b-8c6d-9e0f1a2b3c4d.webp"}

event: token
data: {"text":"교관: 손을 올리게."}

event: completed
data: {"chatId":"7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d","turnId":1203,"aiOutput":"*단상 위 마법수정이 희미하게 떨린다.*\n[[https://cdn.example.com/chat-images/7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d/2-4c9e2b7a-1d3f-4a5b-8c6d-9e0f1a2b3c4d.webp]]\n\n교관: 손을 올리게.","choices":[],"reachedEnding":null}
```

<br>

**3) error 이벤트**

```text
event: error
data: {"code":"AI_STREAM_FAILED","message":"AI 응답 생성 중 오류가 발생했습니다."}
```

<br>

**4) 402 Response body**

```json
{
  "timestamp": "2026-06-12T12:00:00Z",
  "status": 402,
  "code": "INSUFFICIENT_CREDIT",
  "message": "이프가 부족합니다.",
  "path": "/api/v1/chats/7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d/turns/stream",
  "details": []
}
```

</details>

<br>

### 4-2-7 재생성

| 항목 | 값 |
|---|---|
| 요청 | `POST /chats/{chatId}/turns/regenerate/stream` |
| 인증 | 선택 |
| 성공 | 200, SSE |

마지막 턴의 AI 응답을 같은 입력으로 다시 생성해 교체한다. 과금, 체험, 모델, 이벤트는 이어쓰기와 같다. 요청 시점의 유효 모델 가격을 차감하며 원래 턴의 모델을 이어받지 않는다. `completed`의 `turnId`는 교체한 턴의 ID를 그대로 유지한다.

**1. 요청 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `turnId` | `integer` | 필수 | 클라이언트가 보고 있는 마지막 턴 ID, 1 이상 |
| `realtimeImage` | `boolean` | 선택 | 기본값 `true` |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `turnId` 누락이나 0 이하<br>게스트의 `X-Manyak-Device-Id` 누락 |
| 402 | `INSUFFICIENT_CREDIT` | 회원의 이프 부족 |
| 402 | `GUEST_TRIAL_LIMIT_EXCEEDED` | 게스트의 턴 체험 소진 |
| 403 | `FORBIDDEN` | 정지 계정<br>소유자가 아님 |
| 404 | `NOT_FOUND` | 채팅이 없거나 삭제됨<br>턴이 없음 |
| 409 | `CHAT_TURN_IN_PROGRESS` | 같은 채팅의 이어쓰기나 재생성이 생성 중 |
| 503 | `SERVICE_UNAVAILABLE` | Redis 오류로 생성 중 키를 획득하지 못함<br>과금 없음 |
| 409 | `CHAT_TURN_STALE` | `turnId`가 마지막 턴이 아님 |
| 409 | `CHAT_ENDED` | 엔딩에 도달한 채팅 |

스트림을 연 뒤 저장 시점에 마지막 턴이 바뀌었으면 `CHAT_TURN_STALE`의 `error` 이벤트로 끝나고 환불한다.

<details>
<summary><b>재생성 요청, 응답 예시</b></summary>

<br>

**1) Request body**

```json
{ "turnId": 1203, "realtimeImage": false }
```

<br>

**2) 200 Response stream**

```text
event: started
data: {"chatId":"7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d","generationId":"5e7b9a10-2c34-4d56-8e90-123456789abc"}

event: token
data: {"text":"*검사장의 공기가 "}

event: completed
data: {"chatId":"7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d","turnId":1203,"aiOutput":"*검사장의 공기가 무겁게 가라앉는다.*\n\n교관: 천천히 올리게.","choices":[],"reachedEnding":null}
```

<br>

**3) 409 Response body**

```json
{
  "timestamp": "2026-06-12T12:00:00Z",
  "status": 409,
  "code": "CHAT_TURN_STALE",
  "message": "마지막 턴이 아니거나 이미 변경되었습니다.",
  "path": "/api/v1/chats/7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d/turns/regenerate/stream",
  "details": []
}
```

</details>

<br>

### 4-2-8 선택지 생성

| 항목 | 값 |
|---|---|
| 요청 | `POST /chats/{chatId}/turns/{turnId}/choices` |
| 인증 | 선택 |
| 성공 | 200 |

요청 본문은 없다. 무료이며 체험 한도를 소모하지 않는다. 이어쓰기와 재생성의 생성 중 키를 사용하지 않는다. 이미 선택지가 있으면 AI를 호출하지 않고 저장된 값을 반환한다. 클라이언트는 응답 본문이 아니라 상세 재조회의 `turns[].choices`로 표시한다.

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `choices` | `string[]` | 저장된 선택지 3개 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `turnId`가 정수가 아님 |
| 403 | `FORBIDDEN` | 정지 계정<br>소유자가 아님 |
| 404 | `NOT_FOUND` | 채팅이 없거나 삭제됨<br>턴이 없음 |
| 409 | `CHAT_TURN_STALE` | `turnId`가 마지막 턴이 아님<br>저장 시점에 마지막 턴이 바뀌거나 본문이 재생성됨 |
| 502 | `BAD_GATEWAY` | AI 선택지 생성 실패<br>클라이언트가 재시도 |

<details>
<summary><b>선택지 생성 응답 예시</b></summary>

<br>

**1) 200 Response body**

```json
{ "choices": ["손을 올린다.", "교관에게 질문한다.", "주변 학생들을 살핀다."] }
```

<br>

**2) 502 Response body**

```json
{
  "timestamp": "2026-06-12T12:00:00Z",
  "status": 502,
  "code": "BAD_GATEWAY",
  "message": "AI 선택지 생성 요청에 실패했습니다.",
  "path": "/api/v1/chats/7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d/turns/1203/choices",
  "details": []
}
```

</details>

<br>

### 4-2-9 공유 발급

| 항목 | 값 |
|---|---|
| 요청 | `POST /chats/{chatId}/shares` |
| 인증 | 선택 |
| 성공 | 201, 재발급 포함 |

요청 본문은 없다. 같은 턴 수로 다시 호출하면 기존 공유를 반환한다. 턴이 진행된 뒤 발급하면 새 공유가 생기고 기존 공유도 유효하다.

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `shareId` | `string` | 열람 토큰<br>채팅 식별자와 무관한 UUID |
| `turnCount` | `integer` | 공유에 포함된 턴 수 |
| `createdAt` | `string` | 최초 발급 시각 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 403 | `FORBIDDEN` | 소유자가 아님 |
| 404 | `NOT_FOUND` | 채팅이 없거나 삭제됨, 형식 오류 |

<details>
<summary><b>공유 발급 응답 예시</b></summary>

<br>

**1) 201 Response body**

```json
{ "shareId": "2c4e6a8b-1d3f-4a5b-9c7d-0e1f2a3b4c5d", "turnCount": 2, "createdAt": "2026-06-12T12:20:00Z" }
```

</details>

<br>

### 4-2-10 공유 열람

| 항목 | 값 |
|---|---|
| 요청 | `GET /shares/{shareId}` |
| 인증 | 선택<br>회원이면 그 회원으로, 익명이면 공개 스토리 기준으로 제목과 프롤로그 판정 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `id` | `string` | 열람 토큰 |
| `storyId` | `string` | |
| `storyTitle` | `string` | 열람자가 읽을 수 있으면 현재 제목, 아니면 마지막 공개본의 제목 |
| `prologue` | `string` | 공유 원본 채팅의 이름으로 치환 |
| `turns` | `object[]` | 발급 시점 턴 수까지<br>공유 범위에 포함된 턴의 재생성 결과는 반영 |
| `turns[].userInput` | `string` | |
| `turns[].aiOutput` | `string` | 활성본 전문<br>이미지 마커 포함 |
| `turns[].reachedEnding` | `string / null` | |
| `turns[].createdAt` | `string` | |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 404 | `NOT_FOUND` | 토큰 형식 오류, 공유 없음, 원본 채팅 삭제 |

<details>
<summary><b>공유 열람 응답 예시</b></summary>

<br>

**1) 200 Response body**

```json
{
  "id": "2c4e6a8b-1d3f-4a5b-9c7d-0e1f2a3b4c5d",
  "storyId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "storyTitle": "호아킨 아카데미의 무속성 신입생",
  "prologue": "마법 세계에서 민우는 호아킨 아카데미의 1학년으로 입학했다.",
  "turns": [
    {
      "userInput": "검사장을 둘러본다.",
      "aiOutput": "*검사장은 한순간 숨소리조차 사라진 듯 조용해졌다.*",
      "reachedEnding": null,
      "createdAt": "2026-06-12T12:05:00Z"
    }
  ]
}
```

</details>

<br>

### 4-2-11 피드백 등록

| 항목 | 값 |
|---|---|
| 요청 | `POST /feedbacks` |
| 인증 | 선택 |
| 성공 | 201, 본문 없음 |

**1. 요청 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `body` | `string` | 필수 | 공백만 있으면 안 되고 2,000자 이하 |
| `email` | `string` | 선택 | 이메일 형식, 320자 이하<br>비어 있으면 저장하지 않음 |
| `platform` | `string` | 선택 | `IOS`, `ANDROID`, `WEB` |
| `appVersion` | `string` | 선택 | 50자 이하<br>비어 있으면 저장하지 않음 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 본문 누락이나 길이 초과, 이메일 형식 오류, 플랫폼 허용값 밖 |

<details>
<summary><b>피드백 등록 요청 예시</b></summary>

<br>

**1) Request body**

```json
{
  "body": "이야기 진행 중 가끔 응답이 끊겨요.",
  "email": "user@example.com",
  "platform": "WEB",
  "appVersion": "1.2.0"
}
```

<br>

**2) 400 Response body**

```json
{
  "timestamp": "2026-06-12T12:00:00Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "요청 값이 올바르지 않습니다.",
  "path": "/api/v1/feedbacks",
  "details": [
    { "field": "body", "message": "크기가 1에서 2000 사이여야 합니다" }
  ]
}
```

</details>

<br>

### 4-2-12 다른 도메인과의 경계

| 도메인 | CHAT이 제공하는 것 | CHAT이 사용하는 것 |
|---|---|---|
| STORY | 삭제된 채팅을 포함한 누적 턴 수(완료 턴과 재생성 횟수 합)<br>회원 엔딩 도달 집계 행 | 읽기 판정과 현재 표시 판정, 공개본 데이터, 시작 설정과 추천 입력, 엔딩, 주요 사건, 인물 이미지, 표지 URL, 기본 주인공 이름, 토큰 치환, 간편 제작 생성 요청 ID |
| ACCOUNT | 회원의 내 채팅 목록 조회 메서드와 카드 구조<br>게스트 이관 시 채팅 소유권 이전과 도달 집계 보정 | 계정 상태, 페르소나 스냅샷 |
| PAYMENT | 턴과 이미지의 차감, 환불, 체험 예약과 복원 요청<br>정책값 응답에 싣는 라이트(`LITE`)의 턴 가격 | 지갑 일괄 차감, 환불, 체험 카운터 `chat_turn`과 `chat_image`, 정책값 `chat_image_cost` |
| AI 서버 | 턴 요청(회원 공개 식별자, 청구 모델, 출력 분량, 대화 요약 포함), 선택지 요청, 대화 요약 요청 | 본문 스트림, 판정, 인물 이미지 이벤트, 선택지, 갱신된 대화 요약 |

<br>

### 4-2-13 생성 스트림 재연결

| 항목 | 값 |
|---|---|
| 요청 | `GET /chats/{chatId}/generations/{generationId}/stream` |
| 인증 | 선택<br>채팅 상세와 같은 접근 게이트 |
| 성공 | 200, SSE |

**1. 요청 경로**

| 필드명 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `chatId` | `string` | 필수 | 채팅 공개 식별자 |
| `generationId` | `string` | 필수 | 생성 ID인 UUID 문자열<br>`started.generationId` 또는 상세의 `generatingTurn.generationId` |

요청 본문은 없다. 생성 중 키가 사라져도 보관 중인 해당 생성의 스트림은 읽을 수 있다.

<br>

**2. 이벤트**

이어쓰기의 SSE 이벤트 계약을 사용한다. 보관 중인 이벤트는 생성의 첫 이벤트부터 재생한 뒤 새 이벤트를 이어서 전송한다. 상세 조회 직후 재연결했을 때 큐 대기 등으로 아직 스트림이 없어도 생성 중 키가 해당 생성 ID를 담고 있으면 스트림을 기다린다.

수신 연결은 종료 이벤트(`completed`, `error`)를 받으면 닫는다. 읽기 대기는 코드 상수인 5초 단위로 끊어 확인한다. 생성 중 키가 더 이상 해당 생성 ID를 담고 있지 않으면 남은 이벤트를 대기 없이 끝까지 전달한다. 그중 종료 이벤트가 있으면 전달한 뒤 닫고 없으면 종료 이벤트 없이 닫는다. 기록 실패, 서버 강제 종료, 스트림 만료, 수신 중 Redis 읽기 오류가 종료 이벤트 없이 닫히는 경우다. 클라이언트는 종료 이벤트 없이 닫힌 연결을 상세 재조회로 처리한다.

끝난 스트림의 보관 기간은 종료 후 5분이다. 저장 진입 뒤 저장이 길어져 생성 시 TTL 150초로 스트림이 먼저 만료되면 재생할 이벤트가 없다. TTL 연장 장치는 두지 않는다. 수신 연결은 위 종료 조건으로 닫히고 클라이언트는 상세 재조회로 복구한다. 턴과 과금은 DB의 저장 결과가 기준이므로 스트림 만료의 영향을 받지 않는다. 스트림 부재의 404와 수신 불가의 503을 받으면 상세를 다시 조회한다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 403 | `FORBIDDEN` | 채팅 상세 조회 권한 없음 |
| 404 | `NOT_FOUND` | 채팅이 없거나 삭제됨 또는 형식 오류<br>해당 채팅의 생성 스트림이 없고 생성 중 키도 해당 생성 ID를 담고 있지 않음(만료 또는 잘못된 생성 ID) |
| 503 | `SERVICE_UNAVAILABLE` | 수신 연결 상한 초과<br>스트림 존재 확인이나 생성 중 키 확인의 Redis 오류<br>생성과 과금에 영향 없음 |

<details>
<summary><b>재연결 응답 예시</b></summary>

<br>

**1) 200 Response stream**

```text
event: started
data: {"chatId":"7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d","generationId":"5e7b9a10-2c34-4d56-8e90-123456789abc"}

event: token
data: {"text":"*검사장의 공기가 "}

event: completed
data: {"chatId":"7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d","turnId":1203,"aiOutput":"*검사장의 공기가 무겁게 가라앉는다.*","choices":[],"reachedEnding":null}
```

<br>

**2) 404 Response body**

```json
{
  "timestamp": "2026-10-16T12:00:00Z",
  "status": 404,
  "code": "NOT_FOUND",
  "message": "요청한 리소스를 찾을 수 없습니다.",
  "path": "/api/v1/chats/{chatId}/generations/{generationId}/stream",
  "details": []
}
```

</details>

<br>

### 4-2-14 모델 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /chats/models` |
| 인증 | 선택 |
| 성공 | 200 |

노출 중인 모델을 노출 순서로 반환한다. 식별자는 문자열 `code`다. 채팅 설정 변경 요청의 `model`에 그대로 쓴다. 게스트도 같은 목록과 가격을 받는다. 가격은 회원 턴에 적용된다. 회원 요청이고 그 모델의 프로모션이 진행 중이면 `promotion`에 프로모션 가격을 싣고 그동안 회원 턴은 그 가격을 적용한다. 회원의 턴 체험은 적용 가격이 0보다 큰 라이트(`LITE`) 턴에만 적용되므로 그 가격은 체험을 소진한 뒤의 턴부터 적용된다. 라이트의 프로모션 가격이 0이면 체험 사용량 조회의 회원 턴 `limit`이 `null`이다. ([4-2-4 체험 사용량 조회](../../PAYMENT/BACKEND/4-2-CONTRACT.md#4-2-4-체험-사용량-조회))

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `[].code` | `string` | 모델 코드 |
| `[].name` | `string` | 표시 이름 |
| `[].turnCost` | `integer` | 모델 가격<br>턴당 소모 이프, 재생성 포함<br>라이트(`LITE`)는 회원 체험을 소진한 뒤 적용<br>프로모션이 진행 중이어도 바뀌지 않음 |
| `[].promotion` | `object / null` | 진행 중인 프로모션<br>회원 요청에만 싣고 게스트와 진행 중이 아닌 모델은 `null` |
| `[].promotion.turnCost` | `integer` | 회원 턴에 적용하는 프로모션 가격<br>0이면 무료 |
| `[].promotion.endsAt` | `string` | 종료 시각, 제외 |
| `[].isDefault` | `boolean` | 새 채팅의 기본 모델<br>목록에 정확히 하나 |

<br>

**2. 제공 모델**

| 코드 | 이름 | 턴당 이프 | 기본 |
|---|---|---|---|
| `LITE` | 라이트 | 20 | |
| `AURORA` | 오로라 | 50 | 기본 |

<br>

**3. 실패 응답**

공통 실패 외에는 없다.

<details>
<summary><b>모델 목록 응답 예시</b></summary>

<br>

**1) 200 Response body**

```json
[
  { "code": "LITE", "name": "라이트", "turnCost": 20, "isDefault": false, "promotion": null },
  { "code": "AURORA", "name": "오로라", "turnCost": 50, "isDefault": true, "promotion": null }
]
```

<br>

**2) 200 Response body: 라이트 프로모션 진행 중, 회원 요청**

```json
[
  { "code": "LITE", "name": "라이트", "turnCost": 20, "isDefault": false, "promotion": { "turnCost": 0, "endsAt": "2026-11-05T15:00:00Z" } },
  { "code": "AURORA", "name": "오로라", "turnCost": 50, "isDefault": true, "promotion": null }
]
```

</details>

<br>

### 4-2-15 채팅 설정 변경

| 항목 | 값 |
|---|---|
| 요청 | `PATCH /chats/{chatId}` |
| 인증 | 선택 |
| 성공 | 200 |

채팅에 보관한 모델과 출력 분량을 바꾼다. 진행 중인 턴은 시작 시점의 모델, 가격, 출력 분량으로 끝나고 바꾼 값은 다음 이어쓰기와 재생성부터 적용된다. 생성 중에도 거절하지 않는다. 게스트 채팅도 바꿀 수 있다. 게스트 턴은 라이트(`LITE`)로 처리하고 보관한 모델은 이관 뒤 회원 턴부터 적용된다. 출력 분량은 게스트 턴에도 보관한 값 그대로 적용된다.

**1. 요청 본문**

`model`과 `longResponse` 중 하나 이상을 보낸다.

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `model` | `string` | 선택 | 노출 중인 모델 코드<br>생략하면 모델을 바꾸지 않음<br>`null`은 거절 |
| `longResponse` | `boolean` | 선택 | 출력 분량<br>`false`는 짧은 응답, `true`는 긴 응답<br>생략하면 출력 분량을 바꾸지 않음<br>`null`은 거절 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `id` | `string` | 채팅 공개 식별자 |
| `model` | `string` | 유효 모델 코드<br>보관한 모델이 노출 중이면 그 코드, 아니면 기본 모델 코드<br>`longResponse`만 보낸 요청도 같은 규칙 |
| `longResponse` | `boolean` | 변경 뒤 채팅에 보관한 출력 분량 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `model`과 `longResponse`가 모두 없음<br>`model`이나 `longResponse`가 `null`<br>`model`이 빈 값<br>노출 중인 모델 코드가 아님 |
| 403 | `FORBIDDEN` | 정지 계정<br>소유자가 아님 |
| 404 | `NOT_FOUND` | 채팅이 없거나 삭제됨, 형식 오류 |

<details>
<summary><b>채팅 설정 변경 요청, 응답 예시</b></summary>

<br>

**1) Request body: 출력 분량만 변경**

```json
{ "longResponse": true }
```

<br>

**2) Request body: 모델과 출력 분량 변경**

```json
{ "model": "LITE", "longResponse": false }
```

<br>

**3) 200 Response body: 출력 분량만 변경**

```json
{ "id": "7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d", "model": "AURORA", "longResponse": true }
```

<br>

**4) 400 Response body**

```json
{
  "timestamp": "2026-10-22T12:00:00Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "선택할 수 없는 모델입니다.",
  "path": "/api/v1/chats/7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d",
  "details": []
}
```

</details>

<br>

### 4-2-16 모델 프로모션 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/chat-models` |
| 인증 | 관리자 |
| 성공 | 200 |

비활성 모델을 포함한 모든 모델을 노출 순서로 반환한다.

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items` | `object[]` | 모델<br>노출 순서 |
| `items[].code` | `string` | 모델 코드 |
| `items[].name` | `string` | 표시 이름 |
| `items[].turnCost` | `integer` | 모델 가격 |
| `items[].isActive` | `boolean` | 노출 여부 |
| `items[].isDefault` | `boolean` | 기본 모델 여부 |
| `items[].promotion` | `object / null` | 프로모션<br>없으면 `null` |
| `items[].promotion.turnCost` | `integer` | 프로모션 가격<br>0 이상 |
| `items[].promotion.startsAt` | `string` | 시작 시각, 포함 |
| `items[].promotion.endsAt` | `string` | 종료 시각, 제외 |
| `items[].promotion.status` | `string` | 응답 시각 기준 상태<br>`SCHEDULED`: 시작 전<br>`ACTIVE`: 진행 중<br>`ENDED`: 종료 |

<br>

**2. 실패 응답**

공통 실패만 있다.

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/chat-models
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "items": [
    {
      "code": "LITE", "name": "라이트", "turnCost": 20, "isActive": true, "isDefault": false,
      "promotion": { "turnCost": 0, "startsAt": "2026-10-31T01:00:00Z", "endsAt": "2026-11-05T15:00:00Z", "status": "SCHEDULED" }
    },
    { "code": "AURORA", "name": "오로라", "turnCost": 50, "isActive": true, "isDefault": true, "promotion": null }
  ]
}
```

</details>

<br>

### 4-2-17 모델 프로모션 설정

| 항목 | 값 |
|---|---|
| 요청 | `PUT /admin/chat-models/{code}/promotion` |
| 인증 | 관리자 |
| 성공 | 200<br>모델 프로모션 조회의 항목 구조 |

**1. 경로와 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `code` | 경로 | 필수 | 모델 코드<br>비활성 모델도 허용 |
| `turnCost` | `integer` | 필수 | 프로모션 가격<br>0 이상 10,000 이하 |
| `startsAt` | `string` | 필수 | 시작 시각<br>과거도 허용하며 과거면 즉시 진행 |
| `endsAt` | `string` | 필수 | 종료 시각<br>`startsAt`과 현재보다 이후 |
| `reason` | `string` | 필수 | 사유<br>1~500자 |

- 모델당 한 프로모션이며 이미 있으면 덮어쓴다.
- 변경 감사 기록(`CHAT_MODEL_PROMOTION_UPSERTED`)과 모델 행 갱신을 한 트랜잭션에서 수행한다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 범위 밖 `turnCost`<br>`endsAt`이 `startsAt` 이전이거나 같음<br>`endsAt`이 현재 이전<br>필수 필드 누락, `reason` 길이 위반 |
| 404 | `NOT_FOUND` | 없는 모델 코드 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
PUT /api/v1/admin/chat-models/LITE/promotion
Authorization: Bearer {adminToken}
Content-Type: application/json

{ "turnCost": 0, "startsAt": "2026-10-31T01:00:00Z", "endsAt": "2026-11-05T15:00:00Z", "reason": "할로윈 이벤트 라이트 무료" }
```

**2) 200 Response body**

```json
{
  "code": "LITE", "name": "라이트", "turnCost": 20, "isActive": true, "isDefault": false,
  "promotion": { "turnCost": 0, "startsAt": "2026-10-31T01:00:00Z", "endsAt": "2026-11-05T15:00:00Z", "status": "SCHEDULED" }
}
```

**3) 400 Response body**

```json
{
  "timestamp": "2026-10-30T15:00:00Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "종료 시각은 시작 시각 이후여야 합니다.",
  "path": "/api/v1/admin/chat-models/LITE/promotion",
  "details": []
}
```

</details>

<br>

### 4-2-18 모델 프로모션 해제

| 항목 | 값 |
|---|---|
| 요청 | `DELETE /admin/chat-models/{code}/promotion` |
| 인증 | 관리자 |
| 성공 | 200<br>모델 프로모션 조회의 항목 구조, `promotion`은 `null` |

**1. 경로와 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `code` | 경로 | 필수 | 모델 코드 |
| `reason` | `string` | 필수 | 사유<br>1~500자 |

- 진행 중인 프로모션도 즉시 끝난다. 이미 시작한 턴은 시작 시점의 적용 가격으로 끝난다.
- 변경 감사 기록(`CHAT_MODEL_PROMOTION_DELETED`)과 모델 행 갱신을 한 트랜잭션에서 수행한다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `reason` 누락, 길이 위반 |
| 404 | `NOT_FOUND` | 없는 모델 코드<br>프로모션 없음 |

# 4-2 계약

이 문서는 MODERATION 도메인의 클라이언트 API와 다른 도메인과의 경계를 정한다.

접수 요청의 본문과 실패 조건은 STORY 세트의 등록과 수정 계약에, 처리 순서와 판정 규칙은 처리 흐름에, 앱 코드 전체 목록과 복구는 오류 처리에 있다. ([STORY 4-2-15 일반 제작 등록](../../STORY/BACKEND/4-2-CONTRACT.md#4-2-15-일반-제작-등록), [STORY 4-2-17 스토리 수정](../../STORY/BACKEND/4-2-CONTRACT.md#4-2-17-스토리-수정), [4-1 처리 흐름](4-1-PIPELINES.md), [5-3-2 앱 코드](5-3-ERROR-HANDLING.md#5-3-2-앱-코드))

<br>

### 4-2-1 공통 규칙과 헤더

**1. 공통 규칙**

| 항목 | 규칙 |
|---|---|
| 경로 | `/api/v1`을 생략해 적음 |
| JSON 필드 이름 | camelCase |
| 시각 | ISO 8601 UTC 문자열 |
| 식별자 | 제출본과 스토리는 UUID 공개 식별자<br>내부 PK와 회차, 임대, 재시도 상태는 노출하지 않음 |
| 위치 | 위반 항목과 이미지 오류의 `path`는 응답 폼 기준의 필드 경로<br>배열 인덱스는 0부터 |
| 예시 값 | 모든 예시는 구조를 설명하기 위한 가상 값 |

<br>

**2. 인증 수준**

| 수준 | 토큰 없음 또는 무효 | 유효한 토큰 |
|---|---|---|
| `필수` | 거절 | 회원으로 처리 |

<br>

**3. 요청 헤더**

| 요청 헤더 | 값 형식 | 쓰임 | 필수 |
|---|---|---|---|
| `Authorization` | `Bearer {accessToken}` | 회원 식별 | 인증 수준에 따름 |
| `X-Manyak-Request-Id` | 문자열 | 로그 연결<br>없으면 생성하고 응답 헤더로 반환 | 선택 |
| `X-Manyak-Session-Id` | 문자열 | 클라이언트 분석 세션 식별 | 선택 |

<br>

**4. 계정 상태 규칙**

| 요청 | 정지 계정 | 탈퇴 계정 |
|---|---|---|
| 제출본 상세, 미승인 목록 | 처리 | 401 |
| 재제출, 취소 | 403 | 401 |

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
| `details` | `object[]` | 선언적 필드 검증, 타입 변환, 기본 주인공 이름 검증 실패 시 `field`와 `message` 포함<br>그 외는 빈 배열 |

| `details[].field` 규칙 | 값 |
|---|---|
| 필드 검증 | 필드명 |
| 본문 파싱 실패 | 빈 `details` |

각 절의 실패 표에는 해당 엔드포인트에서 발생하는 상태와 `code`를 적는다. 다음 공통 실패는 각 절에서 생략한다.

| 상태 | `code` | 조건 |
|---|---|---|
| 401 | `UNAUTHORIZED` | 토큰 누락, 만료, 위조, 주체 형식 오류, 사용자 없음<br>확인된 탈퇴 계정 |
| 403 | `FORBIDDEN` | 계정 상태 규칙 표의 403 |
| 403 | `CONSENT_REQUIRED` | 동의 게이트가 켜진 환경에서 미동의 회원의 허용 목록 밖 요청 |
| 500 | `INTERNAL_SERVER_ERROR` | 예상하지 못한 오류 |

<br>

**6. 제출본 응답 구조**

제출본 상세와 미승인 목록의 항목은 같은 구조를 쓴다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `submissionId` | `string` | 제출본 공개 식별자 |
| `storyId` | `string / null` | 수정 대상 또는 승인 시 생성된 스토리 공개 식별자<br>승인 전 등록은 `null` |
| `kind` | `string` | `CREATE`, `UPDATE` |
| `payload` | `object` | 복원한 전체 폼<br>승인본은 접수 시점 폼, 미승인 등록본은 요청 원본, 미승인 수정본은 현재 스토리에 입력을 적용한 폼<br>등록본은 등록 요청 본문에 이미지 URL과 검수 상태를 추가한 구조<br>등록본의 새 항목에는 `id`가 없으며 `thumbnailObjectKey`는 유지됨<br>수정본은 STORY 수정 폼 응답과 같은 구조<br>`submission` 필드는 없음 |
| `status` | `string` | `PENDING`, `APPROVED`, `REJECTED`, `FAILED` |
| `issues` | `object[]` | 위반 항목<br>없으면 빈 배열 |
| `issues[].path` | `string` | 폼 기준 필드 경로 |
| `issues[].type` | `string` | `TEXT`, `IMAGE` |
| `issues[].rule` | `string` | `EXPLICIT_SEXUAL_CONTENT`, `DRUGS`, `EXTREME_GORE`, `SELF_HARM_PROMOTION`, `HATE_VIOLENCE_INCITEMENT`, `GAMBLING_PROMOTION` |
| `issues[].reason` | `string` | 위반 이유 |
| `imageErrors` | `object[]` | 이미지 오류<br>없으면 빈 배열 |
| `imageErrors[].path` | `string` | 폼 기준 이미지 필드 경로 |
| `imageErrors[].errorCode` | `string` | `IMAGE_DOWNLOAD_FAILED`, `IMAGE_INVALID`, `IMAGE_UNREADABLE` |
| `errorCode` | `string / null` | 실행 실패 코드<br>실패가 아니면 `null` |
| `createdAt` | `string` | 접수 시각 |
| `updatedAt` | `string` | 마지막 변경 시각 |
| `decidedAt` | `string / null` | 판정 시각<br>대기는 `null` |

| `errorCode` | 의미 |
|---|---|
| `IMAGE_DOWNLOAD_FAILED` | AI 서버가 이미지를 내려받지 못함 |
| `IMAGE_INVALID` | 이미지 형식 또는 크기 오류<br>사용자가 교체해야 함 |
| `IMAGE_UNREADABLE` | 모델이 이미지를 판독하지 못함<br>사용자가 교체해야 함 |
| `MODEL_CALL_FAILED` | AI 서버의 모델 호출 실패 |
| `MODERATION_UNAVAILABLE` | 이미지 복사 실패, AI 서버 호출 실패, 시간 초과, 응답 형식 오류 |
| `APPLY_FAILED` | 승인 뒤 현재 스토리 적용 단계의 검증 실패 |

- 반려는 저장된 `issues`가 하나 이상이고 `errorCode`가 `null`이다. 응답의 `issues`는 재대응으로 비어 있을 수 있다. 실패는 `errorCode`가 있고 `issues`와 `imageErrors`가 함께 있을 수 있다.
- 대상이 사라진 항목은 `issues`와 `imageErrors`에서 뺀다.

<br>

### 4-2-2 제출본 상세

| 항목 | 값 |
|---|---|
| 요청 | `GET /stories/submissions/{submissionId}` |
| 인증 | 필수 |
| 성공 | 200, 제출본 응답 구조 |

**1. 경로**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `submissionId` | `string` | 필수 | 경로 변수, 제출본 공개 식별자 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 404 | `NOT_FOUND` | 부재, 타인 소유, 형식 오류 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/stories/submissions/f1e2d3c4-b5a6-4978-8a9b-0c1d2e3f4a5b
Authorization: Bearer {accessToken}
```

**2) 200 Response body**

반려된 신규 등록본이다. `payload`의 `startSettings`와 `mainEvents` 안쪽은 등록 요청 예시와 같아 생략했다.

```json
{
  "submissionId": "f1e2d3c4-b5a6-4978-8a9b-0c1d2e3f4a5b",
  "storyId": null,
  "kind": "CREATE",
  "payload": {
    "title": "{username}의 계약서",
    "oneLineIntro": "기억을 잃은 마법사 {username}이가 금지된 숲에서 과거를 추적한다",
    "description": "계약 마법이 지배하는 왕국에서 잃어버린 기억과 사라진 가족의 비밀을 추적한다.",
    "protagonistName": "서린",
    "genres": ["판타지", "미스터리"],
    "storySettings": {
      "worldSetting": "# 세계관\n계약 마법이 지배하는 왕국.",
      "characterSetting": "# 도윤\n침착한 도서관 사서.",
      "userRoleSetting": "# 주인공\n기억을 잃은 마법사.",
      "ruleSetting": "# 전개 규칙\n사용자의 행동에 따라 단서를 공개한다."
    },
    "startSettings": [],
    "mainEvents": [],
    "visibility": "PRIVATE",
    "thumbnailObjectKey": "thumbnails/uploaded/drafts/3f2504e0-4f89-41d3-9a0c-0305e82c3301/4c9e2b7a-1d3f-4a5b-8c6d-9e0f1a2b3c4d.webp",
    "thumbnailUrl": "https://cdn.example.com/thumbnails/uploaded/drafts/3f2504e0-4f89-41d3-9a0c-0305e82c3301/4c9e2b7a-1d3f-4a5b-8c6d-9e0f1a2b3c4d.webp",
    "thumbnailModerationStatus": "APPROVED",
    "characters": [
      {
        "id": null,
        "name": "도윤",
        "description": "기록을 지키는 과묵한 사서.",
        "images": [
          {
            "id": null,
            "imageName": "도윤_기본",
            "imageUrl": "https://cdn.example.com/characters/uploaded/drafts/3f2504e0-4f89-41d3-9a0c-0305e82c3301/5d0f3c8b-2e4a-4b6c-9d7e-0f1a2b3c4d5e.webp",
            "moderationStatus": "APPROVED",
            "objectKey": "characters/uploaded/drafts/3f2504e0-4f89-41d3-9a0c-0305e82c3301/5d0f3c8b-2e4a-4b6c-9d7e-0f1a2b3c4d5e.webp"
          }
        ]
      }
    ]
  },
  "status": "REJECTED",
  "issues": [
    { "path": "storySettings.worldSetting", "type": "TEXT", "rule": "EXTREME_GORE", "reason": "신체 훼손을 상세히 묘사합니다." }
  ],
  "imageErrors": [],
  "errorCode": null,
  "createdAt": "2026-10-16T01:23:45.678Z",
  "updatedAt": "2026-10-16T01:25:10.123Z",
  "decidedAt": "2026-10-16T01:25:10.123Z"
}
```

**3) 404 Response body**

```json
{
  "timestamp": "2026-10-16T01:23:45.678Z",
  "status": 404,
  "code": "NOT_FOUND",
  "message": "제출본 또는 스토리를 찾을 수 없습니다.",
  "path": "/api/v1/stories/submissions/00000000-0000-0000-0000-000000000000",
  "details": []
}
```

</details>

<br>

### 4-2-3 미승인 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /stories/submissions` |
| 인증 | 필수 |
| 성공 | 200, 제출본 응답 구조의 배열 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `limit` | `integer` | 선택 | 최대 건수, 기본값 100<br>1~100 범위를 벗어나면 범위 안으로 보정 |

- 승인본을 제외한 본인 제출본을 접수 시각 내림차순으로 반환한다. 페이지네이션은 없다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `limit`이 정수가 아님 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/stories/submissions?limit=20
Authorization: Bearer {accessToken}
```

**2) 200 Response body**

항목 구조는 제출본 상세와 같아 `payload` 안쪽을 생략했다.

```json
[
  {
    "submissionId": "f1e2d3c4-b5a6-4978-8a9b-0c1d2e3f4a5b",
    "storyId": null,
    "kind": "CREATE",
    "payload": {},
    "status": "PENDING",
    "issues": [],
    "imageErrors": [],
    "errorCode": null,
    "createdAt": "2026-10-16T01:23:45.678Z",
    "updatedAt": "2026-10-16T01:23:45.678Z",
    "decidedAt": null
  }
]
```

</details>

<br>

### 4-2-4 재제출

| 항목 | 값 |
|---|---|
| 요청 | `PUT /stories/submissions/{submissionId}` |
| 인증 | 필수 |
| 성공 | 202 |

**1. 경로와 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `submissionId` | `string` | 필수 | 경로 변수, 신규 등록의 반려 또는 실패 제출본 |
| 본문 | `object` | 필수 | STORY 일반 제작 등록 요청과 같은 구조와 검증<br>`draftId`는 접수 트랜잭션에서 요청자 소유 초안 삭제 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `submissionId` | `string` | 같은 제출본 공개 식별자 |
| `status` | `string` | 항상 `PENDING` |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 등록과 같은 검증 실패<br>업로드 접두어 범위 밖 객체 키, 지원하지 않는 형식, 크기 초과 |
| 400 | `INVALID_GENRE` | 허용되지 않는 장르 |
| 400 | `UPLOAD_NOT_FOUND` | 객체 키에 아직 파일이 없음 |
| 400 | `IMAGES_TOO_LARGE` | 검수 요청 예상 용량 초과 |
| 404 | `NOT_FOUND` | 부재, 타인 소유, 형식 오류<br>입력 검증보다 먼저 판정 |
| 409 | `CONFLICT` | 수정 종류이거나 대기 또는 승인 상태<br>같은 인물 안의 이미지 이름 중복 |
| 503 | `SERVICE_UNAVAILABLE` | 이미지가 있는 요청에서 이미지 저장소 미설정 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

반려된 신규 등록본을 고쳐 다시 보낸다. 본문 구조는 STORY 일반 제작 등록과 같다.

```http
PUT /api/v1/stories/submissions/f1e2d3c4-b5a6-4978-8a9b-0c1d2e3f4a5b
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "title": "{username}의 계약서",
  "oneLineIntro": "기억을 잃은 마법사 {username}이가 금지된 숲에서 과거를 추적한다",
  "description": "계약 마법이 지배하는 왕국에서 잃어버린 기억과 사라진 가족의 비밀을 추적한다.",
  "protagonistName": "서린",
  "genres": ["판타지", "미스터리"],
  "storySettings": {
    "worldSetting": "# 세계관\n계약 마법이 지배하는 왕국. 계약서는 서명자의 기억을 담보로 잡는다.",
    "characterSetting": "# 도윤\n침착한 도서관 사서. 계약서의 출처를 알고 있다.",
    "userRoleSetting": "# 주인공\n기억을 잃은 마법사. 자신의 이름이 적힌 계약서를 발견했다.",
    "ruleSetting": "# 전개 규칙\n사용자의 행동에 따라 단서를 공개한다."
  },
  "startSettings": [
    {
      "name": "폐관 뒤의 도서관",
      "prologue": "*마지막 종이 울린 뒤, {username}은 빈 기록장 가장자리에서 푸른 빛을 발견한다.*",
      "startSituation": "폐관 직후 기록 열람실에서 계약서를 살핀다.",
      "suggestedInputs": ["기록장을 빛에 비춰 본다.", "도윤에게 푸른 흔적을 가리킨다.", "기록장의 보관 위치를 확인한다."],
      "endings": [
        {
          "name": "되찾은 기억",
          "requirement": { "minTurns": 8, "achievementCondition": "계약서의 출처를 밝히고 기억을 되찾는다." },
          "epilogue": "되찾은 기억과 함께 숲을 떠나는 장면을 여운 있게 묘사한다."
        }
      ]
    }
  ],
  "mainEvents": [
    { "name": "계약서 발견", "description": "자신의 이름이 적힌 계약서를 발견한다.", "keySentence": "계약서의 서명을 확인한다." }
  ],
  "visibility": "PRIVATE",
  "thumbnailObjectKey": "thumbnails/uploaded/drafts/7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d/4c9e2b7a-1d3f-4a5b-8c6d-9e0f1a2b3c4d.webp",
  "characters": [
    {
      "name": "도윤",
      "description": "기록을 지키는 과묵한 사서.",
      "images": [
        { "objectKey": "characters/uploaded/drafts/7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d/5d0f3c8b-2e4a-4b6c-9d7e-0f1a2b3c4d5e.webp", "imageName": "도윤_기본" }
      ]
    }
  ]
}
```

**2) 202 Response body**

```json
{ "submissionId": "f1e2d3c4-b5a6-4978-8a9b-0c1d2e3f4a5b", "status": "PENDING" }
```

**3) 409 Response body**

```json
{
  "timestamp": "2026-10-16T01:23:45.678Z",
  "status": 409,
  "code": "CONFLICT",
  "message": "검수 상태에서 허용되지 않는 요청입니다.",
  "path": "/api/v1/stories/submissions/f1e2d3c4-b5a6-4978-8a9b-0c1d2e3f4a5b",
  "details": []
}
```

</details>

<br>

### 4-2-5 취소

| 항목 | 값 |
|---|---|
| 요청 | `DELETE /stories/submissions/{submissionId}` |
| 인증 | 필수 |
| 성공 | 204, 본문 없음 |

**1. 경로**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `submissionId` | `string` | 필수 | 경로 변수, 대기, 반려, 실패 제출본 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 404 | `NOT_FOUND` | 부재, 타인 소유, 형식 오류 |
| 409 | `CONFLICT` | 승인본 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
DELETE /api/v1/stories/submissions/f1e2d3c4-b5a6-4978-8a9b-0c1d2e3f4a5b
Authorization: Bearer {accessToken}
```

**2) 204 Response**

본문 없음

**3) 409 Response body**

```json
{
  "timestamp": "2026-10-16T01:23:45.678Z",
  "status": 409,
  "code": "CONFLICT",
  "message": "검수 상태에서 허용되지 않는 요청입니다.",
  "path": "/api/v1/stories/submissions/f1e2d3c4-b5a6-4978-8a9b-0c1d2e3f4a5b",
  "details": []
}
```

</details>

<br>

### 4-2-6 다른 도메인과의 경계

| 도메인 | MODERATION이 제공하는 것 | MODERATION이 사용하는 것 |
|---|---|---|
| STORY | 등록과 수정의 접수, 대기 중 제출본 존재 확인, 수정 폼의 제출본 메타데이터 | 입력 검증과 이미지 객체 검증, 수정 폼 조회, 승인 시 등록 저장과 수정 적용, 공개 스냅샷 갱신, 초안 삭제 |
| NOTIFICATION | 검수 완료 이벤트 | 없음 |
| ACCOUNT | 회원의 제출본 전부 삭제 연산 | 계정 상태, 사용자 행 잠금 |
| AI 서버 | 검수 입력 | 판정 결과 |
| 모든 도메인 | 없음 | 인증 필터, 탈퇴 거부, 동의 게이트 |

다른 도메인이 호출하거나 받는 연산의 입력과 결과는 다음과 같다.

| 연산 | 입력 | 결과 |
|---|---|---|
| 등록 접수 | 등록 요청, 회원 내부 ID | 제출본 공개 식별자와 대기 상태 |
| 수정 접수 | 스토리 공개 식별자, 수정 요청, 회원 내부 ID | 제출본 공개 식별자와 대기 상태<br>공개 범위만 변경하면 즉시 반영한 수정 폼<br>대기 중 제출본이 있으면 공개 범위만 바꿔도 거절 예외 |
| 대기 중 존재 확인 | 스토리 내부 ID | 대기 중 제출본이 있으면 거절 예외 |
| 수정 폼 메타데이터 | 스토리 공개 식별자, 회원 내부 ID | 최신 미승인 제출본의 식별자, 상태, 위반 항목, 오류 코드, 이미지 오류 또는 `null` |
| 검수 완료 이벤트 발행 | 회원 내부 ID, 제출본 식별자, 스토리 공개 식별자, 상태, 회차, 제목 | NOTIFICATION의 발송 경로 |
| 회원 제출본 전부 삭제 | 회원 내부 ID | 없음 |
| 스토리 제출본 전부 삭제 | 스토리 내부 ID | 없음 |

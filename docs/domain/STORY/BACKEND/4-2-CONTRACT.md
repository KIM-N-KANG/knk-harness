# 4-2 계약

이 문서는 STORY 도메인 백엔드와 클라이언트, 다른 도메인 사이의 계약을 정한다. 엔드포인트별 요청 필드, 성공과 실패 응답의 필드와 예시, 도메인 경계를 다룬다.

AI 서버로 보내는 값과 받은 값의 처리는 처리 흐름에, 앱 코드 전체 목록과 복구는 오류 처리에, 읽기와 소유 판정의 보안 관점은 보안에, 관리자 토큰과 권한 판정은 관리자 계약에 있다. ([4-1-11 간편 제작 스토리라인 생성](4-1-PIPELINES.md#4-1-11-간편-제작-스토리라인-생성), [4-1-12 간편 제작 완성](4-1-PIPELINES.md#4-1-12-간편-제작-완성), [5-3-2 앱 코드](5-3-ERROR-HANDLING.md#5-3-2-앱-코드), [5-1-2 소유권과 읽기 판정](5-1-SECURITY.md#5-1-2-소유권과-읽기-판정), [ADMIN 4-2-1 공통 규칙과 헤더](../../ADMIN/BACKEND/4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더))

<br>

### 4-2-1 공통 규칙과 헤더

**1. 공통 규칙**

| 항목 | 규칙 |
|---|---|
| 경로 | `/api/v1`을 생략해 적음 |
| JSON 필드 이름 | camelCase |
| 시각 | ISO 8601 UTC 문자열 |
| 문자 수 | UTF-16 코드 유닛 기준 |
| 식별자 | 스토리, 시작 설정, 인물, 이미지, 제출본은 UUID 공개 식별자<br>초안은 클라이언트가 만든 UUID<br>간편 제작 진행, 스토리라인, 추천 정보, 태그, 로어북은 정수 ID |
| 예시 값 | 모든 예시는 구조를 설명하기 위한 가상 값 |

<br>

**2. 인증 수준**

| 수준 | 토큰 없음 또는 무효 | 유효한 토큰 |
|---|---|---|
| `불필요` | 검사하지 않음 | 검사하지 않음 |
| `선택` | 익명으로 처리 | 회원으로 처리 |
| `필수` | 거절 | 회원으로 처리 |
| `관리자` | 거절 | 앱 접근 토큰은 거절<br>관리자 토큰은 역할과 계정 상태를 다시 확인해 통과 |

<br>

**3. 요청 헤더**

| 요청 헤더 | 값 형식 | 쓰임 | 필수 |
|---|---|---|---|
| `Authorization` | `Bearer {accessToken}` 또는 `Bearer {adminToken}` | 회원 또는 관리자 식별 | 인증 수준에 따름 |
| `X-Manyak-Request-Id` | 문자열 | 로그와 AI 호출 연결<br>없으면 서버가 생성하고 응답 헤더로 항상 반환 | 선택 |
| `X-Manyak-Session-Id` | 문자열 | 클라이언트 분석 세션 식별 | 선택 |
| `X-Manyak-Device-Id` | 문자열 | 게스트의 스토리라인 생성과 완성 체험 한도 집계<br>생성 요청 기록의 멱등성과 복구 조회 소유권 판정<br>AI 서버에는 해시로 전달<br>서버 분석 이벤트의 `device_id` | 게스트 간편 제작은 필수 |

<br>

**4. 읽기와 소유 규칙**

| 요청 | 허용 |
|---|---|
| 공개 목록, 검색 | 발행 상태이며 공개된 회원 소유 스토리만 실림 |
| 상세, 일괄 조회, 좋아요, 신고 | 발행 상태이며 공개된 스토리는 누구나<br>소유자 없는 스토리는 식별자를 아는 누구나<br>회원 소유 비공개 스토리는 소유자만<br>위반은 404, 일괄 조회는 제외 |
| 삭제, 수정 폼 | 소유 스토리는 소유자만<br>소유자 없는 스토리는 익명 요청만 |
| 수정, presign, 표지와 인물 이미지 삭제 | 회원 소유자만 |
| 완성 | 회원 소유 진행은 해당 회원만<br>게스트 진행은 요청자의 신원으로 귀속되며 디바이스 소유권 검사는 하지 않음 |
| 평가 | 회원 소유 진행은 해당 회원만<br>소유자 없는 진행은 요청자 제한 없음 |
| 복구 조회 | 회원 요청 기록은 회원 ID, 게스트 요청 기록은 디바이스 해시로 소유권 판정 |
| 초안 | 회원 전용, 소유 회원만<br>타인의 초안은 없는 것으로 응답<br>정지 계정은 조회도 거절 |

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
| `details` | `object[]` | 필드 검증 실패 시 `field`와 `message` 포함<br>그 외는 빈 배열 |

| `details[].field` 규칙 | 값 |
|---|---|
| 필드 검증 | 필드명 |
| 객체 수준 검증 | 객체명 |
| 쿼리 파라미터 | 프로퍼티 경로 |
| 장르 검증 | 원본 인덱스별 `genres[i]` |
| 본문 파싱 실패 | 빈 `details` |

각 절의 실패 표에는 해당 엔드포인트에서 발생하는 상태와 `code`를 적는다. 다음 공통 실패는 각 절에서 생략한다.

| 상태 | `code` | 조건 |
|---|---|---|
| 401 | `UNAUTHORIZED` | 인증 필수 경로의 토큰 누락, 만료, 위조, 사용자 없음<br>인증 선택 또는 필수 경로에서 확인된 탈퇴 계정 |
| 403 | `CONSENT_REQUIRED` | 동의 게이트가 켜진 환경에서 미동의 회원의 허용 목록 밖 요청 |
| 500 | `INTERNAL_SERVER_ERROR` | 예상하지 못한 오류 |

<details>
<summary><b>공통 실패 응답 예시</b></summary>

<br>

**1) 401 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 401,
  "code": "UNAUTHORIZED",
  "message": "로그인이 필요합니다.",
  "path": "/api/v1/stories/general",
  "details": []
}
```

<br>

**2) 500 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 500,
  "code": "INTERNAL_SERVER_ERROR",
  "message": "서버 오류가 발생했습니다.",
  "path": "/api/v1/stories/simple",
  "details": []
}
```

</details>

<br>

### 4-2-2 공개 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /stories` |
| 인증 | 불필요 |
| 성공 | 200 |

**1. 쿼리**

| 쿼리 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `filter` | `string` | 선택 | `all` 또는 `original`, 기본값 `all` |
| `sort` | `string` | 선택 | `popular`, `latest`, `likes`, `chats`, 기본값 `popular` |
| `limit` | `integer` | 선택 | 기본값 20, 1~50으로 보정 |
| `cursor` | `string` | 선택 | 이전 응답의 `nextCursor`<br>같은 `filter`와 `sort`를 함께 보냄<br>형식이 잘못됐거나 정렬이 다르면 거절<br>이전 좋아요 기반 인기순의 `p` 커서도 거절 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items` | `object[]` | 카드 목록 |
| `nextCursor` | `string / null` | 다음 페이지 커서<br>마지막 페이지는 `null` |

<br>

**3. 카드 필드**

검색, 일괄 조회, 내 스토리 목록의 카드도 같은 구조다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `id` | `string` | 공개 식별자 |
| `isOriginal` | `boolean` | 공식 계정 소유 여부 |
| `thumbnailUrlSm` | `string / null` | 카드용 표지<br>승인된 생성 또는 업로드 표지의 원본 URL, 없으면 `null`<br>과거 프리셋 키가 남은 기존 스토리만 그 키의 `_sm` 변형 |
| `title` | `string` | 기본 주인공 이름으로 치환한 제목 |
| `oneLineIntro` | `string` | 기본 주인공 이름으로 치환한 한 줄 소개<br>없으면 빈 문자열 |
| `genres` | `string[]` | 저장한 장르 표기 목록 |
| `author` | `object / null` | `id`, `nickname`, `profileImageUrl`<br>`id`는 항상 `null`<br>게스트 스토리는 `author`가 `null` |
| `turnCount` | `integer` | 미삭제 채팅의 완료 턴 합 |
| `likeCount` | `integer` | 좋아요 수 |
| `status` | `string` | `DRAFT` 또는 `PUBLISHED`<br>현재 만들어지는 스토리는 모두 `PUBLISHED` |
| `visibility` | `string` | `PUBLIC` 또는 `PRIVATE` |
| `createdAt` | `string` | 생성 시각 |

<br>

**4. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `filter`, `sort`의 허용 범위를 벗어난 값, `limit`이 숫자가 아님<br>잘못된 커서, 정렬이 다른 커서, 옛 `p` 커서 |

<details>
<summary><b>목록 요청, 응답 예시</b></summary>

<br>

**1) Request**

```text
GET /stories?sort=popular&limit=2
```

<br>

**2) 200 Response body**

```json
{
  "items": [
    {
      "id": "9c5b94b1-35ad-49bb-b118-8e8fc24abf80",
      "isOriginal": true,
      "thumbnailUrlSm": "https://cdn.example.com/thumbnails/thumb_0012_sm.png",
      "title": "잿빛 왕관",
      "oneLineIntro": "무너진 왕국에서 견습 기사 아린이 옥좌의 진실을 좇는다",
      "genres": [
        "다크 판타지",
        "정치극"
      ],
      "author": {
        "id": null,
        "nickname": "manyak",
        "profileImageUrl": "https://cdn.example.com/profiles/manyak.png"
      },
      "turnCount": 96,
      "likeCount": 41,
      "status": "PUBLISHED",
      "visibility": "PUBLIC",
      "createdAt": "2026-05-28T09:30:00Z"
    },
    {
      "id": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
      "isOriginal": false,
      "thumbnailUrlSm": "https://cdn.example.com/thumbnails/generated/3f2504e0-4f89-41d3-9a0c-0305e82c3301/썸네일_기본.webp",
      "title": "사라지는 내일의 기록",
      "oneLineIntro": "마법 도서관에서 지워진 미래를 추적하는 신입 기록관 서린의 이야기",
      "genres": [
        "판타지",
        "미스터리"
      ],
      "author": {
        "id": null,
        "nickname": "은빛여우",
        "profileImageUrl": null
      },
      "turnCount": 128,
      "likeCount": 32,
      "status": "PUBLISHED",
      "visibility": "PUBLIC",
      "createdAt": "2026-06-10T12:00:00Z"
    }
  ],
  "nextCursor": "czo0NDg6M2YyNTA0ZTAtNGY4OS00MWQzLTlhMGMtMDMwNWU4MmMzMzAx"
}
```

<br>

**3) 다음 페이지 요청**

```text
GET /stories?sort=popular&limit=2&cursor=czo0NDg6M2YyNTA0ZTAtNGY4OS00MWQzLTlhMGMtMDMwNWU4MmMzMzAx
```

<br>

**4) 400 Response body**

정렬이 다른 커서를 보낸 경우다.

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "커서 형식이 올바르지 않습니다.",
  "path": "/api/v1/stories",
  "details": []
}
```

</details>

<br>

### 4-2-3 검색

| 항목 | 값 |
|---|---|
| 요청 | `GET /stories/search` |
| 인증 | 불필요 |
| 성공 | 200 |

**1. 쿼리**

| 쿼리 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `q` | `string` | 필수 | 검색어, 2~100자 |
| `limit` | `integer` | 선택 | 목록과 같음 |
| `cursor` | `string` | 선택 | 이전 검색 응답의 `nextCursor`<br>같은 `q`를 함께 보냄 |

<br>

**2. 응답**

공개 목록 응답과 같은 `items`, `nextCursor` 구조다.

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 검색어 길이 위반, 잘못된 커서 |
| 503 | `SERVICE_UNAVAILABLE` | 검색 저장소 미설정 또는 장애 |

<details>
<summary><b>실패 응답 예시</b></summary>

<br>

**503 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 503,
  "code": "SERVICE_UNAVAILABLE",
  "message": "검색을 사용할 수 없습니다.",
  "path": "/api/v1/stories/search",
  "details": []
}
```

</details>

<br>

### 4-2-4 제공 장르

| 항목 | 값 |
|---|---|
| 요청 | `GET /stories/genres` |
| 인증 | 선택 |
| 성공 | 200 |

페이지네이션이 없다. 검색어를 별칭으로 입력해도 정식 장르의 이름과 ID를 반환한다. 같은 배열에는 한 번만 포함한다.

**1. 쿼리**

| 쿼리 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `query` | `string` | 선택 | 원문 30자 이하<br>누락, 빈 문자열, 공백뿐이면 전체 목록 |

<br>

**2. 응답**

| 응답 필드명 | 타입 | 의미 |
|---|---|---|
| `genres` | `object[]` | 활성 제공 장르 중 검색 결과<br>검색어가 없으면 197개를 카탈로그 순으로 반환<br>결과가 없으면 `[]` |
| `featuredGenres` | `object[]` | 검색어와 결과 유무에 관계없이 대표 15개를 대표 순서로 |
| `genres[].id`, `featuredGenres[].id` | `integer` | 태그 ID<br>같은 장르는 두 배열에서 같은 ID이며 스토리라인 생성의 `genreTagIds`와 같음 |
| `genres[].name`, `featuredGenres[].name` | `string` | 정식 표시명 |

<br>

**3. 질의 예**

| 질의 예 | 기대 동작 |
|---|---|
| `로맨스` | 로맨스가 먼저, 로맨스판타지도 포함 |
| `ㄹㅁㅅ` | 로맨스와 로맨스판타지 포함 |
| `현대 판타지` | 현대판타지 완전 일치 |
| `bl` | BL 완전 일치 |
| `로판` | 로맨스판타지 반환 |
| 일치하지 않는 질의 | `genres: []`, 대표 15개 유지 |

<br>

**4. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 검색어 30자 초과 |

<details>
<summary><b>장르 요청, 응답 예시</b></summary>

<br>

**1) Request**

```text
GET /stories/genres?query=로판
```

<br>

**2) 200 Response body**

대표 장르는 15개 중 3개만 표시했다.

```json
{
  "genres": [
    { "id": 45, "name": "로맨스판타지" }
  ],
  "featuredGenres": [
    { "id": 10, "name": "계약결혼" },
    { "id": 15, "name": "괴담" },
    { "id": 45, "name": "로맨스판타지" }
  ]
}
```

<br>

**3) 400 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "요청 값이 올바르지 않습니다.",
  "path": "/api/v1/stories/genres",
  "details": [
    {
      "field": "query",
      "message": "30자 이하여야 합니다."
    }
  ]
}
```

</details>

<br>

### 4-2-5 로어북 카탈로그

| 항목 | 값 |
|---|---|
| 요청 | `GET /stories/lorebooks` |
| 인증 | 불필요 |
| 성공 | 200 |

일반 제작에서 참조할 활성 로어북 목록을 반환한다.

**1. 쿼리**

| 쿼리 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `genre` | `string` | 선택 | 장르 필터, 생략하면 전체 |

<br>

**2. 응답**

| 응답 항목 | 타입 | 의미 |
|---|---|---|
| `[].id` | `integer` | 로어북 ID |
| `[].name` | `string` | 로어북 이름 |
| `[].genre` | `string / null` | 장르 |

<br>

**3. 실패 응답**

공통 실패 외에는 없다.

<details>
<summary><b>로어북 응답 예시</b></summary>

<br>

```json
[
  { "id": 7, "name": "기록의 잔향", "genre": "판타지" },
  { "id": 12, "name": "무협 용어집", "genre": "무협" }
]
```

</details>

<br>

### 4-2-6 일괄 조회

| 항목 | 값 |
|---|---|
| 요청 | `POST /stories/batch` |
| 인증 | 선택 |
| 성공 | 200 |

**1. 요청 본문**

| 요청 필드명 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `storyIds` | `string[]` | 필수 | 공개 식별자 1~100개 |

<br>

**2. 응답**

요청 순서를 유지한 카드 배열이다. 존재하지 않거나 읽을 수 없는 스토리, 형식이 잘못된 식별자는 오류 없이 제외한다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `storyIds` 개수 위반 |

<details>
<summary><b>일괄 조회 요청, 응답 예시</b></summary>

<br>

**1) Request body**

```json
{
  "storyIds": [
    "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
    "00000000-0000-0000-0000-000000000000"
  ]
}
```

<br>

**2) 200 Response body**

두 번째 식별자는 존재하지 않아 제외됐다.

```json
[
  {
    "id": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
    "isOriginal": false,
    "thumbnailUrlSm": "https://cdn.example.com/thumbnails/generated/3f2504e0-4f89-41d3-9a0c-0305e82c3301/썸네일_기본.webp",
    "title": "사라지는 내일의 기록",
    "oneLineIntro": "마법 도서관에서 지워진 미래를 추적하는 신입 기록관 서린의 이야기",
    "genres": ["판타지", "미스터리"],
    "author": null,
    "turnCount": 128,
    "likeCount": 32,
    "status": "PUBLISHED",
    "visibility": "PRIVATE",
    "createdAt": "2026-06-10T12:00:00Z"
  }
]
```

<br>

**3) 400 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "요청 값이 올바르지 않습니다.",
  "path": "/api/v1/stories/batch",
  "details": [
    {
      "field": "storyIds",
      "message": "1개 이상 100개 이하여야 합니다."
    }
  ]
}
```

</details>

<br>

### 4-2-7 상세

| 항목 | 값 |
|---|---|
| 요청 | `GET /stories/{storyId}` |
| 인증 | 선택 |
| 성공 | 200 |

**1. 응답**

카드 필드에서 `isOriginal`과 `thumbnailUrlSm`을 빼고 다음 필드를 더한다. 텍스트 필드는 이름 토큰을 기본 주인공 이름으로 치환해 반환한다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `thumbnailUrl` | `string / null` | 원본 표지<br>승인된 생성 또는 업로드 URL, 없으면 `null`<br>과거 프리셋 키가 남은 기존 스토리만 그 키의 URL |
| `description` | `string / null` | 주요 내용 |
| `hashtags` | `string[]` | 항상 빈 배열 |
| `isOwner` | `boolean` | 요청 회원이 소유자인지<br>게스트는 `false` |
| `isLiked` | `boolean` | 요청 회원의 좋아요 여부<br>게스트는 `false` |
| `startSettings` | `object[]` | 등록 순서의 시작 설정 |
| `startSettings[].id` | `string` | 시작 설정 공개 식별자<br>`POST /chats`의 `startSettingId` |
| `startSettings[].name` | `string` | 시작 장면 이름 |
| `startSettings[].prologue` | `string / null` | 프롤로그 |
| `startSettings[].startSituation` | `string / null` | 시작 상황 |
| `startSettings[].suggestedInputs` | `string[]` | 추천 입력 |
| `startSettings[].endings` | `object[]` | 활성 엔딩만, 표시 순서 |
| `startSettings[].endings[].name` | `string` | 엔딩 이름 |
| `startSettings[].endings[].requirement` | `object` | `minTurns`(0 이상 정수)와 `achievementCondition`(자연어) |
| `startSettings[].endings[].epilogue` | `string` | 엔딩 연출 방향 |
| `lorebooks` | `object[]` | `id`, `name`, `genre`, `content` |
| `mainEvents` | `object[]` | `name`, `description`, `keySentence`, `sortOrder`(0부터) |
| `characters` | `object[]` | 저장 순서의 인물 |
| `characters[].name` | `string` | 인물 이름 |
| `characters[].imageUrl` | `string / null` | 대표 이미지<br>`{이름}_기본`, 없으면 첫 장, 그것도 없으면 `null` |
| `characters[].description` | `string / null` | 인물 소개<br>없으면 `null` |
| `reachedEndings` | `string[]` | 요청 회원이 도달한 엔딩 이름<br>게스트는 빈 배열 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 404 | `NOT_FOUND` | 부재, 삭제, 형식 오류, 읽을 수 없는 스토리 |

<details>
<summary><b>상세 응답 예시</b></summary>

<br>

**1) Request**

```text
GET /stories/3f2504e0-4f89-41d3-9a0c-0305e82c3301
Authorization: Bearer <accessToken>
```

<br>

**2) 200 Response body**

```json
{
  "id": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "thumbnailUrl": "https://cdn.example.com/thumbnails/generated/3f2504e0-4f89-41d3-9a0c-0305e82c3301/썸네일_기본.webp",
  "title": "사라지는 내일의 기록",
  "oneLineIntro": "마법 도서관에서 지워진 미래를 추적하는 신입 기록관 서린의 이야기",
  "description": "서린과 도윤은 마법 도서관에서 사라진 기록의 출처를 추적한다.",
  "genres": ["판타지", "미스터리"],
  "hashtags": [],
  "author": { "id": null, "nickname": "은빛여우", "profileImageUrl": null },
  "turnCount": 128,
  "likeCount": 32,
  "isOwner": false,
  "isLiked": true,
  "startSettings": [
    {
      "id": "1b2e4d6f-8a9c-4b1d-9e2f-3a4b5c6d7e8f",
      "name": "폐관 뒤의 도서관",
      "prologue": "*마지막 종이 울린 뒤, 서린은 빈 기록장 가장자리에서 푸른 빛을 발견한다.*",
      "startSituation": "폐관 직후 기록 열람실에서 서린과 도윤이 빛나는 기록장을 살핀다.",
      "suggestedInputs": ["기록장을 빛에 비춰 본다.", "도윤에게 푸른 흔적을 가리킨다.", "기록장의 보관 위치를 확인한다."],
      "endings": [
        {
          "name": "되찾은 기록",
          "requirement": { "minTurns": 8, "achievementCondition": "소실 원인을 밝히고 원본을 보존한다." },
          "epilogue": "서린의 선택이 도서관의 기록을 지켜낸 결과를 보여준다."
        }
      ]
    }
  ],
  "visibility": "PUBLIC",
  "status": "PUBLISHED",
  "lorebooks": [
    { "id": 7, "name": "기록의 잔향", "genre": "판타지", "content": "마법으로 지워진 문장은 원본이 보관된 장소에 푸른 빛의 흔적을 남긴다." }
  ],
  "mainEvents": [
    { "name": "기록의 잔향 발견", "description": "기록장에 남은 푸른 흔적이 지하 보관실로 이어진다는 단서를 찾는다.", "keySentence": "사라진 문장의 흔적을 조사한다.", "sortOrder": 0 }
  ],
  "characters": [
    { "name": "도윤", "imageUrl": "https://cdn.example.com/characters/generated/3f2504e0-4f89-41d3-9a0c-0305e82c3301/도윤_기본.webp", "description": "기록을 지키는 과묵한 사서. 서린의 조사를 조용히 돕는다." }
  ],
  "reachedEndings": [],
  "createdAt": "2026-06-10T12:00:00Z"
}
```

<br>

**3) 404 Response body**

비공개 스토리를 소유자가 아닌 회원이 조회한 경우도 같은 응답이다.

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 404,
  "code": "NOT_FOUND",
  "message": "스토리를 찾을 수 없습니다.",
  "path": "/api/v1/stories/00000000-0000-0000-0000-000000000000",
  "details": []
}
```

</details>

<br>

### 4-2-8 삭제

| 항목 | 값 |
|---|---|
| 요청 | `DELETE /stories/{storyId}` |
| 인증 | 선택 |
| 성공 | 204, 본문 없음 |

요청 본문은 없다. 삭제한 스토리는 모든 조회에서 제외한다. 삭제는 되돌릴 수 없다.

**1. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 403 | `FORBIDDEN` | 소유자가 아닌 요청 |
| 404 | `NOT_FOUND` | 부재, 삭제, 형식 오류 |

<details>
<summary><b>실패 응답 예시</b></summary>

<br>

**403 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 403,
  "code": "FORBIDDEN",
  "message": "권한이 없습니다.",
  "path": "/api/v1/stories/3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "details": []
}
```

</details>

<br>

### 4-2-9 간편 제작 태그 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /stories/simple/tags` |
| 인증 | 불필요 |
| 성공 | 200 |

활성 제공 태그를 카테고리, 노출 순서로 반환한다. `GENRE`는 대표 15개만 대표 순서로 반환한다. 전체 장르는 제공 장르 조회를 쓴다.

**1. 응답**

| 응답 항목 | 타입 | 의미 |
|---|---|---|
| `[].id` | `integer` | 태그 ID |
| `[].name` | `string` | 태그 이름 |
| `[].category` | `string` | `GENRE`, `PROTAGONIST`, `SUPPORTING_CHARACTER` |

<br>

**2. 실패 응답**

공통 실패 외에는 없다.

<details>
<summary><b>태그 응답 예시</b></summary>

<br>

```json
[
  { "id": 10, "name": "계약결혼", "category": "GENRE" },
  { "id": 45, "name": "로맨스판타지", "category": "GENRE" },
  { "id": 205, "name": "기억을 잃은", "category": "PROTAGONIST" },
  { "id": 301, "name": "냉정한", "category": "SUPPORTING_CHARACTER" }
]
```

</details>

<br>

### 4-2-10 화풍 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /stories/art-styles` |
| 인증 | 선택 |
| 성공 | 200 |

활성 화풍을 노출 순서로 반환한다. 식별자는 문자열 `code`다. 간편 제작 완성 요청의 `artStyle`과 AI 컴파일 요청의 `art_style`에 그대로 쓴다.

**1. 응답**

| 응답 항목 | 타입 | 의미 |
|---|---|---|
| `[].code` | `string` | 화풍 코드 |
| `[].name` | `string` | 표시 이름 |
| `[].description` | `string` | 설명 |
| `[].previewImageUrl` | `string / null` | 미리보기 이미지<br>초기 시드는 `null` |

<br>

**2. 제공 화풍**

| 코드 | 이름 |
|---|---|
| `ANIME` | 애니메이션 |
| `SEMI_REAL` | 반실사 |
| `LIGHT_NOVEL` | 라노벨 |
| `CINEMATIC` | 시네마틱 |
| `WEBTOON` | 웹툰 |
| `SHOJO` | 순정 |
| `MOE` | 모에 |
| `RETRO` | 레트로 |
| `OIL_PAINTING` | 유화 |
| `INK_WASH` | 수묵 |
| `NONE` | 없음, 인물 이미지와 표지를 만들지 않음 |

<br>

**3. 실패 응답**

공통 실패 외에는 없다.

<details>
<summary><b>화풍 목록 응답 예시</b></summary>

<br>

```json
[
  { "code": "ANIME", "name": "애니메이션", "description": "깔끔한 선과 선명한 색의 일본 애니메이션 그림체", "previewImageUrl": null },
  { "code": "NONE", "name": "없음", "description": "인물 이미지를 만들지 않아요", "previewImageUrl": null }
]
```

</details>

<br>

### 4-2-11 간편 제작 스토리라인 생성

| 항목 | 값 |
|---|---|
| 요청 | `POST /stories/simple/storylines` |
| 인증 | 선택 |
| 성공 | 201 |

**1. 요청 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `requestId` | `string` | 필수 | 클라이언트가 생성한 UUID<br>같은 값으로 다시 보내면 완료된 요청은 같은 응답 반환<br>진행 중이면 409<br>실패한 요청은 재실행 |
| `genreTagIds` | `integer[]` | 선택 | 제공 장르 태그 ID 최대 20개, 각 1 이상<br>선택 순서 유지, 기본값 `[]` |
| `customGenreTags` | `string[]` | 선택 | 누락 또는 빈 배열만 허용<br>값이 하나라도 있으면 거절 |
| `protagonist` | `object` | 필수 | 주인공 인물 객체 |
| `supportingCharacters` | `object[]` | 선택 | 주변 인물 객체 최대 5개, 기본값 `[]` |
| `parentCreationId` | `string` | 선택 | 재생성이면 직전 생성의 `requestId`<br>검증에 실패해도 거절하지 않고 연결 헤더만 생략 |
| `isRegenerated` | `boolean` | 선택 | AI 호출 헤더로 그대로 전달 |

<br>

**2. 인물 객체**

장르와 특징이 모두 비어 있어도 스토리라인을 생성한다. 인물 이름이 겹치면 거절한다. 중복 판정 키는 NFC 정규화, 공백 제거, 소문자 변환을 적용한 값이다.

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `name` | `string` | 선택 | 30자 이하<br>비우면 AI가 정함 |
| `gender` | `string` | 선택 | `MALE` 또는 `FEMALE`<br>비우면 AI가 정함 |
| `featureTagIds` | `integer[]` | 선택 | 제공 특징 태그 ID, 기본값 `[]` |
| `customTags` | `string[]` | 선택 | 직접 입력 특징, 각 30자 이하, 기본값 `[]`<br>`featureTagIds`와 합쳐 최대 3개<br>개수는 중복 제거 전 기준 |

<br>

**3. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `simpleCreationId` | `integer` | 간편 제작 진행 ID<br>스토리 완성 요청에 사용 |
| `selectedTags.genreTags` | `object[]` | 저장된 제공 장르, `id`, `name`, `category` |
| `selectedTags.protagonist` | `object` | `name`, `gender`, `features[]`<br>`features`는 `id`, `name`, `category`<br>직접 입력 특징은 `id` 없이 이름만 |
| `selectedTags.supportingCharacters` | `object[]` | 주인공과 같은 구조 |
| `storylines` | `object[]` | 정확히 3개 |
| `storylines[].id` | `integer` | 스토리라인 ID<br>스토리 완성과 평가에 사용 |
| `storylines[].storyline` | `string` | 줄거리 |
| `storylines[].recommendedInfos` | `object[]` | 추천 추가 정보 3개, `id`와 `text` |

<br>

**4. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 게스트의 필수 디바이스 헤더 누락, 검증 실패, 무효 태그 ID, 인물 이름 중복 |
| 400 | `CUSTOM_GENRE_NOT_ALLOWED` | `customGenreTags`에 값 존재 |
| 402 | `GUEST_TRIAL_LIMIT_EXCEEDED` | 게스트 체험 한도 소진 |
| 409 | `CONFLICT` | 같은 `requestId`가 진행 중<br>소유자나 단계가 다른 `requestId` 재사용 |
| 422 | `CONTENT_REJECTED` | AI가 입력 내용을 이유로 생성을 거절 |
| 502 | `BAD_GATEWAY` | AI 호출 실패, 빈 응답 |

<details>
<summary><b>스토리라인 생성 요청, 응답 예시</b></summary>

<br>

**1) Request body**

```json
{
  "requestId": "6d0f4a2e-1b7c-4e2a-9f11-2a4d1c9e8b10",
  "genreTagIds": [175, 48],
  "customGenreTags": [],
  "protagonist": { "name": "서린", "gender": "FEMALE", "featureTagIds": [205], "customTags": ["꼼꼼한"] },
  "supportingCharacters": [
    { "name": "도윤", "gender": "MALE", "featureTagIds": [301, 302], "customTags": [] }
  ],
  "parentCreationId": null,
  "isRegenerated": false
}
```

<br>

**2) 201 Response body**

스토리라인은 3개 중 1개만 표시했다.

```json
{
  "simpleCreationId": 1207,
  "selectedTags": {
    "genreTags": [
      { "id": 175, "name": "판타지", "category": "GENRE" },
      { "id": 48, "name": "미스터리", "category": "GENRE" }
    ],
    "protagonist": {
      "name": "서린",
      "gender": "FEMALE",
      "features": [
        { "id": 205, "name": "기억을 잃은", "category": "PROTAGONIST" },
        { "id": null, "name": "꼼꼼한", "category": "PROTAGONIST" }
      ]
    },
    "supportingCharacters": [
      {
        "name": "도윤",
        "gender": "MALE",
        "features": [
          { "id": 301, "name": "냉정한", "category": "SUPPORTING_CHARACTER" },
          { "id": 302, "name": "과묵한", "category": "SUPPORTING_CHARACTER" }
        ]
      }
    ]
  },
  "storylines": [
    {
      "id": 5001,
      "storyline": "신입 기록관 서린은 마법 도서관에서 다음 날의 기록이 지워지고 있음을 발견한다. 과묵한 사서 도윤과 함께 사라진 기록의 출처를 추적한다.",
      "recommendedInfos": [
        { "id": 9001, "text": "지워진 기록은 지하 보관실에 흔적으로 남는다." },
        { "id": 9002, "text": "도윤은 과거 기록 소실 사건의 유일한 목격자다." },
        { "id": 9003, "text": "기록을 복원하려면 누군가의 잊힌 기억이 필요하다." }
      ]
    }
  ]
}
```

<br>

**3) 402 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 402,
  "code": "GUEST_TRIAL_LIMIT_EXCEEDED",
  "message": "게스트 체험 횟수를 모두 사용했습니다.",
  "path": "/api/v1/stories/simple/storylines",
  "details": []
}
```

</details>

<br>

### 4-2-12 간편 제작 완성

| 항목 | 값 |
|---|---|
| 요청 | `POST /stories/simple` |
| 인증 | 선택 |
| 성공 | 201 |

회원은 정책에서 정한 양만큼 이프를 선차감하고 게스트는 완성 체험 횟수를 사용한다.

**1. 요청 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `requestId` | `string` | 필수 | 클라이언트가 생성한 UUID<br>스토리라인 생성과 다른 값<br>재요청 규칙은 스토리라인 생성과 같음 |
| `simpleCreationId` | `integer` | 필수 | 스토리라인 생성 응답의 진행 ID |
| `storylineId` | `integer` | 필수 | 선택한 스토리라인 ID |
| `additionalInfos` | `string[]` | 선택 | 추가 정보 최대 13개, 항목당 100자<br>선택한 추천 정보와 직접 입력한 정보를 합쳐 보냄<br>기본값 `[]` |
| `artStyle` | `string` | 선택 | 활성 화풍 코드, 기본값 `ANIME`<br>빈 문자열은 기본값으로 보지 않고 거절<br>`NONE`이면 인물 이미지와 표지를 만들지 않음<br>차감액은 같음 |
| `visibility` | `string` | 선택 | `PUBLIC` 또는 `PRIVATE`, 기본값 `PRIVATE`<br>게스트도 `PUBLIC`을 지정할 수 있음<br>게스트 스토리는 이관으로 회원 소유가 된 뒤 공개 목록과 검색에 실림 |
| `isRegenerated` | `boolean` | 선택 | AI 호출 헤더로 그대로 전달 |
| `draftId` | `string` | 선택 | 접수 시 삭제할 내 초안<br>회원 요청만 처리하고 없거나 타인의 초안이면 무시 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `id` | `string` | 생성된 스토리 공개 식별자 |
| `title` | `string` | 기본 주인공 이름으로 치환한 제목 |
| `oneLineIntro` | `string / null` | 치환한 한 줄 소개 |
| `description` | `string / null` | 치환한 주요 내용 |
| `genres` | `string[]` | 선택한 장르 이름 |
| `startSettings` | `object[]` | 항상 1개, 상세 응답과 같은 구조 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 게스트의 필수 디바이스 헤더 누락, 검증 실패, 무효 화풍 코드 |
| 402 | `INSUFFICIENT_CREDIT` | 회원의 이프 부족 |
| 402 | `GUEST_TRIAL_LIMIT_EXCEEDED` | 게스트 체험 한도 소진 |
| 403 | `FORBIDDEN` | 정지 계정, 회원 소유 진행의 소유권 위반 |
| 404 | `NOT_FOUND` | 진행이나 스토리라인 없음 |
| 409 | `CONFLICT` | 이미 완성된 진행, 같은 `requestId`가 진행 중<br>소유자나 단계가 다른 `requestId` 재사용 |
| 422 | `CONTENT_REJECTED` | AI가 입력 내용을 이유로 생성을 거절 |
| 502 | `BAD_GATEWAY` | AI 호출 실패, 빈 응답<br>컴파일 결과의 사건이나 엔딩 이름 중복, 본문에 이름 토큰이 있는데 주인공 이름 없음 |

<details>
<summary><b>스토리 완성 요청, 응답 예시</b></summary>

<br>

**1) Request body**

```json
{
  "requestId": "0b7c9d1e-3f4a-4b5c-8d6e-7f8091a2b3c4",
  "simpleCreationId": 1207,
  "storylineId": 5001,
  "additionalInfos": [
    "지워진 기록은 지하 보관실에 흔적으로 남는다.",
    "결말은 서린이 기록을 되찾는 여운 있는 해피엔딩"
  ],
  "visibility": "PUBLIC",
  "isRegenerated": false
}
```

<br>

**2) 201 Response body**

```json
{
  "id": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "title": "사라지는 내일의 기록",
  "oneLineIntro": "마법 도서관에서 지워진 미래를 추적하는 신입 기록관 서린의 이야기",
  "description": "서린과 도윤은 마법 도서관에서 사라진 기록의 출처를 추적한다.",
  "genres": ["판타지", "미스터리"],
  "startSettings": [
    {
      "id": "1b2e4d6f-8a9c-4b1d-9e2f-3a4b5c6d7e8f",
      "name": "폐관 뒤의 도서관",
      "prologue": "*마지막 종이 울린 뒤, 서린은 빈 기록장 가장자리에서 푸른 빛을 발견한다.*",
      "startSituation": "폐관 직후 기록 열람실에서 서린과 도윤이 빛나는 기록장을 살핀다.",
      "suggestedInputs": ["기록장을 빛에 비춰 본다.", "도윤에게 푸른 흔적을 가리킨다.", "기록장의 보관 위치를 확인한다."],
      "endings": [
        {
          "name": "되찾은 기록",
          "requirement": { "minTurns": 8, "achievementCondition": "소실 원인을 밝히고 원본을 보존한다." },
          "epilogue": "서린의 선택이 도서관의 기록을 지켜낸 결과를 보여준다."
        },
        {
          "name": "남겨진 빈 페이지",
          "requirement": { "minTurns": 6, "achievementCondition": "추가 소실은 막았지만 사라진 기록을 복원하지 못한다." },
          "epilogue": "서린과 도윤이 남은 단서를 정리하며 다음 조사를 준비한다."
        }
      ]
    }
  ]
}
```

<br>

**3) 502 Response body**

AI 호출이 실패한 경우다. 차감한 이프는 환불되고 같은 `requestId`로 다시 요청할 수 있다.

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 502,
  "code": "BAD_GATEWAY",
  "message": "스토리 생성에 실패했습니다. 다시 시도해 주세요.",
  "path": "/api/v1/stories/simple",
  "details": []
}
```

<br>

**4) 422 Response body**

AI가 입력 내용을 이유로 생성을 거절한 경우다. 차감한 이프는 환불된다. 같은 입력은 다시 거절되므로 입력을 고쳐 새 `requestId`로 요청한다.

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 422,
  "code": "CONTENT_REJECTED",
  "message": "입력 내용이 안전 정책에 맞지 않아 생성할 수 없습니다.",
  "path": "/api/v1/stories/simple",
  "details": []
}
```

</details>

<br>

### 4-2-13 간편 제작 복구 조회

| 항목 | 값 |
|---|---|
| 요청 | `GET /stories/simple/creation-requests/{requestId}` |
| 인증 | 선택 |
| 성공 | 200 |

스토리라인 생성과 스토리 완성 요청의 진행 상태를 반환한다. 응답을 받지 못한 채 연결이 끊겼을 때 쓴다. `PENDING`이면 다시 조회한다. `COMPLETED`이면 `result`를 원래 응답으로 쓴다. `FAILED`이거나 회수 기준 시간을 넘긴 `PENDING`이면 같은 `requestId`로 원래 생성 요청을 다시 보낸다. 다시 보낸 요청이 422 `CONTENT_REJECTED`로 실패하면 같은 입력은 다시 거절되므로 입력을 고쳐 새 `requestId`로 요청한다. ([5-3-5 재시도와 시간 한도](5-3-ERROR-HANDLING.md#5-3-5-재시도와-시간-한도))

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `stage` | `string` | `STORYLINE_GENERATION` 또는 `STORY_COMPLETION` |
| `status` | `string` | `PENDING`, `COMPLETED`, `FAILED` |
| `result` | `object / null` | `COMPLETED`이면 원래 `POST` 응답 본문과 같은 구조, 그 외 `null` |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 404 | `NOT_FOUND` | 없는 `requestId`, 타인의 요청 |

<details>
<summary><b>복구 조회 응답 예시</b></summary>

<br>

**1) 진행 중**

```json
{
  "stage": "STORY_COMPLETION",
  "status": "PENDING",
  "result": null
}
```

<br>

**2) 완료**

`result`는 스토리 완성 응답 본문이며 안쪽은 생략했다.

```json
{
  "stage": "STORY_COMPLETION",
  "status": "COMPLETED",
  "result": {
    "id": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
    "title": "사라지는 내일의 기록",
    "oneLineIntro": "마법 도서관에서 지워진 미래를 추적하는 신입 기록관 서린의 이야기",
    "description": "서린과 도윤은 마법 도서관에서 사라진 기록의 출처를 추적한다.",
    "genres": ["판타지", "미스터리"],
    "startSettings": []
  }
}
```

<br>

**3) 404 Response body**

타인의 요청을 조회한 경우도 같은 응답이다.

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 404,
  "code": "NOT_FOUND",
  "message": "요청을 찾을 수 없습니다.",
  "path": "/api/v1/stories/simple/creation-requests/0b7c9d1e-3f4a-4b5c-8d6e-7f8091a2b3c4",
  "details": []
}
```

</details>

<br>

### 4-2-14 간편 제작 스토리라인 평가

| 항목 | 값 |
|---|---|
| 요청 | `PUT /stories/simple/storylines/{storylineId}/rating` |
| 요청 | `DELETE /stories/simple/storylines/{storylineId}/rating` |
| 인증 | 선택 |
| 성공 | `PUT` 200 |
| 성공 | `DELETE` 204, 본문 없음 |

후보당 한 행을 두고 새 값으로 덮어쓴다. `DELETE`는 평가가 없어도 성공한다.

**1. `PUT` 요청 본문**

| 필드명 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `rating` | `string` | 필수 | `GOOD` 또는 `BAD` |

<br>

**2. `PUT` 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `id` | `integer` | 스토리라인 ID |
| `rating` | `string` | 저장된 평가 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 403 | `FORBIDDEN` | 소유자 있는 진행을 소유자가 아닌 요청자가 평가 |
| 404 | `NOT_FOUND` | 없는 스토리라인 |

<details>
<summary><b>평가 요청, 응답 예시</b></summary>

<br>

**1) Request body**

```json
{ "rating": "GOOD" }
```

<br>

**2) 200 Response body**

```json
{ "id": 5001, "rating": "GOOD" }
```

<br>

**3) 403 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 403,
  "code": "FORBIDDEN",
  "message": "권한이 없습니다.",
  "path": "/api/v1/stories/simple/storylines/5001/rating",
  "details": []
}
```

</details>

<br>

### 4-2-15 일반 제작 등록

| 항목 | 값 |
|---|---|
| 요청 | `POST /stories/general` |
| 인증 | 필수 |
| 성공 | 202 |

**1. 요청 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `title` | `string` | 필수 | 100자 이하, 토큰 원문 |
| `oneLineIntro` | `string` | 필수 | 255자 이하, 토큰 원문 |
| `description` | `string` | 선택 | 주요 내용 |
| `protagonistName` | `string` | 선택 | 기본 주인공 이름, 앞뒤 공백 제거 후 1~30자<br>저장할 본문에 `{username}`이 있는데 없으면 거절 |
| `genres` | `string[]` | 필수 | 활성 제공 장르의 정식 이름 1~8개, 각 30자 이하<br>정규화 키가 같은 표기는 정식 이름으로 변환<br>별칭과 비활성 장르는 거절<br>입력 순서 보존<br>중복은 처음 위치만 유지 |
| `storySettings` | `object` | 필수 | 통글 4필드 |
| `storySettings.worldSetting` | `string` | 필수 | 세계관 |
| `storySettings.characterSetting` | `string` | 필수 | 등장인물 |
| `storySettings.userRoleSetting` | `string` | 필수 | 이름을 제외한 주인공 설명 |
| `storySettings.ruleSetting` | `string` | 필수 | 전개 규칙 |
| `startSettings` | `object[]` | 필수 | 1개 이상 |
| `startSettings[].id` | `string` | 선택 | 등록에서는 무시 |
| `startSettings[].name` | `string` | 필수 | 시작 장면 이름, 100자 이하 |
| `startSettings[].prologue` | `string` | 필수 | 프롤로그 |
| `startSettings[].startSituation` | `string` | 필수 | 시작 상황 |
| `startSettings[].suggestedInputs` | `string[]` | 필수 | 정확히 3개, 빈 문자열 불가 |
| `startSettings[].endings` | `object[]` | 선택 | 시작 설정당 최대 10개, 기본값 `[]`<br>이름은 시작 설정 안에서 유일 |
| `startSettings[].endings[].name` | `string` | 필수 | 엔딩 이름, 100자 이하 |
| `startSettings[].endings[].requirement` | `object` | 필수 | `minTurns`(0 이상 정수)와 `achievementCondition`(자연어, 필수) |
| `startSettings[].endings[].epilogue` | `string` | 필수 | 엔딩 연출 방향 |
| `mainEvents` | `object[]` | 선택 | 최대 10개, 기본값 `[]`<br>배열 순서가 표시 순서<br>이름은 스토리 안에서 유일 |
| `mainEvents[].name` | `string` | 필수 | 사건 이름, 100자 이하 |
| `mainEvents[].description` | `string` | 필수 | 사건 설명 |
| `mainEvents[].keySentence` | `string` | 필수 | 관련성 판단 문장 |
| `visibility` | `string` | 선택 | `PUBLIC` 또는 `PRIVATE`, 기본값 `PRIVATE` |
| `thumbnailObjectKey` | `string` | 선택 | draft presign으로 올린 표지의 객체 키 |
| `characters` | `object[]` | 선택 | 최대 6명, 기본값 `[]`<br>이름은 스토리 안에서 유일 |
| `characters[].id` | `string` | 선택 | 등록에서 값이 있으면 거절 |
| `characters[].name` | `string` | 필수 | 인물 이름, 100자 이하 |
| `characters[].description` | `string` | 선택 | 생략, `null`, 빈 문자열, 공백만 있는 문자열은 `null` 저장<br>그 외는 앞뒤 공백 제거 후 1~150자<br>CR, LF, 탭이 있으면 거절 |
| `characters[].images` | `object[]` | 선택 | 인물당 최대 10장, 배열 순서가 표시 순서 |
| `characters[].images[].objectKey` | `string` | 필수 | draft presign으로 올린 객체 키 |
| `characters[].images[].imageName` | `string` | 필수 | `{인물이름}_{접미}`, 접미사는 한글, 영문, 숫자로 구성된 1~20자<br>같은 인물 안에서 유일 |
| `draftId` | `string` | 선택 | 접수 시 삭제할 내 초안<br>없거나 타인의 초안이면 무시 |

<br>

**2. 응답**

접수 시점에는 스토리 ID가 없다. 검수 결과와 생성된 스토리 ID는 제출본 조회 `GET /stories/submissions/{submissionId}`로 확인한다. 제출본 조회, 재제출, 취소 API는 MODERATION 세트에 있다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `submissionId` | `string` | 제출본 공개 식별자 |
| `status` | `string` | 항상 `PENDING` |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 검증 실패, 토큰이 있는데 기본 주인공 이름 없음, 인물 소개 형식 위반<br>임시 업로드 접두어 범위를 벗어난 객체 키, 지원하지 않는 형식, 5MB 초과 |
| 400 | `INVALID_GENRE` | 허용되지 않는 장르, `details`에 무효 원소의 `genres[i]` |
| 400 | `UPLOAD_NOT_FOUND` | 객체 키에 아직 파일이 없음<br>업로드를 마친 뒤 다시 보냄 |
| 400 | `IMAGES_TOO_LARGE` | 검수 요청 예상 용량 초과 |
| 409 | `CONFLICT` | 같은 인물 안의 이미지 이름 중복 |

<details>
<summary><b>등록 요청, 응답 예시</b></summary>

<br>

**1) Request body**

```json
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

<br>

**2) 202 Response body**

```json
{
  "submissionId": "e3b0c442-98fc-4c14-9afb-f4c8996fb924",
  "status": "PENDING"
}
```

<br>

**3) 400 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 400,
  "code": "INVALID_GENRE",
  "message": "허용되지 않는 장르입니다.",
  "path": "/api/v1/stories/general",
  "details": [
    {
      "field": "genres[1]",
      "message": "활성 제공 장르가 아닙니다."
    }
  ]
}
```

</details>

<br>

### 4-2-16 수정 폼

| 항목 | 값 |
|---|---|
| 요청 | `GET /stories/{storyId}/edit` |
| 인증 | 선택 |
| 성공 | 200 |

소유자 화면이므로 검수 게이트를 적용하지 않은 원본 이미지와 상태를 함께 반환한다. 텍스트 필드는 이름 토큰을 치환하지 않은 원문이다.

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `title`, `oneLineIntro`, `description`, `genres`, `storySettings`, `startSettings`, `mainEvents`, `visibility`, `protagonistName` | 등록 요청과 같음 | 현재 스토리 또는 미승인 제출본을 반영한 값<br>`startSettings`와 `mainEvents`는 상세 응답 구조<br>`storySettings`는 비어 있으면 각 필드가 `null` |
| `thumbnailUrl` | `string / null` | 현재 표지 |
| `thumbnailModerationStatus` | `string` | `APPROVED`, `PENDING`, `REJECTED` |
| `characters` | `object[]` | 인물과 이미지 관리용 |
| `characters[].id` | `string` | 인물 공개 식별자<br>수정 요청의 매칭 키와 이미지 삭제 경로에 사용 |
| `characters[].name` | `string` | 인물 이름 |
| `characters[].description` | `string / null` | 인물 소개 |
| `characters[].images` | `object[]` | 표시 순서의 이미지 전부 |
| `characters[].images[].id` | `string` | 이미지 공개 식별자 |
| `characters[].images[].imageName` | `string` | 이미지 이름 |
| `characters[].images[].imageUrl` | `string` | 이미지 제공 URL |
| `characters[].images[].moderationStatus` | `string` | `APPROVED`, `PENDING`, `REJECTED` |
| `characters[].images[].objectKey` | `string / null` | 승인되지 않은 새 이미지의 업로드 객체 키 |
| `submission` | `object / null` | 최신 제출본이 대기, 반려, 실패면 `submissionId`, `status`, `issues`, `errorCode`, `imageErrors`, 그 외 `null` |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 403 | `FORBIDDEN` | 소유자가 아닌 요청 |
| 404 | `NOT_FOUND` | 부재, 삭제, 형식 오류 |

<details>
<summary><b>수정 폼 응답 예시</b></summary>

<br>

**1) 200 Response body**

반려된 제출본이 있는 상태다. `startSettings`와 `mainEvents` 안쪽은 상세 응답 예시와 같아 생략했다.

```json
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
  "startSettings": [],
  "mainEvents": [],
  "visibility": "PRIVATE",
  "thumbnailUrl": "https://cdn.example.com/thumbnails/uploaded/3f2504e0-4f89-41d3-9a0c-0305e82c3301/4c9e2b7a-1d3f-4a5b-8c6d-9e0f1a2b3c4d.webp",
  "thumbnailModerationStatus": "APPROVED",
  "characters": [
    {
      "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
      "name": "도윤",
      "description": "기록을 지키는 과묵한 사서.",
      "images": [
        {
          "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
          "imageName": "도윤_기본",
          "imageUrl": "https://cdn.example.com/characters/uploaded/3f2504e0-4f89-41d3-9a0c-0305e82c3301/5d0f3c8b-2e4a-4b6c-9d7e-0f1a2b3c4d5e.webp",
          "moderationStatus": "APPROVED",
          "objectKey": null
        }
      ]
    }
  ],
  "submission": {
    "submissionId": "f1e2d3c4-b5a6-4978-8a9b-0c1d2e3f4a5b",
    "status": "REJECTED",
    "issues": [
      { "path": "startSettings[0].prologue", "type": "TEXT", "rule": "VIOLENCE", "reason": "과도한 폭력 묘사" }
    ],
    "errorCode": null,
    "imageErrors": []
  }
}
```

<br>

**2) 403 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 403,
  "code": "FORBIDDEN",
  "message": "권한이 없습니다.",
  "path": "/api/v1/stories/3f2504e0-4f89-41d3-9a0c-0305e82c3301/edit",
  "details": []
}
```

</details>

<br>

### 4-2-17 스토리 수정

| 항목 | 값 |
|---|---|
| 요청 | `PATCH /stories/{storyId}` |
| 인증 | 필수 |
| 성공 | 공개 범위 단독이면 200 수정 폼<br>공개 중단된 스토리를 `PUBLIC`으로 바꾸는 요청은 제외 |
| 성공 | 그 외는 202, 등록 응답과 같은 `submissionId`, `status` |

등록 요청의 모든 필드는 선택적으로 보낼 수 있다. 보낸 필드만 변경한다. `null`은 미전송과 같다. 검수로 접수된 수정의 결과는 수정 폼 응답의 `submission` 또는 제출본 조회로 확인한다.

**1. 요청 본문**

| 필드명 | 규칙 |
|---|---|
| `visibility` | 이 필드만 보내면 즉시 반영하고 200 수정 폼 반환<br>다른 필드와 함께 보내면 검수 접수<br>관리자가 공개 중단한 스토리에 `PUBLIC`을 보내면 이 필드만 보내도 검수 접수하고 승인되면 공개 |
| `protagonistName` | 생략과 `null`은 유지<br>빈 문자열과 공백만 있는 문자열은 거절<br>토큰과 이름의 관계는 기존 값에 요청을 반영한 전체 결과로 검증 |
| `genres` | 활성 제공 장르이거나 해당 스토리에 이미 반영된 장르만 허용<br>기존 장르는 저장 표기 유지<br>제거한 커스텀 장르는 다시 추가 불가 |
| `startSettings` | 보내면 전체 교체, 1개 이상<br>`id`가 기존 항목과 일치하면 해당 행을 갱신<br>`id`가 없으면 추가하고 요청에서 빠진 기존 항목은 삭제 |
| `startSettings[].id`, `characters[].id` | 없는 `id`, 다른 스토리의 `id`, 중복 `id`는 거절 |
| `mainEvents` | 보내면 전체 교체<br>빈 배열은 모두 삭제 |
| `thumbnailObjectKey` | 보내면 표지 교체<br>삭제는 `DELETE /stories/{storyId}/thumbnail` |
| `characters` | 보내면 전체 교체<br>빈 배열은 모두 삭제<br>`id`가 기존 인물과 일치하면 이름을 변경<br>`id`가 없으면 추가하고 요청에서 빠진 기존 인물은 이미지와 함께 삭제 |
| `characters[].description` | 생략과 `null`은 유지<br>빈 문자열과 공백만 있는 문자열은 삭제<br>그 외는 등록과 같은 규칙 |
| `characters[].images` | 생략은 유지<br>빈 배열은 모두 삭제<br>항목은 기존 유지 `{id}` 또는 신규 `{objectKey, imageName}` 중 하나<br>기존 유지에서 `imageName`을 생략하면 접두를 현재 인물 이름으로 맞춘 이름 |
| `storySettings` | 보내면 네 필드 전체 교체, 없던 스토리는 생성 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 등록과 같은 검증 실패<br>인물 이름 변경으로 생성된 이미지 이름이 120자 초과 |
| 400 | `INVALID_GENRE` | 허용되지 않는 장르 |
| 400 | `UPLOAD_NOT_FOUND` | 객체 키에 아직 파일이 없음<br>업로드를 마친 뒤 다시 보냄 |
| 400 | `IMAGES_TOO_LARGE` | 검수 요청 예상 용량 초과 |
| 403 | `FORBIDDEN` | 소유자가 아닌 요청 |
| 404 | `NOT_FOUND` | 부재, 삭제, 형식 오류 |
| 409 | `CONFLICT` | 검수 중인 스토리, 같은 인물 안의 이미지 이름 중복 |

<details>
<summary><b>수정 요청, 응답 예시</b></summary>

<br>

**1) 공개 범위만 바꾸는 Request body**

```json
{ "visibility": "PUBLIC" }
```

공개 중단되지 않은 스토리의 200 응답은 수정 폼이다. 관리자가 공개 중단한 스토리는 같은 요청에도 202로 검수 접수한다.

<br>

**2) 인물 이미지를 바꾸는 Request body**

기존 이미지 한 장은 유지하고 한 장을 새로 추가한다. 이 인물 외의 인물은 요청에서 빠져 삭제된다.

```json
{
  "characters": [
    {
      "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
      "name": "도윤",
      "images": [
        { "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e" },
        { "objectKey": "characters/uploaded/3f2504e0-4f89-41d3-9a0c-0305e82c3301/6e1a4d9c-3f5b-4c7d-8e9f-1a2b3c4d5e6f.webp", "imageName": "도윤_미소" }
      ]
    }
  ]
}
```

<br>

**3) 202 Response body**

```json
{
  "submissionId": "c4d5e6f7-a8b9-4c0d-9e1f-2a3b4c5d6e7f",
  "status": "PENDING"
}
```

<br>

**4) 409 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 409,
  "code": "CONFLICT",
  "message": "검수 중인 스토리는 수정할 수 없습니다.",
  "path": "/api/v1/stories/3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "details": []
}
```

</details>

<br>

### 4-2-18 이미지 presign

| 항목 | 값 |
|---|---|
| 요청 | `POST /stories/images/presign` |
| 요청 | `POST /stories/{storyId}/images/presign` |
| 인증 | 필수 |
| 성공 | 201 |

등록 전 업로드는 임시 업로드 접두어(draft prefix)를 사용한다. 등록된 스토리의 업로드는 해당 스토리의 접두어를 사용한다.

**1. 요청 본문**

| 필드명 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `kind` | `string` | 필수 | `COVER` 또는 `CHARACTER`<br>이미지 종류에 따라 객체 키의 접두어 구분 |
| `contentType` | `string` | 필수 | `image/jpeg`, `image/png`, `image/webp` |
| `contentLength` | `integer` | 필수 | 1~5,242,880바이트<br>클라이언트는 이 값 그대로 `PUT` |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `uploadUrl` | `string` | `PUT` 대상 presigned URL<br>요청한 `Content-Type`과 `Content-Length` 그대로 보내야 서명이 맞음 |
| `objectKey` | `string` | 업로드 뒤 등록이나 수정 요청에 넣는 객체 키 |
| `expiresInSeconds` | `integer` | 서명 만료, 600 |

<br>

**3. 객체 키 형식**

| 발급 경로 | 객체 키 형식 |
|---|---|
| `POST /stories/images/presign` | `thumbnails/uploaded/drafts/{userPublicId}/{uuid}.{ext}` 또는 `characters/uploaded/drafts/{userPublicId}/{uuid}.{ext}` |
| `POST /stories/{storyId}/images/presign` | `thumbnails/uploaded/{storyPublicId}/{uuid}.{ext}` 또는 `characters/uploaded/{storyPublicId}/{uuid}.{ext}` |

등록과 수정 요청은 객체 키가 요청자의 임시 업로드 접두어 또는 해당 스토리의 접두어로 시작하는지 확인한다. 이어서 HEAD로 객체 존재 여부, 크기, 형식을 다시 확인한다. 이미지 해상도와 가로세로 비율은 확인하지 않는다.

<br>

**4. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 지원하지 않는 형식, 5,242,880 바이트 초과, 게스트 소유 스토리 |
| 403 | `FORBIDDEN` | 정지 계정, 소유자가 아닌 요청 |
| 404 | `NOT_FOUND` | 부재, 삭제, 형식 오류 |
| 503 | `SERVICE_UNAVAILABLE` | 이미지 저장소 미설정 |

<details>
<summary><b>presign 요청, 응답 예시</b></summary>

<br>

**1) Request body**

```json
{
  "kind": "COVER",
  "contentType": "image/webp",
  "contentLength": 204800
}
```

<br>

**2) 201 Response body**

```json
{
  "uploadUrl": "https://assets.example.com/thumbnails/uploaded/3f2504e0-4f89-41d3-9a0c-0305e82c3301/4c9e2b7a-1d3f-4a5b-8c6d-9e0f1a2b3c4d.webp?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Expires=600&X-Amz-Signature=...",
  "objectKey": "thumbnails/uploaded/3f2504e0-4f89-41d3-9a0c-0305e82c3301/4c9e2b7a-1d3f-4a5b-8c6d-9e0f1a2b3c4d.webp",
  "expiresInSeconds": 600
}
```

<br>

**3) 업로드 요청**

```text
PUT https://assets.example.com/thumbnails/uploaded/3f2504e0-.../4c9e2b7a-....webp?X-Amz-...
Content-Type: image/webp
Content-Length: 204800

<WebP 바이너리>
```

<br>

**4) 400 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "요청 값이 올바르지 않습니다.",
  "path": "/api/v1/stories/images/presign",
  "details": [
    {
      "field": "contentLength",
      "message": "5242880 이하여야 합니다."
    }
  ]
}
```

</details>

<br>

### 4-2-19 표지 삭제

| 항목 | 값 |
|---|---|
| 요청 | `DELETE /stories/{storyId}/thumbnail` |
| 인증 | 필수 |
| 성공 | 204, 본문 없음 |

표지를 삭제해 `null`로 변경한다. 표지가 없어도 성공한다.

**1. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 게스트 소유 스토리 |
| 403 | `FORBIDDEN` | 정지 계정, 소유자가 아닌 요청 |
| 404 | `NOT_FOUND` | 부재, 삭제, 형식 오류 |
| 409 | `CONFLICT` | 검수 중인 스토리 |

<details>
<summary><b>실패 응답 예시</b></summary>

<br>

**409 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 409,
  "code": "CONFLICT",
  "message": "검수 중인 스토리는 수정할 수 없습니다.",
  "path": "/api/v1/stories/3f2504e0-4f89-41d3-9a0c-0305e82c3301/thumbnail",
  "details": []
}
```

</details>

<br>

### 4-2-20 인물 이미지 삭제

| 항목 | 값 |
|---|---|
| 요청 | `DELETE /stories/{storyId}/characters/{characterId}/images/{imageId}` |
| 인증 | 필수 |
| 성공 | 204, 본문 없음 |

이미지가 없어도 성공한다.

**1. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 게스트 소유 스토리 |
| 403 | `FORBIDDEN` | 정지 계정, 소유자가 아닌 요청 |
| 404 | `NOT_FOUND` | 부재, 삭제, 형식 오류 |
| 409 | `CONFLICT` | 검수 중인 스토리 |

<details>
<summary><b>실패 응답 예시</b></summary>

<br>

**409 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 409,
  "code": "CONFLICT",
  "message": "검수 중인 스토리는 수정할 수 없습니다.",
  "path": "/api/v1/stories/3f2504e0-4f89-41d3-9a0c-0305e82c3301/characters/a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d/images/b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
  "details": []
}
```

</details>

<br>

### 4-2-21 좋아요

| 항목 | 값 |
|---|---|
| 요청 | `POST /stories/{storyId}/like` |
| 요청 | `DELETE /stories/{storyId}/like` |
| 인증 | 필수 |
| 성공 | 204, 본문 없음 |

요청 본문은 없다. 이미 등록한 좋아요를 다시 등록하거나 없는 좋아요를 취소해도 성공한다.

**1. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 403 | `FORBIDDEN` | 정지 계정 |
| 404 | `NOT_FOUND` | 부재, 삭제, 형식 오류, 읽을 수 없는 스토리 |

<details>
<summary><b>실패 응답 예시</b></summary>

<br>

**404 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 404,
  "code": "NOT_FOUND",
  "message": "스토리를 찾을 수 없습니다.",
  "path": "/api/v1/stories/00000000-0000-0000-0000-000000000000/like",
  "details": []
}
```

</details>

<br>

### 4-2-22 신고

| 항목 | 값 |
|---|---|
| 요청 | `POST /stories/{storyId}/reports` |
| 인증 | 필수 |
| 성공 | 201, 본문 없음 |

같은 회원의 재신고도 성공한다.

**1. 요청 본문**

| 필드명 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `reason` | `string` | 필수 | `SPAM`, `INAPPROPRIATE`, `ETC` |
| `detail` | `string` | 선택 | 500자 이하 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `reason`의 허용 범위를 벗어난 값, `detail` 길이 위반 |
| 403 | `FORBIDDEN` | 정지 계정 |
| 404 | `NOT_FOUND` | 부재, 삭제, 형식 오류, 읽을 수 없는 스토리 |

<details>
<summary><b>신고 요청 예시</b></summary>

<br>

```json
{
  "reason": "ETC",
  "detail": "다른 작품의 설정을 그대로 옮긴 것으로 보입니다."
}
```

<br>

**1) 400 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "요청 값이 올바르지 않습니다.",
  "path": "/api/v1/stories/3f2504e0-4f89-41d3-9a0c-0305e82c3301/reports",
  "details": [
    {
      "field": "detail",
      "message": "500자 이하여야 합니다."
    }
  ]
}
```

</details>

<br>

### 4-2-23 초안 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /users/me/story-drafts` |
| 인증 | 필수 |
| 성공 | 200 |

초안 카드와 진행 중인 생성 요청 카드를 합쳐 생성 시각 내림차순 배열로 반환한다. 페이지네이션이 없다.

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `[].kind` | `string` | `DRAFT` 또는 `CREATION_REQUEST` |
| `[].draftId` | `string` | `DRAFT`만, 초안 식별자 |
| `[].mode` | `string` | `DRAFT`만, `SIMPLE` 또는 `GENERAL` |
| `[].stage` | `string` | `DRAFT`는 `GENERAL_DRAFT`, `KEYWORD_DRAFT`, `STORY_DRAFT`<br>`CREATION_REQUEST`는 `STORYLINE_GENERATION` 또는 `STORY_COMPLETION` |
| `[].title` | `string / null` | `DRAFT`만, 목록용 요약 |
| `[].oneLineIntro` | `string / null` | `DRAFT`만, 목록용 요약 |
| `[].thumbnailUrl` | `string / null` | `DRAFT`만, 저장한 표지 키의 읽기 URL |
| `[].version` | `integer` | `DRAFT`만 |
| `[].requestId` | `string` | `CREATION_REQUEST`만, 생성 요청 식별자 |
| `[].createdAt` | `string` | |
| `[].updatedAt` | `string` | `DRAFT`만 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 403 | `FORBIDDEN` | 정지 계정 |

<details>
<summary><b>초안 목록 응답 예시</b></summary>

<br>

**1) 200 Response body**

```json
[
  {
    "kind": "CREATION_REQUEST",
    "requestId": "0b7c9d1e-3f4a-4b5c-8d6e-7f8091a2b3c4",
    "stage": "STORY_COMPLETION",
    "createdAt": "2026-06-10T12:05:00Z"
  },
  {
    "kind": "DRAFT",
    "draftId": "8f1c2d3e-4a5b-4c6d-9e7f-0a1b2c3d4e5f",
    "mode": "GENERAL",
    "stage": "GENERAL_DRAFT",
    "title": "{username}의 계약서",
    "oneLineIntro": "기억을 잃은 마법사가 금지된 숲에서 과거를 추적한다",
    "thumbnailUrl": "https://cdn.example.com/thumbnails/uploaded/drafts/7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d/4c9e2b7a-1d3f-4a5b-8c6d-9e0f1a2b3c4d.webp",
    "version": 3,
    "createdAt": "2026-06-10T11:00:00Z",
    "updatedAt": "2026-06-10T11:40:00Z"
  }
]
```

</details>

<br>

### 4-2-24 초안 상세

| 항목 | 값 |
|---|---|
| 요청 | `GET /users/me/story-drafts/{draftId}` |
| 인증 | 필수 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `draftId` | `string` | |
| `mode` | `string` | `SIMPLE` 또는 `GENERAL` |
| `stage` | `string` | `GENERAL_DRAFT`, `KEYWORD_DRAFT`, `STORY_DRAFT` |
| `title` | `string / null` | 목록용 요약 |
| `oneLineIntro` | `string / null` | 목록용 요약 |
| `thumbnailUrl` | `string / null` | 저장한 표지 키의 읽기 URL |
| `version` | `integer` | 1부터 시작 |
| `createdAt` | `string` | |
| `updatedAt` | `string` | |
| `schemaVersion` | `integer` | 클라이언트 payload 스키마 버전 |
| `payload` | `object` | 저장한 입력 그대로 |
| `generationRequestId` | `string / null` | 연결한 스토리라인 생성 요청 |
| `imageUrls` | `object` | payload 안의 임시 업로드 키를 키로, 읽기 URL을 값으로 하는 맵<br>없으면 빈 객체 |
| `generation` | `object / null` | `STORY_DRAFT`이고 생성 요청이 연결됐을 때 복구 조회와 같은 `stage`, `status`, `result`<br>그 외 `null` |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 403 | `FORBIDDEN` | 정지 계정 |
| 404 | `NOT_FOUND` | 없거나 타인의 초안, UUID 형식 오류 |

<details>
<summary><b>초안 상세 응답 예시</b></summary>

<br>

**1) 200 Response body**

`payload` 안쪽과 `generation.result`는 생략했다.

```json
{
  "draftId": "2c4e6a8b-1d3f-4a5b-9c7d-0e1f2a3b4c5d",
  "mode": "SIMPLE",
  "stage": "STORY_DRAFT",
  "title": null,
  "oneLineIntro": null,
  "thumbnailUrl": null,
  "version": 2,
  "createdAt": "2026-06-10T10:00:00Z",
  "updatedAt": "2026-06-10T10:20:00Z",
  "schemaVersion": 1,
  "payload": { "genreTagIds": [175, 48], "protagonist": { "name": "서린" } },
  "generationRequestId": "6d0f4a2e-1b7c-4e2a-9f11-2a4d1c9e8b10",
  "imageUrls": {},
  "generation": { "stage": "STORYLINE_GENERATION", "status": "COMPLETED", "result": { "simpleCreationId": 1207 } }
}
```

<br>

**2) 404 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 404,
  "code": "NOT_FOUND",
  "message": "초안을 찾을 수 없습니다.",
  "path": "/api/v1/users/me/story-drafts/00000000-0000-0000-0000-000000000000",
  "details": []
}
```

</details>

<br>

### 4-2-25 초안 저장

| 항목 | 값 |
|---|---|
| 요청 | `PUT /users/me/story-drafts/{draftId}` |
| 인증 | 필수 |
| 성공 | 200, 신규와 갱신 모두 |

전체 교체 방식이다. 같은 내용을 다시 보내면 버전과 시각이 바뀌지 않는다. `draftId`는 클라이언트가 만든 UUID다.

**1. 요청 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `mode` | `string` | 필수 | `GENERAL`은 `GENERAL_DRAFT`만, `SIMPLE`은 `KEYWORD_DRAFT`와 `STORY_DRAFT`만 허용 |
| `stage` | `string` | 필수 | 초안 단계 |
| `schemaVersion` | `integer` | 필수 | 클라이언트 payload 스키마 버전<br>서버는 해석하지 않음 |
| `payload` | `object` | 필수 | 작성 중 입력<br>JSON 객체만 허용<br>직렬화 크기 64KB 이하<br>안의 문자열 중 업로드 경로로 시작하는 값은 요청자의 임시 업로드 키 형식이어야 함 |
| `baseVersion` | `integer` | 선택 | 클라이언트가 기준으로 삼은 서버 버전<br>신규는 생략하거나 `null` |
| `title` | `string` | 선택 | 목록용 요약 |
| `oneLineIntro` | `string` | 선택 | 목록용 요약 |
| `thumbnailObjectKey` | `string` | 선택 | 목록용 표지의 임시 업로드 객체 키 |
| `generationRequestId` | `string` | 선택 | 요청자 소유의 스토리라인 생성 요청 ID |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `draftId` | `string` | |
| `version` | `integer` | 신규는 1<br>갱신은 이전 값 +1<br>같은 내용이면 유지 |
| `createdAt` | `string` | 갱신해도 유지 |
| `updatedAt` | `string` | 갱신 시각 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 방식과 단계 불일치, payload가 객체가 아님, 임시 업로드 키 형식 또는 소유 위반, 타인 또는 다른 단계의 생성 요청, 신규인데 `baseVersion`이 있음 |
| 400 | `DRAFT_PAYLOAD_TOO_LARGE` | payload 직렬화 크기 64KB 초과 |
| 400 | `DRAFT_LIMIT_EXCEEDED` | 6번째 신규 초안 |
| 403 | `FORBIDDEN` | 정지 계정 |
| 404 | `NOT_FOUND` | 타인의 초안 ID, UUID 형식 오류 |
| 409 | `DRAFT_VERSION_CONFLICT` | 내용이 다른데 `baseVersion`이 현재 버전과 다름<br>`details`에 `version`과 `updatedAt` |

<details>
<summary><b>초안 저장 요청, 응답 예시</b></summary>

<br>

**1) Request body**

```json
{
  "mode": "GENERAL",
  "stage": "GENERAL_DRAFT",
  "schemaVersion": 1,
  "baseVersion": 2,
  "title": "{username}의 계약서",
  "oneLineIntro": "기억을 잃은 마법사가 금지된 숲에서 과거를 추적한다",
  "thumbnailObjectKey": "thumbnails/uploaded/drafts/7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d/4c9e2b7a-1d3f-4a5b-8c6d-9e0f1a2b3c4d.webp",
  "payload": { "genres": ["판타지", "미스터리"], "storySettings": { "worldSetting": "# 세계관" } }
}
```

<br>

**2) 200 Response body**

```json
{
  "draftId": "8f1c2d3e-4a5b-4c6d-9e7f-0a1b2c3d4e5f",
  "version": 3,
  "createdAt": "2026-06-10T11:00:00Z",
  "updatedAt": "2026-06-10T11:40:00Z"
}
```

<br>

**3) 409 Response body**

```json
{
  "timestamp": "2026-06-10T12:00:00Z",
  "status": 409,
  "code": "DRAFT_VERSION_CONFLICT",
  "message": "초안이 다른 곳에서 변경되었습니다.",
  "path": "/api/v1/users/me/story-drafts/8f1c2d3e-4a5b-4c6d-9e7f-0a1b2c3d4e5f",
  "details": [
    {
      "field": "version",
      "message": "3"
    },
    {
      "field": "updatedAt",
      "message": "2026-06-10T11:40:00Z"
    }
  ]
}
```

</details>

<br>

### 4-2-26 초안 삭제

| 항목 | 값 |
|---|---|
| 요청 | `DELETE /users/me/story-drafts/{draftId}` |
| 인증 | 필수 |
| 성공 | 204, 본문 없음 |

요청 본문은 없다. 없거나 타인의 초안이어도 성공한다.

**1. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 403 | `FORBIDDEN` | 정지 계정 |

<br>

### 4-2-27 오리지널 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/originals` |
| 인증 | 관리자 |
| 성공 | 200<br>관리자 목록 공통의 페이지 구조 |

관리자 오리지널 API는 공식 계정이 소유한 스토리만 다룬다. 페이지, 정렬, 검색어 규칙은 관리자 목록 공통이다.

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `q` | `string` | 선택 | 제목 부분 일치<br>스토리 공개 식별자 정확 일치 |
| `status` | `string` | 선택 | `DRAFT`, `PUBLISHED` |
| `visibility` | `string` | 선택 | `PUBLIC`, `PRIVATE` |
| `sort` | `string` | 선택 | `updatedAt`, `chatCount`, `totalTurns`<br>기본 `updatedAt` |
| 페이지 쿼리 | | 선택 | 공통 페이지 쿼리 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items[].storyId` | `string` | 스토리 공개 식별자 |
| `items[].title` | `string` | 토큰 원문 |
| `items[].genres` | `string[]` | 장르 정식 이름 |
| `items[].status` | `string` | `DRAFT`, `PUBLISHED` |
| `items[].visibility` | `string` | `PUBLIC`, `PRIVATE` |
| `items[].owner` | `object` | 공식 계정의 `memberId`, `nickname` |
| `items[].chatCount` | `integer` | 삭제되지 않은 채팅 수 |
| `items[].totalTurns` | `integer` | 삭제되지 않은 채팅의 현재 턴 합 |
| `items[].thumbnailUrl` | `string / null` | 표지 |
| `items[].updatedAt` | `string` | 마지막 수정 시각 |

- 삭제된 스토리는 싣지 않는다. 공식 계정 설정이 비어 있으면 빈 페이지다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 검색어, enum, 공통 페이지 쿼리 오류 |

<br>

### 4-2-28 오리지널 상세

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/originals/{storyId}` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 응답**

오리지널 목록 항목에 수정 폼의 필드를 더한다. ([4-2-16 수정 폼](#4-2-16-수정-폼))

| 필드명 | 타입 | 의미 |
|---|---|---|
| `title`, `oneLineIntro`, `description`, `protagonistName`, `genres`, `storySettings`, `startSettings`, `mainEvents`, `characters`, `thumbnailUrl`, `thumbnailModerationStatus` | 수정 폼과 같음 | 현재 저장값<br>미승인 제출본은 없음 |

- 수정 폼의 `submission`은 없다. 오리지널은 검수를 거치지 않는다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `storyId`가 UUID 형식이 아님 |
| 404 | `NOT_FOUND` | 없거나 삭제된 스토리<br>공식 계정 소유가 아닌 스토리 |

<br>

### 4-2-29 오리지널 등록

| 항목 | 값 |
|---|---|
| 요청 | `POST /admin/originals` |
| 인증 | 관리자 |
| 성공 | 201<br>오리지널 상세 |

**1. 요청 본문**

일반 제작 등록의 필드를 그대로 쓴다. ([4-2-15 일반 제작 등록](#4-2-15-일반-제작-등록)) 다른 점은 다음과 같다.

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `status` | `string` | 선택 | `DRAFT` 또는 `PUBLISHED`<br>기본 `DRAFT` |
| `visibility` | `string` | 선택 | 기본 `PRIVATE`<br>`PUBLIC`은 `PUBLISHED`와 함께만 |
| `reason` | `string` | 필수 | 사유<br>1~500자 |
| `draftId` | | | 없음<br>보내면 400 |
| `thumbnailObjectKey`, `characters[].images[].objectKey` | `string` | 선택 | 오리지널 presign으로 올린 객체 키 |

- `DRAFT`는 `title`만 필수이고 나머지 필드는 선택이다. 시작 설정이 없으면 빈 배열로 저장한다.
- `PUBLISHED`는 일반 제작 등록과 같은 검증을 모두 통과해야 한다.
- 소유자는 공식 계정이다. 검수 접수 없이 바로 저장하고 감사 로그 `ORIGINAL_CREATED`를 남긴다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 일반 제작 등록과 같은 검증 실패<br>`DRAFT`에 `PUBLIC`<br>`draftId` 포함<br>`reason` 누락 |
| 400 | `INVALID_GENRE` | 허용되지 않는 장르 |
| 400 | `UPLOAD_NOT_FOUND` | 객체 키에 아직 파일이 없음 |
| 409 | `CONFLICT` | 같은 인물 안의 이미지 이름 중복 |
| 503 | `SERVICE_UNAVAILABLE` | 공식 계정 설정이 비어 있거나 그 회원이 없음 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request body**

일반 제작 등록 예시의 필드에 다음을 더한다.

```json
{
  "status": "PUBLISHED",
  "visibility": "PUBLIC",
  "reason": "11월 오리지널 1편 공개"
}
```

**2) 201 Response body**

오리지널 상세와 같다.

</details>

<br>

### 4-2-30 오리지널 수정

| 항목 | 값 |
|---|---|
| 요청 | `PATCH /admin/originals/{storyId}` |
| 인증 | 관리자 |
| 성공 | 200<br>오리지널 상세 |

**1. 요청 본문**

스토리 수정의 필드와 규칙을 그대로 쓴다. ([4-2-17 스토리 수정](#4-2-17-스토리-수정)) 다른 점은 다음과 같다.

| 필드명 | 규칙 |
|---|---|
| `status` | `DRAFT`에서 `PUBLISHED`로만 바꿀 수 있음<br>`PUBLISHED`로 바꿀 때 기존 값에 요청을 반영한 전체 결과가 등록 검증을 통과해야 함 |
| `visibility` | 다른 필드와 함께 보내도 즉시 반영<br>`DRAFT`인 스토리에 `PUBLIC`은 거절 |
| `reason` | 필수 |
| 모든 변경 | 검수 접수 없이 바로 반영<br>발행 상태이고 공개면 공개 스냅샷 갱신 |

- 시드로 등록한 기존 오리지널도 같은 경로로 수정한다.
- 감사 로그 `ORIGINAL_UPDATED`를 남긴다. 변경 전후 값은 `status`, `visibility`, `title`, `genres`다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 스토리 수정과 같은 검증 실패<br>`PUBLISHED`에서 `DRAFT`로 변경<br>`DRAFT`에 `PUBLIC`<br>`reason` 누락 |
| 400 | `INVALID_GENRE` | 허용되지 않는 장르 |
| 400 | `UPLOAD_NOT_FOUND` | 객체 키에 아직 파일이 없음 |
| 404 | `NOT_FOUND` | 없거나 삭제된 스토리<br>공식 계정 소유가 아닌 스토리 |
| 409 | `CONFLICT` | 같은 인물 안의 이미지 이름 중복 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) 공개로 전환하는 Request body**

```json
{ "status": "PUBLISHED", "visibility": "PUBLIC", "reason": "검토 완료" }
```

**2) 비공개로 바꾸는 Request body**

```json
{ "visibility": "PRIVATE", "reason": "오탈자 수정 중" }
```

</details>

<br>

### 4-2-31 오리지널 표지 삭제

| 항목 | 값 |
|---|---|
| 요청 | `DELETE /admin/originals/{storyId}/thumbnail` |
| 인증 | 관리자 |
| 성공 | 200<br>오리지널 상세 |

**1. 본문**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `reason` | `string` | 필수 | 사유<br>1~500자 |

- 표지가 이미 없어도 성공이다. 감사 로그 `ORIGINAL_THUMBNAIL_DELETED`를 남긴다. 인물 이미지 삭제는 수정의 `characters[].images` 전체 교체로 한다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `reason` 누락<br>`storyId`가 UUID 형식이 아님 |
| 404 | `NOT_FOUND` | 없거나 삭제된 스토리<br>공식 계정 소유가 아닌 스토리 |

<br>

### 4-2-32 오리지널 이미지 presign

| 항목 | 값 |
|---|---|
| 요청 | `POST /admin/originals/images/presign` |
| 요청 | `POST /admin/originals/{storyId}/images/presign` |
| 인증 | 관리자 |
| 성공 | 201 |

요청 본문과 응답은 이미지 presign과 같다. ([4-2-18 이미지 presign](#4-2-18-이미지-presign)) 다른 점은 다음과 같다.

| 항목 | 규칙 |
|---|---|
| 객체 키 | 등록 전은 공식 계정의 임시 업로드 접두어<br>등록 뒤는 그 스토리의 접두어 |
| 소유 판정 | 공식 계정 소유 스토리만<br>아니면 없는 것으로 응답 |
| 감사 기록 | 없음<br>업로드 자체는 스토리를 바꾸지 않음 |

<br>

**실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 지원하지 않는 형식, 5,242,880 바이트 초과 |
| 404 | `NOT_FOUND` | 없거나 삭제된 스토리<br>공식 계정 소유가 아닌 스토리 |
| 503 | `SERVICE_UNAVAILABLE` | 이미지 저장소 미설정<br>공식 계정 설정이 비어 있음 |

<br>

### 4-2-33 다른 도메인과의 경계

| 상대 | STORY가 주는 것 | STORY가 받는 것 |
|---|---|---|
| CHAT | 읽기 판정과 현재 표시 판정 | 미삭제 채팅의 `current_turn` 합계 |
| CHAT | 공개 스냅샷과 턴 생성에 필요한 데이터 캡처, 기본 주인공 이름, 토큰 치환 | 엔딩 도달 집계 행 |
| CHAT | 시작 설정, 엔딩, 주요 사건 조회 |  |
| MODERATION | 제출본 접수, 승인 시 등록 저장과 수정 적용 진입점 | 판정 결과와 승인 시 호출 |
| MODERATION | 이미지 객체 검증 | `PENDING` 제출본 존재 여부 |
| MODERATION | 검수 입력의 토큰 원문과 `protagonist_name`, 인물 소개 |  |
| MODERATION | 공개 중단 적용, 공개 중단 표시 조회, 승인 시 공개 중단 해제 | 관리자 공개 중단 요청 |
| PAYMENT | 차감과 환불 요청(`ref_type` `STORY`), 게스트 카운터 예약과 복원 요청 | 잔액 부족과 한도 소진 예외 |
| PAYMENT |  | 정책값 `story_creation_cost` |
| NOTIFICATION | 완성 이벤트(회원, 요청 ID, 스토리 공개 ID, 제목), 캠페인 이동 대상 스토리의 공개 판정 | 없음 |
| ADMIN | 공식 계정 식별, 스토리와 제작 세션 조회 | 관리자 요청자, 관리자 판정 필터, 변경 감사 기록 |
| ACCOUNT | 회원의 내 스토리 목록 조회 메서드, 닉네임 변경 시 재색인 대상 스토리, 탈퇴 시 초안 삭제 메서드 | 소유자 프로필, 게스트 이관 시 `user_id`로 소유권 확보와 이관된 스토리의 색인 요청 이벤트 |
| ACCOUNT |  | 동의 게이트 허용 목록 |
| 검색 | 색인 요청 이벤트(스토리 ID) | 검색 결과 카드 |

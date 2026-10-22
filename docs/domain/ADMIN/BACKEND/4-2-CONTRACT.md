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
| 식별자 | 회원, 감사 로그, 주문, 스토리, 채팅방은 UUID 공개 식별자<br>내부 PK는 노출하지 않음 |
| 채팅 대화 원문 | 어떤 관리자 응답에도 사용자 메시지, AI 응답, 추천 입력을 싣지 않음 |
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
| `X-Manyak-Request-Id` | 1~64자의 영문, 숫자, 하이픈, 밑줄 | 로그 연결과 감사 로그의 요청 ID<br>없거나 조건에 어긋나면 서버가 생성하고 응답 헤더로 항상 반환 | 선택 |

<br>

**4. 관리자 토큰**

| 항목 | 값 |
|---|---|
| 형식 | HS256 JWT<br>앱 접근 토큰과 같은 대칭키 |
| 클레임 | 발급자 `manyak`, 주체는 회원 공개 식별자, 대상 `manyak-admin`, 발급 시각, 만료 |
| 수명 | 2시간<br>갱신 없음 |
| 구분 | 대상 클레임이 `manyak-admin`을 포함하면 관리자 토큰<br>앱 경로는 대상 클레임이 있는 토큰을 회원으로 식별하지 않음 |

<br>

**5. 앱 경로의 관리자 토큰**

| 앱 경로의 인증 수준 | 관리자 토큰 |
|---|---|
| 토큰을 읽지 않는 경로 | 읽지 않으므로 처리 |
| 선택 인증 경로 | 유효하지 않은 토큰과 같이 익명으로 처리<br>회원으로 식별하지 않음 |
| 인증 필수 경로 | 인증 실패로 거절 |

<br>

**6. 공통 실패 응답**

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

**7. 공통 응답 구조**

회원 목록 항목, 스토리와 채팅방의 소유자, 주문과 이프 거래의 회원, 감사 로그의 처리자는 같은 회원 요약 구조를 쓴다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `memberId` | `string` | 회원 공개 식별자 |
| `nickname` | `string` | 탈퇴 계정은 익명화된 이름 |
| `status` | `string` | `ACTIVE`, `SUSPENDED`, `DELETED` |
| `isAdmin` | `boolean` | 관리자 역할 보유 여부 |
| `createdAt` | `string` | 가입 시각 |

관리자 목록은 모두 같은 페이지 쿼리와 페이지 구조를 쓴다. 다른 도메인의 관리자 목록도 같다.

| 쿼리 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `page` | `integer` | 선택 | 1부터 시작하는 페이지 번호<br>기본 1<br>전체 페이지 수를 넘으면 빈 `items` |
| `size` | `integer` | 선택 | 페이지 크기<br>1~100<br>기본 20 |
| `sort` | `string` | 선택 | 정렬 열<br>허용 값과 기본값은 각 절 |
| `order` | `string` | 선택 | `asc` 또는 `desc`<br>기본 `desc` |

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items` | `object[]` | 현재 페이지의 항목 |
| `page` | `integer` | 요청한 페이지 번호 |
| `size` | `integer` | 요청한 페이지 크기 |
| `totalElements` | `integer` | 필터를 적용한 전체 건수 |
| `totalPages` | `integer` | 전체 페이지 수<br>건수가 0이면 0 |

- 정렬 열의 값이 같은 항목은 그 항목의 공개 식별자 오름차순으로 순서를 고정한다. `null`은 방향과 무관하게 마지막이다.
- `page`와 `size`가 정수가 아니거나 범위 밖이면 400이다. 허용하지 않는 `sort`와 `order` 값도 400이다. `cursor`와 `limit`는 받지 않으며 보내면 400이다.

목록의 검색어와 날짜 필터는 다음 규칙을 공유한다. 검색어, 필터, 정렬은 모두 AND로 적용한다.

| 쿼리 | 규칙 |
|---|---|
| `q` | 1~50자<br>앞뒤 공백을 지우고 연속 공백을 하나로 줄인 뒤 대소문자를 무시해 비교<br>부분 일치 대상과 정확 일치 대상은 각 절<br>정규화 뒤 빈 값은 400 |
| 날짜 | `YYYY-MM-DD` 형식의 KST 달력 날짜<br>`from`과 `to`는 양 끝 포함이고 한쪽만 지정 가능<br>`from`이 `to`보다 뒤이거나 형식이 틀리면 400 |
| 필터 enum | 허용 값 밖은 400 |

목록 항목의 스토리 요약은 다음 구조다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `storyId` | `string` | 스토리 공개 식별자 |
| `title` | `string` | 제목<br>이름 토큰 원문 |
| `genre` | `string` | 장르 정식 이름을 `, `로 이은 문자열 |

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

<br>

- 관리자 페이지는 이프 지급 카드를 `direction=granted`, 이프 소진 카드를 `direction=spent`의 이프 거래 내역으로 잇는다. ([4-2-13 이프 거래 내역](#4-2-13-이프-거래-내역))

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
  "members": { "total": 1240, "joinedToday": 12 },
  "chats": { "startedTotal": 8210, "startedToday": 64, "turnsTotal": 96320, "turnsToday": 710 },
  "stories": { "total": 1530, "createdToday": 9 },
  "credits": { "grantedTotal": 2480000, "grantedToday": 6250, "spentTotal": 1902400, "spentToday": 14200 },
  "payments": { "completedTotal": 41, "completedToday": 1, "amountKrwTotal": 312800, "amountKrwToday": 4800 }
}
```

</details>

<br>

### 4-2-4 대시보드 차트

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/dashboard/charts` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to` | `string` | 선택 | KST 날짜 `YYYY-MM-DD`, 양 끝 포함<br>둘 다 주거나 둘 다 생략<br>`to`는 오늘 이하, 기간은 1일 이상 366일 이하 |
| `days` | `integer` | 선택 | `7`, `30`, `90` 중 하나<br>오늘을 포함한 최근 N일<br>`from`, `to`와 함께 보내면 400 |

- 셋 다 없으면 오늘을 포함한 최근 30일이다.

<br>

**2. 응답**

지표 정의와 팀 계정 제외 규칙은 제품 제약에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약))

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string` | 집계 기준 시각 |
| `from` | `string` | 범위 첫날의 KST 날짜 |
| `to` | `string` | 범위 마지막 날의 KST 날짜 |
| `daily` | `object[]` | 날짜 오름차순<br>범위의 모든 날짜가 한 항목씩 있고 없는 날은 0 |
| `daily[].date` | `string` | KST 날짜 |
| `daily[].joined` | `integer` | 가입 |
| `daily[].chats` | `integer` | 채팅 시작 |
| `daily[].turns` | `integer` | 턴 |
| `daily[].stories` | `integer` | 스토리 생성 |
| `daily[].granted` | `integer` | 이프 지급 |
| `daily[].spent` | `integer` | 이프 소진 |
| `daily[].payments` | `integer` | 결제 건수 |
| `daily[].revenue` | `integer` | 결제 금액 |
| `daily[].attendance` | `integer` | 출석 회원 수 |
| `distributions` | `object[]` | 분포 차트<br>아래 표의 순서로 항상 8개 |
| `distributions[].chartId` | `string` | 차트 식별자 |
| `distributions[].title` | `string` | 제목 |
| `distributions[].description` | `string` | 집계 기준 설명<br>첫 사용자 메시지까지 시간은 제외한 채팅방 수 포함 |
| `distributions[].unit` | `string` | 값의 단위 |
| `distributions[].points` | `object[]` | 막대 하나가 한 항목 |
| `distributions[].points[].label` | `string` | 막대 이름 |
| `distributions[].points[].value` | `number` | 값<br>비율은 0~100의 백분율 |
| `distributions[].points[].link` | `object` | 막대를 눌렀을 때 열 목록 |
| `distributions[].points[].link.list` | `string` | `stories`, `chats`, `members`, `credit-transactions` |
| `distributions[].points[].link.params` | `object` | 그 목록의 쿼리 이름과 값<br>값은 모두 문자열 |

| `chartId` | `label` | `unit` | `link` |
|---|---|---|---|
| `genre-depth` | 범위 안에 생성된 채팅이 있는 장르 정식 이름 | `턴` | `stories`<br>`genre`, `chatFrom`, `chatTo` |
| `turns` | `0`, `1`, `2`, `3~4`, `5~6`, `7~9`, `10~14`, `15~19`, `20~29`, `30~49`, `50+` | `개` | `chats`<br>`turnBucket`(0부터 10), `from`, `to` |
| `started-as` | `게스트`, `회원` | `%` | `chats`<br>`startedAs`, `from`, `to` |
| `member-chats` | `1개`, `2개`, `3~4개`, `5~9개`, `10개+` | `명` | `members`<br>`chatBucket`(0부터 4), `chatFrom`, `chatTo` |
| `first-message` | `평균`, `P50`, `P75`, `P90` | `초` | `chats`<br>`hasFirstMessage=true`, `from`, `to` |
| `ai-latency` | `chat_response`, `choice_generation`, `storyline_generation`, `story_completion` | `초` | 채팅 기능은 `chats`, 제작 기능은 `stories`<br>`aiFeature`, `aiStatus=SUCCEEDED`, `hasLatency=true`, `aiFrom`, `aiTo` |
| `ai-success` | 같음 | `%` | 같은 목록<br>`aiFeature`, `aiStatus=FINISHED`, `aiFrom`, `aiTo` |
| `characters` | `0명`부터 `5명`<br>사용자가 직접 입력한 주변 인물 수 | `세션` | `stories`<br>`supportingCharacterCount`, `creationFrom`, `creationTo` |

일별 추이의 한 날짜를 눌렀을 때 여는 목록은 관리자 페이지가 다음 쿼리로 만든다.

| `daily` 필드 | 목록 | 쿼리 |
|---|---|---|
| `joined` | `members` | `from`과 `to`에 그 날짜 |
| `chats` | `chats` | `from`과 `to`에 그 날짜 |
| `turns` | `chats` | `turnDate` |
| `stories` | `stories` | `from`과 `to`에 그 날짜 |
| `granted`, `spent` | `credit-transactions` | `direction`에 `granted` 또는 `spent`, `date` |
| `payments`, `revenue` | `payments` | `from`과 `to`에 그 날짜 |
| `attendance` | `members` | `attendanceDate` |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 허용하지 않는 `days`, `days`와 `from` 또는 `to` 동시 지정, 한쪽만 있는 `from` 또는 `to`, 날짜 형식 오류, `from`이 `to`보다 뒤, `to`가 오늘 이후, 366일 초과 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/dashboard/charts?from=2026-10-15&to=2026-10-21
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

`daily`는 두 날, `distributions`는 한 차트만 보였다.

```json
{
  "asOf": "2026-10-21T05:12:00Z",
  "from": "2026-10-15",
  "to": "2026-10-21",
  "daily": [
    { "date": "2026-10-15", "joined": 9, "chats": 58, "turns": 640, "stories": 7, "granted": 5250, "spent": 12800, "payments": 1, "revenue": 4800, "attendance": 21 },
    { "date": "2026-10-16", "joined": 11, "chats": 61, "turns": 702, "stories": 5, "granted": 6000, "spent": 14040, "payments": 0, "revenue": 0, "attendance": 24 }
  ],
  "distributions": [
    {
      "chartId": "turns",
      "title": "턴 수 분포",
      "description": "채팅 시작일 기준, 구간별 채팅방 수",
      "unit": "개",
      "points": [
        { "label": "0", "value": 41, "link": { "list": "chats", "params": { "turnBucket": "0", "from": "2026-10-15", "to": "2026-10-21" } } },
        { "label": "1", "value": 37, "link": { "list": "chats", "params": { "turnBucket": "1", "from": "2026-10-15", "to": "2026-10-21" } } }
      ]
    }
  ]
}
```

</details>

<br>

### 4-2-5 스토리 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/stories` |
| 인증 | 관리자 |
| 성공 | 200<br>페이지 구조 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `q` | `string` | 선택 | 제목과 소유 회원 닉네임 부분 일치<br>스토리 공개 식별자 정확 일치 |
| `scope` | `string` | 선택 | `original`은 공식 계정 소유<br>`user`는 그 외 회원과 게스트 소유 |
| `genre` | `string` | 선택 | 장르 정식 이름 하나<br>스토리 장르 문자열에 포함된 스토리 |
| `visibility` | `string` | 선택 | `PUBLIC`, `PRIVATE` |
| `moderationStatus` | `string` | 선택 | `HELD`는 보류 중인 제출본이 있는 스토리<br>`APPROVED`는 그 외 |
| `memberId` | `string` | 선택 | 소유 회원 공개 식별자 |
| `supportingCharacterCount` | `integer` | 선택 | 0~5<br>제작 세션에서 사용자가 직접 입력한 주변 인물 수<br>이름, 성별, 특징 태그가 모두 빈 자리는 세지 않음<br>제작 세션이 없는 스토리는 어떤 값에도 해당하지 않음 |
| `from`, `to` | `string` | 선택 | 스토리 생성일 |
| `chatFrom`, `chatTo` | `string` | 선택 | 채팅 생성일<br>지정하면 `chatCount`와 `totalTurns`를 그 기간의 채팅으로만 세고 기간에 채팅이 없는 스토리는 제외 |
| `creationFrom`, `creationTo` | `string` | 선택 | 제작 세션 생성일 |
| `aiFrom`, `aiTo` | `string` | 선택 | AI 호출 기록 생성일 |
| `aiFeature` | `string` | 선택 | `storyline_generation`, `story_completion` |
| `aiStatus` | `string` | 선택 | `SUCCEEDED`, `FAILED`, `STARTED`<br>`FINISHED`는 성공과 실패 |
| `hasLatency` | `boolean` | 선택 | 지연 값이 있는 호출만 |
| `sort` | `string` | 선택 | `createdAt`, `chatCount`, `totalTurns`<br>기본 `createdAt` |
| 페이지 쿼리 | | 선택 | 공통 페이지 쿼리 |

- `ai`로 시작하는 쿼리 중 하나라도 있으면 조건에 맞는 AI 호출 기록이 연결된 스토리만 남긴다.

<br>

**2. 응답**

항목은 스토리 요약 구조에 다음 필드를 더한다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items[].description` | `string / null` | 주요 내용 |
| `items[].scope` | `string` | `original`, `user` |
| `items[].visibility` | `string` | `PUBLIC`, `PRIVATE` |
| `items[].moderationStatus` | `string` | `HELD`, `APPROVED` |
| `items[].tags` | `string[]` | 제작 세션에서 선택한 태그 이름<br>장르, 주인공, 주변 인물 특징 순<br>제작 세션이 없으면 빈 배열 |
| `items[].supportingCharacterCount` | `integer / null` | 제작 세션에서 사용자가 직접 입력한 주변 인물 수<br>제작 세션이 없으면 `null` |
| `items[].owner` | `object / null` | 소유 회원의 회원 요약 구조<br>게스트 소유는 `null` |
| `items[].chatCount` | `integer` | 삭제되지 않은 채팅 수 |
| `items[].totalTurns` | `integer` | 삭제되지 않은 채팅의 현재 턴 합 |
| `items[].createdAt` | `string` | 생성 시각 |

- 삭제된 스토리는 싣지 않는다. 팀 계정 제외는 적용하지 않는다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 검색어, 날짜, enum, 공통 페이지 쿼리 오류<br>`memberId`가 UUID 형식이 아님 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/stories?genre=판타지&chatFrom=2026-10-15&chatTo=2026-10-21&sort=totalTurns&size=1
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "items": [
    {
      "storyId": "7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d",
      "title": "{username}의 계약서",
      "genre": "판타지, 미스터리",
      "description": "계약 마법이 지배하는 왕국에서 잃어버린 기억을 추적한다.",
      "scope": "user",
      "visibility": "PUBLIC",
      "moderationStatus": "APPROVED",
      "tags": ["판타지", "기억을 잃은", "과묵한 조력자"],
      "supportingCharacterCount": 1,
      "owner": { "memberId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301", "nickname": "차분한 등대", "status": "ACTIVE", "isAdmin": false, "createdAt": "2026-07-01T09:00:00Z" },
      "chatCount": 42,
      "totalTurns": 388,
      "createdAt": "2026-09-30T12:00:00Z"
    }
  ],
  "page": 1,
  "size": 1,
  "totalElements": 17,
  "totalPages": 17
}
```

</details>

<br>

### 4-2-6 스토리 상세

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/stories/{storyId}` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 경로**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `storyId` | 경로 | 필수 | 스토리 공개 식별자 |

<br>

**2. 응답**

스토리 목록 항목에 다음 필드를 더한다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `retention` | `object[]` | 턴 유지율<br>`turn`이 1, 3, 5, 10, 20인 항목 5개 |
| `retention[].turn` | `integer` | 기준 턴 |
| `retention[].rate` | `number` | 삭제되지 않은 채팅 중 현재 턴이 기준 턴 이상인 비율<br>0~1<br>채팅이 없으면 0 |
| `recentChats` | `object[]` | 최근 생성된 채팅방 5개<br>채팅방 목록 항목 구조 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `storyId`가 UUID 형식이 아님 |
| 404 | `NOT_FOUND` | 없거나 삭제된 스토리 |

<br>

### 4-2-7 채팅방 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/chats` |
| 인증 | 관리자 |
| 성공 | 200<br>페이지 구조 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `q` | `string` | 선택 | 스토리 제목과 회원 닉네임 부분 일치<br>채팅방 공개 식별자 정확 일치 |
| `storyId` | `string` | 선택 | 스토리 공개 식별자 |
| `memberId` | `string` | 선택 | 소유 회원 공개 식별자 |
| `startedAs` | `string` | 선택 | `GUEST`, `MEMBER` |
| `turnBucket` | `integer` | 선택 | 0~10<br>턴 수 분포 차트의 구간 순서 |
| `hasFirstMessage` | `boolean` | 선택 | `true`는 생성 뒤 900초 안에 첫 사용자 메시지가 있는 채팅방<br>`false`는 그 외 |
| `turnDate` | `string` | 선택 | 그 KST 날짜에 AI 응답 메시지가 생성된 채팅방 |
| `from`, `to` | `string` | 선택 | 채팅방 생성일 |
| `aiFrom`, `aiTo` | `string` | 선택 | AI 호출 기록 생성일 |
| `aiFeature` | `string` | 선택 | `chat_response`, `choice_generation` |
| `aiStatus` | `string` | 선택 | 스토리 목록과 같음 |
| `hasLatency` | `boolean` | 선택 | 스토리 목록과 같음 |
| `sort` | `string` | 선택 | `startedAt`, `lastActiveAt`, `turnCount`, `creditsSpent`<br>기본 `startedAt` |
| 페이지 쿼리 | | 선택 | 공통 페이지 쿼리 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items[].chatId` | `string` | 채팅방 공개 식별자 |
| `items[].story` | `object` | 스토리 요약 구조 |
| `items[].member` | `object / null` | 소유 회원의 회원 요약 구조<br>게스트는 `null` |
| `items[].startedAs` | `string` | 소유 회원이 없으면 `GUEST`, 있으면 `MEMBER`<br>게스트에서 이관된 채팅방은 `MEMBER` |
| `items[].turnCount` | `integer` | 현재 턴 |
| `items[].startedAt` | `string` | 생성 시각 |
| `items[].lastActiveAt` | `string` | 마지막 갱신 시각 |
| `items[].creditsSpent` | `integer` | 이 채팅방을 참조하는 원장 소모 행 합계의 절댓값<br>턴과 이미지 |
| `items[].firstMessageSeconds` | `integer / null` | 생성부터 첫 사용자 메시지까지 초<br>사용자 메시지가 없으면 `null` |

- 삭제된 채팅방은 싣지 않는다. 메시지 원문은 어떤 필드에도 없다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 검색어, 날짜, enum, 공통 페이지 쿼리 오류<br>`storyId` 또는 `memberId`가 UUID 형식이 아님 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/chats?turnBucket=3&from=2026-10-15&to=2026-10-21&size=1
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "items": [
    {
      "chatId": "c4d5e6f7-a8b9-4c0d-9e1f-2a3b4c5d6e7f",
      "story": { "storyId": "7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d", "title": "{username}의 계약서", "genre": "판타지, 미스터리" },
      "member": null,
      "startedAs": "GUEST",
      "turnCount": 4,
      "startedAt": "2026-10-20T13:02:11Z",
      "lastActiveAt": "2026-10-20T13:31:40Z",
      "creditsSpent": 0,
      "firstMessageSeconds": 42
    }
  ],
  "page": 1,
  "size": 1,
  "totalElements": 96,
  "totalPages": 96
}
```

</details>

<br>

### 4-2-8 채팅방 상세

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/chats/{chatId}` |
| 인증 | 관리자 |
| 성공 | 200<br>채팅방 목록 항목 구조 |

**1. 경로**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `chatId` | 경로 | 필수 | 채팅방 공개 식별자 |

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `chatId`가 UUID 형식이 아님 |
| 404 | `NOT_FOUND` | 없거나 삭제된 채팅방 |

<br>

### 4-2-9 회원 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/members` |
| 인증 | 관리자 |
| 성공 | 200<br>페이지 구조 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `q` | `string` | 선택 | 닉네임 부분 일치<br>회원 공개 식별자와 활성 소셜 연동 이메일 정확 일치<br>이메일은 소문자로 바꿔 비교 |
| `status` | `string` | 선택 | `ACTIVE`, `SUSPENDED`, `DELETED` |
| `excludeDeleted` | `boolean` | 선택 | `true`면 탈퇴 회원 제외 |
| `from`, `to` | `string` | 선택 | 가입일 |
| `chatBucket` | `integer` | 선택 | 0~4<br>회원별 채팅방 생성 횟수 차트의 구간 순서<br>채팅방이 없는 회원은 어떤 값에도 해당하지 않음 |
| `chatFrom`, `chatTo` | `string` | 선택 | 채팅방 생성일<br>지정하면 `chatBucket` 판정과 `periodChatCount`를 그 기간으로 세고 기간에 채팅방이 없는 회원은 제외 |
| `creditDirection` | `string` | 선택 | `granted`, `spent`<br>그 방향의 원장 행이 있는 회원 |
| `creditDate` | `string` | 선택 | 원장 기록일<br>`creditDirection`과 함께만 |
| `attendanceDate` | `string` | 선택 | 그 KST 날짜에 출석 보상을 받은 회원 |
| `sort` | `string` | 선택 | `createdAt`, `lastActiveAt`, `creditsSpent`, `paidKrw`, `chatCount`<br>기본 `createdAt` |
| 페이지 쿼리 | | 선택 | 공통 페이지 쿼리 |

<br>

**2. 응답**

항목은 회원 요약 구조에 다음 필드를 더한다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items[].lastActiveAt` | `string / null` | 삭제되지 않은 채팅방의 마지막 갱신, 원장 기록, 스토리 생성 중 가장 최근 시각<br>없으면 `null` |
| `items[].creditsSpent` | `integer` | 소모 사유 원장 행 합계의 절댓값 |
| `items[].paidKrw` | `integer` | 완료 상태 주문의 금액 합<br>환불된 주문 제외 |
| `items[].chatCount` | `integer` | 삭제되지 않은 채팅방 수 |
| `items[].periodChatCount` | `integer / null` | `chatFrom` 또는 `chatTo`를 지정했을 때 그 기간의 채팅방 수<br>지정하지 않으면 `null` |

- `q`가 있으면 접속 기록으로 감사 로그에 남는다. 이메일은 검색에만 쓰고 응답에는 없다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 검색어, 날짜, enum, 공통 페이지 쿼리 오류<br>`creditDate`만 지정 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/members?q=등대&sort=creditsSpent&size=1
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "items": [
    {
      "memberId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
      "nickname": "차분한 등대",
      "status": "ACTIVE",
      "isAdmin": false,
      "createdAt": "2026-07-01T09:00:00Z",
      "lastActiveAt": "2026-10-21T04:58:12Z",
      "creditsSpent": 18640,
      "paidKrw": 9600,
      "chatCount": 17,
      "periodChatCount": null
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

### 4-2-10 회원 상세

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

회원 목록 항목에 다음 필드를 더한다. `periodChatCount`는 항상 `null`이다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `creditBalance` | `integer` | 만료되지 않은 이프 잔액 |
| `storyCount` | `integer` | 삭제되지 않은 소유 스토리 수 |
| `deletedAt` | `string / null` | 탈퇴 시각 |

- 상세 조회는 접속 기록으로 감사 로그에 남는다.
- 이 회원의 결제, 채팅방, 스토리는 각 목록을 `memberId`로 조회한다. 이프 거래와 출석은 다음 두 절이다.

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
  "lastActiveAt": "2026-10-21T04:58:12Z",
  "creditsSpent": 18640,
  "paidKrw": 9600,
  "chatCount": 17,
  "periodChatCount": null,
  "creditBalance": 1230,
  "storyCount": 4,
  "deletedAt": null
}
```

</details>

<br>

### 4-2-11 회원 이프 거래 내역

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/members/{memberId}/transactions` |
| 인증 | 관리자 |
| 성공 | 200<br>페이지 구조 |

**1. 경로와 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `memberId` | 경로 | 필수 | 회원 공개 식별자 |
| `sort` | `string` | 선택 | `createdAt`만 허용<br>기본 `createdAt` |
| 페이지 쿼리 | | 선택 | 공통 페이지 쿼리 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items[].amount` | `integer` | 부호 있는 수량 |
| `items[].reason` | `string` | 원장 사유 |
| `items[].balanceAfter` | `integer` | 이 행까지의 원장 누계 |
| `items[].createdAt` | `string` | 기록 시각 |

- 원장 행에는 공개 식별자가 없어 항목에 식별자가 없다. 같은 시각의 행은 내부 기록 순서를 유지한다.
- 조회는 회원 상세와 같은 접속 기록을 남긴다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `memberId`가 UUID 형식이 아님<br>공통 페이지 쿼리 오류 |
| 404 | `NOT_FOUND` | 없는 회원 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/members/3f2504e0-4f89-41d3-9a0c-0305e82c3301/transactions?size=2
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "items": [
    { "amount": -20, "reason": "CHAT_TURN", "balanceAfter": 1230, "createdAt": "2026-10-21T04:58:12Z" },
    { "amount": 250, "reason": "ATTENDANCE_REWARD", "balanceAfter": 1250, "createdAt": "2026-10-20T15:00:03Z" }
  ],
  "page": 1,
  "size": 2,
  "totalElements": 318,
  "totalPages": 159
}
```

</details>

<br>

### 4-2-12 회원 출석 기록

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/members/{memberId}/attendance` |
| 인증 | 관리자 |
| 성공 | 200<br>페이지 구조 |

**1. 경로와 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `memberId` | 경로 | 필수 | 회원 공개 식별자 |
| `sort` | `string` | 선택 | `date`만 허용<br>기본 `date` |
| 페이지 쿼리 | | 선택 | 공통 페이지 쿼리 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items[].date` | `string` | 출석 보상을 받은 KST 날짜 |
| `items[].creditAmount` | `integer` | 받은 이프 |

- 조회는 회원 상세와 같은 접속 기록을 남긴다.

<br>

**3. 실패 응답**

회원 이프 거래 내역과 같다.

<br>

### 4-2-13 이프 거래 내역

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/credits/transactions` |
| 인증 | 관리자 |
| 성공 | 200<br>페이지 구조 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `direction` | `string` | 선택 | `granted`는 지급 사유의 양수 행, `spent`는 소모 사유의 음수 행<br>정의는 대시보드의 이프 지급과 소진과 같음<br>생략하면 모든 원장 행 |
| `date` | `string` | 선택 | 원장 기록일 |
| `sort` | `string` | 선택 | `createdAt`만 허용<br>기본 `createdAt` |
| 페이지 쿼리 | | 선택 | 공통 페이지 쿼리 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items[].amount` | `integer` | 부호 있는 수량 |
| `items[].reason` | `string` | 원장 사유 |
| `items[].createdAt` | `string` | 기록 시각 |
| `items[].member` | `object` | 회원 요약 구조 |

- 원장 행에는 공개 식별자가 없어 항목에 식별자가 없다. 같은 시각의 행은 내부 기록 순서의 역순이다.
- 회원별 누계와 회원 필터는 없다. 한 회원의 거래는 회원 거래 내역에서 본다. ([4-2-11 회원 이프 거래 내역](#4-2-11-회원-이프-거래-내역))
- 팀 계정 제외를 적용하지 않으므로 대시보드 카드와 추이의 지급·소진 값과 이 목록의 합계는 팀 계정의 행만큼 다를 수 있다.
- 접속 기록을 남기지 않는다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `direction` 허용 값 밖, 날짜 형식 오류, 공통 페이지 쿼리 오류 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/credits/transactions?direction=spent&date=2026-10-21&size=2
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "items": [
    { "amount": -20, "reason": "CHAT_TURN", "createdAt": "2026-10-21T04:58:12Z", "member": { "memberId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301", "nickname": "차분한 등대", "status": "ACTIVE", "isAdmin": false, "createdAt": "2026-07-01T09:00:00Z" } },
    { "amount": -250, "reason": "STORY_CREATION", "createdAt": "2026-10-21T04:40:02Z", "member": { "memberId": "9a8b7c6d-5e4f-4a3b-9c2d-1e0f9a8b7c6d", "nickname": "고요한 서고", "status": "ACTIVE", "isAdmin": true, "createdAt": "2026-07-01T09:00:00Z" } }
  ],
  "page": 1,
  "size": 2,
  "totalElements": 713,
  "totalPages": 357
}
```

</details>

<br>

### 4-2-14 결제 내역

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/payments/orders` |
| 인증 | 관리자 |
| 성공 | 200<br>페이지 구조 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `q` | `string` | 선택 | 회원 닉네임 부분 일치<br>주문과 회원 공개 식별자 정확 일치 |
| `status` | `string` | 선택 | `COMPLETED`, `REFUNDED` |
| `memberId` | `string` | 선택 | 주문 회원 공개 식별자 |
| `from`, `to` | `string` | 선택 | 완료일 |
| `sort` | `string` | 선택 | `completedAt`, `refundedAt`, `priceKrw`, `creditAmount`<br>기본 `completedAt` |
| 페이지 쿼리 | | 선택 | 공통 페이지 쿼리 |

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
| 400 | `BAD_REQUEST` | 검색어, 날짜, enum, 공통 페이지 쿼리 오류<br>`memberId`가 UUID 형식이 아님 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/payments/orders?status=COMPLETED&from=2026-10-01&to=2026-10-21&size=1
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
  "page": 1,
  "size": 1,
  "totalElements": 12,
  "totalPages": 12
}
```

</details>

<br>

### 4-2-15 결제 상세

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/payments/orders/{orderId}` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 경로**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `orderId` | 경로 | 필수 | 주문 공개 식별자 |

<br>

**2. 응답**

결제 내역 항목에 다음 필드를 더한다. 전후 비교의 기준은 그 회원의 첫 완료 주문 완료 시각이다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `firstPaidAt` | `string` | 회원의 첫 완료 주문 완료 시각 |
| `before` | `object` | 기준 시각 전 |
| `before.turns` | `integer` | 채팅 턴 소모 원장 행 수 |
| `before.stories` | `integer` | 간편 제작 소모 원장 행 수 |
| `before.creditsSpent` | `integer` | 소모 사유 합계의 절댓값에서 환불 합계를 뺀 값 |
| `after` | `object` | 기준 시각 이후<br>`before`와 같은 세 필드 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `orderId`가 UUID 형식이 아님 |
| 404 | `NOT_FOUND` | 없는 주문<br>완료 시각이 없는 대기 주문 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/payments/orders/7c9e6679-7425-40de-944b-e07fc1f90ae7
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "orderId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "member": { "memberId": "3f2504e0-4f89-41d3-9a0c-0305e82c3301", "nickname": "차분한 등대", "status": "ACTIVE", "isAdmin": false, "createdAt": "2026-07-01T09:00:00Z" },
  "productId": "if_5000",
  "status": "COMPLETED",
  "priceKrw": 4800,
  "creditAmount": 5000,
  "completedAt": "2026-10-21T01:22:03Z",
  "refundedAt": null,
  "reversalShortfall": null,
  "firstPaidAt": "2026-09-01T03:00:00Z",
  "before": { "turns": 112, "stories": 2, "creditsSpent": 2740 },
  "after": { "turns": 795, "stories": 5, "creditsSpent": 17150 }
}
```

</details>

<br>

### 4-2-16 감사 로그 조회

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
| `q` | `string` | 선택 | 처리자 닉네임, 작업 이름, 사유 부분 일치<br>감사 로그 공개 식별자와 대상 식별자 정확 일치 |
| `from`, `to` | `string` | 선택 | 기록일 |
| `category` | `string` | 선택 | `CHANGE`, `ACCESS` |
| `sort` | `string` | 선택 | `createdAt`, `category`, `action`, `targetType`, `admin`<br>`admin`은 처리자 닉네임<br>기본 `createdAt` |
| 페이지 쿼리 | | 선택 | 공통 페이지 쿼리 |

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
| 400 | `BAD_REQUEST` | `adminId`가 UUID 형식이 아님, `targetId`만 지정, 검색어, 날짜, enum, 공통 페이지 쿼리 오류 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/audit-logs?action=CREDIT_GRANTED&size=1
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
  "page": 1,
  "size": 1,
  "totalElements": 1,
  "totalPages": 1
}
```

</details>

<br>

### 4-2-17 분석 지표

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/dashboard/analytics` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to` | `string` | 선택 | KST 날짜 `YYYY-MM-DD`, 양 끝 포함<br>둘 다 주거나 둘 다 생략<br>`to`는 오늘 이하, 기간은 1일 이상 366일 이하 |
| `days` | `integer` | 선택 | `7`, `30`, `90` 중 하나<br>오늘을 포함한 최근 N일<br>`from`, `to`와 함께 보내면 400 |

- 셋 다 없으면 오늘을 포함한 최근 30일이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string` | 서버가 분석 도구에서 이 범위의 값을 받은 시각<br>캐시된 응답은 캐시한 시각이며 갱신 중이나 쿨다운 중에는 10분보다 오래될 수 있음 |
| `from` | `string` | 범위 첫날의 KST 날짜 |
| `to` | `string` | 범위 마지막 날의 KST 날짜 |
| `todayActiveUsers` | `integer` | 오늘 활성 사용자 수<br>범위와 무관하게 오늘 값 |
| `daily` | `object[]` | 날짜 오름차순 |
| `daily[].date` | `string` | KST 날짜 |
| `daily[].activeUsers` | `integer` | 그 날 이벤트가 있는 고유 사용자 수 |
| `daily[].newUsers` | `integer` | 그 날 처음 이벤트가 있었던 고유 사용자 수 |

- 값은 분석 도구가 집계한 것이며 팀 계정 코호트에 속한 사용자를 제외한다. 집계가 몇 분 늦을 수 있다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 허용하지 않는 `days`, `days`와 `from` 또는 `to` 동시 지정, 한쪽만 있는 `from` 또는 `to`, 날짜 형식 오류, `from`이 `to`보다 뒤, `to`가 오늘 이후, 366일 초과 |
| 503 | `SERVICE_UNAVAILABLE` | 분석 도구 자격 증명 미설정<br>호출 실패, 호출 한도 초과, 실패 뒤 쿨다운, 다른 요청이 갱신 중인데 캐시도 없음 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/dashboard/analytics?from=2026-10-15&to=2026-10-21
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

`daily`는 두 날만 보였다.

```json
{
  "asOf": "2026-10-21T05:10:00Z",
  "from": "2026-10-15",
  "to": "2026-10-21",
  "todayActiveUsers": 318,
  "daily": [
    { "date": "2026-10-15", "activeUsers": 402, "newUsers": 31 },
    { "date": "2026-10-16", "activeUsers": 377, "newUsers": 27 }
  ]
}
```

**3) 503 Response body**

```json
{
  "timestamp": "2026-10-21T05:10:00.000Z",
  "status": 503,
  "code": "SERVICE_UNAVAILABLE",
  "message": "분석 지표를 가져올 수 없습니다.",
  "path": "/api/v1/admin/dashboard/analytics",
  "details": []
}
```

</details>

<br>

### 4-2-18 설치 지표

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/dashboard/play-installs` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string` | 보고서 마지막 행의 날짜 `YYYY-MM-DD`<br>Play 기준 날짜라 KST로 바꾸지 않음 |
| `totalInstalls` | `integer` | 보고서 전체 기간의 일별 기기 설치 수 합 |
| `activeDevices` | `integer` | 마지막 행의 활성 기기 설치 수 |
| `daily` | `object[]` | 보고서 첫 날짜부터 마지막 날짜까지 모든 날이 한 항목씩<br>날짜 오름차순<br>보고서에 행이 없는 날도 채움 |
| `daily[].date` | `string` | Play 기준 날짜 |
| `daily[].installs` | `integer` | 그 날 기기 설치 수<br>행이 없는 날은 0 |
| `daily[].uninstalls` | `integer` | 그 날 기기 삭제 수<br>행이 없는 날은 0 |
| `daily[].cumulativeInstalls` | `integer` | 첫 날부터 그 날까지의 기기 설치 누계<br>행이 없는 날은 전날 값<br>마지막 항목은 `totalInstalls`와 같음 |
| `daily[].activeDevices` | `integer / null` | 그 날의 활성 기기 설치 수<br>행이 없는 날은 `null` |

- 값은 Play Console 일괄 보고서가 집계한 것이며 보고서는 며칠 늦게 채워진다. 보고서가 2026년 9월부터라 행 수가 작아 기간 쿼리는 없다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 503 | `SERVICE_UNAVAILABLE` | 서비스 계정 키 미설정<br>보고서 저장소 호출 실패, 보고서 없음, 해석 실패, 실패 뒤 쿨다운, 다른 요청이 갱신 중인데 캐시도 없음 |

<details>
<summary><b>요청·응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/dashboard/play-installs
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

`daily`는 두 날만 보였다.

```json
{
  "asOf": "2026-10-17",
  "totalInstalls": 31,
  "activeDevices": 11,
  "daily": [
    { "date": "2026-10-16", "installs": 1, "uninstalls": 0, "cumulativeInstalls": 29, "activeDevices": 10 },
    { "date": "2026-10-17", "installs": 2, "uninstalls": 1, "cumulativeInstalls": 31, "activeDevices": 11 }
  ]
}
```

</details>

<br>

### 4-2-19 다른 도메인과의 경계

| 도메인 | ADMIN이 제공하는 것 | ADMIN이 사용하는 것 |
|---|---|---|
| ACCOUNT | 관리자 요청자 식별과 감사 기록 연산 | 신원 검증기, 회원 조회와 검색, 활성 소셜 연동 이메일 일치 조회, 계정 상태, 회원 수 집계 |
| PAYMENT | 관리자 요청자 식별과 감사 기록 연산 | 잔액, 주문 조회, 원장 조회, 지급과 소진 집계 |
| NOTIFICATION, NOTICE | 관리자 요청자 식별과 감사 기록 연산 | 없음 |
| MODERATION | 관리자 요청자 식별과 감사 기록 연산 | 스토리별 보류 제출본 존재 여부 |
| STORY | 관리자 요청자 식별과 감사 기록 연산 | 스토리 수, 스토리와 제작 세션 조회, 공식 계정 식별 |
| CHAT | 없음 | 채팅 시작 수, 턴 수, 채팅방 조회, AI 호출 기록 조회 |
| Amplitude | 없음 | Dashboard REST API의 활성·신규 사용자 수 조회 |
| Google Cloud Storage | 없음 | Play Console 일괄 보고서 객체 목록과 내려받기 |
| 모든 도메인 | 관리자 판정 필터와 앱 토큰 검증 보강 | 인증 필터와 상관관계 필터 |

다른 도메인이 호출하는 연산의 입력과 결과는 다음과 같다.

| 연산 | 입력 | 결과 |
|---|---|---|
| 관리자 요청자 | 현재 요청 | 관리자의 회원 내부 ID<br>필터가 확정한 값 |
| 변경 감사 기록 | 관리자, 작업 이름, 대상 종류, 대상 식별자, 사유, 변경 전 값, 변경 후 값 | 감사 로그 행<br>호출자의 트랜잭션에 참여하고 트랜잭션이 없으면 거부 |
| 접속 기록 | 관리자, 작업 이름, 대상 종류, 대상 식별자 | 감사 로그 행<br>독립 트랜잭션 |

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
| 시각 | ISO 8601 UTC 문자열<br>날짜 필드는 `YYYY-MM-DD`이며 기준 시간대는 각 절에 적음 |
| 식별자 | 회원, 감사 로그, 주문, 스토리, 채팅은 UUID 공개 식별자<br>내부 PK는 노출하지 않음 |
| 채팅 대화 원문 | 어떤 관리자 응답에도 채팅의 사용자 메시지, AI 응답, 추천 입력을 싣지 않음<br>시작 설정의 추천 입력은 제작 입력이라 스토리 설정 응답에만 실음 |
| 호출 주체 | 관리자 페이지의 서버 측 처리기<br>브라우저가 직접 호출하지 않으므로 관리자 페이지 주소는 CORS 허용 목록에 없음 |
| 사유 | 변경 작업의 요청 본문에 `reason` 필수<br>스토리 공개 중단은 `reason` 대신 사유 분류 `reasonCode`가 필수이고 `ETC`면 입력 사유 `reasonDetail`도 필수이며 메모 `memo`는 선택 ([MODERATION 4-2-10 공개 중단](../../MODERATION/BACKEND/4-2-CONTRACT.md#4-2-10-공개-중단)) |
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

회원 목록 항목, 스토리와 채팅의 소유자, 주문과 이프 내역의 회원, 감사 로그의 처리자는 같은 회원 요약 구조를 쓴다.

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
<summary><b>요청과 응답 예시</b></summary>

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
| `members.total` | `integer` | 누적 가입자 수<br>탈퇴 회원을 포함한 전체 회원 수 |
| `members.active` | `integer` | 현재 회원 수<br>탈퇴하지 않은 회원 수이며 정지 회원 포함 |
| `members.withdrawn` | `integer` | 누적 탈퇴 수<br>`status`가 `DELETED`인 회원 수 |
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
| `credits.grantedTotal` | `integer` | 누적 적립 |
| `credits.grantedToday` | `integer` | 오늘 적립 |
| `credits.spentTotal` | `integer` | 누적 소모 |
| `credits.spentToday` | `integer` | 오늘 소모 |
| `payments` | `object` | 결제 |
| `payments.completedTotal` | `integer` | 결제 건수 누적 |
| `payments.completedToday` | `integer` | 오늘 결제 건수 |
| `payments.amountKrwTotal` | `integer` | 결제 금액 누적 |
| `payments.amountKrwToday` | `integer` | 오늘 결제 금액 |

<br>

- `members.total`은 `members.active`와 `members.withdrawn`의 합이다. 세 값 모두 팀 계정 제외 목록을 뺀다.
- 관리자 페이지는 가입자 카드를 탈퇴 회원을 포함한 회원 목록(`excludeDeleted` 없음)에 잇는다. 회원 목록은 팀 계정을 제외하지 않아 건수가 카드와 다를 수 있다.
- 관리자 페이지는 이프 적립 카드는 `direction=granted`로, 이프 소모 카드는 `direction=spent`로 이프 내역에 잇는다. ([4-2-14 이프 내역](#4-2-14-이프-내역))

<br>

**2. 실패 응답**

공통 실패만 있다.

<details>
<summary><b>요청과 응답 예시</b></summary>

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
  "members": { "total": 1300, "active": 1240, "withdrawn": 60, "joinedToday": 12 },
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
| `daily[].granted` | `integer` | 이프 적립 |
| `daily[].spent` | `integer` | 이프 소모 |
| `daily[].payments` | `integer` | 결제 건수 |
| `daily[].revenue` | `integer` | 결제 금액 |
| `daily[].attendance` | `integer` | 출석 회원 수 |
| `totals` | `object` | 범위의 기간 합계<br>`joined`, `chats`, `turns`, `stories`, `granted`, `spent`, `payments`, `revenue`의 8개 정수 필드<br>`attendance`는 없음 |
| `previous` | `object` | 직전 기간 |
| `previous.from` | `string` | 직전 기간 첫날의 KST 날짜<br>`from`에서 범위 길이만큼 앞선 날 |
| `previous.to` | `string` | 직전 기간 마지막 날의 KST 날짜<br>`from`의 전날 |
| `previous.totals` | `object` | 직전 기간의 합계<br>`totals`와 같은 8개 필드 |
| `distributions` | `object[]` | 분포 차트<br>아래 표의 순서로 항상 9개 |
| `distributions[].chartId` | `string` | 차트 식별자 |
| `distributions[].category` | `string` | 분석 화면의 구역<br>`users`, `engagement`, `content`, `ai-quality` |
| `distributions[].title` | `string` | 제목 |
| `distributions[].description` | `string` | 집계 기준 설명<br>`started-as`는 채팅 수로 나눈 비율이고 가입 뒤 이관된 게스트 채팅은 회원이며 게스트 사용자 수는 AI 호출을 보낸 기기 수라는 것 포함<br>첫 사용자 입력까지 걸린 시간은 제외한 채팅 수 포함 |
| `distributions[].unit` | `string` | 값의 단위 |
| `distributions[].points` | `object[]` | 막대 하나가 한 항목 |
| `distributions[].points[].label` | `string` | 막대 이름 |
| `distributions[].points[].value` | `number` | 값<br>비율은 0~100의 백분율 |
| `distributions[].points[].chats` | `integer` | `genre-depth`, `started-as`에만 있음<br>그 장르나 그 소유자 유형의 채팅 수 |
| `distributions[].points[].users` | `integer` | `started-as`에만 있음<br>그 소유자 유형 채팅의 사용자 수<br>게스트는 AI 호출을 보낸 기기 수 |
| `distributions[].points[].totalTurns` | `integer` | `genre-depth`에만 있음<br>그 장르 채팅의 현재 턴 합<br>`value`는 `totalTurns`를 `chats`로 나눈 값 |
| `distributions[].points[].link` | `object` | 막대를 눌렀을 때 열 목록 |
| `distributions[].points[].link.list` | `string` | `stories`, `chats`, `members`, `credit-transactions` |
| `distributions[].points[].link.params` | `object` | 그 목록의 쿼리 이름과 값<br>값은 모두 문자열 |

| `chartId` | `category` | `label` | `unit` | `link` |
|---|---|---|---|---|
| `genre-depth` | `engagement` | 범위 안에 생성된 채팅이 있는 장르 정식 이름<br>`value` 내림차순, 같으면 이름 순<br>채팅 수와 무관하게 모든 장르 | `턴` | `stories`<br>`genre`, `chatFrom`, `chatTo` |
| `turns` | `engagement` | `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7~9`, `10~14`, `15~19`, `20~29`, `30~49`, `50+` | `개` | `chats`<br>`turnBucket`(0부터 12), `from`, `to` |
| `started-as` | `users` | `게스트`, `회원` | `%` | `chats`<br>`startedAs`, `from`, `to` |
| `member-chats` | `users` | `1개`, `2개`, `3~4개`, `5~9개`, `10개+` | `명` | `members`<br>`chatBucket`(0부터 4), `chatFrom`, `chatTo` |
| `first-message` | `engagement` | `평균`, `P50`, `P75`, `P90` | `초` | `chats`<br>`hasFirstMessage=true`, `from`, `to` |
| `ai-latency` | `ai-quality` | `chat_response`, `choice_generation`, `chat_image`, `storyline_generation`, `story_completion`, `chat_compact` | `초` | 채팅 기능은 `chats`, 제작 기능은 `stories`<br>`aiFeature`, `aiStatus=SUCCEEDED`, `hasLatency=true`, `aiFrom`, `aiTo` |
| `ai-success` | `ai-quality` | 같음 | `%` | 같은 목록<br>`aiFeature`, `aiStatus=FINISHED`, `aiFrom`, `aiTo` |
| `creation-mode` | `content` | `일반 제작`, `간편 제작` | `개` | `stories`<br>`creationMode`(`GENERAL`, `SIMPLE`), `from`, `to` |
| `characters` | `content` | `0명`부터 `5명`<br>간편 제작별 직접 입력한 주변 인물 수 | `건` | `stories`<br>`supportingCharacterCount`, `creationFrom`, `creationTo` |

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
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/dashboard/charts?from=2026-10-15&to=2026-10-21
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

예시에는 `daily`의 날짜 항목 2개와 `distributions`의 차트 1개만 표시했다.

```json
{
  "asOf": "2026-10-21T05:12:00Z",
  "from": "2026-10-15",
  "to": "2026-10-21",
  "daily": [
    { "date": "2026-10-15", "joined": 9, "chats": 58, "turns": 640, "stories": 7, "granted": 5250, "spent": 12800, "payments": 1, "revenue": 4800, "attendance": 21 },
    { "date": "2026-10-16", "joined": 11, "chats": 61, "turns": 702, "stories": 5, "granted": 6000, "spent": 14040, "payments": 0, "revenue": 0, "attendance": 24 }
  ],
  "totals": { "joined": 71, "chats": 418, "turns": 4790, "stories": 39, "granted": 41250, "spent": 96300, "payments": 4, "revenue": 19200 },
  "previous": {
    "from": "2026-10-08",
    "to": "2026-10-14",
    "totals": { "joined": 58, "chats": 377, "turns": 4120, "stories": 44, "granted": 38500, "spent": 88700, "payments": 2, "revenue": 9600 }
  },
  "distributions": [
    {
      "chartId": "turns",
      "category": "engagement",
      "title": "턴 수 분포",
      "description": "채팅 생성일을 기준으로 구간별 채팅 수 집계",
      "unit": "개",
      "points": [
        { "label": "0", "value": 41, "link": { "list": "chats", "params": { "turnBucket": "0", "from": "2026-10-15", "to": "2026-10-21" } } },
        { "label": "1", "value": 37, "link": { "list": "chats", "params": { "turnBucket": "1", "from": "2026-10-15", "to": "2026-10-21" } } },
        { "label": "2", "value": 28, "link": { "list": "chats", "params": { "turnBucket": "2", "from": "2026-10-15", "to": "2026-10-21" } } },
        { "label": "3", "value": 22, "link": { "list": "chats", "params": { "turnBucket": "3", "from": "2026-10-15", "to": "2026-10-21" } } },
        { "label": "4", "value": 19, "link": { "list": "chats", "params": { "turnBucket": "4", "from": "2026-10-15", "to": "2026-10-21" } } },
        { "label": "5", "value": 17, "link": { "list": "chats", "params": { "turnBucket": "5", "from": "2026-10-15", "to": "2026-10-21" } } },
        { "label": "6", "value": 15, "link": { "list": "chats", "params": { "turnBucket": "6", "from": "2026-10-15", "to": "2026-10-21" } } },
        { "label": "7~9", "value": 24, "link": { "list": "chats", "params": { "turnBucket": "7", "from": "2026-10-15", "to": "2026-10-21" } } },
        { "label": "10~14", "value": 18, "link": { "list": "chats", "params": { "turnBucket": "8", "from": "2026-10-15", "to": "2026-10-21" } } },
        { "label": "15~19", "value": 9, "link": { "list": "chats", "params": { "turnBucket": "9", "from": "2026-10-15", "to": "2026-10-21" } } },
        { "label": "20~29", "value": 7, "link": { "list": "chats", "params": { "turnBucket": "10", "from": "2026-10-15", "to": "2026-10-21" } } },
        { "label": "30~49", "value": 4, "link": { "list": "chats", "params": { "turnBucket": "11", "from": "2026-10-15", "to": "2026-10-21" } } },
        { "label": "50+", "value": 2, "link": { "list": "chats", "params": { "turnBucket": "12", "from": "2026-10-15", "to": "2026-10-21" } } }
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
| `deleted` | `string` | 선택 | 삭제된 스토리의 포함 여부<br>없으면 삭제된 스토리 제외<br>`include`는 삭제된 스토리도 포함<br>`only`는 삭제된 스토리만 |
| `memberId` | `string` | 선택 | 소유 회원 공개 식별자 |
| `creationMode` | `string` | 선택 | 제작 방식<br>`SIMPLE`은 스토리를 완성한 제작 세션이 있는 간편 제작 스토리<br>`GENERAL`은 그 밖의 일반 제작 스토리 |
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
| `items[].chatCount` | `integer` | 삭제되지 않은 채팅 수<br>스토리가 삭제돼도 같음 |
| `items[].totalTurns` | `integer` | 삭제되지 않은 채팅의 현재 턴 수 합계 |
| `items[].createdAt` | `string` | 생성 시각 |
| `items[].deletedAt` | `string / null` | 삭제 시각<br>삭제되지 않았으면 `null` |
| `items[].takenDownAt` | `string / null` | 관리자의 공개 중단 시각<br>공개 중단 표시가 없으면 `null` |
| `items[].takedownReason` | `string / null` | 공개 중단 사유 분류<br>`SEXUAL_CONTENT`, `COPYRIGHT_INFRINGEMENT`, `HATE_SPEECH`, `ETC`<br>공개 중단 표시가 없으면 `null` |
| `items[].takedownReasonDetail` | `string / null` | 사유 분류가 `ETC`일 때 관리자가 입력해 소유자에게 보인 사유<br>그 밖에는 `null` |

- 삭제된 스토리는 `deleted`에 따라 싣는다. 팀 계정 제외는 적용하지 않는다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 검색어, 날짜, enum, 공통 페이지 쿼리 오류<br>`memberId`가 UUID 형식이 아님 |

<details>
<summary><b>요청과 응답 예시</b></summary>

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
      "createdAt": "2026-09-30T12:00:00Z",
      "deletedAt": null,
      "takenDownAt": null,
      "takedownReason": null,
      "takedownReasonDetail": null
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
| `retention` | `object[]` | 기준 턴 도달률<br>`turn`이 1, 2, 3, 4, 5, 6, 7, 10, 15, 20, 30, 50인 항목 12개, 오름차순 |
| `retention[].turn` | `integer` | 기준 턴 |
| `retention[].rate` | `number` | 삭제되지 않은 채팅 중 현재 턴이 기준 턴 이상인 비율<br>0~1<br>채팅이 없으면 0 |
| `recentChats` | `object[]` | 삭제되지 않은 채팅 중 최근 생성된 5개<br>채팅 목록 항목 구조 |

- 삭제된 스토리도 응답한다. `retention`과 `recentChats`는 삭제되지 않은 스토리와 같은 정의다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `storyId`가 UUID 형식이 아님 |
| 404 | `NOT_FOUND` | 없는 스토리 |

<br>

### 4-2-7 스토리 설정

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/stories/{storyId}/settings` |
| 인증 | 관리자 |
| 성공 | 200 |

제작자가 저장한 설정을 읽기 전용으로 돌려준다. 대상은 모든 스토리이며 초안 여부, 공개 범위, 보류 여부, 소유자(회원, 게스트, 공식 계정), 삭제 여부를 가리지 않는다. 값은 현재 저장값이고 승인 전 제출본의 내용은 반영하지 않는다. 텍스트 필드는 이름 토큰을 치환하지 않은 원문이다. 표지와 인물 이미지에는 공개 노출의 검수 게이트를 적용하지 않고 검수 상태와 무관하게 전부 싣는다.

**1. 경로**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `storyId` | 경로 | 필수 | 스토리 공개 식별자 |

<br>

**2. 응답**

STORY 세트 수정 폼의 현재 저장값에서 `submission`과 `characters[].images[].objectKey`를 빼고 `deletedAt`을 더한 구조다. ([STORY 4-2-16 수정 폼](../../STORY/BACKEND/4-2-CONTRACT.md#4-2-16-수정-폼))

| 필드명 | 타입 | 의미 |
|---|---|---|
| `title` | `string` | 제목 |
| `oneLineIntro` | `string / null` | 한 줄 소개 |
| `description` | `string / null` | 주요 내용 |
| `protagonistName` | `string / null` | 기본 주인공 이름<br>기존 스토리는 `null` |
| `genres` | `string[]` | 장르 정식 이름<br>저장 순서 |
| `storySettings` | `object` | 스토리 설정 통글 4필드<br>저장 행이 없으면 네 필드 모두 `null` |
| `storySettings.worldSetting` | `string / null` | 세계관 |
| `storySettings.characterSetting` | `string / null` | 등장인물 |
| `storySettings.userRoleSetting` | `string / null` | 이름을 제외한 주인공 설명 |
| `storySettings.ruleSetting` | `string / null` | 전개 규칙 |
| `startSettings` | `object[]` | 시작 설정<br>등록 순서, 없으면 빈 배열 |
| `startSettings[].id` | `string` | 시작 설정 공개 식별자 |
| `startSettings[].name` | `string` | 상황 이름 |
| `startSettings[].prologue` | `string / null` | 프롤로그 |
| `startSettings[].startSituation` | `string / null` | 시작 상황 |
| `startSettings[].suggestedInputs` | `string[]` | 추천 입력<br>입력 순서, 없으면 빈 배열 |
| `startSettings[].endings` | `object[]` | 활성 엔딩만, 표시 순서<br>없으면 빈 배열 |
| `startSettings[].endings[].name` | `string` | 엔딩 이름 |
| `startSettings[].endings[].requirement` | `object` | 엔딩 조건 |
| `startSettings[].endings[].requirement.minTurns` | `integer` | 최소 턴 수 |
| `startSettings[].endings[].requirement.achievementCondition` | `string` | 달성 조건 |
| `startSettings[].endings[].epilogue` | `string` | 엔딩 에필로그 |
| `mainEvents` | `object[]` | 주요 사건<br>`sortOrder` 오름차순, 없으면 빈 배열 |
| `mainEvents[].name` | `string` | 사건 이름 |
| `mainEvents[].description` | `string` | 사건 설명 |
| `mainEvents[].keySentence` | `string` | 키 문장 |
| `mainEvents[].sortOrder` | `integer` | 표시 순서<br>0부터 |
| `visibility` | `string` | `PUBLIC`, `PRIVATE` |
| `thumbnailUrl` | `string / null` | 현재 표지<br>업로드 또는 생성 URL, 없으면 프리셋 키의 URL, 둘 다 없으면 `null`<br>검수 상태와 무관 |
| `thumbnailModerationStatus` | `string` | 표지 검수 상태<br>`APPROVED`, `PENDING`, `REJECTED` |
| `characters` | `object[]` | 인물<br>저장 순서, 없으면 빈 배열 |
| `characters[].id` | `string` | 인물 공개 식별자<br>현재 저장값만 응답하므로 `null` 없음 |
| `characters[].name` | `string` | 인물 이름 |
| `characters[].description` | `string / null` | 인물 소개 |
| `characters[].images` | `object[]` | 그 인물의 이미지 전부<br>표시 순서, 검수 상태와 무관, 없으면 빈 배열 |
| `characters[].images[].id` | `string` | 이미지 공개 식별자<br>현재 저장값만 응답하므로 `null` 없음 |
| `characters[].images[].imageName` | `string` | 인물 이미지 이름 |
| `characters[].images[].imageUrl` | `string` | 이미지 제공 URL |
| `characters[].images[].moderationStatus` | `string` | 이미지 검수 상태<br>`APPROVED`, `PENDING`, `REJECTED` |
| `deletedAt` | `string / null` | 스토리 삭제 시각<br>삭제되지 않았으면 `null` |

- 검수 경과는 MODERATION 세트의 관리자 제출본 상세에서 본다. ([MODERATION 4-2-9 관리자 제출본 상세](../../MODERATION/BACKEND/4-2-CONTRACT.md#4-2-9-관리자-제출본-상세))
- 화풍은 스토리에 저장되지 않아 응답에 없다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `storyId`가 UUID 형식이 아님 |
| 404 | `NOT_FOUND` | 없는 스토리 |

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/stories/7a1d3c5e-9b2f-4e6a-8c0d-1f2e3a4b5c6d/settings
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

회원이 소유한 비공개 스토리이며 인물 이미지 한 장의 검수 상태가 `PENDING`이다.

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
      "id": "5b6c7d8e-9f0a-4b1c-8d2e-3f4a5b6c7d8e",
      "name": "선왕의 장례식 날",
      "prologue": "잿빛 비가 사흘째 왕성을 적신다.",
      "startSituation": "장례식이 끝난 늦은 밤, 기사단 숙소.",
      "suggestedInputs": ["편지를 열어본다", "창밖의 인기척을 확인한다", "여관 주인을 찾아간다"],
      "endings": [
        {
          "name": "왕좌를 되찾다",
          "requirement": { "minTurns": 10, "achievementCondition": "주인공이 반란군을 규합해 왕좌를 되찾는다." },
          "epilogue": "주인공이 왕좌에 오르는 대관식을 장엄하게 묘사한다."
        }
      ]
    }
  ],
  "mainEvents": [
    { "name": "잃어버린 편지를 발견한다", "description": "주인공이 다락방에서 어머니가 남긴 봉인된 편지를 찾아낸다.", "keySentence": "봉인된 편지를 열어 어머니의 비밀을 마주한다.", "sortOrder": 0 }
  ],
  "visibility": "PRIVATE",
  "thumbnailUrl": "https://cdn.example.com/thumbnails/uploaded/3f2504e0-4f89-41d3-9a0c-0305e82c3301/4c9e2b7a-1d3f-4a5b-8c6d-9e0f1a2b3c4d.webp",
  "thumbnailModerationStatus": "APPROVED",
  "characters": [
    {
      "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
      "name": "도윤",
      "description": "기록을 지키는 과묵한 사서.",
      "images": [
        { "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e", "imageName": "도윤_기본", "imageUrl": "https://cdn.example.com/characters/uploaded/3f2504e0-4f89-41d3-9a0c-0305e82c3301/5d0f3c8b-2e4a-4b6c-9d7e-0f1a2b3c4d5e.webp", "moderationStatus": "APPROVED" },
        { "id": "c3d4e5f6-a7b8-4c9d-8e1f-2a3b4c5d6e7f", "imageName": "도윤_놀람", "imageUrl": "https://cdn.example.com/characters/uploaded/3f2504e0-4f89-41d3-9a0c-0305e82c3301/6e1a4d9c-3f5b-4c7d-8e9f-1a2b3c4d5e6f.webp", "moderationStatus": "PENDING" }
      ]
    }
  ],
  "deletedAt": null
}
```

</details>

<br>

### 4-2-8 채팅 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/chats` |
| 인증 | 관리자 |
| 성공 | 200<br>페이지 구조 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `q` | `string` | 선택 | 스토리 제목과 회원 닉네임 부분 일치<br>채팅 공개 식별자 정확 일치 |
| `storyId` | `string` | 선택 | 스토리 공개 식별자 |
| `memberId` | `string` | 선택 | 소유 회원 공개 식별자 |
| `startedAs` | `string` | 선택 | `GUEST`, `MEMBER` |
| `turnBucket` | `integer` | 선택 | 0~12<br>턴 수 분포 차트의 구간 순서 |
| `hasFirstMessage` | `boolean` | 선택 | `true`는 생성 뒤 900초 안에 첫 사용자 메시지가 있는 채팅<br>`false`는 그 외 |
| `turnDate` | `string` | 선택 | 그 KST 날짜에 AI 응답 메시지가 생성된 채팅 |
| `from`, `to` | `string` | 선택 | 채팅 생성일 |
| `aiFrom`, `aiTo` | `string` | 선택 | AI 호출 기록 생성일 |
| `aiFeature` | `string` | 선택 | `chat_response`, `choice_generation`, `chat_image`, `chat_compact` |
| `aiStatus` | `string` | 선택 | 스토리 목록과 같음 |
| `hasLatency` | `boolean` | 선택 | 스토리 목록과 같음 |
| `deleted` | `string` | 선택 | 삭제된 채팅의 포함 여부<br>값은 스토리 목록과 같음<br>스토리의 삭제 여부와 무관 |
| `sort` | `string` | 선택 | `startedAt`, `lastActiveAt`, `turnCount`, `creditsSpent`<br>기본 `startedAt` |
| 페이지 쿼리 | | 선택 | 공통 페이지 쿼리 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items[].chatId` | `string` | 채팅 공개 식별자 |
| `items[].story` | `object` | 스토리 요약 구조 |
| `items[].member` | `object / null` | 소유 회원의 회원 요약 구조<br>게스트는 `null` |
| `items[].startedAs` | `string` | 현재 소유자 유형이며 시작 당시 유형이 아님<br>소유 회원이 없으면 `GUEST`, 있으면 `MEMBER`<br>게스트에서 이관된 채팅은 `MEMBER` |
| `items[].turnCount` | `integer` | 현재 턴 수 |
| `items[].summaryThroughTurn` | `integer` | 요약 끝 턴<br>0이면 요약 없음<br>재생성으로 요약이 비워진 채팅도 0이라 요약을 만든 적 없는 채팅과 구별하지 않음 ([CHAT 3-2-3 채팅](../../CHAT/BACKEND/3-2-DB-SCHEMA.md#3-2-3-채팅)) |
| `items[].startedAt` | `string` | 생성 시각 |
| `items[].lastActiveAt` | `string` | 마지막 갱신 시각 |
| `items[].creditsSpent` | `integer` | 이 채팅을 참조하는 원장 소모 행 합계의 절댓값<br>턴과 이미지 |
| `items[].firstMessageSeconds` | `integer / null` | 생성부터 첫 사용자 메시지까지 초<br>사용자 메시지가 없으면 `null` |
| `items[].deletedAt` | `string / null` | 삭제 시각<br>삭제되지 않았으면 `null` |

- 삭제된 채팅은 `deleted`에 따라 싣는다. 메시지 원문과 대화 요약 본문은 어떤 필드에도 없다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 검색어, 날짜, enum, 공통 페이지 쿼리 오류<br>`storyId` 또는 `memberId`가 UUID 형식이 아님 |

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/chats?turnBucket=4&from=2026-10-15&to=2026-10-21&size=1
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
      "summaryThroughTurn": 0,
      "startedAt": "2026-10-20T13:02:11Z",
      "lastActiveAt": "2026-10-20T13:31:40Z",
      "creditsSpent": 0,
      "firstMessageSeconds": 42,
      "deletedAt": null
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

### 4-2-9 채팅 상세

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/chats/{chatId}` |
| 인증 | 관리자 |
| 성공 | 200<br>채팅 목록 항목 구조 |

**1. 경로**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `chatId` | 경로 | 필수 | 채팅 공개 식별자 |

- 삭제된 채팅도 응답한다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `chatId`가 UUID 형식이 아님 |
| 404 | `NOT_FOUND` | 없는 채팅 |

<br>

### 4-2-10 회원 목록

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
| `chatBucket` | `integer` | 선택 | 0~4<br>회원별 채팅 생성 횟수 차트의 구간 순서<br>채팅이 없는 회원은 어떤 값에도 해당하지 않음 |
| `chatFrom`, `chatTo` | `string` | 선택 | 채팅 생성일<br>지정하면 `chatBucket` 판정과 `periodChatCount`, `periodTurnCount`를 그 기간으로 세고 기간에 채팅이 없는 회원은 제외 |
| `creditDirection` | `string` | 선택 | `granted`, `spent`<br>그 방향의 원장 행이 있는 회원 |
| `creditDate` | `string` | 선택 | 원장 기록일<br>`creditDirection`과 함께만 |
| `attendanceDate` | `string` | 선택 | 그 KST 날짜에 출석 보상을 받은 회원 |
| `sort` | `string` | 선택 | `createdAt`, `lastActiveAt`, `creditsSpent`, `paidKrw`, `chatCount`, `turnCount`<br>`chatCount`와 `turnCount`는 채팅 기간과 무관한 누적 값으로 정렬<br>기본 `createdAt` |
| 페이지 쿼리 | | 선택 | 공통 페이지 쿼리 |

<br>

**2. 응답**

항목은 회원 요약 구조에 다음 필드를 더한다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items[].lastActiveAt` | `string / null` | 삭제되지 않은 채팅의 마지막 갱신, 원장 기록, 스토리 생성 중 가장 최근 시각<br>없으면 `null` |
| `items[].creditsSpent` | `integer` | 누적 이프 소모량<br>소모 사유 원장 행 합계의 절댓값이며 환불을 빼지 않음 |
| `items[].paidKrw` | `integer` | 완료 상태 주문의 금액 합<br>환불된 주문 제외 |
| `items[].chatCount` | `integer` | 삭제되지 않은 채팅 수 |
| `items[].periodChatCount` | `integer / null` | `chatFrom` 또는 `chatTo`를 지정했을 때 그 기간의 채팅 수<br>지정하지 않으면 `null` |
| `items[].turnCount` | `integer` | 누적 턴 수<br>소유 채팅의 AI 응답 메시지 수이며 재생성 판본은 세지 않음<br>삭제된 채팅과 게스트 때 만들어 이관된 채팅 포함<br>대시보드 채팅 턴 수와 같은 정의이고 팀 계정 제외 없음 |
| `items[].periodTurnCount` | `integer / null` | `chatFrom` 또는 `chatTo`를 지정했을 때 그 기간에 생성된 소유 채팅의 누적 턴 수<br>채팅 생성일만 기간으로 거르고 나머지는 `turnCount`와 같은 정의<br>지정하지 않으면 `null` |

- `q`가 있으면 접속 기록으로 감사 로그에 남는다. 이메일은 검색에만 쓰고 응답에는 없다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 검색어, 날짜, enum, 공통 페이지 쿼리 오류<br>`creditDate`만 지정 |

<details>
<summary><b>요청과 응답 예시</b></summary>

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
      "periodChatCount": null,
      "turnCount": 312,
      "periodTurnCount": null
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

### 4-2-11 회원 상세

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

회원 목록 항목에 다음 필드를 더한다. `periodChatCount`와 `periodTurnCount`는 항상 `null`이고 `turnCount`는 목록과 같은 값이다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `creditBalance` | `integer` | 만료되지 않은 이프 잔액 |
| `storyCount` | `integer` | 삭제되지 않은 소유 스토리 수 |
| `deletedAt` | `string / null` | 탈퇴 시각 |

- 상세 조회는 접속 기록으로 감사 로그에 남는다.
- 이 회원의 결제, 채팅, 스토리는 각 목록을 `memberId`로 조회한다. 이프 내역과 출석은 다음 두 절이다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `memberId`가 UUID 형식이 아님<br>`details[].field`는 `memberId` |
| 404 | `NOT_FOUND` | 없는 회원 |

<details>
<summary><b>요청과 응답 예시</b></summary>

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
  "turnCount": 312,
  "periodTurnCount": null,
  "creditBalance": 1230,
  "storyCount": 4,
  "deletedAt": null
}
```

</details>

<br>

### 4-2-12 회원 이프 내역

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
| `items[].balanceAfter` | `integer` | 기록 시각과 내부 ID 오름차순으로 이 행까지 `amount`를 합한 원장 누계<br>만료와 로트 상태를 반영한 사용 가능 잔액(`creditBalance`)과 다름 |
| `items[].createdAt` | `string` | 기록 시각 |

- 원장 행에는 공개 식별자가 없어 항목에 식별자가 없다. 정렬은 기록 시각과 내부 ID를 `order` 방향으로 함께 적용해 기본 `desc`에서는 같은 시각의 행도 내부 ID 내림차순이다.
- 조회는 회원 상세와 같은 접속 기록을 남긴다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `memberId`가 UUID 형식이 아님<br>공통 페이지 쿼리 오류 |
| 404 | `NOT_FOUND` | 없는 회원 |

<details>
<summary><b>요청과 응답 예시</b></summary>

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

### 4-2-13 회원 출석 기록

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

회원 이프 내역과 같다.

<br>

### 4-2-14 이프 내역

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/credits/transactions` |
| 인증 | 관리자 |
| 성공 | 200<br>페이지 구조 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `direction` | `string` | 선택 | `granted`는 적립 사유의 양수 행, `spent`는 소모 사유의 음수 행<br>정의는 대시보드의 이프 적립과 소모와 같음<br>생략하면 모든 원장 행 |
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
- 회원별 누계와 회원 필터는 없다. 한 회원의 원장 행은 회원 이프 내역에서 본다. ([4-2-12 회원 이프 내역](#4-2-12-회원-이프-내역))
- 팀 계정 제외를 적용하지 않으므로 대시보드 카드와 추이의 적립량과 소모량과 이 목록의 합계는 팀 계정의 행만큼 다를 수 있다.
- 접속 기록을 남기지 않는다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `direction` 허용 값 밖, 날짜 형식 오류, 공통 페이지 쿼리 오류 |

<details>
<summary><b>요청과 응답 예시</b></summary>

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

### 4-2-15 결제 내역

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
| `items[].creditAmount` | `integer` | 구매로 적립된 이프 수량 |
| `items[].completedAt` | `string` | 완료 시각 |
| `items[].refundedAt` | `string / null` | 환불 시각 |
| `items[].reversalShortfall` | `integer / null` | 구매 환불 회수에서 돌려받지 못한 이프 수량<br>환불 전은 `null` |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 검색어, 날짜, enum, 공통 페이지 쿼리 오류<br>`memberId`가 UUID 형식이 아님 |

<details>
<summary><b>요청과 응답 예시</b></summary>

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

### 4-2-16 결제 상세

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

결제 내역 항목에 다음 필드를 더한다. 전후 비교의 기준은 그 회원의 완료 시각이 있는 주문 가운데 가장 이른 완료 시각이며 환불된 주문도 포함한다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `firstPaidAt` | `string` | 회원의 완료 시각이 있는 주문 가운데 가장 이른 완료 시각<br>환불된 주문도 포함 |
| `before` | `object` | 기준 시각 전 |
| `before.turns` | `integer` | 이프가 소모된 채팅 처리 횟수<br>채팅 턴 사유 원장 행 수이며 재생성 포함, 무료 체험 제외 |
| `before.stories` | `integer` | 이프가 소모된 간편 제작 횟수<br>간편 제작 사유 원장 행 수 |
| `before.creditsSpent` | `integer` | 환불을 반영한 이프 순소모량<br>소모 사유 합계의 절댓값에서 AI 실패 환불 합계를 뺀 값 |
| `after` | `object` | 기준 시각 이후<br>`before`와 같은 세 필드 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `orderId`가 UUID 형식이 아님 |
| 404 | `NOT_FOUND` | 없는 주문<br>완료 시각이 없는 대기 주문 |

<details>
<summary><b>요청과 응답 예시</b></summary>

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

### 4-2-17 감사 로그 조회

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
| `category` | `string` | 선택 | 작업 분류<br>`CHANGE`, `ACCESS` |
| `sort` | `string` | 선택 | `createdAt`, `category`, `action`, `targetType`, `admin`<br>`admin`은 처리자 닉네임<br>기본 `createdAt` |
| 페이지 쿼리 | | 선택 | 공통 페이지 쿼리 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items[].auditLogId` | `string` | 감사 로그 공개 식별자 |
| `items[].admin` | `object` | 처리자의 회원 요약 구조 |
| `items[].category` | `string` | 작업 분류<br>`CHANGE`<br>`ACCESS` |
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
<summary><b>요청과 응답 예시</b></summary>

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

### 4-2-18 분석 지표

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
- 지난 날짜 값은 서버 DB에 저장되어 있어 비어 있는 날짜만 분석 도구에서 받는다. 비어 있는 날짜가 비용 예산보다 많으면 받은 날짜만 응답하고 나머지는 `pendingDates`에 넣는다. 관리자 페이지는 `pendingDates`가 비어 있지 않으면 60초 뒤 같은 요청을 다시 보낸다. ([4-1-20 Amplitude 조회 공통](4-1-PIPELINES.md#4-1-20-amplitude-조회-공통))

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string` | 응답에 쓴 값을 분석 도구에서 받은 시각<br>오늘과 어제처럼 확정 전 값이 있으면 그 가운데 가장 이른 시각, 확정 값만이면 그 가운데 가장 늦은 시각<br>만료된 저장 값으로 바로 응답하면(갱신을 시작한 요청, 갱신 중, 쿨다운 중) 오늘 값이 10분보다 오래될 수 있음 |
| `pendingDates` | `string[]` | 준비 중 날짜<br>아직 값을 받지 못해 `daily`에서 뺀 KST 날짜, 오름차순<br>비어 있으면 범위 전체가 준비됨 |
| `from` | `string` | 범위 첫날의 KST 날짜 |
| `to` | `string` | 범위 마지막 날의 KST 날짜 |
| `todayActiveUsers` | `object / null` | 오늘 활성 사용자 수<br>플랫폼 값 구조<br>범위와 무관하게 KST 오늘 날짜의 값이며 10분마다 다시 받음<br>오늘 값을 아직 받지 못했으면 `null` |
| `daily` | `object[]` | 날짜 오름차순<br>`pendingDates`의 날짜는 없음 |
| `daily[].date` | `string` | KST 날짜 |
| `daily[].activeUsers` | `object` | 그날 이벤트가 있는 고유 사용자 수<br>플랫폼 값 구조 |
| `daily[].newUsers` | `object` | 그날 처음 이벤트가 있었던 고유 사용자 수<br>플랫폼 값 구조 |

플랫폼 값 구조는 다음 세 정수다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `total` | `integer` | 전체 조건(웹이나 앱)의 고유 사용자 수<br>`web`과 `android`의 합이 아님 |
| `web` | `integer` | 웹 조건의 고유 사용자 수 |
| `android` | `integer` | 앱 조건의 고유 사용자 수 |

- 같은 사람이 같은 날 웹과 앱에서 활동하면 `web`과 `android`에 한 번씩 들고 `total`에는 한 번 든다. 그래서 `web`과 `android`의 합이 `total`보다 클 수 있다.
- 조회 조건은 처리 흐름에 있다. ([4-1-20 Amplitude 조회 공통](4-1-PIPELINES.md#4-1-20-amplitude-조회-공통)) 국가 조건 밖의 사용자와 플랫폼 속성이 없는 사용자(게스트의 서버 전용 식별자)는 어느 값에도 들지 않는다.
- 값은 분석 도구가 집계한 것이며 코호트 ID가 설정돼 있으면 팀 계정 코호트에 속한 사용자를 제외한다. 집계가 몇 분 늦을 수 있다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 허용하지 않는 `days`, `days`와 `from` 또는 `to` 동시 지정, 한쪽만 있는 `from` 또는 `to`, 날짜 형식 오류, `from`이 `to`보다 뒤, `to`가 오늘 이후, 366일 초과 |
| 503 | `SERVICE_UNAVAILABLE` | 준비된 날짜가 하나도 없는데 자격 증명 미설정, 호출 실패, 호출 한도 초과, 비용 예산 부족, 실패 뒤 쿨다운, 다른 요청의 갱신 중, 요청 대기 10초 초과로 값을 받지 못함 |

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/dashboard/analytics?from=2026-10-15&to=2026-10-21
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

예시에는 `daily`의 날짜 항목 2개만 표시했다.

```json
{
  "asOf": "2026-10-21T05:10:00Z",
  "from": "2026-10-15",
  "to": "2026-10-21",
  "todayActiveUsers": { "total": 203, "web": 186, "android": 19 },
  "pendingDates": [],
  "daily": [
    {
      "date": "2026-10-15",
      "activeUsers": { "total": 211, "web": 195, "android": 18 },
      "newUsers": { "total": 31, "web": 28, "android": 3 }
    },
    {
      "date": "2026-10-16",
      "activeUsers": { "total": 198, "web": 181, "android": 19 },
      "newUsers": { "total": 27, "web": 25, "android": 2 }
    }
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

### 4-2-19 설치 지표

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/dashboard/play-installs` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string` | 집계 기준 날짜 `YYYY-MM-DD`<br>월별 보고서 전체에서 날짜가 가장 늦은 행의 날짜<br>Play 기준 날짜라 KST로 바꾸지 않으며 캐시한 시각이 아님 |
| `totalInstalls` | `integer` | Android 누적 기기 설치 수<br>보고서 전체 기간의 일별 기기 설치 수 합이며 고유 설치 사용자 수가 아님 |
| `activeDevices` | `integer` | 날짜가 가장 늦은 행의 활성 기기 수 |
| `daily` | `object[]` | 보고서 첫 날짜부터 마지막 날짜까지 모든 날이 한 항목씩<br>날짜 오름차순<br>보고서에 행이 없는 날도 채움 |
| `daily[].date` | `string` | Play 기준 날짜 |
| `daily[].installs` | `integer` | 그날 기기 설치 수<br>행이 없는 날은 0 |
| `daily[].uninstalls` | `integer` | 그날 앱 삭제 수<br>행이 없는 날은 0 |
| `daily[].cumulativeInstalls` | `integer` | 첫날부터 그날까지의 기기 설치 누계<br>행이 없는 날은 전날 값<br>마지막 항목은 `totalInstalls`와 같음 |
| `daily[].activeDevices` | `integer / null` | 그날의 활성 기기 수<br>행이 없는 날은 `null` |

- 값은 Play Console 일괄 보고서가 집계한 것이며 보고서는 며칠 늦게 채워진다. 보고서가 2026년 9월부터라 행 수가 작아 기간 쿼리는 없다.

<br>

**2. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 503 | `SERVICE_UNAVAILABLE` | 서비스 계정 키 미설정<br>보고서 저장소 호출 실패, 보고서 없음, 해석 실패, 실패 뒤 쿨다운, 다른 요청이 갱신 중인데 캐시도 없음 |

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/dashboard/play-installs
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

예시에는 `daily`의 날짜 항목 2개만 표시했다.

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

### 4-2-20 캠페인 목록

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/campaigns` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 응답**

캠페인 목록은 설정 파일 고정값이다. 항목을 더하거나 고치려면 배포한다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `items` | `object[]` | 시작일 오름차순 |
| `items[].key` | `string` | 항목 식별자<br>`meta-web-1`부터 `meta-web-4` |
| `items[].name` | `string` | 표시 이름<br>`1차`부터 `4차` |
| `items[].campaign` | `string` | UTM 캠페인 값 |
| `items[].startDate` | `string` | 시작 KST 날짜 |
| `items[].endDate` | `string / null` | 종료 KST 날짜<br>진행 중이면 `null` |
| `items[].storyId` | `string / null` | 상세 진입 퍼널의 기본 대상 스토리 공개 식별자 |

| `key` | `campaign` | `startDate` | `endDate` | `storyId` |
|---|---|---|---|---|
| `meta-web-1` | `KR_META_WEB_ACTIVATION_COLD_202607` | `2026-07-21` | `2026-07-31` | `null` |
| `meta-web-2` | `KR_META_WEB_ACTIVATION_COLD_202608` | `2026-08-21` | `2026-09-16` | `null` |
| `meta-web-3` | `KR_META_WEB_ACTIVATION_COLD_202609` | `2026-09-17` | `2026-10-21` | `cca6358a-0ef3-4709-88d1-100b9faeeca8` |
| `meta-web-4` | `KR_META_WEB_ACTIVATION_COLD_202610` | `2026-10-22` | `null` | `cca6358a-0ef3-4709-88d1-100b9faeeca8` |

<br>

**2. 실패 응답**

공통 실패만 있다.

<br>

### 4-2-21 캠페인 추이

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/campaigns/analytics` |
| 인증 | 관리자 |
| 성공 | 200 |

캠페인 분석은 분석 도구 Amplitude에서 광고 캠페인의 유입과 가입, 이용 횟수를 계산해 돌려준다. 광고 구분 조건과 이벤트 정의는 제품 제약에 있고 값 저장과 비용 예산, 기간 상한의 근거는 처리 흐름에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약), [4-1-20 Amplitude 조회 공통](4-1-PIPELINES.md#4-1-20-amplitude-조회-공통))

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `campaign` | `string` | 선택 | UTM 캠페인 값, 1~100자<br>캠페인 목록에 없는 값도 허용<br>생략하면 캠페인 목록에서 종료일이 없는 마지막 항목의 값 |
| `from`, `to` | `string` | 선택 | 분석 지표와 같은 규칙<br>기간은 1일 이상 366일 이하 |
| `days` | `integer` | 선택 | `7`, `30` 중 하나<br>`from`, `to`와 함께 보내면 400 |

- 셋 다 없으면 오늘을 포함한 최근 30일이다. 관리자 페이지는 캠페인 목록의 시작일과 종료일로 범위를 미리 채운다.

<br>

**2. 응답**

세그먼트 묶음 구조는 `all`(전체 Web), `ads`(광고 유입), `nonAds`(광고 외 유입)의 세 정수다. `nonAds`는 `all`에서 `ads`를 뺀 값이다. 신규 가입자도 Web만 세고 Android 가입은 광고 구분 없이 `androidSignups`로 따로 준다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string` | 분석 지표와 같음 |
| `pendingDates` | `string[]` | 분석 지표와 같음 |
| `from` | `string` | 범위 첫날의 KST 날짜 |
| `to` | `string` | 범위 마지막 날의 KST 날짜 |
| `campaign` | `string` | 적용한 캠페인 값 |
| `daily` | `object[]` | 날짜 오름차순 |
| `daily[].date` | `string` | KST 날짜 |
| `daily[].activeUsers` | `integer` | 웹 DAU<br>그날 활성 이벤트가 있는 고유 사용자 수 |
| `daily[].newVisitors` | `object` | 신규 방문자<br>세그먼트 묶음 구조 |
| `daily[].newVisitorsBySource` | `object` | 유입 소스별 신규 방문자 |
| `daily[].newVisitorsBySource.ads` | `integer` | 광고 유입<br>`newVisitors.ads`와 같음 |
| `daily[].newVisitorsBySource.instagram` | `integer` | 캠페인이 아니면서 소스가 인스타그램 |
| `daily[].newVisitorsBySource.threads` | `integer` | 캠페인이 아니면서 소스가 쓰레드 |
| `daily[].newVisitorsBySource.dcinside` | `integer` | 캠페인이 아니면서 소스가 디시인사이드 |
| `daily[].newVisitorsBySource.other` | `integer` | 캠페인이 아니면서 소스 목록 밖 |
| `daily[].newVisitorsByDevice` | `object` | 기기 유형별 신규 방문자<br>광고 구분 없음 |
| `daily[].newVisitorsByDevice.ios` | `integer` | 사용자 속성 `device_type`이 `Apple iPhone` 또는 `Apple iPad` |
| `daily[].newVisitorsByDevice.android` | `integer` | `device_type`이 `Android` |
| `daily[].newVisitorsByDevice.other` | `integer` | `device_type`이 앞의 세 값이 아님<br>데스크톱과 값 없음 포함 |
| `daily[].signups` | `object` | Web 신규 가입자<br>가입 커스텀 이벤트의 고유 사용자 수라 같은 날 구글과 카카오로 모두 가입한 사람도 한 번<br>세그먼트 묶음 구조 |
| `daily[].cumulativeSignups` | `object` | 범위 첫날부터 그날까지 준비된 날짜의 `signups` 누계<br>세그먼트 묶음 구조 |
| `daily[].androidSignups` | `integer` | Android 신규 가입자<br>광고 구분 없음 |
| `daily[].storylineRequests` | `integer` | 스토리라인 생성 요청 횟수 |
| `daily[].completionRequests` | `integer` | 간편 제작 요청 횟수 |
| `daily[].chatMessages` | `integer` | 채팅 메시지 전송 횟수 |
| `totals` | `object` | 준비된 날짜의 합계<br>`pendingDates`가 있으면 범위 일부의 값 |
| `totals.activeUsersAverage` | `number` | `daily[].activeUsers` 평균 |
| `totals.newVisitors` | `object` | 일별 합<br>세그먼트 묶음 구조 |
| `totals.newVisitorsByDevice` | `object` | 일별 합<br>`daily[].newVisitorsByDevice`와 같은 구조 |
| `totals.signups` | `object` | 일별 합<br>세그먼트 묶음 구조 |
| `totals.androidSignups` | `integer` | 일별 합 |
| `totals.adsShare` | `number / null` | `totals.newVisitors.ads`를 `totals.newVisitors.all`로 나눈 0~1<br>`all`이 0이면 `null` |
| `totals.storylineRequests`, `totals.completionRequests`, `totals.chatMessages` | `integer` | 일별 합 |

- 팀 계정 코호트 제외는 적용하지 않는다. 캠페인 분석은 광고가 데려온 사용자를 보는 것이 목적이고 원본 차트에도 제외가 없다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 분석 지표와 같은 기간 오류, 366일 초과, 허용하지 않는 `days`, `campaign` 길이 오류, `campaign`이 없고 캠페인 목록에 종료일 없는 항목도 없음 |
| 503 | `SERVICE_UNAVAILABLE` | 분석 지표와 같은 조건 |

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/campaigns/analytics?from=2026-10-22&to=2026-10-23
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

예시에는 `daily`의 날짜 항목 1개만 표시했다.

```json
{
  "asOf": "2026-10-23T05:10:00Z",
  "from": "2026-10-22",
  "to": "2026-10-23",
  "campaign": "KR_META_WEB_ACTIVATION_COLD_202610",
  "pendingDates": [],
  "daily": [
    {
      "date": "2026-10-22",
      "activeUsers": 162,
      "newVisitors": { "all": 162, "ads": 152, "nonAds": 10 },
      "newVisitorsBySource": { "ads": 152, "instagram": 4, "threads": 2, "dcinside": 1, "other": 3 },
      "newVisitorsByDevice": { "ios": 70, "android": 85, "other": 7 },
      "signups": { "all": 21, "ads": 18, "nonAds": 3 },
      "cumulativeSignups": { "all": 21, "ads": 18, "nonAds": 3 },
      "androidSignups": 30,
      "storylineRequests": 40,
      "completionRequests": 17,
      "chatMessages": 231
    }
  ],
  "totals": {
    "activeUsersAverage": 150.5,
    "newVisitors": { "all": 301, "ads": 280, "nonAds": 21 },
    "newVisitorsByDevice": { "ios": 130, "android": 158, "other": 13 },
    "signups": { "all": 39, "ads": 33, "nonAds": 6 },
    "androidSignups": 52,
    "adsShare": 0.93,
    "storylineRequests": 71,
    "completionRequests": 30,
    "chatMessages": 402
  }
}
```

</details>

<br>

### 4-2-22 캠페인 간편 제작 퍼널

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/campaigns/funnels/creation` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `campaign` | `string` | 선택 | 캠페인 추이와 같음 |
| `from`, `to` | `string` | 선택 | 분석 지표와 같은 규칙<br>기간은 1일 이상 20일 이하 |
| `days` | `integer` | 선택 | `7`만 허용<br>`from`, `to`와 함께 보내면 400 |

- 셋 다 없으면 오늘을 포함한 최근 7일이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string` | 범위 값을 분석 도구에서 받은 시각 |
| `from`, `to`, `campaign` | | 캠페인 추이와 같음 |
| `steps` | `object[]` | 단계 순서<br>6개 |
| `steps[].event` | `string` | 단계의 이벤트 이름 |
| `steps[].users` | `object` | 범위 안에 첫 단계를 한 사용자 가운데 전환 창 1일 안에 이 단계까지 순서대로 도달한 고유 사용자 수<br>세그먼트 묶음 구조 |

- 단계 사이 전환율은 관리자 페이지가 앞 단계로 나눠 만든다. 단계 정의는 제품 제약에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약))

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 캠페인 추이와 같은 오류, 20일 초과 |
| 503 | `SERVICE_UNAVAILABLE` | 캠페인 추이와 같음 |

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/campaigns/funnels/creation?from=2026-10-22&to=2026-10-28
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

예시에는 처음 두 단계만 표시했다.

```json
{
  "asOf": "2026-10-29T05:10:00Z",
  "from": "2026-10-22",
  "to": "2026-10-28",
  "campaign": "KR_META_WEB_ACTIVATION_COLD_202610",
  "steps": [
    { "event": "client_storyCreate_viewed", "users": { "all": 410, "ads": 372, "nonAds": 38 } },
    { "event": "client_storyCreate_tagCategory_selected", "users": { "all": 251, "ads": 228, "nonAds": 23 } }
  ]
}
```

</details>

<br>

### 4-2-23 캠페인 상세 진입 퍼널

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/campaigns/funnels/story-detail` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `campaign` | `string` | 선택 | 캠페인 추이와 같음 |
| `storyId` | `string` | 선택 | 대상 스토리 공개 식별자<br>생략하면 적용한 캠페인과 값이 같은 캠페인 목록 항목의 `storyId`<br>그것도 없으면 400 |
| `from`, `to` | `string` | 선택 | 분석 지표와 같은 규칙<br>기간은 1일 이상 31일 이하 |
| `days` | `integer` | 선택 | `7`, `30` 중 하나<br>`from`, `to`와 함께 보내면 400 |

- 셋 다 없으면 오늘을 포함한 최근 7일이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string` | 범위 값을 분석 도구에서 받은 시각 |
| `from`, `to`, `campaign` | | 캠페인 추이와 같음 |
| `storyId` | `string` | 적용한 대상 스토리 |
| `steps` | `object[]` | 단계 순서<br>7개 |
| `steps[].event` | `string` | 단계의 이벤트 이름 |
| `steps[].turnNumber` | `integer / null` | 채팅 메시지 전송 단계의 턴 번호 1~5<br>그 외 `null` |
| `steps[].users` | `integer` | 전환 창 1일 안에 이 단계까지 순서대로 도달한 고유 사용자 수<br>전체 세그먼트만 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 캠페인 추이와 같은 오류, 31일 초과, `storyId`가 UUID 형식이 아님, 대상 스토리가 요청과 목록 모두에 없음 |
| 503 | `SERVICE_UNAVAILABLE` | 캠페인 추이와 같음 |

<br>

### 4-2-24 캠페인 유입 소스

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/campaigns/sources` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to` | `string` | 선택 | 분석 지표와 같은 규칙<br>기간은 1일 이상 10일 이하 |
| `days` | `integer` | 선택 | `7`만 허용<br>`from`, `to`와 함께 보내면 400 |

- 셋 다 없으면 오늘을 포함한 최근 7일이다. 캠페인 값은 받지 않으며 모든 유입을 보여 준다.
- 두 표 모두 값이 열린 묶음 조회라 하루 비용이 커서 기간이 짧다. ([4-1-20 Amplitude 조회 공통](4-1-PIPELINES.md#4-1-20-amplitude-조회-공통))

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string` | 범위 값을 분석 도구에서 받은 시각 |
| `from`, `to` | | 캠페인 추이와 같음 |
| `sources` | `object[]` | 첫 유입 소스별 신규 방문자<br>`newVisitors` 내림차순 |
| `sources[].source` | `string / null` | 사용자 속성 `gp:initial_utm_source`<br>없으면 `null` |
| `sources[].newVisitors` | `integer` | 범위 안 `_new` 고유 사용자 수 |
| `posts` | `object[]` | 커뮤니티와 SNS 게시글별 방문자<br>`visitors` 내림차순 |
| `posts[].content` | `string / null` | 이벤트 속성 `utm_content`<br>없으면 `null` |
| `posts[].visitors` | `integer` | 이벤트 속성 `utm_medium`이 `community` 또는 `social`인 페이지 조회의 고유 사용자 수 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 분석 지표와 같은 기간 오류, 10일 초과, 허용하지 않는 `days` |
| 503 | `SERVICE_UNAVAILABLE` | 캠페인 추이와 같음 |

<br>

### 4-2-25 사용자 활동

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/users/activity` |
| 인증 | 관리자 |
| 성공 | 200 |

사용자 메뉴의 Amplitude 지표다. 플랫폼 묶음 구조는 `all`(전체), `web`, `android`, `unknown`(플랫폼 속성 없음)의 네 정수다. `all`은 전체 조건(웹이나 앱) 조회 값이라 같은 날 웹과 앱에서 함께 활동한 사용자도 한 번 들고 `unknown`은 들지 않는다. `web`과 `android`의 합은 `all`보다 클 수 있다. `unknown`은 활성 사용자의 플랫폼 구성을 보이는 값이다. 정의는 제품 제약에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약))

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to` | `string` | 선택 | 분석 지표와 같은 규칙<br>기간은 1일 이상 366일 이하 |
| `days` | `integer` | 선택 | `7`, `30` 중 하나<br>`from`, `to`와 함께 보내면 400 |

- 셋 다 없으면 오늘을 포함한 최근 30일이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to`, `pendingDates` | | 분석 지표와 같음 |
| `monthlyActiveUsers` | `integer / null` | `to`를 끝으로 하는 30일의 고유 활성 사용자 수<br>그 30일을 한 번에 조회한 전체 조건 세분화 응답의 `seriesCollapsed` 값이며 일별 값의 합이 아님<br>30일 안에 웹과 앱을 함께 쓴 사용자도 한 번<br>전체만이며 플랫폼별 값은 없음<br>아직 받지 못했으면 `null` |
| `daily` | `object[]` | 날짜 오름차순<br>`pendingDates`의 날짜는 없음 |
| `daily[].date` | `string` | KST 날짜 |
| `daily[].activeUsers` | `object` | DAU<br>플랫폼 묶음 구조 |
| `daily[].newVisitors` | `object` | 신규 방문자<br>플랫폼 묶음 구조 |
| `daily[].cumulativeNewVisitors` | `object` | 범위 첫날부터 그날까지 준비된 날짜의 누계<br>플랫폼 묶음 구조 |
| `daily[].messagesPerUser` | `object` | 사용자당 채팅 메시지 전송 수<br>`web`과 `android`만 값이 있는 소수이고 `all`과 `unknown`은 `null` |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 분석 지표와 같은 기간 오류, 366일 초과, 허용하지 않는 `days` |
| 503 | `SERVICE_UNAVAILABLE` | 분석 지표와 같음 |

<br>

### 4-2-26 사용자 리텐션

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/users/retention` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to` | `string` | 선택 | 분석 지표와 같은 규칙<br>기간은 1일 이상 366일 이하<br>`to`는 어제 이하 |
| `days` | `integer` | 선택 | `7`만 허용<br>어제를 끝으로 하는 최근 7일<br>`from`, `to`와 함께 보내면 400 |
| `cohort` | `string` | 선택 | 시작 집단<br>`visitor`(방문자), `signup`(가입자), `first-chat`(채팅 시작자)<br>기본 `visitor` |

- 기간 쿼리가 모두 없으면 어제를 끝으로 하는 최근 7일이다. 범위는 시작일 기준이다. 시작 집단의 정의는 제품 제약에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약))

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to` | | 분석 지표와 같음 |
| `pendingDates` | `string[]` | 아직 값을 받지 못해 `cohorts`에서 뺀 코호트 날짜<br>그 밖은 분석 지표와 같음 |
| `cohort` | `string` | 적용한 `cohort` |
| `platforms` | `object[]` | `all`, `web`, `android` 세 항목 |
| `platforms[].platform` | `string` | `all`, `web`, `android`<br>`all`은 전체 조건 코호트이며 시작과 복귀가 웹이나 앱이면 복귀로 셈<br>`web`은 웹 조건, `android`는 앱 조건 코호트이며 시작과 복귀가 같은 플랫폼일 때만 복귀로 셈 |
| `platforms[].cohorts` | `object[]` | 시작일마다 한 항목<br>날짜 오름차순<br>`pendingDates`의 날짜는 없음 |
| `platforms[].cohorts[].date` | `string` | 시작일 |
| `platforms[].cohorts[].users` | `integer` | 그날 시작 인원 |
| `platforms[].cohorts[].d1`, `d2`, `d3`, `d4`, `d5`, `d6`, `d7`, `d30` | `number / null` | 그날로부터 정확히 1일, 2일, 3일, 4일, 5일, 6일, 7일, 30일 뒤에 활성인 비율 0~1<br>아직 그 날짜가 끝나지 않았거나 분석 도구 값이 없거나 집계 중이거나 분모가 0이면 `null` |
| `platforms[].summary` | `object` | 범위 전체의 가중 평균 `d1`, `d2`, `d3`, `d4`, `d5`, `d6`, `d7`, `d30`<br>필드마다 값이 `null`이 아닌 코호트를 그 분모로 가중<br>그런 코호트가 없으면 `null` |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 분석 지표와 같은 기간 오류, 366일 초과, `to`가 어제보다 뒤, 허용하지 않는 `days`와 `cohort` |
| 503 | `SERVICE_UNAVAILABLE` | 분석 지표와 같음 |

<br>

### 4-2-27 사용자 세션

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/users/sessions` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to` | `string` | 선택 | 분석 지표와 같은 규칙<br>기간은 1일 이상 366일 이하 |
| `days` | `integer` | 선택 | `7`, `14` 중 하나<br>`from`, `to`와 함께 보내면 400 |
| `segment` | `string` | 선택 | `all`, `guest`, `member`<br>기본 `all`<br>`guest`는 사용자 속성 `user_id`가 없는 사용자의 세션, `member`는 있는 사용자의 세션<br>세션 조회의 세그먼트 조건으로 거름 |

- 셋 다 없으면 오늘을 포함한 최근 14일이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to`, `pendingDates` | | 분석 지표와 같음 |
| `daily` | `object[]` | 날짜 오름차순<br>`pendingDates`의 날짜는 없음 |
| `daily[].date` | `string` | KST 날짜 |
| `segment` | `string` | 적용한 `segment` |
| `daily[].averageSessionSeconds` | `object` | 평균 세션 길이 초<br>`all`, `web`, `android`의 소수이고 `unknown`은 `null`<br>`all`은 전체 조건 조회 값이며 `web`과 `android`의 평균이 아님 |
| `daily[].sessionsPerUser` | `object` | 그날 세션이 있는 사용자 1명당 세션 수<br>`averageSessionSeconds`와 같은 구조와 조건 |

- 세션 정의는 분석 도구의 기본 세션이다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 분석 지표와 같은 기간 오류, 366일 초과, 허용하지 않는 `days`와 `segment` |
| 503 | `SERVICE_UNAVAILABLE` | 분석 지표와 같음 |

<br>

**4. 세션 길이 분포**

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/users/session-lengths` |
| 인증 | 관리자 |
| 성공 | 200 |

쿼리와 실패 응답은 평균 세션 길이와 같다. 평균 세션 길이와 따로 저장하고 갱신해 한쪽의 준비 중 날짜와 실패가 다른 쪽에 영향을 주지 않는다. 정의는 제품 제약에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약))

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to`, `pendingDates` | | 분석 지표와 같음 |
| `segment` | `string` | 적용한 `segment` |
| `bins` | `object[]` | 세션 길이 구간 9개, 짧은 구간부터 |
| `bins[].fromSeconds` | `integer` | 구간 시작 초, 포함 |
| `bins[].toSeconds` | `integer` | 구간 끝 초, 제외<br>마지막 구간은 86400 |
| `platforms` | `object[]` | `all`, `web`, `android` 세 항목<br>`pendingDates`를 뺀 날짜의 합 |
| `platforms[].platform` | `string` | `all`, `web`, `android`<br>`all`은 전체 조건 조회이며 `web`과 `android`의 합이 아님 |
| `platforms[].sessions` | `integer[]` | `bins` 순서의 구간별 세션 수 |
| `platforms[].totalSessions` | `integer` | `sessions`의 합 |
| `platforms[].medianBin` | `integer / null` | 중앙값이 속한 구간의 `bins` 인덱스(0부터)<br>짧은 구간부터 더한 세션 수가 처음으로 `totalSessions`의 절반 이상이 되는 구간<br>`totalSessions`가 0이면 `null` |
| `daily` | `object[]` | 날짜 오름차순<br>`pendingDates`의 날짜는 없음 |
| `daily[].date` | `string` | KST 날짜 |
| `daily[].sessions` | `object` | 그날 세션 수<br>`all`, `web`, `android`의 정수이고 그날 구간별 세션 수의 합 |

- 분석 도구가 정확한 중앙값을 주지 않아 구간만 응답한다.

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/users/session-lengths?days=7&segment=all
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

예시에는 `platforms`의 첫 항목과 `daily`의 날짜 항목 1개만 표시했다.

```json
{
  "asOf": "2026-10-28T05:10:00Z",
  "from": "2026-10-22",
  "to": "2026-10-28",
  "segment": "all",
  "pendingDates": [],
  "bins": [
    { "fromSeconds": 0, "toSeconds": 3 }, { "fromSeconds": 3, "toSeconds": 10 }, { "fromSeconds": 10, "toSeconds": 30 },
    { "fromSeconds": 30, "toSeconds": 60 }, { "fromSeconds": 60, "toSeconds": 180 }, { "fromSeconds": 180, "toSeconds": 600 },
    { "fromSeconds": 600, "toSeconds": 1800 }, { "fromSeconds": 1800, "toSeconds": 3600 }, { "fromSeconds": 3600, "toSeconds": 86400 }
  ],
  "platforms": [
    { "platform": "all", "sessions": [973, 211, 187, 164, 290, 247, 158, 52, 35], "totalSessions": 2317, "medianBin": 1 }
  ],
  "daily": [
    { "date": "2026-10-22", "sessions": { "all": 342, "web": 301, "android": 45 } }
  ]
}
```

</details>

<br>

### 4-2-28 신규 가입자

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/users/signups` |
| 인증 | 관리자 |
| 성공 | 200 |

가입 수와 누계, 가입 경로, 게스트 이관은 서버 DB로 계산하고 팀 계정 제외 목록을 적용한다. 회원 수에서는 재가입으로 소셜 연동을 새 계정에 넘긴 예전 계정 행을 뺀다. 플랫폼별 가입 수와 가입 전환율은 Amplitude 가입 커스텀 이벤트와 신규 방문자로 계산하며 팀 계정을 제외하지 않는다. 두 원본은 따로 세므로 같은 날의 DB 가입 수와 플랫폼 값이 다를 수 있다. 정의는 제품 제약에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약))

플랫폼 묶음 구조는 `all`, `web`, `android`의 세 값이다. 이 절과 채팅 턴 도달률, 채팅 옵션 비중의 `web`과 `android`는 국내 조건 안의 웹 조건과 앱 조건 조회다. 이 절과 채팅 옵션 비중의 채팅 시작 사용자 수처럼 고유 사용자 수인 `all`은 전체 조건(웹이나 앱) 조회라 같은 날 웹과 앱에 함께 잡힌 사람도 한 번이다. 채팅 턴 도달률과 채팅 옵션 비중의 모델 턴 수처럼 이벤트 수인 `all`은 `web`과 `android`의 합이다. 플랫폼 속성이 없는 이벤트와 국가 조건 밖의 사용자는 세지 않는다.

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to` | `string` | 선택 | 대시보드 차트와 같은 규칙<br>기간은 1일 이상 366일 이하 |
| `days` | `integer` | 선택 | `7`, `30`, `90` 중 하나<br>`from`, `to`와 함께 보내면 400 |

- 셋 다 없으면 오늘을 포함한 최근 30일이다.
- 플랫폼별 가입 수는 분석 지표처럼 저장 값을 쓰고 비어 있는 날짜만 받는다. 받지 못한 날짜는 `pendingDates`에 넣고 DB 값은 그대로 응답한다. 관리자 페이지는 `pendingDates`가 비어 있지 않으면 60초 뒤 같은 요청을 다시 보낸다. ([4-1-20 Amplitude 조회 공통](4-1-PIPELINES.md#4-1-20-amplitude-조회-공통))

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to` | | 대시보드 차트와 같음 |
| `platformAsOf` | `string / null` | 플랫폼별 가입 수를 분석 도구에서 받은 시각<br>분석 지표의 `asOf`와 같은 규칙<br>준비된 날짜가 없으면 `null` |
| `pendingDates` | `string[]` | 플랫폼별 가입 수를 아직 받지 못한 KST 날짜, 오름차순<br>`daily`에는 그 날짜도 있고 `signupsByPlatform`만 `null` |
| `daily` | `object[]` | 날짜 오름차순<br>범위의 모든 날짜가 한 항목씩 |
| `daily[].date` | `string` | KST 날짜 |
| `daily[].signups` | `object` | 그날 생성된 회원 수<br>재가입으로 연동을 넘긴 예전 계정 행은 뺌 |
| `daily[].signups.total` | `integer` | 전체<br>로그인 경로가 구글과 카카오뿐이라 `google`과 `kakao`의 합과 같음 |
| `daily[].signups.google` | `integer` | 첫 소셜 연동이 구글 |
| `daily[].signups.kakao` | `integer` | 첫 소셜 연동이 카카오 |
| `daily[].cumulativeSignups` | `integer` | 서비스 시작부터 그날까지 생성된 회원 수<br>범위 첫날 전의 가입과 탈퇴 회원을 포함한 전체 누계이며 `signups`와 같이 예전 계정 행은 뺌<br>대시보드 요약의 `members.total`보다 예전 계정 행 수만큼 작음 |
| `daily[].migratedFromGuest` | `integer` | 그날 생성된 회원 중 게스트 데이터를 이관한 회원 수<br>예전 계정 행은 뺌 |
| `daily[].signupsByPlatform` | `object / null` | 그날 가입 커스텀 이벤트의 고유 사용자 수<br>구글과 카카오로 모두 가입한 사람도 한 번<br>플랫폼 묶음 구조의 정수<br>`pendingDates`의 날짜는 `null` |
| `daily[].newVisitorsByPlatform` | `object / null` | 가입 전환율의 분모인 그날 신규 방문자 수<br>사용자 활동의 `newVisitors`와 같은 값<br>플랫폼 묶음 구조의 정수<br>`pendingDates`의 날짜는 `null` |
| `daily[].signupRate` | `object / null` | 가입 전환율<br>`signupsByPlatform`을 `newVisitorsByPlatform`으로 나눈 0 이상의 값<br>플랫폼 묶음 구조의 소수이고 분모가 0인 플랫폼은 `null`<br>그날 처음 기록된 사용자가 아닌 사람의 가입도 분자에 들어 1을 넘을 수 있음<br>`pendingDates`의 날짜는 `null` |

- 플랫폼별 가입 수는 회원을 세는 지표라 게스트와 회원 구분이 없다.
- `signupsByPlatform`, `newVisitorsByPlatform`, `signupRate`는 같은 날짜에 함께 값이 있거나 함께 `null`이다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 대시보드 차트와 같음 |

- 분석 도구를 쓸 수 없거나 플랫폼 조회가 5초 안에 끝나지 않아도 실패로 응답하지 않는다. 플랫폼별 가입 수를 받지 못한 날짜는 `pendingDates`에 넣고 DB 값을 기다리지 않고 응답한다.

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/users/signups?from=2026-10-26&to=2026-10-27
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

오늘 날짜인 10-27의 플랫폼별 가입 수를 아직 받지 못한 응답이다.

```json
{
  "asOf": "2026-10-27T05:10:00Z",
  "from": "2026-10-26",
  "to": "2026-10-27",
  "platformAsOf": "2026-10-27T04:58:00Z",
  "pendingDates": ["2026-10-27"],
  "daily": [
    {
      "date": "2026-10-26",
      "signups": { "total": 24, "google": 15, "kakao": 9 },
      "cumulativeSignups": 1830,
      "migratedFromGuest": 11,
      "signupsByPlatform": { "all": 22, "web": 7, "android": 15 },
      "newVisitorsByPlatform": { "all": 410, "web": 380, "android": 31 },
      "signupRate": { "all": 0.0537, "web": 0.0184, "android": 0.4839 }
    },
    {
      "date": "2026-10-27",
      "signups": { "total": 9, "google": 6, "kakao": 3 },
      "cumulativeSignups": 1839,
      "migratedFromGuest": 4,
      "signupsByPlatform": null,
      "newVisitorsByPlatform": null,
      "signupRate": null
    }
  ]
}
```

</details>

<br>

### 4-2-29 전환 퍼널

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/conversion/funnels/{funnel}` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 경로와 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `funnel` | 경로 | 필수 | `web-first-visit`, `android-first-visit`, `first-visit-activation`, `login-signup`, `android-activation`, `web-to-android`, `story-creation`, `creation-entry-chat`, `story-detail-chat`, `guest-limit-login` |
| `platform` | `string` | 선택 | `web`, `android`<br>`first-visit-activation`, `login-signup`, `story-creation`, `creation-entry-chat`, `story-detail-chat`, `guest-limit-login`에서만 받으며 기본 `web`<br>`web-first-visit`, `android-first-visit`, `android-activation`, `web-to-android`는 플랫폼이 정해져 있어 받지 않음 |
| `storyId` | `string` | 선택 | `story-detail-chat`에서만<br>지정하면 1단계와 2단계를 그 스토리로 한정, 생략하면 모든 스토리 |
| `from`, `to` | `string` | 선택 | 분석 지표와 같은 규칙<br>기간은 1일 이상 31일 이하 |
| `days` | `integer` | 선택 | `7`, `30` 중 하나<br>`from`, `to`와 함께 보내면 400 |

- 셋 다 없으면 오늘을 포함한 최근 7일이다. 단계 정의는 제품 제약에 있다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string` | 범위 값을 분석 도구에서 받은 시각 |
| `from`, `to` | | 분석 지표와 같음 |
| `funnel` | `string` | 요청한 퍼널 |
| `platform` | `string / null` | 적용한 플랫폼<br>`android-activation`은 `android`, `web-to-android`는 단계마다 플랫폼이 달라 `null` |
| `storyId` | `string / null` | 적용한 대상 스토리 |
| `steps` | `object[]` | 단계 순서 |
| `steps[].event` | `string` | 단계의 이벤트 이름<br>`guest-limit-login`의 마지막 단계는 로그인 커스텀 이벤트 단계라 `login_succeeded`<br>가입 커스텀 이벤트 단계는 `signup_succeeded`, 핵심 활동 커스텀 이벤트 단계는 `core_activity` |
| `steps[].turnNumber` | `integer / null` | 채팅 메시지 전송 단계의 턴 번호<br>그 외 `null` |
| `steps[].minTurnNumber` | `integer / null` | 턴 번호가 이 값 이상인 채팅 메시지 전송 단계의 하한<br>`first-visit-activation`의 3단계는 5, 그 외 `null` |
| `steps[].platform` | `string / null` | 단계마다 플랫폼이 다른 `web-to-android`에서 그 단계의 플랫폼 `web`, `android`<br>그 외 `null` |
| `steps[].users` | `integer` | 전환 창 1일 안에 이 단계까지 순서대로 도달한 고유 사용자 수 |

- `web-to-android`의 전환 창은 30일이라 `to`에서 30일이 지나기 전의 범위는 마지막 단계가 아직 다 차지 않는다. 서버는 그 범위를 확정하지 않고 하루 한 번 다시 받는다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 분석 지표와 같은 기간 오류, 31일 초과, 허용하지 않는 `funnel`과 `platform`과 `days`, 퍼널이 받지 않는 쿼리 지정, `storyId`가 UUID 형식이 아님 |
| 503 | `SERVICE_UNAVAILABLE` | 분석 지표와 같음 |

<br>

### 4-2-30 채팅 턴 도달률

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/conversion/turn-reach` |
| 인증 | 관리자 |
| 성공 | 200 |

`segments`와 `guestToMember`는 서버 DB로 계산하고 팀 계정 제외 목록을 적용한다. `platforms`는 Amplitude의 AI 응답 성공 이벤트로 계산하며 팀 계정을 제외하지 않는다. 플랫폼 묶음은 신규 가입자와 같은 국내 조건 안의 웹과 앱 조회다. `platforms`는 채팅 생성일이 아니라 턴을 저장한 날짜로 세고 분모가 1턴 응답 수라 `segments`와 비율의 뜻이 다르다. 정의는 제품 제약에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약))

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to`, `days` | | 선택 | 신규 가입자와 같음 |
| `segment` | `string` | 선택 | `all`, `guest`, `member`<br>기본 `all`<br>`platforms`만 이 값으로 거름<br>`guest`는 이벤트에 회원 식별자가 없는 턴, `member`는 있는 턴 |

- 셋 다 없으면 오늘을 포함한 최근 30일이다. 플랫폼 값의 저장과 `pendingDates`, 재요청은 신규 가입자와 같다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to` | | 대시보드 차트와 같음 |
| `segment` | `string` | 적용한 `segment` |
| `platformAsOf`, `pendingDates` | | 신규 가입자와 같음<br>대상은 `platforms` |
| `segments` | `object[]` | `all`, `guest`, `member` 세 항목<br>범위 안에 생성된 삭제되지 않은 채팅을 현재 소유자 유형으로 나눔<br>`segment` 쿼리와 무관하게 세 항목 모두 |
| `segments[].segment` | `string` | `all`, `guest`, `member` |
| `segments[].chats` | `integer` | 채팅 수 |
| `segments[].reached` | `object[]` | 기준 턴 1, 2, 3, 4, 5, 6, 7, 10, 15, 20, 30, 50의 항목 12개, 오름차순<br>턴 수 분포 13구간에서 0을 뺀 구간 시작 턴 |
| `segments[].reached[].turn` | `integer` | 기준 턴 |
| `segments[].reached[].chats` | `integer` | 현재 턴이 기준 이상인 채팅 수 |
| `segments[].reached[].rate` | `number` | `chats`로 나눈 0~1<br>채팅이 없으면 0 |
| `guestToMember` | `object` | 게스트로 시작해 회원이 된 뒤 이어 간 채팅 |
| `guestToMember.chatsReached5` | `integer` | 소유 회원의 게스트 이관 시각보다 먼저 생성됐고 현재 턴이 5 이상인 채팅 수 |
| `guestToMember.chatsReached6` | `integer` | 그중 현재 턴이 6 이상인 채팅 수 |
| `guestToMember.rate` | `number` | `chatsReached6`을 `chatsReached5`로 나눈 0~1<br>0이면 0 |
| `platforms` | `object[] / null` | `all`, `web`, `android` 세 항목<br>`pendingDates`를 뺀 날짜의 합<br>준비된 날짜가 없으면 `null` |
| `platforms[].platform` | `string` | `all`, `web`, `android`<br>`all`은 `web`과 `android`의 합 |
| `platforms[].chats` | `integer` | 1턴 응답을 저장한 채팅 수<br>턴 번호 1인 성공 이벤트 수 |
| `platforms[].reached` | `object[]` | `segments[].reached`와 같은 기준 턴 12개, 오름차순 |
| `platforms[].reached[].turn` | `integer` | 기준 턴 |
| `platforms[].reached[].chats` | `integer` | 기준 턴의 응답을 저장한 채팅 수<br>턴 번호가 기준 턴인 성공 이벤트 수 |
| `platforms[].reached[].rate` | `number` | `platforms[].chats`로 나눈 0 이상의 값<br>범위 전에 1턴을 저장한 채팅이 범위 안에서 기준 턴에 닿으면 1을 넘을 수 있음<br>`platforms[].chats`가 0이면 0 |

<br>

**3. 실패 응답**

신규 가입자와 같다. 허용하지 않는 `segment`도 400이다.

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/conversion/turn-reach?days=7&segment=member
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

예시에는 `segments`와 `platforms`의 첫 항목과 기준 턴 두 개만 표시했다.

```json
{
  "asOf": "2026-10-27T05:10:00Z",
  "from": "2026-10-21",
  "to": "2026-10-27",
  "segment": "member",
  "platformAsOf": "2026-10-27T05:02:00Z",
  "pendingDates": [],
  "segments": [
    { "segment": "all", "chats": 812, "reached": [{ "turn": 1, "chats": 640, "rate": 0.79 }, { "turn": 5, "chats": 301, "rate": 0.37 }] }
  ],
  "guestToMember": { "chatsReached5": 40, "chatsReached6": 31, "rate": 0.78 },
  "platforms": [
    { "platform": "all", "chats": 402, "reached": [{ "turn": 1, "chats": 402, "rate": 1.0 }, { "turn": 5, "chats": 233, "rate": 0.58 }] }
  ]
}
```

</details>

<br>

### 4-2-31 기능 사용과 안정성

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/quality/client` |
| 인증 | 관리자 |
| 성공 | 200 |

기능과 품질 메뉴의 Amplitude 지표와 서버 DB의 간편 제작 실패율이다. 간편 제작 실패율은 팀 계정 제외 목록을 적용하고 `platform`, `segment`, `pendingDates`와 무관하다.

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `platform` | `string` | 선택 | `all`, `web`, `android`<br>기본 `all`<br>`web`은 웹 조건, `android`는 앱 조건, `all`은 전체 조건(웹이나 앱)<br>`all`의 사용자 수는 웹과 앱을 함께 쓴 사람을 한 번 셈 |
| `segment` | `string` | 선택 | `all`, `guest`, `member`<br>기본 `all`<br>`guest`는 회원 식별자가 없는 이벤트, `member`는 있는 이벤트 |
| `from`, `to` | `string` | 선택 | 분석 지표와 같은 규칙<br>기간은 1일 이상 366일 이하 |
| `days` | `integer` | 선택 | `7`, `30` 중 하나<br>`from`, `to`와 함께 보내면 400 |

- 셋 다 없으면 오늘을 포함한 최근 30일이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to`, `pendingDates` | | 분석 지표와 같음 |
| `platform` | `string` | 적용한 플랫폼 |
| `segment` | `string` | 적용한 `segment` |
| `daily` | `object[]` | 날짜 오름차순<br>`pendingDates`의 날짜는 없음 |
| `daily[].date` | `string` | KST 날짜 |
| `daily[].messagesByInputMode` | `object` | 채팅 메시지 전송 횟수<br>`choice`, `plain`, `block`, `unknown`의 정수<br>`unknown`은 전송 합계에서 나머지 셋을 뺀 값 |
| `daily[].streamErrors` | `integer` | 스트림 오류 표시 횟수 |
| `daily[].streamErrorRate` | `number / null` | `streamErrors`를 전송 합계로 나눈 0 이상의 값<br>두 이벤트의 단순 건수 비율이라 한 전송에 오류가 여러 번 표시되면 1을 넘을 수 있음<br>전송이 0이면 `null` |
| `daily[].users` | `object` | 그날 이벤트가 있었던 고유 사용자 수 |
| `daily[].users.chatLoadError` | `integer` | 채팅 불러오기 오류 |
| `daily[].users.storyListLoadError` | `integer` | 스토리 목록 불러오기 오류 |
| `daily[].users.creditShortage` | `integer` | 이프 부족 안내 |
| `daily[].users.creditChargeViewed` | `integer` | 충전 화면 조회 |
| `daily[].users.attendanceClicked` | `integer` | 충전 화면의 출석 버튼 클릭 |
| `daily[].users.inviteSucceeded` | `integer` | 초대 코드 입력 성공 |
| `daily[].activity` | `object` | 활동량 |
| `daily[].activity.aiResponses` | `integer` | 저장한 AI 응답 수<br>AI 응답 성공 이벤트 가운데 재생성이 아닌 것의 합계 |
| `daily[].activity.simpleCompletions` | `integer` | 간편 제작 완료 이벤트 수 |
| `daily[].activity.generalSubmissions` | `integer` | 일반 제작 제출 이벤트 수<br>검수 승인이 아니라 제출 접수 |
| `daily[].activity.coreActiveUsers` | `integer` | 핵심 활동 고유 사용자 수 |
| `daily[].activity.messagesPerCoreUser` | `number / null` | 채팅 메시지 전송 합계를 `coreActiveUsers`로 나눈 값<br>`coreActiveUsers`가 0이면 `null` |
| `daily[].activity.simpleCompletionsPerCoreUser` | `number / null` | `simpleCompletions`를 `coreActiveUsers`로 나눈 값<br>`coreActiveUsers`가 0이면 `null` |
| `storyCompletion` | `object[]` | 서버 DB의 간편 제작 완성 요청<br>날짜 오름차순<br>범위의 모든 날짜가 한 항목씩 |
| `storyCompletion[].date` | `string` | KST 날짜 |
| `storyCompletion[].requests` | `integer` | 그날 받아 완료나 실패로 끝난 요청 수 |
| `storyCompletion[].failed` | `integer` | 그중 실패로 끝난 요청 수 |
| `storyCompletion[].failureRate` | `number / null` | `failed`를 `requests`로 나눈 0~1<br>`requests`가 0이면 `null` |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 분석 지표와 같은 기간 오류, 366일 초과, 허용하지 않는 `platform`과 `days`와 `segment` |
| 503 | `SERVICE_UNAVAILABLE` | 분석 지표와 같음 |

<br>

### 4-2-32 채팅 옵션 비중

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/quality/chat-options` |
| 인증 | 관리자 |
| 성공 | 200 |

`chats`, `withPersona`, `byModel`, `turnsByModel`은 서버 DB로 계산하고 팀 계정 제외 목록을 적용한다. 채팅 시작 사용자 수와 플랫폼별 모델 턴 수는 Amplitude 이벤트로 계산하며 팀 계정을 제외하지 않는다. 플랫폼 묶음은 신규 가입자와 같은 국내 조건 안의 웹과 앱 조회다. `all`은 채팅 시작 사용자 수가 전체 조건 조회 값이고 모델 턴 수가 둘의 합이다. 채팅 수, 페르소나 채팅 수, 채팅 모델별 채팅 수는 채팅 생성과 그 모델을 알리는 이벤트가 없어 플랫폼으로 나누지 않는다. 정의는 제품 제약에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약))

**1. 쿼리**

채팅 턴 도달률과 같다. `segment`는 채팅 시작 사용자 수와 플랫폼별 모델 턴 수만 거른다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to` | | 대시보드 차트와 같음 |
| `segment` | `string` | 적용한 `segment` |
| `platformAsOf`, `pendingDates` | | 신규 가입자와 같음<br>대상은 `daily[]`의 플랫폼 값 |
| `daily` | `object[]` | 날짜 오름차순<br>범위의 모든 날짜가 한 항목씩<br>DB 값은 범위 안에 생성된 삭제되지 않은 채팅 |
| `daily[].date` | `string` | KST 날짜 |
| `daily[].chats` | `integer` | 채팅 수 |
| `daily[].withPersona` | `integer` | 페르소나 이름 스냅샷이 있는 채팅 수 |
| `daily[].byModel` | `object` | 채팅 모델 코드별 채팅 수<br>키는 채팅의 현재 선택 모델 `chat_models.code`<br>모델을 바꾼 채팅은 바꾼 모델로 셈 |
| `daily[].turnsByModel` | `object` | 청구 모델 코드별 턴 수<br>그날 생성된 AI 응답 메시지를 메시지에 기록한 청구 모델 코드로 묶은 수이며 재생성 판본은 세지 않음<br>게스트 턴은 채팅 모델과 무관하게 `LITE`<br>모델 기록 전의 메시지는 키 `UNRECORDED`<br>`daily[]`의 다른 값과 달리 채팅의 생성일과 삭제 여부를 보지 않아 모든 키의 합이 대시보드 차트의 그날 `turns`와 같음<br>턴이 없는 키는 없음 |
| `daily[].chatStarters` | `object / null` | 그날 채팅 시작 버튼을 누른 고유 사용자 수<br>주인공 종류와 무관<br>플랫폼 묶음 구조이고 `all`은 전체 조건 조회 값<br>`pendingDates`의 날짜는 `null` |
| `daily[].chatStartersByPersonaType` | `object / null` | 주인공 종류별 그날 채팅 시작 버튼을 누른 고유 사용자 수<br>키는 `default`(기본 주인공), `persona`(페르소나), `none`(주인공 종류 정보 없음)이고 값은 플랫폼 묶음 구조<br>한 사용자가 두 종류로 시작하면 두 키에 모두 들어 키의 합이 `chatStarters`보다 클 수 있음<br>`pendingDates`의 날짜는 `null` |
| `daily[].platformTurnsByModel` | `object / null` | 그날 저장한 AI 응답 턴 수를 청구 모델 코드와 플랫폼으로 나눈 값<br>키는 `chat_models.code`, 값은 플랫폼 묶음 구조<br>재생성은 세지 않음<br>`pendingDates`의 날짜는 `null` |

- 페르소나 시작 사용자 비율은 관리자 페이지가 날짜마다 `chatStartersByPersonaType.persona`를 `chatStarters`로 나눠 만든다. 버튼을 누른 사용자 수라 `withPersona`를 `chats`로 나눈 값과 다를 수 있다.
- `platformTurnsByModel`의 키에는 모델 기록 전 `UNRECORDED`가 없고 턴이 0인 모델도 키가 있다.

<br>

**3. 실패 응답**

채팅 턴 도달률과 같다.

<br>

### 4-2-33 AI 비용

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/quality/ai-cost` |
| 인증 | 관리자 |
| 성공 | 200 |

금액은 Langfuse가 모델 설정의 단가로 계산한 비용을 Metrics API로 받아 원화로 바꾼다. 호출 수와 토큰 수는 서버 DB의 AI 호출 기록으로 센다. 실시간 이미지는 설정 파일의 장당 원가로 계산한다. 팀 계정 제외 목록은 적용하지 않는다. ([4-1-23 AI 비용의 Langfuse 조회](4-1-PIPELINES.md#4-1-23-ai-비용의-langfuse-조회))

**1. 쿼리**

신규 가입자와 같다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to` | | 대시보드 차트와 같음<br>`asOf`는 응답에 쓴 Langfuse 값을 받은 시각 가운데 가장 이른 시각<br>Langfuse 값을 하나도 쓰지 않았으면 `asOf`는 `null` |
| `pendingDates` | `string[]` | 보관 기간 안에서 Langfuse 값을 아직 받지 못해 `daily`의 비용을 비운 KST 날짜<br>오름차순, 보관 기간 밖 날짜는 넣지 않음 |
| `expiredDates` | `string[]` | Langfuse 보관 기간이 지나 조회하지 않았고 저장 값도 없어 `daily`의 비용을 비운 KST 날짜<br>오름차순 |
| `retentionDays` | `integer` | Langfuse 보관 일수<br>설정값 |
| `retentionStartDate` | `string` | Langfuse에 조회하는 가장 이른 KST 날짜<br>오늘에서 (`retentionDays` − 2)일 전 |
| `currency` | `string` | 항상 `KRW` |
| `usdKrwRate` | `number` | Langfuse 비용(USD)을 원화로 바꾼 환율<br>설정값 |
| `chatImageUnitCostKrw` | `number` | 실시간 이미지 장당 원가<br>설정값이며 초기값 48 |
| `daily` | `object[]` | 날짜 오름차순<br>범위의 모든 날짜가 한 항목씩 |
| `daily[].date` | `string` | KST 날짜 |
| `daily[].byFeature` | `object[]` | 기능과 모델 조합마다 한 항목<br>AI 호출 기록과 Langfuse 가운데 한쪽에만 있는 조합도 항목 |
| `daily[].byFeature[].feature` | `string` | `chat_response`, `choice_generation`, `chat_image`, `storyline_generation`, `story_completion`, `chat_compact` |
| `daily[].byFeature[].model` | `string / null` | 모델 이름<br>AI 호출 기록의 `model`과 Langfuse의 모델 이름이 같으면 한 항목<br>모델이 없는 기록은 `null` 항목 하나로 묶음 |
| `daily[].byFeature[].calls` | `integer` | AI 호출 기록의 성공 호출 수<br>Langfuse에만 있는 조합은 0 |
| `daily[].byFeature[].callsWithoutTokens` | `integer` | 성공 호출 중 입력이나 출력 토큰 수가 없는 호출 수<br>`chat_image`는 항상 0 |
| `daily[].byFeature[].inputTokens`, `outputTokens` | `integer` | AI 호출 기록의 토큰 합<br>토큰 수가 없는 호출은 0으로 더함<br>`chat_image`는 항상 0 |
| `daily[].byFeature[].costKrw` | `number / null` | Langfuse 비용 합 × `usdKrwRate`<br>Langfuse에 그 조합의 비용이 없으면 `null`<br>그 날짜가 `pendingDates`나 `expiredDates`에 있으면 `null`<br>`chat_image`는 `calls × chatImageUnitCostKrw`이고 Langfuse를 쓰지 않음 |
| `unmapped` | `object[]` | 기능 매핑 표에 없는 Langfuse 추적 이름의 범위 비용 |
| `unmapped[].traceName` | `string` | Langfuse 추적 이름 |
| `unmapped[].costKrw` | `number` | 범위 비용 합 × `usdKrwRate` |
| `totals` | `object` | 범위 합계 |
| `totals.costKrw` | `number` | `byFeature`의 `costKrw`가 `null`이 아닌 항목과 `unmapped`의 합<br>`pendingDates`와 `expiredDates`의 날짜는 실시간 이미지 비용만 더해짐 |
| `totals.costPerTurnKrw` | `number / null` | `chat_response`, `choice_generation`, `chat_compact` 항목의 `costKrw` 합을 `chat_response` 성공 호출 수로 나눔<br>분모는 모델과 비용 유무와 무관한 AI 호출 기록의 호출 수이며 `pendingDates`와 `expiredDates` 날짜의 호출은 뺌<br>호출이 0이면 `null` |
| `totals.costPerStoryKrw` | `number / null` | `storyline_generation`과 `story_completion` 항목의 `costKrw` 합을 `story_completion` 성공 호출 수로 나눔<br>분모는 `costPerTurnKrw`와 같은 규칙<br>호출이 0이면 `null` |
| `unpricedModels` | `string[]` | 범위 안에 Langfuse 사용량(토큰 합)은 있으나 비용 합이 0인 모델 이름<br>단가가 없는지, 정상 0원인지, 일부 관측의 비용이 빠졌는지는 구별하지 않음<br>이름은 호환을 위해 유지 |

- 비용은 Langfuse가 입력, 출력, 캐시 입력 토큰을 모델 설정의 단가로 계산한 값이다. 서버는 단가를 갖지 않는다.
- 금액에는 실패한 AI 호출 과정에서 생긴 관측 비용도 들어간다. 호출 수, 토큰 수, 원가의 분모는 성공한 AI 호출 기록이다.
- 간편 제작의 표지와 인물 이미지 생성 비용은 `스토리 컴파일` 추적에 들어 있어 `story_completion`에 포함된다. 채팅의 실시간 이미지 생성 관측은 Langfuse 합에서 빼고 장당 원가로 더한다.
- 대화 요약(`chat_compact`)은 AI 요약 응답에 `meta`가 없어 AI 호출 기록에 모델과 토큰 수가 없다. 호출 수는 모델 `null` 항목에 모이고 그 항목의 `callsWithoutTokens`는 `calls`와 같다. 금액은 Langfuse가 모델 이름별로 주므로 모델 이름 항목에 `calls` 0으로 실린다. ([CHAT 5-4-4 AI 호출 기록](../../CHAT/BACKEND/5-4-OBSERVABILITY.md#5-4-4-ai-호출-기록))
- 실시간 이미지는 턴당 원가와 스토리당 원가에 넣지 않으므로 `totals.costKrw`는 두 원가의 분자 합보다 클 수 있다. 장당 원가 48원인 날 성공 3장은 144원이다.
- 호출 수는 서버 기록이고 비용은 Langfuse 기록이라 한쪽이 수집에 실패하면 두 값의 대응이 어긋날 수 있다.
- 보관 기간 밖 날짜는 서버가 미리 저장한 값으로만 응답한다. 배치가 날짜마다 확정 값을 저장하므로 배포 뒤 날짜는 보관 기간이 지나도 값이 남는다.
- 범위의 모든 날짜가 `retentionStartDate` 전이면 Langfuse를 호출하지 않으므로 설정 없음, 쿨다운, 호출 제한과 무관하게 200이다. 저장 값이 없는 날짜는 `expiredDates`다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 대시보드 차트와 같음 |
| 503 | `SERVICE_UNAVAILABLE` | Langfuse 키나 환경 설정이 비어 있음<br>Langfuse 호출 실패, 호출 제한, 시간 초과, 응답 형식 오류, 실패 뒤 쿨다운 중이고 범위에 저장 값이 하나도 없음<br>두 경우 모두 범위의 모든 날짜가 `retentionStartDate` 전이면 503이 아니라 200 |

<br>

### 4-2-34 인프라 지표

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/infra/metrics` |
| 인증 | 관리자 |
| 성공 | 200 |

서버가 태스크 역할로 CloudWatch와 ECS를 불러 운영 AWS 리소스의 핵심 지표를 응답한다. 앱 지표와 로그와 트레이스는 OpenSearch UI가 맡고 이 응답에 넣지 않는다. ([4-1-21 인프라 지표](4-1-PIPELINES.md#4-1-21-인프라-지표))

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to` | `string` | 선택 | KST 날짜 `YYYY-MM-DD`, 양 끝 포함<br>둘 다 주거나 둘 다 생략<br>`to`는 오늘 이하, 기간은 1일 이상 31일 이하 |

- 둘 다 없으면 KST 오늘 하루다.
- 조회 시작은 `from`의 KST 자정이고 끝은 `to` 다음 날 KST 자정과 현재 시각 가운데 이른 쪽이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string` | CloudWatch와 ECS에서 값을 받은 시각<br>캐시로 응답하면 그 캐시를 만든 시각 |
| `from`, `to` | `string` | 적용한 KST 날짜 |
| `periodSeconds` | `integer` | 점 하나의 집계 간격(초)<br>기간 2일 이하 `300`, 7일 이하 `900`, 그보다 길면 `3600`<br>조회 시작이 63일보다 오래되면 기간과 무관하게 `3600` |
| `ecs` | `object / null` | ECS 서비스 지표<br>클러스터나 서비스 설정이 비어 있으면 `null` |
| `ecs.services` | `object[]` | 설정한 서비스 순서 |
| `ecs.services[].name` | `string` | 설정의 표시 키<br>운영은 `server`, `ai`, `notification` |
| `ecs.services[].runningTasks` | `integer` | 조회 시각(`asOf`)에 실행 중인 태스크 수 |
| `ecs.services[].desiredTasks` | `integer` | 조회 시각의 목표 태스크 수 |
| `ecs.services[].pendingTasks` | `integer` | 조회 시각에 시작 중인 태스크 수 |
| `ecs.services[].cpu` | 점 목록 | `AWS/ECS` `CPUUtilization` 평균(%) |
| `ecs.services[].memory` | 점 목록 | `AWS/ECS` `MemoryUtilization` 평균(%) |
| `ecs.services[].cpuMax` | 점 목록 | `CPUUtilization` 최댓값(%)<br>구간 안에서 서비스의 태스크 가운데 가장 높은 값 |
| `ecs.services[].memoryMax` | 점 목록 | `MemoryUtilization` 최댓값(%)<br>구간 안에서 서비스의 태스크 가운데 가장 높은 값 |
| `alb` | `object / null` | ALB 지표<br>설정이 비어 있으면 `null` |
| `alb.requests` | 점 목록 | `AWS/ApplicationELB` `RequestCount` 합(회) |
| `alb.elb5xx` | 점 목록 | `HTTPCode_ELB_5XX_Count` 합(회)<br>ALB가 생성한 5xx이며 대상이 반환한 5xx는 제외 |
| `alb.target5xx` | 점 목록 | `HTTPCode_Target_5XX_Count` 합(회)<br>서버가 돌려준 5xx |
| `alb.responseTimeP95Ms` | 점 목록 | `TargetResponseTime`의 `p95`(밀리초) |
| `rds` | `object / null` | RDS 인스턴스 지표<br>설정이 비어 있으면 `null` |
| `rds.cpu` | 점 목록 | `AWS/RDS` `CPUUtilization` 평균(%) |
| `rds.freeStorageBytes` | 점 목록 | `FreeStorageSpace` 최솟값(바이트) |
| `rds.connections` | 점 목록 | `DatabaseConnections` 최댓값(개) |
| `rds.readLatencyMs` | 점 목록 | `ReadLatency` 평균(밀리초) |
| `rds.writeLatencyMs` | 점 목록 | `WriteLatency` 평균(밀리초) |
| `redis` | `object / null` | ElastiCache Redis 노드 지표<br>설정이 비어 있으면 `null` |
| `redis.nodes` | `object[]` | 설정한 노드 순서 |
| `redis.nodes[].id` | `string` | 캐시 클러스터 ID |
| `redis.nodes[].cpu` | 점 목록 | `AWS/ElastiCache` `EngineCPUUtilization` 평균(%) |
| `redis.nodes[].memory` | 점 목록 | `DatabaseMemoryUsagePercentage` 평균(%) |
| `redis.nodes[].connections` | 점 목록 | `CurrConnections` 최댓값(개) |
| `opensearch` | `object / null` | OpenSearch 도메인 지표<br>도메인이나 계정 ID 설정이 비어 있으면 `null` |
| `opensearch.freeStorageBytes` | 점 목록 | `AWS/ES` `FreeStorageSpace` 최솟값(바이트)<br>CloudWatch 값이 MB라 1,048,576을 곱함 |
| `opensearch.jvmMemoryPressure` | 점 목록 | `JVMMemoryPressure` 최댓값(%) |

점 목록은 다음 구조의 배열이다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `[].at` | `string` | 집계 구간이 시작하는 시각 |
| `[].value` | `number` | 그 구간의 값 |

- 점은 시각 오름차순이다.
- 건수 지표(`alb.requests`, `alb.elb5xx`, `alb.target5xx`)는 CloudWatch가 값이 없는 구간을 빼고 주므로 서버가 조회 범위의 모든 구간을 0으로 채운다. 나머지 지표는 CloudWatch가 값을 준 구간만 담고 빈 구간을 채우지 않는다.
- 태스크 수는 조회 시각(`asOf`) 기준 값이라 기간과 무관하다.
- 리소스 이름과 계정 ID는 응답에 넣지 않는다. Redis 노드만 노드를 구분하려고 캐시 클러스터 ID를 넣는다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 한쪽만 있는 `from` 또는 `to`, 날짜 형식 오류, `from`이 `to`보다 뒤, `to`가 오늘 이후, 31일 초과 |
| 503 | `SERVICE_UNAVAILABLE` | 리소스 설정이 모두 비어 있음<br>CloudWatch나 ECS 호출 실패, 권한 거부, 호출 제한, 불완전하거나 오류인 질의 결과, 시간 초과, 실패 뒤 쿨다운 중이거나 다른 요청이 갱신 중인데 캐시도 없음 |

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/infra/metrics?from=2026-10-23&to=2026-10-23
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

예시에는 점 목록마다 점 1~2개만 표시하고 `ai`와 `notification` 서비스, 두 번째 Redis 노드를 줄였다.

```json
{
  "asOf": "2026-10-23T01:12:40Z",
  "from": "2026-10-23",
  "to": "2026-10-23",
  "periodSeconds": 300,
  "ecs": {
    "services": [
      {
        "name": "server",
        "runningTasks": 2,
        "desiredTasks": 2,
        "pendingTasks": 0,
        "cpu": [{ "at": "2026-10-22T15:00:00Z", "value": 7.4 }, { "at": "2026-10-22T15:05:00Z", "value": 8.1 }],
        "memory": [{ "at": "2026-10-22T15:00:00Z", "value": 41.2 }, { "at": "2026-10-22T15:05:00Z", "value": 41.5 }],
        "cpuMax": [{ "at": "2026-10-22T15:00:00Z", "value": 21.0 }, { "at": "2026-10-22T15:05:00Z", "value": 12.3 }],
        "memoryMax": [{ "at": "2026-10-22T15:00:00Z", "value": 44.0 }, { "at": "2026-10-22T15:05:00Z", "value": 44.1 }]
      }
    ]
  },
  "alb": {
    "requests": [{ "at": "2026-10-22T15:00:00Z", "value": 312 }, { "at": "2026-10-22T15:05:00Z", "value": 0 }],
    "elb5xx": [{ "at": "2026-10-22T15:00:00Z", "value": 0 }, { "at": "2026-10-22T15:05:00Z", "value": 0 }],
    "target5xx": [{ "at": "2026-10-22T15:00:00Z", "value": 1 }, { "at": "2026-10-22T15:05:00Z", "value": 0 }],
    "responseTimeP95Ms": [{ "at": "2026-10-22T15:00:00Z", "value": 182.0 }]
  },
  "rds": {
    "cpu": [{ "at": "2026-10-22T15:00:00Z", "value": 4.9 }],
    "freeStorageBytes": [{ "at": "2026-10-22T15:00:00Z", "value": 18253611008 }],
    "connections": [{ "at": "2026-10-22T15:00:00Z", "value": 21 }],
    "readLatencyMs": [{ "at": "2026-10-22T15:00:00Z", "value": 0.8 }],
    "writeLatencyMs": [{ "at": "2026-10-22T15:00:00Z", "value": 1.6 }]
  },
  "redis": {
    "nodes": [
      {
        "id": "manyak-prod-redis-rg-001",
        "cpu": [{ "at": "2026-10-22T15:00:00Z", "value": 1.2 }],
        "memory": [{ "at": "2026-10-22T15:00:00Z", "value": 3.4 }],
        "connections": [{ "at": "2026-10-22T15:00:00Z", "value": 18 }]
      }
    ]
  },
  "opensearch": {
    "freeStorageBytes": [{ "at": "2026-10-22T15:00:00Z", "value": 6442450944 }],
    "jvmMemoryPressure": [{ "at": "2026-10-22T15:00:00Z", "value": 58.0 }]
  }
}
```

**3) 503 Response body**

```json
{
  "timestamp": "2026-10-23T01:12:40.000Z",
  "status": 503,
  "code": "SERVICE_UNAVAILABLE",
  "message": "인프라 지표를 가져올 수 없습니다.",
  "path": "/api/v1/admin/infra/metrics",
  "details": []
}
```

</details>

<br>

### 4-2-35 DB 테이블 크기

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/infra/db-tables` |
| 인증 | 관리자 |
| 성공 | 200 |

서버의 PostgreSQL 카탈로그에서 데이터베이스 크기와 테이블별 크기를 읽어 큰 순서로 응답한다. 기간과 무관한 현재 값이다. ([4-1-22 DB 테이블 크기](4-1-PIPELINES.md#4-1-22-db-테이블-크기))

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `limit` | `integer` | 선택 | 응답할 테이블 수<br>1~100, 기본 20 |

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string` | 카탈로그를 읽은 시각 |
| `databaseBytes` | `integer` | 현재 데이터베이스 전체 크기(바이트) |
| `tableCount` | `integer` | 집계 대상 테이블 수 |
| `tables` | `object[]` | `totalBytes` 내림차순, 최대 `limit`개<br>같으면 `schema`, `name` 오름차순 |
| `tables[].schema` | `string` | 스키마 이름 |
| `tables[].name` | `string` | 테이블 이름 |
| `tables[].totalBytes` | `integer` | 테이블, 인덱스, TOAST를 합한 크기 |
| `tables[].tableBytes` | `integer` | 본 테이블만의 크기 |
| `tables[].indexBytes` | `integer` | 그 테이블 인덱스의 합 |
| `tables[].estimatedRows` | `integer` | 통계가 추정한 살아 있는 행 수<br>정확한 개수가 아니며 통계 수집 전이면 0 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `limit`가 정수가 아니거나 1~100 밖 |

- DB 오류는 공통 처리를 따른다.

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/infra/db-tables?limit=2
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "asOf": "2026-10-23T01:12:40Z",
  "databaseBytes": 1288490188,
  "tableCount": 74,
  "tables": [
    { "schema": "public", "name": "chat_messages", "totalBytes": 402653184, "tableBytes": 301989888, "indexBytes": 83886080, "estimatedRows": 412380 },
    { "schema": "public", "name": "ai_call_logs", "totalBytes": 268435456, "tableBytes": 209715200, "indexBytes": 50331648, "estimatedRows": 520117 }
  ]
}
```

</details>

<br>

### 4-2-36 푸시 열람

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/campaigns/push-opens` |
| 인증 | 관리자 |
| 성공 | 200 |

관리자 캠페인과 활동 알림마다 푸시와 알림함에서 알림을 눌러 연 열람 수를 웹, 앱, 합계로 도달 회원 수와 함께 돌려준다. 열람 정의는 제품 제약에, 조회 구성과 측정 상태 판정은 처리 흐름에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약), [4-1-24 푸시 열람](4-1-PIPELINES.md#4-1-24-푸시-열람))

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to` | `string` | 선택 | 분석 지표와 같은 규칙<br>기간은 1일 이상 366일 이하 |
| `days` | `integer` | 선택 | `7`, `30` 중 하나<br>`from`, `to`와 함께 보내면 400 |

- 셋 다 없으면 오늘을 포함한 최근 7일이다.
- 웹과 앱 측정 시작일이 모두 비었거나 범위 전체가 설정된 측정 시작일보다 앞서면 분석 도구를 조회하지 않고 200으로 응답한다. 이때 `asOf`는 `null`, `pendingDates`는 빈 배열이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string / null` | 분석 지표와 같음<br>측정 구간이 없어 조회하지 않았으면 `null` |
| `pendingDates` | `string[]` | 분석 지표와 같음<br>측정 시작 전 날짜는 넣지 않고 측정 구간이 없으면 빈 배열<br>있으면 열람 수는 준비된 날짜만 더한 값이고 열람률은 그 열람 수를 전체 도달 회원 수로 나눈 값 |
| `from`, `to` | `string` | 캠페인 추이와 같음 |
| `measuredFrom` | `string / null` | 웹 측정 시작일 KST 날짜<br>설정되지 않았으면 `null` |
| `androidMeasuredFrom` | `string / null` | 앱 측정 시작일 KST 날짜<br>설정되지 않았으면 `null` |
| `campaigns` | `object[]` | 마지막 회차의 선점 시각이 범위 안인 관리자 캠페인<br>선점 시각 내림차순<br>항목마다 아래 필드와 열람 값 구조 |
| `campaigns[].campaignId` | `string` | 캠페인 공개 식별자 |
| `campaigns[].kind` | `string` | `SERVICE`, `MARKETING` |
| `campaigns[].title` | `string` | 광고 표기 없는 제목 |
| `campaigns[].noticeId` | `string / null` | 공지 알림이면 공지 공개 식별자 |
| `campaigns[].startedAt` | `string` | 마지막 회차의 선점 시각 |
| `campaigns[].deliveredMembers` | `integer` | 도달 기기가 하나 이상인 회원 수 |
| `activityFrom` | `string / null` | 활동 알림 집계 구간의 첫날<br>`from`과 가장 이른 측정 시작일 가운데 늦은 날<br>집계 구간이 없으면 `null` |
| `activityTypes` | `object[]` | `STORY_COMPLETED`, `STORY_MODERATION_COMPLETED`, `ATTENDANCE_REMINDER`, `CREDIT_EXPIRY_REMINDER` 순서의 4항목<br>항목마다 아래 필드와 열람 값 구조 |
| `activityTypes[].type` | `string` | 시나리오 식별자 |
| `activityTypes[].deliveredMembers` | `integer` | 종류와 날짜마다 중복 없이 센 도달 회원 수의 합<br>`activityFrom`이 있으면 `activityFrom`부터 `to`까지, 없으면 범위 전체 |

열람 값 구조와 채팅 전환 값 구조는 캠페인 항목, 활동 알림 항목, 캠페인 열람 응답이 함께 쓴다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `openState` | `string` | `MEASURED` 측정함<br>`BEFORE_MEASUREMENT` 측정한 플랫폼이 없음<br>`NO_LINK` 딥링크를 넣은 발송 요청이 없어 측정 불가<br>`PENDING` 발송 요청 기록이 아직 없음<br>활동 알림은 `MEASURED`, `BEFORE_MEASUREMENT`만 |
| `pushOpens` | `integer / null` | 푸시 열람 수 합계<br>`webPushOpens`와 `androidPushOpens` 가운데 `null`이 아닌 값의 합<br>`openState`가 `MEASURED`가 아니면 `null` |
| `webPushOpens` | `integer / null` | 웹 푸시 열람 수<br>웹을 측정하지 않았거나 `openState`가 `MEASURED`가 아니면 `null` |
| `androidPushOpens` | `integer / null` | 앱 푸시 열람 수<br>앱을 측정하지 않았거나 `openState`가 `MEASURED`가 아니면 `null` |
| `pushOpenRate` | `number / null` | `pushOpens`를 `deliveredMembers`로 나눈 값<br>`pushOpens`가 `null`이거나 `deliveredMembers`가 0이면 `null` |
| `inboxOpens` | `integer / null` | 알림함 열람 수 합계<br>`webInboxOpens`와 `androidInboxOpens` 가운데 `null`이 아닌 값의 합<br>`openState`가 `MEASURED`가 아니면 `null` |
| `webInboxOpens` | `integer / null` | 웹 알림함 열람 수<br>`null` 조건은 `webPushOpens`와 같음 |
| `androidInboxOpens` | `integer / null` | 앱 알림함 열람 수<br>`null` 조건은 `androidPushOpens`와 같음 |

- 플랫폼은 측정 시작일이 설정돼 있고 대상의 시작이 그 날 이후일 때 측정한다. 대상의 시작은 캠페인이면 `startedAt`의 KST 날짜, 활동 알림이면 `activityFrom`이다.
- 열람 수는 날짜별 고유 사용자 수의 합이라 열람률이 1을 넘을 수 있다. 같은 날 웹과 앱에서 모두 연 회원은 합계에 두 번 든다. 서버는 값을 자르지 않는다.
- 알림함 열람에는 열람률이 없다.
- `CREDIT_EXPIRY_REMINDER`는 알림함 사본의 딥링크도 푸시 UTM이라 알림함에서 누른 열람이 푸시 열람에 들고 알림함 열람은 0이다.

채팅 전환 값은 서버 DB만으로 세고 `openState`와 무관하다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `chattedMembers` | `integer / null` | 도달 회원 가운데 도달 뒤 24시간 안에 채팅 메시지를 보낸 회원 수<br>도달 회원 수가 0이면 `null` |
| `chattedBeforeMembers` | `integer / null` | 도달 회원 가운데 도달 전 24시간 안에 채팅 메시지를 보낸 회원 수<br>도달 회원 수가 0이면 `null` |
| `chatRate` | `number / null` | `chattedMembers`를 `deliveredMembers`로 나눈 값<br>도달 회원 수가 0이면 `null` |

- 활동 알림의 채팅 전환 값은 `deliveredMembers`와 같은 집계 구간(`activityFrom`이 있으면 `activityFrom`부터 `to`까지, 없으면 범위 전체)에서 같은 방식(종류와 날짜마다 센 수의 합)으로 센다. 측정 시작 전이어도 범위 전체의 도달 회원으로 값을 센다.
- 캠페인 열람 응답의 채팅 전환 값은 집계 범위와 무관하게 마지막 회차의 도달 회원 전체로 센다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 분석 지표와 같은 기간 오류, 366일 초과, 허용하지 않는 `days` |
| 503 | `SERVICE_UNAVAILABLE` | 분석 지표와 같은 조건 |

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/campaigns/push-opens?from=2026-10-18&to=2026-10-24
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

웹 측정 시작일이 2026-10-21, 앱 측정 시작일이 2026-10-23인 경우다. 활동 알림은 집계 구간 첫날이 앱 측정 시작일보다 앞서 앱 값이 `null`이다.

```json
{
  "asOf": "2026-10-24T05:10:00Z",
  "pendingDates": [],
  "from": "2026-10-18",
  "to": "2026-10-24",
  "measuredFrom": "2026-10-21",
  "androidMeasuredFrom": "2026-10-23",
  "campaigns": [
    {
      "campaignId": "4b7f0c2a-9d1e-4f3a-8c5b-6e2d1a0f9b37",
      "kind": "SERVICE",
      "title": "10월 25일 새벽 점검 안내",
      "noticeId": "2d5a9c1e-7b3f-4e8a-9c0d-1f2e3a4b5c6d",
      "startedAt": "2026-10-23T02:00:31Z",
      "deliveredMembers": 412,
      "chattedMembers": 97,
      "chattedBeforeMembers": 64,
      "chatRate": 0.2354,
      "openState": "MEASURED",
      "pushOpens": 79,
      "webPushOpens": 58,
      "androidPushOpens": 21,
      "pushOpenRate": 0.1917,
      "inboxOpens": 8,
      "webInboxOpens": 3,
      "androidInboxOpens": 5
    },
    {
      "campaignId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
      "kind": "MARKETING",
      "title": "가을 이벤트 안내",
      "noticeId": null,
      "startedAt": "2026-10-22T10:00:12Z",
      "deliveredMembers": 230,
      "chattedMembers": 41,
      "chattedBeforeMembers": 38,
      "chatRate": 0.1783,
      "openState": "NO_LINK",
      "pushOpens": null,
      "webPushOpens": null,
      "androidPushOpens": null,
      "pushOpenRate": null,
      "inboxOpens": null,
      "webInboxOpens": null,
      "androidInboxOpens": null
    },
    {
      "campaignId": "9e8d7c6b-5a4f-4e3d-8c2b-1a0f9e8d7c6b",
      "kind": "MARKETING",
      "title": "주말 출석 이벤트",
      "noticeId": null,
      "startedAt": "2026-10-19T03:00:05Z",
      "deliveredMembers": 198,
      "chattedMembers": 52,
      "chattedBeforeMembers": 47,
      "chatRate": 0.2626,
      "openState": "BEFORE_MEASUREMENT",
      "pushOpens": null,
      "webPushOpens": null,
      "androidPushOpens": null,
      "pushOpenRate": null,
      "inboxOpens": null,
      "webInboxOpens": null,
      "androidInboxOpens": null
    }
  ],
  "activityFrom": "2026-10-21",
  "activityTypes": [
    { "type": "STORY_COMPLETED", "deliveredMembers": 61, "chattedMembers": 44, "chattedBeforeMembers": 61, "chatRate": 0.7213, "openState": "MEASURED", "pushOpens": 27, "webPushOpens": 27, "androidPushOpens": null, "pushOpenRate": 0.4426, "inboxOpens": 6, "webInboxOpens": 6, "androidInboxOpens": null },
    { "type": "STORY_MODERATION_COMPLETED", "deliveredMembers": 11, "chattedMembers": 5, "chattedBeforeMembers": 3, "chatRate": 0.4545, "openState": "MEASURED", "pushOpens": 4, "webPushOpens": 4, "androidPushOpens": null, "pushOpenRate": 0.3636, "inboxOpens": 1, "webInboxOpens": 1, "androidInboxOpens": null },
    { "type": "ATTENDANCE_REMINDER", "deliveredMembers": 1206, "chattedMembers": 231, "chattedBeforeMembers": 188, "chatRate": 0.1915, "openState": "MEASURED", "pushOpens": 104, "webPushOpens": 104, "androidPushOpens": null, "pushOpenRate": 0.0862, "inboxOpens": 12, "webInboxOpens": 12, "androidInboxOpens": null },
    { "type": "CREDIT_EXPIRY_REMINDER", "deliveredMembers": 40, "chattedMembers": 14, "chattedBeforeMembers": 6, "chatRate": 0.35, "openState": "MEASURED", "pushOpens": 9, "webPushOpens": 9, "androidPushOpens": null, "pushOpenRate": 0.225, "inboxOpens": 0, "webInboxOpens": 0, "androidInboxOpens": null }
  ]
}
```

</details>

<br>

### 4-2-37 캠페인 첫 방문 활성화 퍼널

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/campaigns/funnels/activation` |
| 인증 | 관리자 |
| 성공 | 200 |

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `campaign` | `string` | 선택 | 캠페인 추이와 같음 |
| `from`, `to` | `string` | 선택 | 분석 지표와 같은 규칙<br>기간은 1일 이상 31일 이하 |
| `days` | `integer` | 선택 | `7`, `30` 중 하나<br>`from`, `to`와 함께 보내면 400 |

- 셋 다 없으면 오늘을 포함한 최근 7일이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string` | 범위 값을 분석 도구에서 받은 시각 |
| `from`, `to`, `campaign` | | 캠페인 추이와 같음 |
| `steps` | `object[]` | 단계 순서<br>4개 |
| `steps[].event` | `string` | 단계의 이벤트 이름<br>`_active`, `client_chat_messageInput_submitted`, `client_chat_messageInput_submitted`, `signup_succeeded`<br>`signup_succeeded`는 가입 커스텀 이벤트 단계 |
| `steps[].minTurnNumber` | `integer / null` | 턴 번호가 이 값 이상인 채팅 메시지 전송 단계의 하한<br>3단계는 5, 그 외 `null` |
| `steps[].users` | `object` | 범위 안에 처음 기록된 신규 웹 사용자 가운데 전환 창 1일 안에 이 단계까지 순서대로 도달한 고유 사용자 수<br>세그먼트 묶음 구조 |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 캠페인 추이와 같은 오류, 31일 초과 |
| 503 | `SERVICE_UNAVAILABLE` | 캠페인 추이와 같음 |

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/campaigns/funnels/activation?from=2026-10-22&to=2026-10-28
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "asOf": "2026-10-29T05:10:00Z",
  "from": "2026-10-22",
  "to": "2026-10-28",
  "campaign": "KR_META_WEB_ACTIVATION_COLD_202610",
  "steps": [
    { "event": "_active", "minTurnNumber": null, "users": { "all": 1520, "ads": 1390, "nonAds": 130 } },
    { "event": "client_chat_messageInput_submitted", "minTurnNumber": null, "users": { "all": 402, "ads": 371, "nonAds": 31 } },
    { "event": "client_chat_messageInput_submitted", "minTurnNumber": 5, "users": { "all": 133, "ads": 120, "nonAds": 13 } },
    { "event": "signup_succeeded", "minTurnNumber": null, "users": { "all": 21, "ads": 18, "nonAds": 3 } }
  ]
}
```

</details>

<br>

### 4-2-38 캠페인 누적 도달

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/campaigns/reach` |
| 인증 | 관리자 |
| 성공 | 200 |

범위 전체에서 채팅 메시지를 보낸 웹 사용자 수다. 첫 방문 활성화 퍼널과 달리 첫 방문 1일 조건이 없어 퍼널의 같은 단계보다 크다.

**1. 쿼리**

캠페인 첫 방문 활성화 퍼널과 같다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string` | 범위 값을 분석 도구에서 받은 시각 |
| `from`, `to`, `campaign` | | 캠페인 추이와 같음 |
| `chatUsers` | `object` | 범위 안에 채팅 메시지 전송이 한 번 이상인 고유 사용자 수<br>세그먼트 묶음 구조 |
| `deepChatUsers` | `object` | 범위 안에 턴 번호 5 이상의 채팅 메시지 전송이 한 번 이상인 고유 사용자 수<br>세그먼트 묶음 구조 |

<br>

**3. 실패 응답**

캠페인 첫 방문 활성화 퍼널과 같다.

<br>

### 4-2-39 캠페인 광고 소재

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/campaigns/creatives` |
| 인증 | 관리자 |
| 성공 | 200 |

광고 유입 웹 사용자를 사용자 속성 `gp:initial_utm_content`(첫 유입 광고 소재)로 나눈다. 광고 외 유입은 소재가 없어 응답에 없다.

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `campaign` | `string` | 선택 | 캠페인 추이와 같음 |
| `from`, `to` | `string` | 선택 | 분석 지표와 같은 규칙<br>기간은 1일 이상 366일 이하 |
| `days` | `integer` | 선택 | `7`, `30` 중 하나<br>`from`, `to`와 함께 보내면 400 |

- 셋 다 없으면 오늘을 포함한 최근 30일이다. 관리자 페이지는 캠페인 목록의 시작일과 종료일로 범위를 미리 채운다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `pendingDates` | | 분석 지표와 같음 |
| `from`, `to`, `campaign` | | 캠페인 추이와 같음 |
| `daily` | `object[]` | 날짜 오름차순<br>`pendingDates`의 날짜는 없음 |
| `daily[].date` | `string` | KST 날짜 |
| `daily[].signups` | `object[]` | 그날 가입 커스텀 이벤트의 소재별 고유 사용자 수<br>`users` 내림차순 |
| `daily[].signups[].content` | `string / null` | 소재 값<br>없으면 `null` |
| `daily[].signups[].users` | `integer` | 고유 사용자 수 |
| `daily[].deepChatUsers` | `object[]` | 그날 턴 번호 5 이상의 채팅 메시지 전송이 있는 소재별 고유 사용자 수<br>`daily[].signups`와 같은 구조 |
| `totals` | `object` | 준비된 날짜의 합계 |
| `totals.signups` | `object[]` | 소재별 일별 가입 수의 합<br>`daily[].signups`와 같은 구조, `users` 내림차순 |

- 5턴 이상 채팅 사용자는 날짜마다 고유 사용자라 기간 합을 주지 않는다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 캠페인 추이와 같음 |
| 503 | `SERVICE_UNAVAILABLE` | 분석 지표와 같음 |

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/campaigns/creatives?from=2026-10-22&to=2026-10-28
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

예시에는 `daily`의 날짜 항목 1개만 표시했다.

```json
{
  "asOf": "2026-10-28T05:10:00Z",
  "from": "2026-10-22",
  "to": "2026-10-28",
  "campaign": "KR_META_WEB_ACTIVATION_COLD_202610",
  "pendingDates": [],
  "daily": [
    {
      "date": "2026-10-22",
      "signups": [{ "content": "ORIGINAL_0HOSUN_VIDEO", "users": 9 }, { "content": "COMMUNITY_POST_IMAGE", "users": 6 }, { "content": null, "users": 1 }],
      "deepChatUsers": [{ "content": "ORIGINAL_0HOSUN_VIDEO", "users": 31 }, { "content": "COMMUNITY_POST_IMAGE", "users": 12 }]
    }
  ],
  "totals": {
    "signups": [{ "content": "ORIGINAL_0HOSUN_VIDEO", "users": 41 }, { "content": "COMMUNITY_POST_IMAGE", "users": 27 }, { "content": null, "users": 3 }]
  }
}
```

</details>

<br>

### 4-2-40 앱 유입

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/campaigns/app-transfer` |
| 인증 | 관리자 |
| 성공 | 200 |

웹의 앱 배너와 앱의 첫 실행 설치 경로를 본다. 앱 배너는 Android 기기로 웹을 연 사용자만 센다. 앱은 첫 실행 때 Play 설치 귀속의 UTM을 사용자 속성 `gp:initial_utm_*`로 한 번 남긴다. Play 밖에서 설치했거나 이 값을 아직 남기지 않은 사용자는 설치 경로가 없다. 캠페인 값은 받지 않는다.

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to` | `string` | 선택 | 분석 지표와 같은 규칙<br>기간은 1일 이상 366일 이하 |
| `days` | `integer` | 선택 | `7`, `30` 중 하나<br>`from`, `to`와 함께 보내면 400 |

- 셋 다 없으면 오늘을 포함한 최근 30일이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to`, `pendingDates` | | 분석 지표와 같음 |
| `daily` | `object[]` | 날짜 오름차순<br>`pendingDates`의 날짜는 없음 |
| `daily[].date` | `string` | KST 날짜 |
| `daily[].bannerShown` | `integer` | 앱 배너가 보인 Android 기기 웹 고유 사용자 수 |
| `daily[].bannerClicked` | `integer` | 앱 배너 버튼을 누른 Android 기기 웹 고유 사용자 수 |
| `daily[].bannerClickRate` | `number / null` | `bannerClicked`를 `bannerShown`으로 나눈 0 이상의 값<br>`bannerShown`이 0이면 `null` |
| `daily[].bannerNewUsers` | `integer` | 설치 매체가 앱 배너(`app_banner`)인 앱 신규 사용자 수 |
| `daily[].newUsersBySource` | `object[]` | 설치 소스(`gp:initial_utm_source`)별 앱 신규 사용자 수<br>`users` 내림차순 |
| `daily[].newUsersBySource[].source` | `string / null` | 설치 소스 값<br>없으면 `null` |
| `daily[].newUsersBySource[].users` | `integer` | 앱 신규 사용자 수 |
| `totals` | `object` | 준비된 날짜의 합계 |
| `totals.bannerNewUsers` | `integer` | 일별 합 |
| `totals.newUsersBySource` | `object[]` | 소스별 일별 합<br>`daily[].newUsersBySource`와 같은 구조, `users` 내림차순 |

- 배너 노출과 클릭 사용자는 날짜마다 고유 사용자라 기간 합을 주지 않는다.
- 배너를 누른 웹 사용자와 앱 신규 사용자는 기기 식별자가 달라 같은 사람으로 이어지지 않는다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 분석 지표와 같은 기간 오류, 366일 초과, 허용하지 않는 `days` |
| 503 | `SERVICE_UNAVAILABLE` | 분석 지표와 같음 |

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/campaigns/app-transfer?from=2026-10-28&to=2026-10-29
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

예시에는 `daily`의 날짜 항목 1개만 표시했다.

```json
{
  "asOf": "2026-10-29T05:10:00Z",
  "from": "2026-10-28",
  "to": "2026-10-29",
  "pendingDates": [],
  "daily": [
    {
      "date": "2026-10-28",
      "bannerShown": 140,
      "bannerClicked": 21,
      "bannerClickRate": 0.15,
      "bannerNewUsers": 4,
      "newUsersBySource": [{ "source": "google-play", "users": 12 }, { "source": "manyak_web", "users": 5 }, { "source": null, "users": 3 }]
    }
  ],
  "totals": {
    "bannerNewUsers": 7,
    "newUsersBySource": [{ "source": "google-play", "users": 25 }, { "source": "manyak_web", "users": 9 }, { "source": null, "users": 6 }]
  }
}
```

</details>

<br>

### 4-2-41 앱 신규 활성 사용자

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/users/app-activation` |
| 인증 | 관리자 |
| 성공 | 200 |

그날 Amplitude에 처음 기록된 앱 사용자 가운데 1일 안에 핵심 활동을 한 사용자를 센다. 핵심 활동과 신규 사용자의 정의는 제품 제약에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약))

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to` | `string` | 선택 | 분석 지표와 같은 규칙<br>기간은 1일 이상 366일 이하 |
| `days` | `integer` | 선택 | `7`, `30` 중 하나<br>`from`, `to`와 함께 보내면 400 |

- 셋 다 없으면 오늘을 포함한 최근 30일이다. 오늘과 어제 날짜는 전환 창 1일이 끝나지 않아 값이 아직 늘 수 있다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to`, `pendingDates` | | 분석 지표와 같음 |
| `daily` | `object[]` | 날짜 오름차순<br>`pendingDates`의 날짜는 없음 |
| `daily[].date` | `string` | KST 날짜 |
| `daily[].newUsers` | `integer` | 그날 처음 기록되고 그날 앱 활성 이벤트가 있는 사용자 수 |
| `daily[].activeUsers` | `integer` | 그중 첫 이벤트 뒤 1일 안에 핵심 활동을 한 사용자 수 |
| `daily[].activationRate` | `number / null` | `activeUsers`를 `newUsers`로 나눈 0~1<br>`newUsers`가 0이면 `null` |
| `totals` | `object` | 준비된 날짜의 합계 |
| `totals.newUsers`, `totals.activeUsers` | `integer` | 일별 합 |
| `totals.activationRate` | `number / null` | `totals.activeUsers`를 `totals.newUsers`로 나눈 값<br>`totals.newUsers`가 0이면 `null` |

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 분석 지표와 같은 기간 오류, 366일 초과, 허용하지 않는 `days` |
| 503 | `SERVICE_UNAVAILABLE` | 분석 지표와 같음 |

<br>

### 4-2-42 캠페인 열람

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/campaigns/push-opens/{campaignId}` |
| 인증 | 관리자 |
| 성공 | 200 |

관리자 캠페인 하나의 열람을 마지막 회차의 선점 날짜부터 오늘까지 센다. 알림의 캠페인 상세 화면이 캠페인 상세와 따로 부른다. 집계 범위와 조회는 처리 흐름에 있다. ([4-1-25 캠페인 열람](4-1-PIPELINES.md#4-1-25-캠페인-열람))

**1. 경로**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `campaignId` | 경로 | 필수 | 캠페인 공개 식별자 |

<br>

**2. 응답**

아래 필드와 푸시 열람의 열람 값 구조, 채팅 전환 값 구조를 함께 응답한다. 열람 값은 푸시 열람의 캠페인 항목과 같은 규칙이고 범위만 집계 범위다. 채팅 전환 값은 마지막 회차의 도달 회원 전체로 센다.

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf` | `string / null` | 분석 지표와 같음<br>분석 도구를 조회하지 않았으면 `null` |
| `pendingDates` | `string[]` | 푸시 열람과 같음<br>분석 도구를 조회하지 않았으면 빈 배열 |
| `campaignId` | `string` | 캠페인 공개 식별자 |
| `startedAt` | `string / null` | 마지막 회차의 선점 시각<br>선점 전이면 `null` |
| `from` | `string / null` | 집계 범위의 첫날<br>`startedAt`의 KST 날짜<br>선점 전이면 `null` |
| `to` | `string / null` | 집계 범위의 마지막 날<br>오늘과 `from`에서 365일 뒤 가운데 이른 날<br>선점 전이면 `null` |
| `measuredFrom` | `string / null` | 푸시 열람과 같음 |
| `androidMeasuredFrom` | `string / null` | 푸시 열람과 같음 |
| `deliveredMembers` | `integer` | 도달 기기가 하나 이상인 회원 수<br>캠페인 상세의 `deliveredMembers`와 같은 집계 |

- 선점 전 캠페인은 `openState`가 `PENDING`이고 열람 값은 모두 `null`이다.
- `openState`가 `MEASURED`가 아니면 분석 도구를 조회하지 않는다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | `campaignId`가 UUID 형식이 아님 |
| 404 | `NOT_FOUND` | 없는 캠페인 |
| 503 | `SERVICE_UNAVAILABLE` | 분석 지표와 같은 조건 |

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/campaigns/push-opens/4b7f0c2a-9d1e-4f3a-8c5b-6e2d1a0f9b37
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

오늘이 2026-10-30이고 웹 측정 시작일이 2026-10-21, 앱 측정 시작일이 2026-10-23인 경우다.

```json
{
  "asOf": "2026-10-30T05:10:00Z",
  "pendingDates": [],
  "campaignId": "4b7f0c2a-9d1e-4f3a-8c5b-6e2d1a0f9b37",
  "startedAt": "2026-10-23T02:00:31Z",
  "from": "2026-10-23",
  "to": "2026-10-30",
  "measuredFrom": "2026-10-21",
  "androidMeasuredFrom": "2026-10-23",
  "deliveredMembers": 412,
  "chattedMembers": 97,
  "chattedBeforeMembers": 64,
  "chatRate": 0.2354,
  "openState": "MEASURED",
  "pushOpens": 84,
  "webPushOpens": 61,
  "androidPushOpens": 23,
  "pushOpenRate": 0.2039,
  "inboxOpens": 11,
  "webInboxOpens": 4,
  "androidInboxOpens": 7
}
```

</details>

<br>

### 4-2-43 결제 지표

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/payments/metrics` |
| 인증 | 관리자 |
| 성공 | 200 |

범위 안에 완료된 주문으로 결제 전환율, 결제 회원 1인당 금액, 첫 결제와 재결제, 상품별 매출, 환불, 가입부터 첫 결제까지 걸린 일수를 센다. 지표 정의는 제품 제약에, 집계는 처리 흐름에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약), [4-1-26 수익, 콘텐츠, 몰입, 검수 지표](4-1-PIPELINES.md#4-1-26-수익-콘텐츠-몰입-검수-지표))

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to`, `days` | | 선택 | 대시보드 차트와 같음 |

- 셋 다 없으면 오늘을 포함한 최근 30일이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to` | | 대시보드 차트와 같음 |
| `activeMembers` | `integer` | 범위 안에 채팅 메시지를 보낸 회원 수 |
| `payingMembers` | `integer` | 범위 안에 완료된 주문이 있는 회원 수 |
| `conversionRate` | `number / null` | `payingMembers`를 `activeMembers`로 나눈 0 이상의 값<br>`activeMembers`가 0이면 `null` |
| `orders` | `integer` | 범위 안에 완료된 주문 수 |
| `amountKrw` | `integer` | 그 주문의 가격 합 |
| `arppu` | `number / null` | `amountKrw`를 `payingMembers`로 나눈 값<br>`payingMembers`가 0이면 `null` |
| `firstTime` | `object` | 회원의 첫 완료 주문인 주문 |
| `firstTime.orders` | `integer` | 주문 수 |
| `firstTime.amountKrw` | `integer` | 가격 합 |
| `repeat` | `object` | 첫 완료 주문이 아닌 주문<br>`firstTime`과 같은 필드 |
| `products` | `object[]` | 상품마다 한 항목<br>`amountKrw` 내림차순, 같으면 `productId` 오름차순<br>범위 안 주문이 없는 상품은 없음 |
| `products[].productId` | `string` | 주문에 기록된 상품 식별자 |
| `products[].orders` | `integer` | 주문 수 |
| `products[].amountKrw` | `integer` | 가격 합 |
| `products[].creditAmount` | `integer` | 주문에 기록된 지급 이프 합 |
| `refundedOrders` | `integer` | 범위 안에 완료된 주문 가운데 지금 환불 상태인 주문 수 |
| `refundRate` | `number / null` | `refundedOrders`를 `orders`로 나눈 값<br>`orders`가 0이면 `null` |
| `daysToFirstPayment` | `object[]` | 범위 안에 첫 완료 주문을 한 회원을 가입일부터 첫 완료일까지 KST 날짜 차이로 나눈 5구간<br>`0`, `1~3`, `4~7`, `8~30`, `31+` 순서로 항상 5항목 |
| `daysToFirstPayment[].bucket` | `string` | 구간 이름 |
| `daysToFirstPayment[].members` | `integer` | 회원 수 |

- 완료된 주문은 완료 시각이 범위 안인 주문이고 뒤에 환불됐어도 센다. 대시보드 차트의 결제 건수와 같은 정의다.
- 첫 완료 주문은 같은 회원의 완료 시각이 더 이른 주문이 없는 주문이다. 완료 시각이 같으면 먼저 만든 주문이 첫 주문이다. 범위 밖의 이전 주문도 본다.
- 모든 값은 팀 계정 제외 목록을 적용한다.

<br>

**3. 실패 응답**

대시보드 차트와 같다.

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/payments/metrics?from=2026-10-01&to=2026-10-31
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "asOf": "2026-11-02T02:10:00Z",
  "from": "2026-10-01",
  "to": "2026-10-31",
  "activeMembers": 412,
  "payingMembers": 23,
  "conversionRate": 0.0558,
  "orders": 31,
  "amountKrw": 190000,
  "arppu": 8260.9,
  "firstTime": { "orders": 18, "amountKrw": 86000 },
  "repeat": { "orders": 13, "amountKrw": 104000 },
  "products": [
    { "productId": "if_10000", "orders": 12, "amountKrw": 112800, "creditAmount": 120000 },
    { "productId": "if_5000", "orders": 14, "amountKrw": 67200, "creditAmount": 70000 },
    { "productId": "if_2000", "orders": 5, "amountKrw": 10000, "creditAmount": 10000 }
  ],
  "refundedOrders": 1,
  "refundRate": 0.0323,
  "daysToFirstPayment": [
    { "bucket": "0", "members": 6 },
    { "bucket": "1~3", "members": 4 },
    { "bucket": "4~7", "members": 3 },
    { "bucket": "8~30", "members": 3 },
    { "bucket": "31+", "members": 2 }
  ]
}
```

</details>

<br>

### 4-2-44 이프 경제 지표

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/credits/metrics` |
| 인증 | 관리자 |
| 성공 | 200 |

범위 안의 이프 적립과 소모를 사유별로 나눠 소모 비율을 보이고 현재 시점의 회원 유효 잔액 분포와 잔액 구성을 센다. 지표 정의는 제품 제약에, 집계는 처리 흐름에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약), [4-1-26 수익, 콘텐츠, 몰입, 검수 지표](4-1-PIPELINES.md#4-1-26-수익-콘텐츠-몰입-검수-지표))

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to`, `days` | | 선택 | 대시보드 차트와 같음 |

- 셋 다 없으면 오늘을 포함한 최근 30일이다. 잔액 분포와 잔액 구성은 기간과 무관한 현재 값이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to` | | 대시보드 차트와 같음 |
| `granted` | `integer` | 범위 안 적립 합<br>대시보드 차트의 이프 적립과 같은 정의 |
| `spent` | `integer` | 범위 안 소모 합<br>대시보드 차트의 이프 소모와 같은 정의 |
| `sinkRate` | `number / null` | `spent`를 `granted`로 나눈 0 이상의 값<br>`granted`가 0이면 `null` |
| `grantedByReason` | `object[]` | `SIGNUP_REWARD`, `INVITE_REWARD`, `ATTENDANCE_REWARD`, `PURCHASE`, `ADMIN_GRANT` 순서로 항상 5항목 |
| `grantedByReason[].reason` | `string` | 원장 사유 |
| `grantedByReason[].amount` | `integer` | 범위 안 합 |
| `spentByReason` | `object[]` | `STORY_CREATION`, `CHAT_TURN`, `CHAT_IMAGE` 순서로 항상 3항목<br>필드는 `grantedByReason`과 같고 값은 절댓값 |
| `balances` | `object` | 탈퇴하지 않은 회원의 현재 유효 잔액 |
| `balances.members` | `integer` | 대상 회원 수 |
| `balances.total` | `integer` | 유효 잔액 합 |
| `balances.buckets` | `object[]` | 유효 잔액을 `0`, `1~99`, `100~499`, `500~1999`, `2000+`로 나눈 회원 수<br>이 순서로 항상 5항목 |
| `balances.buckets[].bucket` | `string` | 구간 이름 |
| `balances.buckets[].members` | `integer` | 회원 수 |
| `balances.purchased` | `integer` | 구매로 생긴 로트의 잔여 합 |
| `balances.rewarded` | `integer` | 보상과 환불과 관리자 지급으로 생긴 로트의 잔여 합 |
| `balances.legacy` | `integer` | 원장 연결이 없는 승계 로트의 잔여 합 |
| `balances.expiringIn30Days` | `integer` | 지금부터 30일 안에 만료되는 로트의 잔여 합 |

- 유효 잔액은 요청 시각에 잔여가 있고 만료되지 않은 로트의 잔여 합이다. 만료 시각이 지났으나 아직 정리되지 않은 로트는 넣지 않는다.
- `balances.total`은 `purchased`, `rewarded`, `legacy`의 합이다.
- 모든 값은 팀 계정 제외 목록을 적용한다.

<br>

**3. 실패 응답**

대시보드 차트와 같다.

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/credits/metrics?days=30
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "asOf": "2026-11-02T02:10:00Z",
  "from": "2026-10-04",
  "to": "2026-11-02",
  "granted": 412500,
  "spent": 268400,
  "sinkRate": 0.6507,
  "grantedByReason": [
    { "reason": "SIGNUP_REWARD", "amount": 71000 },
    { "reason": "INVITE_REWARD", "amount": 12000 },
    { "reason": "ATTENDANCE_REWARD", "amount": 98500 },
    { "reason": "PURCHASE", "amount": 215000 },
    { "reason": "ADMIN_GRANT", "amount": 16000 }
  ],
  "spentByReason": [
    { "reason": "STORY_CREATION", "amount": 41750 },
    { "reason": "CHAT_TURN", "amount": 213480 },
    { "reason": "CHAT_IMAGE", "amount": 13170 }
  ],
  "balances": {
    "members": 1240,
    "total": 1388200,
    "buckets": [
      { "bucket": "0", "members": 318 },
      { "bucket": "1~99", "members": 402 },
      { "bucket": "100~499", "members": 361 },
      { "bucket": "500~1999", "members": 128 },
      { "bucket": "2000+", "members": 31 }
    ],
    "purchased": 612000,
    "rewarded": 540200,
    "legacy": 236000,
    "expiringIn30Days": 182300
  }
}
```

</details>

<br>

### 4-2-45 콘텐츠 소비 지표

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/stories/consumption` |
| 인증 | 관리자 |
| 성공 | 200 |

공개 스토리 가운데 다른 회원이 플레이한 비율, 상위 스토리 집중도, 플레이 순위, 창작자 비율과 창작자 유지를 센다. 지표 정의는 제품 제약에, 집계는 처리 흐름에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약), [4-1-26 수익, 콘텐츠, 몰입, 검수 지표](4-1-PIPELINES.md#4-1-26-수익-콘텐츠-몰입-검수-지표))

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to`, `days` | | 선택 | 대시보드 차트와 같음 |
| `limit` | `integer` | 선택 | 순위 항목 수, 1~50<br>기본 20 |

- 날짜 쿼리가 모두 없으면 오늘을 포함한 최근 30일이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to` | | 대시보드 차트와 같음 |
| `publicStories` | `integer` | 지금 공개 목록 조건을 만족하는 스토리 수 |
| `officialStories` | `integer` | 그 가운데 공식 계정 소유 스토리 수 |
| `playedStories` | `integer` | 공개 스토리 가운데 범위 안에 다른 회원의 채팅이 하나 이상 생성된 스토리 수 |
| `playedRate` | `number / null` | `playedStories`를 `publicStories`로 나눈 값<br>`publicStories`가 0이면 `null` |
| `otherMemberChats` | `integer` | 범위 안에 생성된 다른 회원의 채팅 수<br>공개 여부와 무관 |
| `topConcentration` | `number / null` | 다른 회원의 채팅 수 상위 10편의 채팅 수 합을 `otherMemberChats`로 나눈 값<br>`otherMemberChats`가 0이면 `null` |
| `ranking` | `object[]` | 다른 회원의 채팅 수 내림차순, 같으면 턴 합 내림차순, 같으면 스토리 공개 식별자 순<br>`limit`개 이하 |
| `ranking[].storyId` | `string` | 스토리 공개 식별자 |
| `ranking[].title` | `string` | 제목 |
| `ranking[].official` | `boolean` | 공식 계정 소유 여부 |
| `ranking[].deleted` | `boolean` | 삭제 여부 |
| `ranking[].chats` | `integer` | 범위 안에 생성된 다른 회원의 채팅 수 |
| `ranking[].players` | `integer` | 그 채팅의 서로 다른 회원 수 |
| `ranking[].turns` | `integer` | 그 채팅의 현재 턴 합 |
| `creators` | `object` | 창작자 |
| `creators.activeMembers` | `integer` | 범위 안에 채팅 메시지를 보낸 회원 수 |
| `creators.members` | `integer` | 범위 안에 스토리를 만든 회원 수 |
| `creators.rate` | `number / null` | `members`를 `activeMembers`로 나눈 0 이상의 값<br>`activeMembers`가 0이면 `null` |
| `creators.previousMembers` | `integer` | 직전 기간에 스토리를 만든 회원 수<br>직전 기간은 대시보드 차트와 같음 |
| `creators.retained` | `integer` | 직전 기간 창작자 가운데 범위 안에도 스토리를 만든 회원 수 |
| `creators.retentionRate` | `number / null` | `retained`를 `previousMembers`로 나눈 값<br>`previousMembers`가 0이면 `null` |

- 다른 회원의 채팅은 소유 회원이 있고 그 회원이 스토리 소유자와 다른 채팅이다. 게스트 채팅은 소유 관계를 판정할 수 없어 세지 않는다. 삭제된 채팅은 세지 않는다.
- 공개 목록 조건은 STORY의 공개 목록과 같다. 스토리 수와 순위는 지금 상태로 센다.
- 창작자의 스토리 수는 삭제 여부와 무관하고 공식 계정은 팀 계정 제외 목록으로 빠진다.
- 모든 값은 팀 계정 제외 목록을 적용한다. 공식 계정 소유 스토리는 `publicStories`, `officialStories`, `ranking`에 들어가고 채팅 소유자 기준 제외만 받는다.

<br>

**3. 실패 응답**

| 상태 | `code` | 조건 |
|---|---|---|
| 400 | `BAD_REQUEST` | 대시보드 차트와 같은 기간 오류, `limit`이 1~50 밖 |

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/stories/consumption?days=30&limit=3
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

```json
{
  "asOf": "2026-11-02T02:10:00Z",
  "from": "2026-10-04",
  "to": "2026-11-02",
  "publicStories": 486,
  "officialStories": 8,
  "playedStories": 97,
  "playedRate": 0.1996,
  "otherMemberChats": 1532,
  "topConcentration": 0.6214,
  "ranking": [
    { "storyId": "6f0c2d1e-3b4a-4c5d-8e9f-0a1b2c3d4e5f", "title": "던전의 밤", "official": true, "deleted": false, "chats": 412, "players": 301, "turns": 4120 },
    { "storyId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d", "title": "편의점 야간 알바", "official": false, "deleted": false, "chats": 188, "players": 142, "turns": 1510 },
    { "storyId": "9e8d7c6b-5a4f-4e3d-8c2b-1a0f9e8d7c6b", "title": "졸업식 전날", "official": true, "deleted": false, "chats": 131, "players": 97, "turns": 902 }
  ],
  "creators": {
    "activeMembers": 412,
    "members": 58,
    "rate": 0.1408,
    "previousMembers": 51,
    "retained": 19,
    "retentionRate": 0.3725
  }
}
```

</details>

<br>

### 4-2-46 채팅 몰입 지표

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/chats/engagement` |
| 인증 | 관리자 |
| 성공 | 200 |

회원의 날짜별 채팅 활동과 활성 회원 1인당 턴, 전날 채팅을 다음 날 이어 간 비율, 재생성 비율, 서버 기준 고착도를 센다. 지표 정의는 제품 제약에, 집계는 처리 흐름에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약), [4-1-26 수익, 콘텐츠, 몰입, 검수 지표](4-1-PIPELINES.md#4-1-26-수익-콘텐츠-몰입-검수-지표))

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to`, `days` | | 선택 | 대시보드 차트와 같음 |

- 셋 다 없으면 오늘을 포함한 최근 30일이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to` | | 대시보드 차트와 같음 |
| `activeMembers` | `integer` | 범위 안에 채팅 메시지를 보낸 회원 수 |
| `monthlyActiveMembers` | `integer` | `to`로 끝나는 30일 안에 채팅 메시지를 보낸 회원 수 |
| `turnsPerActiveMember` | `number / null` | 범위 안 턴 수를 `activeMembers`로 나눈 값<br>`activeMembers`가 0이면 `null` |
| `daily` | `object[]` | 날짜 오름차순<br>범위의 모든 날짜가 한 항목씩 |
| `daily[].date` | `string` | KST 날짜 |
| `daily[].activeMembers` | `integer` | 그날 채팅 메시지를 보낸 회원 수 |
| `daily[].turns` | `integer` | 그날 턴 수<br>대시보드 차트의 턴과 같은 정의 |
| `daily[].turnsPerActiveMember` | `number / null` | `turns`를 `activeMembers`로 나눈 값<br>`activeMembers`가 0이면 `null` |
| `daily[].continuedMembers` | `integer` | 전날 채팅 메시지를 보낸 회원 가운데 그날 전날과 같은 채팅에 채팅 메시지를 보낸 회원 수 |
| `daily[].continuationRate` | `number / null` | `continuedMembers`를 전날 `activeMembers`로 나눈 값<br>전날 값이 0이면 `null`<br>범위 첫날도 범위 전날의 값으로 계산 |
| `daily[].regenerations` | `integer` | 그날 성공한 재생성 수 |
| `daily[].regenerationRate` | `number / null` | `regenerations`를 `turns`로 나눈 값<br>`turns`가 0이면 `null` |
| `daily[].stickiness` | `number / null` | `activeMembers`를 그날로 끝나는 30일 안에 채팅 메시지를 보낸 회원 수로 나눈 값<br>분모가 0이면 `null` |

- 채팅 메시지는 회원이 보낸 사용자 메시지다. 게스트 채팅의 메시지는 소유 회원이 없어 세지 않는다. 삭제된 채팅의 메시지도 센다.
- 모든 값은 팀 계정 제외 목록을 적용한다.

<br>

**3. 실패 응답**

대시보드 차트와 같다.

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/chats/engagement?from=2026-10-26&to=2026-11-01
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

예시에는 `daily`의 날짜 항목 2개만 표시했다.

```json
{
  "asOf": "2026-11-02T02:10:00Z",
  "from": "2026-10-26",
  "to": "2026-11-01",
  "activeMembers": 188,
  "monthlyActiveMembers": 412,
  "turnsPerActiveMember": 26.4,
  "daily": [
    { "date": "2026-10-26", "activeMembers": 61, "turns": 702, "turnsPerActiveMember": 11.5, "continuedMembers": 24, "continuationRate": 0.4138, "regenerations": 31, "regenerationRate": 0.0442, "stickiness": 0.1481 },
    { "date": "2026-10-27", "activeMembers": 58, "turns": 640, "turnsPerActiveMember": 11.0, "continuedMembers": 27, "continuationRate": 0.4426, "regenerations": 22, "regenerationRate": 0.0344, "stickiness": 0.1408 }
  ]
}
```

</details>

<br>

### 4-2-47 검수 지표

| 항목 | 값 |
|---|---|
| 요청 | `GET /admin/moderation/metrics` |
| 인증 | 관리자 |
| 성공 | 200 |

검수 제출본의 날짜별 판정 수와 거절률, 거절 사유별 제출본 수, 현재 보류와 대기 수를 센다. 지표 정의는 제품 제약에, 집계는 처리 흐름에 있다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약), [4-1-26 수익, 콘텐츠, 몰입, 검수 지표](4-1-PIPELINES.md#4-1-26-수익-콘텐츠-몰입-검수-지표))

**1. 쿼리**

| 필드명 | 타입 | 필수 | 의미와 기본값 |
|---|---|---|---|
| `from`, `to`, `days` | | 선택 | 대시보드 차트와 같음 |

- 셋 다 없으면 오늘을 포함한 최근 30일이다.

<br>

**2. 응답**

| 필드명 | 타입 | 의미 |
|---|---|---|
| `asOf`, `from`, `to` | | 대시보드 차트와 같음 |
| `decided` | `integer` | 범위 안에 판정된 제출본 수<br>승인과 거절의 합 |
| `approved` | `integer` | 승인 수 |
| `rejected` | `integer` | 거절 수 |
| `rejectionRate` | `number / null` | `rejected`를 `decided`로 나눈 값<br>`decided`가 0이면 `null` |
| `failed` | `integer` | 범위 안에 실행 실패로 끝난 제출본 수 |
| `held` | `integer` | 지금 보류 중인 제출본 수 |
| `pending` | `integer` | 지금 대기 중이며 보류가 아닌 제출본 수 |
| `daily` | `object[]` | 판정 시각의 KST 날짜 오름차순<br>범위의 모든 날짜가 한 항목씩 |
| `daily[].date` | `string` | KST 날짜 |
| `daily[].submitted` | `integer` | 그날 처음 제출된 제출본 수 |
| `daily[].approved` | `integer` | 그날 승인된 수 |
| `daily[].rejected` | `integer` | 그날 거절된 수 |
| `daily[].failed` | `integer` | 그날 실행 실패로 끝난 수 |
| `rejectionRules` | `object[]` | 범위 안에 거절된 제출본의 위반 항목을 규칙과 종류로 묶은 수<br>제출본 수 내림차순, 같으면 규칙 이름 순<br>한 제출본에 같은 규칙과 종류의 위반이 여럿이어도 한 번 셈 |
| `rejectionRules[].rule` | `string` | 위반 규칙 코드 |
| `rejectionRules[].type` | `string` | 위반 종류<br>`TEXT`, `IMAGE` |
| `rejectionRules[].submissions` | `integer` | 제출본 수 |

- 제출본은 재제출하면 같은 행이 다시 대기로 바뀌어 이전 판정이 남지 않는다. 값은 지금 남아 있는 판정으로 센다.
- 팀 계정 제외 목록을 적용하지 않는다.

<br>

**3. 실패 응답**

대시보드 차트와 같다.

<details>
<summary><b>요청과 응답 예시</b></summary>

<br>

**1) Request**

```http
GET /api/v1/admin/moderation/metrics?days=7
Authorization: Bearer {adminToken}
```

**2) 200 Response body**

예시에는 `daily`의 날짜 항목 2개만 표시했다.

```json
{
  "asOf": "2026-11-02T02:10:00Z",
  "from": "2026-10-27",
  "to": "2026-11-02",
  "decided": 46,
  "approved": 39,
  "rejected": 7,
  "rejectionRate": 0.1522,
  "failed": 2,
  "held": 1,
  "pending": 3,
  "daily": [
    { "date": "2026-10-27", "submitted": 8, "approved": 6, "rejected": 1, "failed": 0 },
    { "date": "2026-10-28", "submitted": 5, "approved": 5, "rejected": 2, "failed": 1 }
  ],
  "rejectionRules": [
    { "rule": "EXPLICIT_SEXUAL_CONTENT", "type": "TEXT", "submissions": 4 },
    { "rule": "EXPLICIT_SEXUAL_CONTENT", "type": "IMAGE", "submissions": 2 },
    { "rule": "HATE_VIOLENCE_INCITEMENT", "type": "TEXT", "submissions": 1 }
  ]
}
```

</details>

<br>

### 4-2-48 다른 도메인과의 경계

| 도메인 | ADMIN이 제공하는 것 | ADMIN이 사용하는 것 |
|---|---|---|
| ACCOUNT | 관리자 요청자 식별과 감사 기록 연산 | 신원 검증기, 회원 조회와 검색, 활성 소셜 연동 이메일 일치 조회, 계정 상태, 회원 수 집계 |
| PAYMENT | 관리자 요청자 식별과 감사 기록 연산 | 잔액, 주문 조회, 원장 조회, 적립과 소모 집계, 로트 잔여 집계, 주문의 상품과 완료와 환불 집계 |
| NOTIFICATION | 관리자 요청자 식별과 감사 기록 연산 | 기간의 캠페인 도달 요약, 캠페인 하나의 도달 요약, 종류별 날짜별 도달 회원 수, 도달 회원 도달 시각 |
| NOTICE | 관리자 요청자 식별과 감사 기록 연산 | 없음 |
| MODERATION | 관리자 요청자 식별과 감사 기록 연산 | 스토리별 보류 제출본 존재 여부, 제출본의 판정과 위반 항목 집계 |
| STORY | 관리자 요청자 식별과 감사 기록 연산 | 스토리 수, 스토리와 제작 세션 조회, 간편 제작 완성 요청의 상태 집계, 수정 폼의 현재 저장값 조립, 공식 계정 식별, 공개 목록 조건 |
| CHAT | 관리자 요청자 식별과 감사 기록 연산 | 채팅 시작 수, 턴 수, 채팅 조회, 턴 도달률, 페르소나와 모델 비중, AI 호출 기록 조회, 회원별 사용자 메시지 날짜, 재생성 이력 수 |
| Amplitude | 없음 | Dashboard REST API의 이벤트 세분화 조회, 퍼널 조회, 리텐션 조회, 세션 조회 |
| Langfuse | 없음 | Metrics API의 관측 비용 합 |
| Google Cloud Storage | 없음 | Play Console 일괄 보고서 객체 목록과 내려받기 |
| AWS CloudWatch, ECS | 없음 | CloudWatch `GetMetricData` 지표 조회, ECS `DescribeServices` 태스크 수 조회 |
| 모든 도메인 | 관리자 판정 필터와 앱 토큰 검증 보강 | 인증 필터와 상관관계 필터 |

다른 도메인이 호출하는 연산의 입력과 결과는 다음과 같다.

| 연산 | 입력 | 결과 |
|---|---|---|
| 관리자 요청자 | 현재 요청 | 관리자의 회원 내부 ID<br>필터가 확정한 값 |
| 변경 감사 기록 | 관리자, 작업 이름, 대상 종류, 대상 식별자, 사유, 변경 전 값, 변경 후 값 | 감사 로그 행<br>호출자의 트랜잭션에 참여하고 트랜잭션이 없으면 거부 |
| 접속 기록 | 관리자, 작업 이름, 대상 종류, 대상 식별자 | 감사 로그 행<br>독립 트랜잭션 |

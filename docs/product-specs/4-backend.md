# 4-BACKEND

이 문서는 마냑 백엔드 서버(`manyak-server`)가 구현하고 QA가 검수해야 할 계약을 정의합니다. API, 데이터 모델, 인증, 오류 처리, 운영·관측 기준을 다룹니다.

각 항목은 실제 구현된 동작을 기준으로 구체값을 적고, 아직 구현하지 않은 항목은 `계획`으로 구분해 표기합니다.

```text
§4-1   문서 목적·범위와 관련 문서
§4-2   기술 환경과 아키텍처
§4-3   API 계약
§4-4   데이터 모델
§4-5   인증과 권한
§4-6   오류와 예외 처리
§4-7   운영과 관측
§4-8   검수 체크리스트
```

| 항목 | 값 |
| --- | --- |
| 버전 | v0.5 |
| 작성일 | 2026-07-03 |
| 수정일 | 2026-07-04 |
| 대상 | 마냑 백엔드 서버 |
| 작성 목적 | 백엔드 API, 데이터 모델, 오류 처리, 운영 기준을 정의합니다. |
| 기준 코드 | `../manyak-server` `dev` 브랜치 (Kotlin 2.2, Spring Boot 4) |

## 4-1. 문서 목적·범위와 관련 문서

### 목적

이 문서는 마냑 백엔드 개발자가 API 계약, 데이터 모델, 오류 처리, 운영 기준을 구현하는 기준입니다. 백엔드는 이 문서를 기준으로 구현하고, 프론트엔드·AI 서버는 이 문서로 백엔드와의 계약을 확인하며, QA는 이 문서를 기준으로 검수합니다.

### 범위

- REST API 계약(엔드포인트, 요청·응답 스키마, 상태 코드, 헤더)
- 채팅 SSE 스트리밍 계약
- 데이터 모델과 식별자·삭제 정책
- 인증(Google 로그인, JWT)과 선택적 인증 정책
- 오류 응답 계약과 예외 처리 기준
- 운영·관측(상관관계 식별자, 구조화 로그, Sentry, `ai_call_logs`, 환경 변수, 헬스체크)

### 제외 범위

- 화면, 사용자 흐름, 프론트엔드 상태 처리 (담당: [`3-frontend.md`](./3-frontend.md))
- AI 서버 내부 구현, 프롬프트, 레이어 구성 (담당: [`5-ai-server.md`](./5-ai-server.md))
- 분석 이벤트 카탈로그, 지표, CloudWatch·Sentry 수집 기준의 원천 정의 (원천: [`6-analytics.md`](./6-analytics.md))
- 코드 구조, 클래스 설계, 테스트 작성 규칙, 로컬 실행 상세 (서버 레포 `README.md`·`CLAUDE.md`가 소유)
- 인프라 구성(Terraform, VPC, RDS 등)과 배포 런북 (`manyak-terraform` 레포가 소유)

### 관련 문서와 경계

| 문서 | 소유 영역 | 이 문서와의 관계 |
| --- | --- | --- |
| [`0-glossary.md`](./0-glossary.md) | 용어, 계층별 표기 컨벤션 | 필드·테이블·로그 이름의 표기 근거 |
| [`1-background.md`](./1-background.md) | 서비스 배경, MVP 범위 | 제품 방향의 상위 근거 |
| [`2-user-stories.md`](./2-user-stories.md) | 화면별 사용자 요구(US ID) | 검수 기준을 US ID로 추적 |
| [`3-frontend.md`](./3-frontend.md) | 화면, API 호출 시점, 실패 처리 | API의 소비자 계약. 호출 흐름은 위임 |
| [`5-ai-server.md`](./5-ai-server.md) | AI 요청·응답 계약, 프롬프트 | AI 와이어 상세 위임 |
| [`6-analytics.md`](./6-analytics.md) | 이벤트, 식별자, 관측 수집 기준 | 관측 계약의 원천. 백엔드 구현 현황은 이 문서가 기술 |

### 작성 원칙

- 구현된 동작을 기준으로 씁니다. 문서 간 기준이 다르면 코드를 기준으로 하고 차이는 [§4-8](#4-8-검수-체크리스트)의 간극 표에 기록합니다.
- API 경로는 `/api/v1` prefix를 생략해 표기합니다. 예외적으로 전체 경로가 필요한 곳(헬스체크 등)만 전체를 적습니다.
- 클라이언트 와이어 필드는 camelCase, DB·로그 필드는 snake_case로 적습니다([`0-glossary.md §0-4`](./0-glossary.md)).
- 이벤트·지표·AI 프롬프트는 원천 문서를 교차 참조하고 중복 서술하지 않습니다.

### 구현 상태 라벨

이 문서는 항목마다 `{로드맵 Phase} · {구현 상태}` 두 축을 라벨로 구분합니다. 로드맵 Phase는 [`roadmap.md`](../planning/roadmap.md)가 기능을 배정한 단계이고, 구현 상태는 `구현`(코드 반영 완료)과 `계획`(미구현, 방향만 합의) 2종입니다. `MVP`(= `Phase 0 · 구현`)와 `계획`(Phase 미배정)은 관례 단축형이며, 라벨이 없는 항목은 모두 `MVP`입니다.

| 라벨 | 의미 | 해당 항목 |
| --- | --- | --- |
| `MVP` | Phase 0 범위. 서버 구현 완료, MVP 프론트엔드가 사용 중 | 스토리·간편 제작·채팅·피드백 API |
| `Phase 1 · 구현` | Phase 1 범위. 서버 구현 완료, MVP 프론트엔드는 아직 미사용 | 인증 API([§4-5](#4-5-인증과-권한)), 로어북·엔딩([§4-3-6](#4-3-api-계약)) |
| `Phase 1 · 계획` | Phase 1 범위. 미구현, 방향만 합의됨 | 계정 — 마이그레이션·내 콘텐츠 목록([§4-3-5](#4-3-api-계약))·가입 프로필 발급([§4-5](#4-5-인증과-권한)). 크레딧([§4-3-7](#4-3-api-계약)). 엔딩 스키마 재정의 · 주요 사건([§4-8](#4-8-검수-체크리스트) B5). 일반 제작 · 스토리 수정 · 재생성 · 이미지는 후속 반영에서 추가 |
| `계획` | Phase 미배정. 미구현, 방향만 합의됨 | 서버 분석 이벤트([§4-7](#4-7-운영과-관측)), AI 와이어 필드 정렬([§4-8](#4-8-검수-체크리스트) B2) |

## 4-2. 기술 환경과 아키텍처

### 기술 환경

| 분류 | 기술 |
| --- | --- |
| 언어·런타임 | Kotlin 2.2, Java 21 (Temurin) |
| 프레임워크 | Spring Boot 4, Spring MVC + `SseEmitter`(SSE), WebClient(AI 스트림 수신) |
| 영속성 | Spring Data JPA, PostgreSQL(운영)·H2(테스트), Flyway 마이그레이션 |
| 캐시·토큰 저장소 | Redis (refresh 토큰) |
| 인증 | Spring Security, OAuth2 Resource Server(JWT), Google ID 토큰 검증 |
| 관측 | Logstash Logback Encoder(JSON 구조화 로그), Sentry, Spring Actuator |
| API 문서 | SpringDoc OpenAPI (Swagger UI) |
| 빌드·배포 | Gradle(Kotlin DSL), Docker multi-stage, GitHub Actions |

### 핵심 아키텍처

일반적인 인증형 API 서버와 다른 지점입니다.

| # | 특징 | 요지 | 상세 |
| --- | --- | --- | --- |
| 1 | 전원 게스트 + 선택적 인증 | MVP는 인증 없이 동작합니다. 대부분의 엔드포인트는 익명을 허용하되, 유효한 토큰이 오면 `user_id`를 귀속합니다. | [§4-5](#4-5-인증과-권한) |
| 2 | 공개 식별자(UUID)만 노출 | 외부에는 `public_id`(UUID)만 노출하고 내부 Long PK는 감춰 IDOR을 차단합니다. | [§4-4](#4-4-데이터-모델) |
| 3 | AI 프록시 | 스토리 생성은 동기 REST로, 채팅 턴은 SSE로 AI 서버를 호출하고 결과를 저장·중계합니다. | [§4-3-3](#4-3-api-계약) |
| 4 | 상관관계 관측 | 모든 요청에 `request_id`를 부여하고 `device_id_hash`로 익명 식별을 이어 로그·Sentry·`ai_call_logs`를 연결합니다. | [§4-7](#4-7-운영과-관측) |
| 5 | 소프트 삭제 | 스토리·채팅 삭제는 `deleted_at` 기록으로 처리하고 조회에서 제외합니다. | [§4-4](#4-4-데이터-모델) |

### 요청 흐름

```text
브라우저
   │  X-Manyak-Device-Id · X-Manyak-Session-Id 주입
   ▼
Next.js BFF 프록시 (/api/* → API_BASE_URL)
   │
   ▼
manyak-server (/api/v1/*)
   │  request_id 부여, device_id 해시, 구조화 로그
   │  X-Manyak-Request-Id · X-Manyak-Session-Id · X-Manyak-Device-Id-Hash forward
   ▼
manyak-ai  — 스토리 생성(동기 REST) · 채팅 턴(SSE)
```

### 도메인 모듈

서버 코드는 도메인 4개와 공통 계층으로 나뉩니다.

| 모듈 | 담당 |
| --- | --- |
| `auth` | Google 로그인, JWT 발급·검증, refresh 토큰 저장소 |
| `story` | 스토리 조회·삭제, 간편 제작 퍼널, 로어북, 스토리 AI 클라이언트 |
| `chat` | 채팅 생성·조회·삭제, 턴 SSE 스트리밍, 채팅 AI 클라이언트 |
| `feedback` | 피드백 저장, Slack 알림 |
| `global` | 보안 설정, 공통 오류 응답, 상관관계 필터, 구조화 로그, `ai_call_logs` |

## 4-3. API 계약

### 공통 규칙

- 모든 비즈니스 API는 `/api/v1` prefix를 사용합니다.
- 요청·응답 JSON 필드는 camelCase입니다([`0-glossary.md §0-4`](./0-glossary.md)).
- 시각 필드(`createdAt`, `updatedAt`)는 ISO 8601 UTC 문자열입니다.
- 배치 조회는 배열이 커질 수 있어 `POST` 본문으로 ID 목록을 받습니다. 상한은 100개입니다.
- 요청 검증 실패는 400과 `ApiErrorResponse.details`로 응답합니다([§4-6](#4-6-오류와-예외-처리)).

### 요청·응답 헤더

프론트엔드가 주입하는 식별 헤더와 백엔드의 처리 규칙입니다. 값의 정책 원천은 [`6-analytics.md §6-6-2`](./6-analytics.md)입니다.

| 헤더 | 방향 | 처리 |
| --- | --- | --- |
| `X-Manyak-Request-Id` | 수신·응답 | 없으면 `req_` + UUID(하이픈 제거)로 생성. 응답 헤더로 항상 echo |
| `X-Manyak-Session-Id` | 수신 | MDC `session_id`에 적재. 없으면 `unknown` |
| `X-Manyak-Device-Id` | 수신 | 원본을 저장하지 않고 해시(`device_id_hash`)로 변환해 MDC에 적재. 없으면 `unknown` |

- 식별 헤더가 없어도 요청을 거부하지 않습니다.
- 해시 방식과 AI 서버로의 forward 규칙은 [§4-7](#4-7-운영과-관측)에 정의합니다.

### 엔드포인트 카탈로그

| 도메인 | 메서드·경로 | 설명 | 성공 | 주요 실패 | 인증 | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| 스토리 | `POST /stories/batch` | 공개 ID 목록으로 스토리 카드 조회 | 200 | 400 | 불필요 | MVP |
| 스토리 | `GET /stories/{storyId}` | 스토리 상세 조회 | 200 | 404 | 불필요 | MVP |
| 스토리 | `DELETE /stories/{storyId}` | 스토리 소프트 삭제 | 204 | 404 | 불필요 | MVP |
| 스토리 | `GET /stories/lorebooks` | 로어북 카탈로그 조회(`?genre` 필터) | 200 | — | 불필요 | Phase 1 · 구현 |
| 간편 제작 | `GET /stories/simple/tags` | 제공 태그 목록 조회 | 200 | — | 불필요 | MVP |
| 간편 제작 | `POST /stories/simple/storylines` | 스토리라인 3개 생성(AI 호출) | 201 | 400·502 | 선택 | MVP |
| 간편 제작 | `POST /stories/simple` | 최종 스토리 생성(AI 호출) | 201 | 400·402·404·409·502 | 선택 | MVP |
| 간편 제작 | `PUT /stories/simple/storylines/{storylineId}/rating` | 스토리라인 평가 설정 | 200 | 400·404 | 선택 | MVP |
| 간편 제작 | `DELETE /stories/simple/storylines/{storylineId}/rating` | 스토리라인 평가 취소(멱등) | 204 | 404 | 선택 | MVP |
| 채팅 | `POST /chats` | 채팅 생성(플레이 시작) | 201 | 400·404 | 선택 | MVP |
| 채팅 | `POST /chats/batch` | 공개 ID 목록으로 채팅 카드 조회 | 200 | 400 | 불필요 | MVP |
| 채팅 | `GET /chats/{chatId}` | 채팅 상세(턴 이력) 조회 | 200 | 404 | 불필요 | MVP |
| 채팅 | `DELETE /chats/{chatId}` | 채팅 소프트 삭제 | 204 | 404 | 불필요 | MVP |
| 채팅 | `POST /chats/{chatId}/turns/stream` | 턴 진행 SSE 스트리밍 | 200(SSE) | 400·402·404 | 선택 | MVP |
| 피드백 | `POST /feedbacks` | 피드백 등록 | 201 | 400 | 선택 | MVP |
| 인증 | `POST /auth/login/google` | Google ID 토큰 로그인 | 200 | 400·401 | 불필요 | Phase 1 · 구현 |
| 인증 | `GET /auth/me` | 현재 사용자 조회 | 200 | 401 | 필수 | Phase 1 · 구현 |
| 인증 | `POST /auth/token/refresh` | 토큰 재발급(회전) | 200 | 400·401 | 불필요 | Phase 1 · 구현 |
| 인증 | `POST /auth/logout` | refresh 토큰 폐기(멱등) | 204 | 400 | 불필요 | Phase 1 · 구현 |
| 인증 | `POST /auth/migrate` | 게스트 데이터 소유권 이관(항목별 부분 성공) | 200 | 400·401 | 필수 | Phase 1 · 계획 |
| 사용자 | `GET /users/me/stories` | 내 스토리 목록(서버 정본) | 200 | 401 | 필수 | Phase 1 · 계획 |
| 사용자 | `GET /users/me/chats` | 내 채팅 목록(서버 정본) | 200 | 401 | 필수 | Phase 1 · 계획 |
| 크레딧 | `GET /users/me/credits` | 크레딧 잔액 조회 | 200 | 401 | 필수 | Phase 1 · 계획 |
| 크레딧 | `POST /users/me/credits/attendance` | 출석체크 적립(1일 1회 멱등) | 200 | 401 | 필수 | Phase 1 · 계획 |
| 크레딧 | `GET /users/me/invite` | 내 초대 코드·링크 조회 | 200 | 401 | 필수 | Phase 1 · 계획 |

인증 열의 `선택`은 익명을 허용하되 유효한 access 토큰이 오면 `user_id`를 귀속하는 엔드포인트입니다([§4-5](#4-5-인증과-권한)).

### 4-3-1. 스토리 조회·삭제

**`POST /stories/batch`** — 요청 `{storyIds: string[]}`(1~100개). 존재하고 삭제되지 않은 스토리만 반환하며, 없는 ID는 오류 없이 제외합니다.

**응답 항목(`StorySummaryResponse`)**

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `id` | string | 스토리 공개 식별자(UUID) |
| `title` | string | 제목 |
| `oneLineIntro` | string | 한 줄 소개 |
| `genres` | string[] | 장르 태그명 목록 |
| `author` | object·null | 작성자 `{id, nickname, profileImageUrl}`. 익명 생성 시 null |
| `chatCount` | number | 스토리로 시작한 채팅 수 |
| `likeCount` | number | 좋아요 수(placeholder) |
| `status` | enum | `DRAFT` · `PUBLISHED` |
| `createdAt` | string | 생성 시각 |

**`GET /stories/{storyId}`** — 상세 응답(`StoryDetailResponse`)은 목록 필드에 다음을 더합니다.

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `description` | string·null | 주요 내용 |
| `coverImageUrl` | string·null | 썸네일 이미지 URL(placeholder — 와이어 필드명은 현행 계약 유지, [`0-glossary.md §0-3-1`](./0-glossary.md)) |
| `hashtags` | string[] | 해시태그(placeholder) |
| `suggestedInputs` | string[] | 채팅 시작 화면의 추천 입력 |
| `startSetting` | object·null | 시작 설정 `{name, prologue, startSituation}` |
| `visibility` | enum | `PUBLIC` · `PRIVATE`(기본 PRIVATE) |
| `lorebooks` | object[] | `Phase 1 · 구현` 로어북 `{id, name, genre, content}` |
| `endings` | object[] | `Phase 1 · 구현` 엔딩 `{title, content, conditionText, sortOrder, enabled}` — 구조 재정의 예정([§4-8](#4-8-검수-체크리스트) B5) |

- `status`·`visibility`·`lorebooks`·`endings`는 MVP 프론트엔드가 사용하지 않습니다([`3-frontend.md §3-13`](./3-frontend.md) G3).
- **`DELETE /stories/{storyId}`** — 소프트 삭제 후 204. 존재하지 않거나 이미 삭제된 ID는 404를 반환하며, 프론트엔드는 404를 무음 성공으로 처리합니다([`3-frontend.md §3-7`](./3-frontend.md)).

### 4-3-2. 간편 제작

간편 제작 퍼널(키워드 선택 → 스토리라인 선택 → 추가 정보 → 완료)의 서버 계약입니다. 화면 흐름은 [`3-frontend.md §3-5`](./3-frontend.md)가 정의합니다.

**`GET /stories/simple/tags`** — 활성화된 제공 태그 목록 `{id, name, category}[]`을 반환합니다. `category`는 `GENRE` · `PROTAGONIST` · `SUPPORTING_CHARACTER`입니다.

**`POST /stories/simple/storylines`** — 태그 선택으로 스토리라인 3개를 생성합니다. AI 서버 `POST /story/storylines`를 동기 호출하며 실패 시 502를 반환합니다.

| 요청 필드 | 제약 | 설명 |
| --- | --- | --- |
| `selectedTagIds` | 최대 20개, 각 ≥ 1 | 선택한 제공 태그 ID |
| `customTags` | 최대 20개 | 직접 추가 태그 `{name(≤30자), category}` |

- `selectedTagIds`와 `customTags` 중 하나 이상은 있어야 합니다. 둘 다 비면 400입니다.
- 응답(201): `{simpleCreationId, selectedTags[], storylines[]}`. `simpleCreationId`는 간편 제작 진행 ID로, 분석 표준 표기는 `creation_id`입니다([`0-glossary.md §0-3-2`](./0-glossary.md)).
- `storylines`는 정확히 3개이며 각 항목은 `{id, storyline, recommendedInfos: {id, text}[3]}`입니다.

**`POST /stories/simple`** — 선택한 스토리라인과 추가 정보로 최종 스토리를 생성합니다. AI 서버 `POST /story/compile`을 동기 호출합니다.

| 요청 필드 | 제약 | 설명 |
| --- | --- | --- |
| `simpleCreationId` | ≥ 1 | 간편 제작 진행 ID |
| `storylineId` | ≥ 1 | 선택한 스토리라인 ID |
| `additionalInfos` | 최대 13개, 각 ≤ 100자 | 추가 정보(추천 채택분 포함 합산) |

- 응답(201, `SimpleStoryCreateResponse`): `{id, title, oneLineIntro, description, genres, startSetting}`. `id`는 스토리 공개 식별자(UUID)이며 클라이언트가 로컬 서재에 저장합니다.
- 같은 진행(`simpleCreationId`)으로 이미 스토리를 생성했다면 409를 반환합니다. 프론트엔드의 완성 재시도는 스토리 생성을 건너뛰므로 정상 흐름에서는 발생하지 않습니다([`3-frontend.md §3-5`](./3-frontend.md)).
- AI 호출 실패는 502입니다.

**`PUT · DELETE /stories/simple/storylines/{storylineId}/rating`** — 평가 설정은 `{rating: "GOOD" | "BAD"}`를 받아 200과 `{id, rating}`을 반환합니다. 같은 사용자·기기의 기존 평가는 덮어씁니다. 취소는 204이며 평가가 없어도 성공하는 멱등 동작입니다.

### 4-3-3. 채팅과 SSE 스트리밍

**`POST /chats`** — 요청 `{storyId: string}`. 스토리가 없으면 404. 응답(201):

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `id` | string | 채팅 공개 식별자(UUID) |
| `storyId` | string | 스토리 공개 식별자 |
| `prologue` | string | 시작 설정의 프롤로그 |
| `suggestedInputs` | string[] | 추천 입력(첫 입력 후보) |
| `createdAt` | string | 생성 시각 |

**`POST /chats/batch`** — 요청 `{chatIds: string[]}`(1~100개). 최근 활동순으로 정렬해 반환하며, 프론트엔드는 이 순서를 유지합니다([`3-frontend.md §3-7`](./3-frontend.md)). 응답 항목(`ChatSummaryResponse`): `{id, storyId, storyTitle, lastStoryPreview, turnCount, updatedAt}`. `turnCount`는 완료된 턴 수입니다.

**`GET /chats/{chatId}`** — 응답(`ChatDetailResponse`): `{id, storyId, storyTitle, prologue, turns[], suggestedInputs}`. 턴 항목은 `{id, userInput, aiOutput, choices: string[], createdAt}`입니다.

**`DELETE /chats/{chatId}`** — 소프트 삭제 후 204, 없으면 404. 처리 규칙은 스토리 삭제와 같습니다.

**`POST /chats/{chatId}/turns/stream`** — 사용자 입력으로 턴을 진행하고 AI 응답을 SSE로 중계합니다.

- 요청: `{userInput: string}`(1~3,000자). 채팅이 없으면 스트림 시작 전에 동기 404로 응답합니다.
- 응답 Content-Type: `text/event-stream;charset=UTF-8`.
- 이벤트 순서: `started` → `token`(반복) → `completed` 또는 `error`.

| 이벤트 | 데이터(JSON) | 설명 |
| --- | --- | --- |
| `started` | `{chatId}` | 스트리밍 시작 |
| `token` | `{text}` | AI 토큰 청크. AI 서버 스트림을 1:1 중계 |
| `completed` | `{chatId, turnId, aiOutput, choices[]}` | 턴 저장 완료. `aiOutput`은 서버 확정본 전문 |
| `error` | `{code, message}` | 실패. `completed`를 대체 |

- 서버는 `completed` 전에 사용자 입력과 AI 출력을 한 턴으로 저장합니다. 저장이 확정한 턴 번호를 `ai_call_logs`에도 반영합니다([§4-7](#4-7-운영과-관측)).
- `error.code`는 AI 서버가 보낸 오류 코드를 그대로 중계하고, AI 이벤트 외 실패는 `AI_STREAM_FAILED`로 분류합니다.
- **타임아웃**: 스트림 전체 상한은 60초입니다. 초과하면 진행 중인 AI 호출을 취소하고 `error` 이벤트 없이 스트림을 종료합니다. 프론트엔드의 EOF 처리 간극은 [`3-frontend.md §3-13`](./3-frontend.md) G5에 기록되어 있습니다.
- 서버 재개(resume) 스트림은 없습니다. 클라이언트는 재진입 시 상세를 다시 조회합니다.

### 4-3-4. 피드백

**`POST /feedbacks`** — 응답 본문 없이 201을 반환합니다.

| 요청 필드 | 필수 | 제약 |
| --- | --- | --- |
| `body` | 예 | 1~2,000자 |
| `email` | 아니오 | 이메일 형식, ≤ 320자 |
| `platform` | 아니오 | `IOS` · `ANDROID` · `WEB` |
| `appVersion` | 아니오 | ≤ 50자 |

- 로그인 상태면 `user_id`를 함께 저장합니다(선택 인증).
- 저장 후 Slack Incoming Webhook으로 알림을 보냅니다. webhook URL 미설정 시 알림만 생략하고, 알림 실패가 저장 성공(201)을 뒤집지 않습니다.
- 본문 상한이 프론트엔드(500자)와 다릅니다([§4-8](#4-8-검수-체크리스트) B4).

### 4-3-5. 인증 API — `Phase 1 · 구현`

구현은 완료됐고 MVP 프론트엔드는 호출하지 않습니다. 흐름과 토큰 정책은 [§4-5](#4-5-인증과-권한)에 정의합니다.

| 엔드포인트 | 요청 | 응답 |
| --- | --- | --- |
| `POST /auth/login/google` | `{idToken}` | `TokenResponse` |
| `GET /auth/me` | `Authorization: Bearer {access}` | `{id, nickname, profileImageUrl, status}` |
| `POST /auth/token/refresh` | `{refreshToken}` | `TokenResponse` |
| `POST /auth/logout` | `{refreshToken}` | 204 (멱등) |

`TokenResponse`: `{accessToken, refreshToken, expiresIn, tokenType: "Bearer"}`. `expiresIn`은 access 토큰 만료까지 남은 초입니다. `status`는 `ACTIVE` · `SUSPENDED` · `DELETED`입니다. 웹에서는 이 응답을 BFF가 가로채 httpOnly 쿠키로 보관하고 `refreshToken`을 JS에 노출하지 않습니다(토큰 세션은 [§4-5](#4-5-인증과-권한) 참조).

#### 게스트 데이터 마이그레이션 — `Phase 1 · 계획`

게스트가 기기에 쌓은 스토리·채팅의 소유권을 로그인 계정으로 이관합니다. 서버에는 게스트 식별 수단이 없으므로(콘텐츠 행에 device_id를 저장하지 않음) 클라이언트가 `localStorage`에 보관한 공개 ID 목록을 제출하는 방식입니다. 프론트엔드는 로그인 성공 직후 사용자 확인 없이 자동 호출합니다([`3-frontend.md`](./3-frontend.md) FE-SCREEN-008).

**`POST /auth/migrate`** — 인증 필수.

| 요청 필드 | 타입 | 규칙 |
| --- | --- | --- |
| `storyIds` | string[] | 스토리 공개 ID(UUID). 최대 100개(로컬 상한과 동일), 빈 배열 허용 |
| `chatIds` | string[] | 채팅 공개 ID(UUID). 최대 100개, 빈 배열 허용 |

동작 규칙:

- `user_id`가 NULL인 행에 요청자의 `user_id`를 설정합니다(클레임). 채팅은 참조하는 스토리의 소유자와 무관하게 독립적으로 이관합니다.
- **항목별 독립 처리·부분 성공.** 일부 항목이 충돌해도 전체를 롤백하지 않습니다.
- **효과 멱등.** 재호출해도 소유권 상태가 변하지 않아 별도 멱등 키가 없습니다. 다만 응답 `status`는 상태를 반영해 달라집니다 — 1회차 `MIGRATED`가 2회차에는 `ALREADY_OWNED`가 됩니다(효과는 동일, 응답은 현재 상태 기준).

응답 200: `{stories: MigrationResult[], chats: MigrationResult[]}` — `MigrationResult`는 `{id, status}`이며 `status`는 다음 4종입니다.

| `status` | 의미 |
| --- | --- |
| `MIGRATED` | 이번 요청으로 소유권이 설정됨 |
| `ALREADY_OWNED` | 이미 요청자 소유(재호출 등) |
| `CONFLICT` | 다른 회원 소유 — 이관하지 않음 |
| `NOT_FOUND` | 존재하지 않거나 삭제됨 |

오류: 400(UUID 형식 오류·배열 100개 초과), 401(미인증). 부분 실패는 오류가 아니라 `status`로 표현합니다.

#### 내 콘텐츠 목록 — `Phase 1 · 계획`

다른 기기에서 로그인해도 같은 서재를 보려면(US-9-4) 회원의 서재는 서버가 정본이어야 합니다. 회원 모드에서 `localStorage` 배치 조회(MVP 방식)를 대체합니다.

| 엔드포인트 | 응답 | 정렬 |
| --- | --- | --- |
| `GET /users/me/stories` | 스토리 카드 배열 — `POST /stories/batch` 응답과 동일 스키마 | 생성 최신순 |
| `GET /users/me/chats` | 채팅 카드 배열 — `POST /chats/batch` 응답과 동일 스키마 | 최근 활동순 |

쿼리 `limit`(기본 100, 최대 100). Phase 1은 페이지네이션 없이 상한 100을 유지하고, 초과분 처리는 Phase 2 스토리 피드 설계와 함께 확장합니다. 소프트 삭제된 항목은 제외합니다.

### 4-3-6. 로어북 — `Phase 1 · 구현`

**`GET /stories/lorebooks`** — 장르 공용 용어 사전 카탈로그 `{id, name, genre}[]`를 반환합니다. 쿼리 `genre`로 필터할 수 있습니다. 스토리 상세 응답의 `lorebooks`·`endings`와 함께 Phase 1 퀄리티 개선 범위이며 MVP 프론트엔드는 사용하지 않습니다.

### 4-3-7. 크레딧 — `Phase 1 · 계획`

크레딧은 회원 전용 재화입니다([`0-glossary.md §0-3-5`](./0-glossary.md)). 게스트는 크레딧 없이 기기 단위 체험 한도로 사용하고, 한도 소진 시 로그인으로 유도합니다. 지급량·소모량·체험 한도 수치는 미정(`계획`)이며 구조가 이 절의 계약입니다.

#### 조회·적립 API

| 엔드포인트 | 요청 | 응답 | 규칙 |
| --- | --- | --- | --- |
| `GET /users/me/credits` | — | `{balance}` | 인증 필수. 지갑이 없으면 0 반환 |
| `POST /users/me/credits/attendance` | — | `{rewarded, amount, balance}` | 인증 필수. KST 자정 기준 1일 1회. 이미 받았으면 `rewarded: false`로 200(멱등) |
| `GET /users/me/invite` | — | `{inviteCode, inviteUrl}` | 인증 필수. 내 초대 코드·공유 링크 조회 |

- **가입 보상** — 회원 최초 생성(find-or-create의 create) 시 서버가 자동 적립합니다. 별도 API가 없습니다.
- **초대 보상** — 피초대자가 `POST /auth/login/google` 요청의 선택 필드 `inviteCode`와 함께 가입을 완료하면 **초대자와 피초대자 양쪽에 적립**합니다. 자기 자신의 코드 제출, 이미 가입된 계정의 코드 제출은 무시합니다(오류 아님).
- 거래 내역 조회 API는 Phase 1 범위 밖입니다(원장은 운영·정산용).

#### 소모 규칙

소모는 별도 API가 아니라 기존 엔드포인트에 내장합니다. 회원 요청은 처리 시작 전에 **선차감**(pre-charge)하고, 생성이 실패로 끝나면 **자동 환불**(원장에 `REFUND` 행 추가)합니다.

**소모자 판정** — 소모 대상 엔드포인트는 선택적 인증([§4-5](#4-5-인증과-권한))으로 회원/게스트를 가릅니다. 유효 토큰이면 회원(지갑 차감), 아니면 게스트(기기 카운터). BFF 선제 재발급으로 만료 토큰이 익명 통과하지 않으므로 회원이 게스트로 오분류되지 않습니다.

**402 반환 형태** — 잔액 부족(회원)·한도 소진(게스트)이면 **SSE 스트림을 열기 전 동기 HTTP 응답으로 `402 PAYMENT_REQUIRED`**를 반환합니다([§4-6](#4-6-오류와-예외-처리)). 선차감·한도 검증이 AI 호출·스트림 시작보다 앞서므로, 채팅 턴도 기존 동기 404와 같은 계층에서 402를 반환합니다(스트림이 열린 뒤 `error` 이벤트로 주지 않음).

| 트리거 | 소모 시점 | 환불 조건 |
| --- | --- | --- |
| 스토리 간편 제작 | `POST /stories/simple`(컴파일) 시작 시 1회 | 컴파일이 성공(`stories` 반환)으로 끝나지 않으면 전액 환불(502, 부분 재호출 소진 실패 포함) |
| 채팅 턴 | `POST /chats/{chatId}/turns/stream` 시작 시 1턴 | `completed` 이벤트 없이 종료되면 전액 환불(`error` 이벤트·연결 끊김·불완전 종료 모두 포함) |
| AI 응답 재생성(KNK-443) | 채팅 턴과 동일 소모 | 채팅 턴과 동일 |

- 소모는 사용자 관점 "만들기·이어가기 1회" 단위입니다. **컴파일당 1회, 완성된 턴당 1회**이며, 컴파일 내부 부분 재호출(refill, [`5-ai-server.md`](./5-ai-server.md))은 추가 소모하지 않습니다(1회 컴파일에 포함).
- 스토리라인 생성·재생성(`POST /stories/simple/storylines`)은 소모하지 않습니다. 반복 생성 남용은 간극표(B8)로 둡니다.
- **게스트 체험과 회원 크레딧은 별개 카운터입니다.** 게스트가 한도를 소진하고 로그인하면 회원 지갑(가입 보상 등)으로 새로 시작하며, 소진된 기기 카운터는 크레딧 잔액에 영향을 주지 않습니다.

#### 게스트 체험 한도

- 기준: **스토리 제작 횟수 + 채팅 턴 수**(기기 단위, 수치 `계획`). 소모 트리거와 1:1 대응합니다.
- 판정: 소모 대상 엔드포인트에서 게스트 요청은 `X-Manyak-Device-Id` 기준 카운터(Redis)로 집계하고, 한도 소진 시 `402`를 반환합니다. 게스트의 소모 대상 요청은 device 헤더를 필수로 강화합니다(현행 best-effort에서 변경 — [§4-8](#4-8-검수-체크리스트) B8).
- 한도는 기기 기준이므로 헤더 변조·기기 변경으로 우회할 수 있습니다. Phase 1은 이 수준을 수용하고 남용 징후는 관측으로 추적합니다(B8).

#### 원장과 동시성

- 모든 증감은 `credit_transactions` 원장에 불변(append-only) 행으로 기록합니다. **상태 컬럼 대신 보상 행 방식**입니다 — 환불은 소모 행(`STORY_CREATION`·`CHAT_TURN`)의 수정이 아니라 그 행을 `ref_id`로 가리키는 `REFUND` 행 추가입니다.
- `credit_wallets.balance`는 원장 합계의 캐시입니다. 차감은 지갑 행 비관적 락(`PESSIMISTIC_WRITE` — 서버 기존 관례)으로 직렬화하고, 같은 트랜잭션에서 원장 행을 함께 씁니다.
- 보상 적립은 결정적 멱등 키로 중복을 차단합니다: `signup:{userId}` · `attendance:{userId}:{KST날짜}` · `invite:{초대자userId}:{피초대자userId}`. 키는 원장 유니크 제약입니다.
- `reason` enum: `SIGNUP_REWARD` · `INVITE_REWARD` · `ATTENDANCE_REWARD`(적립), `STORY_CREATION` · `CHAT_TURN`(소모 — 재생성 포함), `REFUND`(환불), `PURCHASE`(Phase 3 예약).
- 소모 행은 `ref_type`·`ref_id`로 연관 리소스(story·chat·`ai_call_logs`)를 참조합니다. 선차감 후 서버 중단으로 환불 행이 누락되면 `ai_call_logs` 대사(배치)로 복구합니다.

## 4-4. 데이터 모델

### 식별자 정책

- **외부 노출 식별자는 공개 UUID(`public_id`)만 사용합니다.** 내부 Long PK는 FK·조인 전용이며 API 응답, 로그, 분석 프로퍼티에 싣지 않습니다([`0-glossary.md §0-4`](./0-glossary.md)). 순번 PK 노출로 인한 IDOR을 차단하는 장치입니다.
- 공개 식별자를 쓰는 리소스: 스토리(`story_id`), 채팅(`chat_id`), 사용자(`public_id`).
- 간편 제작 진행 ID(`simpleCreationId`)와 태그·스토리라인 ID는 Long을 그대로 노출합니다. 생성 퍼널의 임시 리소스로 소유 개념이 없기 때문입니다.

### 삭제 정책

- 스토리와 채팅은 `deleted_at` 기록으로 소프트 삭제합니다. 삭제된 리소스는 상세 조회에서 404, 배치 조회에서 제외됩니다.
- 삭제 API는 이미 삭제된 리소스에 404를 반환합니다. 클라이언트는 404를 "이미 삭제됨"으로 해석합니다([`3-frontend.md §3-7`](./3-frontend.md)).

### 테이블 구성

스키마의 정본은 Flyway 마이그레이션(`src/main/resources/db/migration/`, 현재 V22)이며, 컬럼 상세와 ER 다이어그램은 서버 레포 `dbdoc/`(tbls 자동 생성)이 소유합니다. 여기서는 도메인 그룹과 역할만 고정합니다.

| 그룹 | 테이블 | 역할 |
| --- | --- | --- |
| 사용자 | `users` | 계정. `public_id`(UUID) · `nickname` · `profile_image_url`(nullable) · `profile_thumbnail_base64`(nullable, 목록·미리보기용 저해상도) · `status` |
| 사용자 | `social_accounts` | 소셜 연동. `(provider, provider_user_id)` 유니크 |
| 스토리 | `stories` | 스토리 메타. `public_id`, 제목·소개·장르, `user_id`(소유자, nullable — NULL이면 게스트 생성분), `deleted_at` |
| 스토리 | `story_settings` | 스토리 설정 통글 4필드(1:1) |
| 스토리 | `story_start_settings` | 시작 설정: `name` · `prologue` · `start_situation`(1:1) |
| 스토리 | `story_suggested_inputs` | 추천 입력(시작 설정별 목록) |
| 간편 제작 | `story_creation_tags` | 태그. `PREDEFINED` · `CUSTOM`, 카테고리 3종 |
| 간편 제작 | `story_creation_sessions` | 간편 제작 진행(퍼널 1회) |
| 간편 제작 | `story_creation_session_tags` | 진행이 선택한 태그(유니크) |
| 간편 제작 | `story_creation_storylines` | AI 생성 스토리라인 후보 |
| 간편 제작 | `story_creation_storyline_recommended_infos` | 스토리라인별 추천 추가 정보 |
| 간편 제작 | `story_creation_storyline_ratings` | 스토리라인 평가(GOOD·BAD, 사용자당 1건) |
| 채팅 | `story_chats` | 채팅. `public_id`(UUID), 진행 턴 수, `user_id`(소유자, nullable), `deleted_at` |
| 채팅 | `story_messages` | 메시지 행. `role`: `USER` · `ASSISTANT` · `SYSTEM` |
| 채팅 | `story_choices` | 메시지별 선택지(3개, 선택 여부 기록) |
| 로어북 | `lorebooks` | `Phase 1 · 구현` 장르 공용 용어 사전 |
| 로어북 | `story_lorebooks` | `Phase 1 · 구현` 스토리-로어북 연결 |
| 스토리 | `story_endings` | `Phase 1 · 구현` 엔딩(제목·내용·도달 조건) — 구조 재정의 예정([§4-8](#4-8-검수-체크리스트) B5) |
| 피드백 | `feedbacks` | 피드백 본문·이메일·플랫폼·앱 버전 |
| 크레딧 | `credit_wallets` | `Phase 1 · 계획` 사용자별 지갑. `user_id`(unique FK) · `balance`(원장 합계 캐시) |
| 크레딧 | `credit_transactions` | `Phase 1 · 계획` 불변 원장. `wallet_id` · `amount`(적립 양수/소모 음수) · `reason`(enum) · `idempotency_key`(unique, nullable) · `ref_type`/`ref_id` |
| 크레딧 | `users.invite_code` | `Phase 1 · 계획` 사용자당 고유 초대 코드(unique, nullable 컬럼 추가) |
| 관측 | `ai_call_logs`(+`_prompt_versions`) | AI 호출 이력([§4-7](#4-7-운영과-관측)) |

### 잔존 표기

용어집 정렬(V20~V22)로 `story_creation_examples` → `story_creation_storylines`, `story_play_sessions` → `story_chats`, `turn_index` → `turn_number` 개명은 끝났습니다. 다음 표기는 아직 남아 있으며, 신규 명명에는 쓰지 않습니다([`0-glossary.md §0-1`](./0-glossary.md)의 점진 적용 원칙).

| 잔존 표기 | 위치 | 공식 표기 |
| --- | --- | --- |
| `creation_session_id` | 간편 제작 FK 컬럼 | `creation_id` 계열 |

## 4-5. 인증과 권한

**상태: `Phase 1 · 구현`.** 인증 스택(Google 로그인, JWT, refresh 저장소)은 서버에 구현 완료됐지만, MVP는 전원 게스트로 동작하므로 프론트엔드가 호출하지 않습니다([`3-frontend.md §3-13`](./3-frontend.md) G1). 로그인 도입 시 이 섹션이 계약 기준이 됩니다.

### Google 로그인 흐름

1. 클라이언트가 Google ID 토큰을 `POST /auth/login/google`로 보냅니다.
2. 서버가 서명(JWKS), 만료, issuer(`https://accounts.google.com`), audience(허용 client ID 목록)를 검증합니다.
3. `(provider, provider_user_id)`로 사용자를 찾거나 새로 만듭니다(find-or-create).
4. access·refresh 토큰을 발급합니다.

### 가입 프로필 발급 — `Phase 1 · 계획`

현행 구현은 닉네임을 Google `name` → 이메일 local-part → "사용자" 순서로 정하고, 프로필 이미지는 Google `picture` URL을 그대로 저장합니다. Phase 1부터 실명·외부 사진 노출을 피하기 위해 랜덤 발급으로 교체합니다([§4-8](#4-8-검수-체크리스트) B7).

| 항목 | 규칙 |
| --- | --- |
| 닉네임 | 한국어 형용사+명사 조합 랜덤 생성(예: "용감한 문어"). 50자 이내, 중복 허용(식별은 `public_id`) |
| 프로필 이미지 | 팀이 사전 제작한 프리셋 이미지 중 랜덤 배정. `profile_image_url`에 자산 URL, `profile_thumbnail_base64`에 저해상도 썸네일을 저장 |
| Google 클레임 | `name`·`picture`를 프로필에 사용하지 않음. `email`은 `social_accounts`에만 저장 |

현행 구현으로 이미 Google `name`·`picture`가 저장된 기존 회원은 백필(재발급) 여부를 KNK-440 구현 시 결정합니다(신규 가입분은 랜덤 발급 우선 적용).

닉네임·프로필 이미지 변경 기능은 Phase 1 범위 밖입니다(백로그).

### 토큰 정책

| 항목 | 값 |
| --- | --- |
| access 토큰 | JWT(HS256 대칭키), TTL 30분, `sub`에 사용자 `public_id` |
| refresh 토큰 | 불투명 랜덤 문자열, TTL 14일, Redis 저장 |
| 재발급 | refresh는 1회용. 재발급 시 새 쌍을 발급하고 이전 값을 즉시 폐기(회전) |
| 재사용 탐지 | 이미 회전된 refresh가 다시 오면 같은 토큰 계열(family) 전체를 폐기 |
| 로그아웃 | 제시된 refresh를 폐기. 이미 폐기된 토큰도 204(멱등) |

### 선택적 인증

- 스토리·간편 제작·채팅·피드백 엔드포인트는 모두 익명을 허용합니다.
- `Authorization: Bearer` 토큰이 유효하면 해당 요청의 생성 리소스에 `user_id`를 귀속합니다. 토큰이 없거나 무효(만료·위조)면 401을 반환하지 않고 익명으로 통과시킵니다.
- 인증을 강제하는 엔드포인트: `GET /auth/me`(MVP). Phase 1 추가분 `POST /auth/migrate` · `GET /users/me/stories` · `GET /users/me/chats`(`Phase 1 · 계획`). 토큰 없음·만료·위조·사용자 삭제 모두 401입니다.

### 소유권과 권한 — `Phase 1 · 계획`

`user_id` 소유 개념이 도입되면 소유자가 있는 리소스는 소유자만 변경할 수 있습니다. 선택적 인증에서 `user_id`를 확인해 다음을 적용합니다.

| 대상 | 규칙 |
| --- | --- |
| `DELETE /stories/{storyId}` · `DELETE /chats/{chatId}` · `POST /chats/{chatId}/turns/stream` · `PATCH /stories/{storyId}`(수정, KNK-442) | 리소스의 `user_id`가 NULL이면 익명 허용(현행 유지). NULL이 아니면 요청자 `user_id`와 일치할 때만 허용하고, 불일치·미인증이면 `403`을 반환 |
| 조회(`GET /stories/{storyId}` 등) | 공개 리소스이므로 소유권 검증 없이 유지 |

`user_id`가 NULL인 리소스는 여전히 UUID를 아는 누구나 클레임·변경할 수 있습니다(게스트 공유 전제). 이관 완료 후에는 소유자가 생기므로 타인이 변경할 수 없습니다.

### 토큰 세션과 재발급 — `Phase 1 · 계획`

- 웹은 access·refresh 토큰을 브라우저 JS에 노출하지 않고 BFF 프록시가 httpOnly 쿠키로 보관합니다([`3-frontend.md §3-8`](./3-frontend.md)). 기존 `POST /auth/token/refresh` · `POST /auth/logout`의 `{refreshToken}` 본문 계약은 유지하되, 그 값을 채우는 주체가 클라이언트 JS에서 BFF로 바뀝니다(계약 무변경, 호출 주체만 변경).
- **선제 재발급.** BFF는 access TTL(30분) 만료가 임박하면 백엔드 요청 전에 `POST /auth/token/refresh`로 갱신해 만료 토큰을 백엔드로 보내지 않습니다. 이로써 회원 요청이 선택적 인증에서 익명으로 통과해 `user_id=NULL`로 저장되는 고아 콘텐츠를 방지합니다.
- 재발급 실패(refresh 만료·회전 재사용 탐지로 family 폐기)면 BFF가 세션 쿠키를 폐기하고 게스트 모드로 되돌립니다.

### 보안 설정

- 세션 없는 stateless 구성입니다. CSRF는 비활성화하고 CORS 허용 origin은 환경 변수로 주입합니다([§4-7](#4-7-운영과-관측)).
- 권한(role) 구분은 없습니다. 관리자 API는 MVP·Phase 1 범위 밖입니다.
- 매핑되지 않은 경로는 500이 아니라 404로 응답합니다.

## 4-6. 오류와 예외 처리

### 오류 응답 계약

모든 오류는 다음 `ApiErrorResponse` 형태로 응답합니다. 프론트엔드 처리 계약은 [`3-frontend.md §3-8`](./3-frontend.md)과 정합합니다.

```json
{
  "timestamp": "2026-07-03T12:00:00Z",
  "status": 400,
  "code": "BAD_REQUEST",
  "message": "요청 값이 올바르지 않습니다.",
  "path": "/api/v1/chats/{chatId}/turns/stream",
  "details": [
    { "field": "userInput", "message": "크기가 1에서 3000 사이여야 합니다" }
  ]
}
```

- `details`는 필드 검증 실패에만 포함합니다.
- `message`에 스택트레이스나 내부 구현 정보를 싣지 않습니다.

### 상태 코드 카탈로그

`code`는 HTTP 상태의 표준 이름을 사용합니다.

| 상태 | code | 발생 상황 |
| --- | --- | --- |
| 400 | `BAD_REQUEST` | 본문 형식 오류, 필드 검증 실패 |
| 401 | `UNAUTHORIZED` | (인증 필수 경로) 토큰 없음·만료·위조, 사용자 없음 |
| 402 | `PAYMENT_REQUIRED` | `Phase 1 · 계획` 크레딧 잔액 부족(회원), 체험 한도 소진(게스트) — [§4-3-7](#4-3-api-계약) |
| 403 | `FORBIDDEN` | `Phase 1 · 계획` 소유자가 있는 리소스에 대한 타인·익명의 변경 시도 — [§4-5](#4-5-인증과-권한) |
| 404 | `NOT_FOUND` | 리소스 없음·이미 삭제됨, 매핑되지 않은 경로 |
| 405 | `METHOD_NOT_ALLOWED` | 지원하지 않는 HTTP 메서드 |
| 406 | `NOT_ACCEPTABLE` | Accept 협상 실패 |
| 409 | `CONFLICT` | 이미 스토리를 생성한 간편 제작 진행으로 재생성 시도 |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | 지원하지 않는 Content-Type |
| 500 | `INTERNAL_SERVER_ERROR` | 예상하지 못한 서버 오류 |
| 502 | `BAD_GATEWAY` | AI 서버 호출 실패(스토리라인 생성·컴파일) |

### SSE 오류 중계

채팅 스트림은 HTTP 오류 대신 SSE `error` 이벤트로 실패를 전달합니다([§4-3-3](#4-3-api-계약)).

- AI 서버가 `error` 이벤트를 보내면 그 `code`·`message`를 그대로 중계합니다.
- AI 이벤트 외 실패(네트워크, idle 타임아웃, 저장 실패)는 `AI_STREAM_FAILED`로 분류합니다.
- 스트림 시작 전 실패(채팅 없음, 검증 실패)는 일반 `ApiErrorResponse`로 응답합니다.

### 로그·Sentry 기준

- 5xx는 스택트레이스와 함께 ERROR로 남기고 Sentry로 보냅니다.
- 예상 가능한 4xx(`BAD_REQUEST` · `NOT_FOUND` · `CONFLICT` 등)는 스택트레이스 없이 요약만 WARN 이하로 남기고 Sentry로 보내지 않습니다. 수집 기준의 원천은 [`6-analytics.md §6-6-6`](./6-analytics.md)입니다.

## 4-7. 운영과 관측

### 상관관계 식별자

모든 요청은 상관관계 필터를 거쳐 MDC에 식별자를 적재하고, 구조화 로그·Sentry·`ai_call_logs`가 같은 값을 공유합니다. 식별자 정책의 원천은 [`6-analytics.md §6-2·§6-6-3`](./6-analytics.md)입니다.

| MDC 필드 | 값 | 규칙 |
| --- | --- | --- |
| `request_id` | `req_` + UUID(하이픈 제거) | 요청 헤더 값 우선, 없으면 생성. 응답 헤더로 echo |
| `session_id` | `X-Manyak-Session-Id` | 없으면 `unknown` |
| `device_id_hash` | `device_hash_` + SHA-256(pepper + 원본) 앞 16자 hex | 원본 `device_id`는 저장하지 않음. pepper는 환경 변수 |

AI 서버 호출 시 다음 헤더를 forward합니다. 값이 `unknown`이면 싣지 않습니다.

| forward 헤더 | 값 |
| --- | --- |
| `X-Manyak-Request-Id` | MDC `request_id` |
| `X-Manyak-Session-Id` | MDC `session_id` |
| `X-Manyak-Device-Id-Hash` | MDC `device_id_hash` |

원본 `X-Manyak-Device-Id`는 forward하지 않습니다. PII가 서버 경계를 넘지 않게 하는 구조적 장치입니다.

### 구조화 로그

- 모든 로그는 JSON으로 남깁니다(Logstash Logback Encoder). MDC의 상관관계 식별자는 인코더가 자동 부착합니다.
- API 요청 로그 필터가 endpoint, HTTP 메서드, 상태 코드, 소요 시간을 기록합니다.
- 비즈니스 이벤트 로그는 snake_case 필드로 남깁니다. 예: 턴 저장 시 `user_message_saved` · `ai_response_saved`(`chat_id`, `story_id`, `turn_number`, `ai_call_log_id`).
- 사용자 입력 원문은 로그에 싣지 않고 길이 구간(`message_length_bucket`)만 남깁니다([`6-analytics.md §6-7`](./6-analytics.md)).
- CloudWatch 로그 이벤트 카탈로그의 원천은 [`6-analytics.md §6-6-5`](./6-analytics.md)입니다.

### AI 호출 계약과 `ai_call_logs`

백엔드는 AI 서버 호출 1회당 `ai_call_logs`에 1행을 기록합니다. 기록 기준의 원천은 [`6-analytics.md §6-6-9`](./6-analytics.md)이며, 프롬프트·모델 상세는 [`5-ai-server.md`](./5-ai-server.md)가 소유합니다.

**호출 경로와 타임아웃**

| feature | AI 엔드포인트 | 방식 | 타임아웃 |
| --- | --- | --- | --- |
| `STORYLINE_GENERATION` | `POST /api/v1/story/storylines` | 동기 REST | 30초 |
| `STORY_COMPLETION` | `POST /api/v1/story/compile` | 동기 REST | 120초 |
| `CHAT_RESPONSE` | `POST /api/v1/chat/turns` | SSE | 연결 5초, 이벤트 간 60초 |
| `CHOICE_GENERATION` | — | 예약(미사용) | — |

**와이어 표기** — AI 계약은 이원 표기가 공식입니다([`0-glossary.md §0-4`](./0-glossary.md)). story 계열 요청·응답은 snake_case(`genre_tags`, `selected_storyline`, `recommended_infos`)이고, chat SSE `completed` 페이로드는 camelCase(`aiOutput`, `choices`)입니다. 현재 AI 와이어의 `story`(스토리라인 본문)·`extra_info` 필드는 용어집 기준으로 정렬 예정입니다([§4-8](#4-8-검수-체크리스트) B2).

**기록 필드** — 행마다 feature, 상태(`STARTED` → `SUCCEEDED` · `FAILED`), 상관관계 식별자(`request_id`, `device_id_hash`, `session_id`), 연결 리소스(스토리·채팅·턴), AI 응답 meta(provider, model, 입·출력 토큰 수, `retry_count`), 프롬프트 버전 맵(JSONB), `latency_ms`, 실패 시 `error_code`와 `sentry_event_id`를 기록합니다. 채팅 턴 번호는 저장 트랜잭션이 확정한 값을 사후 반영합니다.

### 서버 분석 이벤트 — `계획`

[`6-analytics.md §6-4`](./6-analytics.md)가 정의한 `server_*` 분석 이벤트(MVP 6종: 스토리라인 생성·채팅 응답·피드백 제출의 성공·실패, `Phase 1 · 계획` 4종: 로그인·마이그레이션 성공·실패)는 **아직 구현되지 않았습니다.** 현재 서버 측 계측은 구조화 로그와 `ai_call_logs`로만 수행하며, Amplitude 서버 이벤트 발행은 후속 과제입니다([§4-8](#4-8-검수-체크리스트) B1). Phase 1 로그인 이벤트가 P0로 지정되므로 이 발행 인프라 구현이 계정 시스템의 선행 조건입니다.

### 환경 변수

값은 배포 파이프라인이 주입하며 문서·레포에 싣지 않습니다.

| 환경 변수 | 필수 | 용도 |
| --- | --- | --- |
| `MANYAK_DB_URL` · `MANYAK_DB_USERNAME` · `MANYAK_DB_PASSWORD` | 예 | PostgreSQL 연결 |
| `SPRING_DATA_REDIS_HOST` · `SPRING_DATA_REDIS_PORT` | 예(운영) | Redis 연결. 로컬 기본 `localhost:6379` |
| `MANYAK_AI_BASE_URL` | 예 | AI 서버 base URL(scheme 포함) |
| `MANYAK_CORS_ALLOWED_ORIGINS` | 예 | CORS 허용 origin(콤마 구분) |
| `MANYAK_AUTH_JWT_SECRET` | 예 | access JWT HS256 키(32바이트 이상) |
| `MANYAK_GOOGLE_CLIENT_IDS` | 예 | Google OAuth client ID 목록(콤마 구분) |
| `MANYAK_ANALYTICS_DEVICE_ID_PEPPER` | 아니오 | `device_id` 해시 pepper. 미설정 시 무염 해시 |
| `MANYAK_SLACK_FEEDBACK_WEBHOOK_URL` | 아니오 | 피드백 Slack 알림. 미설정 시 알림 생략 |
| `SENTRY_DSN` · `SENTRY_ENVIRONMENT` · `SENTRY_TRACES_SAMPLE_RATE` | 아니오 | Sentry 연동. DSN 미설정 시 비활성 |

### 헬스체크·API 문서·배포

- 헬스체크: `GET /actuator/health`(종합), `/actuator/health/liveness`(컨테이너 활성), `/actuator/health/readiness`(DB·Redis 준비).
- OpenAPI: `GET /v3/api-docs`, Swagger UI `GET /swagger-ui.html`. 운영 환경에서는 비공개입니다.
- 배포: Docker 이미지 빌드 후 `dev`는 GHCR, `main`은 AWS ECR(OIDC)로 푸시합니다. DB 마이그레이션은 앱 기동 시 Flyway가 자동 실행합니다.
- 스키마 문서: 마이그레이션 변경 시 CI가 `dbdoc/`(tbls) 드리프트를 검사합니다.

## 4-8. 검수 체크리스트

### 검수 수단

- 통합·단위 테스트: 서버 레포에서 `./gradlew test`.
- 수동 검증: 서버 레포 `http/` 디렉터리의 `.http` 스크립트(도메인별 요청 모음).
- 스키마 확인: Swagger UI(`/swagger-ui.html`, 비운영 환경)와 `dbdoc/`.

### US ↔ API 매핑

| US | 흐름 | 검증 엔드포인트 |
| --- | --- | --- |
| US-2-1 · 2-4 · 2-6 | 스토리 목록·삭제 | `POST /stories/batch`, `DELETE /stories/{storyId}` |
| US-3-1 ~ 3-4 | 키워드 선택 | `GET /stories/simple/tags`, `POST /stories/simple/storylines` |
| US-3-5 ~ 3-8 | 스토리라인 선택·평가 | `POST /stories/simple/storylines`, `PUT·DELETE …/rating` |
| US-3-9 ~ 3-13 | 추가 정보·완성 | `POST /stories/simple`, `POST /chats` |
| US-4-1 ~ 4-4 | 스토리 상세·채팅 시작·삭제 | `GET·DELETE /stories/{storyId}`, `POST /chats` |
| US-5-1 ~ 5-3 | 채팅 목록·재개·삭제 | `POST /chats/batch`, `GET·DELETE /chats/{chatId}` |
| US-6-1 ~ 6-8 | 채팅 플레이 | `GET /chats/{chatId}`, `POST /chats/{chatId}/turns/stream` |
| US-7-1 ~ 7-3 | 피드백 | `POST /feedbacks` |
| US-9-1 · 9-5 | 로그인·로그아웃 `Phase 1 · 구현` | `POST /auth/login/google`, `POST /auth/logout` |
| US-9-2 | 랜덤 프로필 발급 `Phase 1 · 계획` | `POST /auth/login/google`(가입 시 발급), `GET /auth/me` |
| US-9-3 | 게스트 데이터 이관 `Phase 1 · 계획` | `POST /auth/migrate` |
| US-9-4 | 기기 간 서재 `Phase 1 · 계획` | `GET /users/me/stories`, `GET /users/me/chats` |
| US-10-1 | 잔액 확인 `Phase 1 · 계획` | `GET /users/me/credits` |
| US-10-2 | 크레딧 보상 `Phase 1 · 계획` | 가입 자동 적립, `POST /users/me/credits/attendance`, `GET /users/me/invite` + `POST /auth/login/google`(`inviteCode`) |
| US-10-3 | 소모량 사전 고지 `Phase 1 · 계획` | 소모 표시 UI([`3-frontend.md`](./3-frontend.md) FE-SCREEN-008) — 단가는 수치 확정 후 표기(`계획`) |
| US-10-4 | 부족 안내 `Phase 1 · 계획` | `POST /stories/simple`·`POST /chats/{chatId}/turns/stream` 402 |
| US-10-5 | 게스트 체험 한도 `Phase 1 · 계획` | 소모 엔드포인트의 기기 단위 카운터, 402 |

### 엔드포인트 검수 기준

- 배치 조회는 존재하지 않는 ID를 오류 없이 제외하고, 100개 초과·빈 배열 요청에 400을 반환해야 합니다.
- 삭제는 최초 204, 재시도 404를 반환하고, 삭제된 리소스가 상세·배치 조회에서 사라져야 합니다.
- 간편 제작은 태그 없이 스토리라인 생성 요청 시 400, 같은 진행으로 두 번째 스토리 생성 시 409, AI 실패 시 502를 반환해야 합니다.
- 스토리라인 평가는 설정 → 같은 값 재설정 → 취소 → 재취소가 모두 성공해야 합니다(취소 멱등).
- 채팅 스트림은 `started` → `token` → `completed` 순서로 도착하고, `completed`의 `aiOutput`이 이후 `GET /chats/{chatId}`의 마지막 턴과 일치해야 합니다.
- 채팅 스트림 실패 시 `error` 이벤트에 `code`·`message`가 실려야 하며, 실패한 턴은 저장되지 않아야 합니다.
- 오류 응답이 모든 실패 경로에서 `ApiErrorResponse` 형태를 유지해야 합니다.
- 모든 응답에 `X-Manyak-Request-Id` 헤더가 있어야 하고, 식별 헤더 없는 요청도 거부되지 않아야 합니다.
- 사용자 입력 원문이 로그·Sentry에 남지 않아야 합니다([`6-analytics.md §6-8-5`](./6-analytics.md)).
- `Phase 1` 마이그레이션은 같은 요청 2회에 결과가 불변해야 합니다(1회차 `MIGRATED` → 2회차 `ALREADY_OWNED`). 다른 회원 소유 ID는 `CONFLICT`, 삭제된 ID는 `NOT_FOUND`, 101개 배열은 400을 반환해야 합니다.
- `Phase 1` 내 콘텐츠 목록·마이그레이션은 토큰 없음·만료·위조에 401을 반환해야 합니다.
- `Phase 1` 소유권 검증: 이관으로 `user_id`가 설정된 스토리·채팅은 소유자만 삭제·턴 진행이 가능하고, 타인·익명 요청에 403을 반환해야 합니다. `user_id`가 NULL인 리소스는 익명 삭제·진행이 유지돼야 합니다.
- `Phase 1` 크레딧: 출석 적립은 같은 KST 날짜에 2회 요청 시 두 번째가 `rewarded: false`(잔액 불변)여야 합니다. 초대 적립은 같은 (초대자, 피초대자) 쌍으로 1회만 발생해야 합니다.
- `Phase 1` 크레딧: 잔액 부족 회원·한도 소진 게스트의 컴파일·턴 요청에 402를 반환하고 AI 호출이 시작되지 않아야 합니다. 선차감 후 AI 실패 시 원장에 `REFUND` 행이 추가되고 잔액이 복원돼야 합니다.
- `Phase 1` 크레딧: 동시 턴 요청 2건이 잔액 1턴분만 남은 지갑에서 경합하면 1건만 성공하고 1건은 402여야 합니다(비관적 락).

### 스펙-구현 간극과 계획

문서 기준과 구현이 다르거나 구현이 남은 지점입니다.

| # | 항목 | 현황 | 방향 |
| --- | --- | --- | --- |
| B1 | 서버 분석 이벤트 | [`6-analytics.md §6-4`](./6-analytics.md)의 `server_*` 6종 미구현. 서버 계측은 구조화 로그·`ai_call_logs`뿐 | Amplitude 서버 이벤트 발행을 후속 구현 |
| B2 | AI 와이어 필드 정렬 | AI 계약의 `story`(스토리라인 본문)·`extra_info`가 용어집 기준(`storyline` · `additional_info`)과 불일치. 클라이언트 와이어는 정렬 완료 | AI 서버와 동시 배포로 정렬(KNK-375) |
| B4 | 피드백 본문 상한 | 서버 2,000자 vs 프론트엔드 500자([`3-frontend.md §3-13`](./3-frontend.md) G6) | 상한 정책 정렬 |
| B5 | 엔딩 스키마 재정의 | 현행 `story_endings`(제목·내용·`condition_text` 자유 텍스트, `Phase 1 · 구현`)는 팀 결정(2026-07-04)과 불일치 — 엔딩은 스토리당 3개(`ending_type` `HAPPY` · `NORMAL` · `BAD` 각 1개), 본문 사전 작성 없이 `ending_requirement`(최소 턴 수 · 목적 달성은 하드 AND, 거쳐온 주요 사건은 AI 정성 판정 입력 — 경유 강제 아님) + `ending_epilogue`(출력 가이드)로 정의. 주요 사건(`main_event`: 이름 · 설명 · `key_sentence`) 스키마는 미구현. 엔딩 도달 표시용 메타(채팅 상세 턴·SSE `completed`의 엔딩 필드, 스토리 상세의 본 엔딩 표시)도 미정의 | `Phase 1 · 계획` — 퀄리티 스펙 반영(KNK-444)에서 스키마·API·도달 메타 정의 |
| B6 | 크레딧 도입 시 인증 정책 정합 | 소모 강제·한도 판정 지점을 [§4-3-7](#4-3-api-계약)이 정의함(회원=선차감, 게스트=기기 카운터, 402). 선택적 인증 구조는 유지 | `Phase 1 · 계획` — 계약 정의 완료, 구현 남음 |
| B7 | 가입 프로필 발급 재정의 | 현행은 Google `name`·`picture` 클레임을 닉네임·프로필 이미지에 사용. 팀 결정은 랜덤 발급(형용사+명사 닉네임, 프리셋 이미지 랜덤 배정) — [§4-5](#4-5-인증과-권한) | `Phase 1 · 계획` — 계정 스펙(KNK-440) 기준으로 구현 교체 |
| B8 | 게스트 한도 우회와 스토리라인 남용 | 체험 한도가 기기(device 헤더) 기준이라 헤더 변조·기기 변경으로 우회 가능. 스토리라인 생성·재생성은 무료라 반복 호출로 AI 비용 남용 가능 | `Phase 1 · 계획` — Phase 1은 수용하고 관측(호출량 급증 알림)으로 추적. 강화(rate limit 등)는 후속 결정 |

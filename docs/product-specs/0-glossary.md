# 0-GLOSSARY

이 문서는 **마냑 서비스의 모든 레포지토리와 문서에서 통일해 사용할 용어**를 정의하는 용어 스펙입니다. 같은 개념에 서로 다른 단어를 쓰지 않도록 공식 한국어 용어, 영문 식별자, 지양 표기를 확정합니다. 새 코드, 새 문서, 새 이벤트를 작성할 때 이 문서의 용어를 기준으로 삼습니다.

```text
§0-1  목적과 적용 범위
§0-2  용어 결정 원칙
§0-3  핵심 도메인 용어
§0-4  계층별 표기 컨벤션
§0-5  동명이의·예약어 규칙
§0-6  AI 서버 내부 용어
§0-7  참고 근거
```

| 항목 | 값 |
| --- | --- |
| 버전 | v0.1 |
| 작성일 | 2026-07-02 |
| 대상 | 마냑 전 레포지토리 (manyak-web · manyak-server · manyak-ai · llm-wiki · knk-harness) |
| 작성 목적 | 레포지토리 간 용어 불일치를 없애고, 앞으로의 개발에서 통일된 단어 사용 기준을 정의한다. |

## 0-1. 목적과 적용 범위

이 문서는 다음 범위에 적용합니다.

1. **제품·문서 용어(한국어)** — 스펙 문서, 커밋 메시지, PR, UI 카피에서 쓰는 도메인 단어.
2. **코드 식별자(영문)** — API 필드, DB 테이블·컬럼, 로그 필드, 분석 이벤트·프로퍼티, 모듈·타입 이름.

적용 규칙은 다음과 같습니다.

- **신규 작성 강제, 기존 코드 점진 적용.** 새로 만드는 이름은 이 문서를 따릅니다. 이미 배포된 계약(API 필드, DB 컬럼, 적재된 이벤트)은 마이그레이션 비용을 고려해 별도 과제로 정리하고, 이 문서는 대응 관계만 고정합니다.
- **확정된 용어만 정의합니다.** 의사결정 대기 상태의 초안 용어는 편입하지 않고, 명세가 확정된 뒤 반영합니다.

## 0-2. 용어 결정 원칙

여러 후보 중 공식 용어를 고를 때 다음 순서로 판단했습니다. 새 용어를 추가할 때도 같은 순서를 적용합니다.

1. **개념이 다르면 단어도 다르게.** 서로 다른 개념(예: 추천 입력 vs 선택지)이 같은 단어를 공유하지 않습니다.
2. **데이터 계층의 현행 표기를 우선.** DB·API·이벤트에 이미 넓게 자리 잡은 표기를 UI 카피보다 우선합니다.
3. **업계 표준과 정합.** 대응하는 업계 표준 용어(chat, turn, choice, lorebook, tag, anonymous user 등)가 있으면 따릅니다. 근거는 §0-7에 정리합니다.
4. **미래 용어와 충돌 예방.** 로드맵에 예약된 이름(예: 트리거형 `keyword_notes`)과 겹치는 표기를 피합니다.

## 0-3. 핵심 도메인 용어

각 표의 `지양 표기`는 같은 개념에 쓰지 않을 단어입니다. 문학적 서술이나 UI 감성 카피에서의 예외는 각 항목에 명시합니다.

### 0-3-1. 콘텐츠 단위

| 공식 용어 | 영문 식별자 | 정의 | 지양 표기 |
| --- | --- | --- | --- |
| 스토리 | `story`, `story_id` | 사용자가 제작·플레이하는 세계관·설정 콘텐츠 단위. 외부 노출 식별자는 UUID `story_id` | "이야기"(API 문서·식별자·오류 메시지), "세계관"(스토리 전체를 가리킬 때) |
| 스토리라인 | `storyline`, `storyline_id` | 간편 제작에서 AI가 생성하는 이야기 전개 방향 후보(3개 중 택1). 스토리가 되기 전 단계의 산출물 | `example`(레거시 표기), 스토리라인 본문을 담는 `story` 필드 |
| 스토리 설정 | `story_settings` | 통글 4필드 묶음: `world_setting`(세계관) · `character_setting`(등장인물) · `user_role_setting`(주인공) · `rule_setting`(규칙) | `prompt_settings`(컴파일 내부 세분 스키마 전용, §0-6) |
| 통글 | (한국어 고유 조어) | 섹션 헤더로 구분한 단일 마크다운 필드. 스토리 설정의 저장·전달 단위 | — |
| 시작 설정 | `start_settings` | 채팅 시작 장면 3필드: `name`(상황 이름) · `start_situation`(시작 상황) · `prologue`(프롤로그) | 단수·복수, 접두어가 다른 변형 신설 금지 |
| 프롤로그 | `prologue` | 채팅 시작 시 먼저 보여주는 도입 서사 텍스트 | "채팅 첫 메시지", "도입부 내레이션", first message, greeting |
| 추천 입력 | `suggested_inputs` | 채팅 시작 화면에서 제안하는 첫 입력 후보 문구(3개). 선택지(§0-3-3)와 다른 개념 | `recommendedInputs`, 선택지를 "추천 입력"으로 부르는 것 |
| 태그 | `tag`, `tag_id` | 간편 제작에서 선택하거나 직접 추가하는 스토리 속성. `PREDEFINED`(제공)와 `CUSTOM`(직접 추가)으로 나뉨 | "키워드"(코드·데이터·이벤트·문서. UI 카피 전환은 별도 논의) |
| 태그 카테고리 | `category`: `GENRE` · `PROTAGONIST` · `SUPPORTING_CHARACTER` | 태그 분류 3종: 장르 · 주인공 특징 · 주변 인물 특징 | `tag_type` |
| 추가 정보 | `additional_infos` | 사용자가 스토리라인에 첨부하는 보강 정보(추천 채택분 포함, 총 13개 상한) | `extra_info` |
| 추천 추가 정보 | `recommended_infos` | 스토리라인마다 AI가 제안하는 추가 정보 후보 3개 | "추천 질문"(`questions`, 레거시) |
| 로어북 | `lorebook` | 장르 공용 용어 사전. 트리거 키워드 없는 카탈로그 | world info, "키워드북" |
| 엔딩 | `ending` | 스토리의 종결 정의(스토리와 1:N). 발동 조건은 `condition_text` 자유 텍스트 | — |

### 0-3-2. 제작 흐름

| 공식 용어 | 영문 식별자 | 정의 | 지양 표기 |
| --- | --- | --- | --- |
| 제작 | creation | **사용자가** 스토리를 만드는 행위와 퍼널 전체. 예: 스토리 제작 완료율 | 사용자 행위에 "생성" 사용. UI 버튼 카피 "만들기"는 허용 |
| 생성 | generation | **AI가** 산출물을 만드는 행위. 예: 스토리라인 생성, 응답 생성 | AI 행위 식별자에 `create` 사용(`generate` 계열로 통일) |
| 간편 제작 | simple creation | 태그 선택 → 스토리라인 선택 → 추가 정보의 3단계 제작 방식 | "간편 모드"(레거시) |
| 간편 제작 진행 ID | `creation_id` | 간편 제작 1회 진행 단위의 식별자. 분석·로그 표준 표기 | 로그 필드 `simple_creation_id`. 와이어 `simpleCreationId`, DB `creation_session_id`는 현행 계약으로 유지하되 신규 명명은 `creation_id` 계열 |
| 제작 단계 | `step_name`: `keyword` · `storylineSelect` · `additionalInfo` · `complete` | 간편 제작 퍼널의 4단계. 분석 표기 기준이며 라우팅 슬러그(kebab-case)와의 매핑은 §0-4 | — |
| 컴파일 | compile | 선택한 스토리라인 + 추가 정보 + 태그를 스토리 명세로 확장하는 AI 호출. 스토리당 1회(시점 A-1) | 관측 feature 값 `story_completion`은 이 호출의 역사적 명칭 — 적재 데이터 연속성을 위해 유지하되 새 이름에 쓰지 않음 |
| 완성 | completion | **사용자 관점**에서 스토리 제작을 끝내는 퍼널 단계 | 컴파일(AI 호출)과 혼용 금지 |
| 스토리라인 평가 | `rating`: `GOOD` · `BAD` | 스토리라인에 남기는 좋아요/싫어요 평가 | "좋아요"(스토리 `like`와 혼동) |
| 좋아요 | `like_count` | 스토리에 대한 좋아요 수(현재 placeholder) | — |

### 0-3-3. 플레이(채팅) 단위

| 공식 용어 | 영문 식별자 | 정의 | 지양 표기 |
| --- | --- | --- | --- |
| 채팅 | `chat`, `chat_id` | 스토리를 기반으로 진행하는 플레이 세션. 저장·이어쓰기·삭제의 단위. 외부 노출 식별자는 UUID `chat_id` | "대화"(식별자·계약. 설명문에서는 허용), play session(레거시 표기), "스토리 플레이" · "채팅 플레이" · "체험 플레이", "세션" |
| 채팅 화면 | — | 개별 채팅을 플레이하는 화면(`/chats/[id]`) | "채팅방"(구어. 코드 `room` 계열 식별자 신설 금지) |
| 턴 | `turn`, `turn_number` | 사용자 입력 1회 + AI 출력 1회 + 선택지 1세트. `turn_number`는 **사용자 입력 기준** 1부터 센다 | 메시지와 혼용 금지 |
| 메시지 | `message` | 턴을 구성하는 개별 발화 저장 행. `role`: `USER` · `ASSISTANT` · `SYSTEM` | — |
| 사용자 입력 | `userInput` | 턴에서 사용자가 보낸 텍스트(최대 3,000자) | — |
| AI 출력(본문) | `aiOutput` | 선택지를 제외한 AI 생성 본문(상황 묘사 + 인물 대사) | "답변", "응답"(HTTP 응답과 혼동), `output` 단독 표기 |
| 선택지 | `choice`, `choices` | 턴 말미에 AI가 제안하는 다음 행동 후보(정확히 3개) | next actions(AI 내부 잔존 표기), "다음 행동 선택지", "AI 추천 선택지", "추천 입력"(다른 개념, §0-3-1) |
| 이어쓰기 | continue | 기존 채팅에 턴을 추가하는 행위 | UI 카피 "이어가기"는 허용 |
| 강조 마크업 | emphasis | `*...*`로 감싼 상황·행동 묘사 표기. 사용자 입력과 AI 출력 양방향 공통 규약 | UI 버튼 카피 "상황 묘사 추가"는 허용. "지문"은 프롬프트의 서사 문맥 전용 |
| 요약 | `summary` | 백엔드가 매 턴 AI 서버에 전달하는 대화 요약 문자열. MEMORY 레이어의 `[현재 상태]` 슬롯에 치환 | "세션 상태"(session 예약어와 충돌, §0-5), "메모리 TEXT" |

### 0-3-4. 사용자와 식별자

| 공식 용어 | 영문 식별자 | 정의 | 지양 표기 |
| --- | --- | --- | --- |
| 게스트 | guest | 로그인 없이 서비스를 쓰는 사용자(제품·UI 관점) | "비로그인 사용자"는 설명문에서 허용 |
| 익명 사용자 | anonymous user | 분석·데이터 관점의 게스트. `device_id` 기반으로 식별 | — |
| 디바이스 ID | `device_id` / `device_id_hash` | Amplitude SDK가 만드는 익명 식별자. 프론트엔드는 원본, 서버 저장은 해시(`device_hash_` 접두) | `anonymous_id`(레거시, V17에서 정리 완료) |
| 세션 | `session_id` | **분석 세션 전용 예약어**(Amplitude). 한 번의 방문 단위 | 채팅·간편 제작 진행 단위를 "세션"으로 부르는 것(§0-5) |
| 요청 ID | `request_id` | API 요청 1건의 상관 ID(`req_` + UUID). 헤더 `X-Manyak-Request-Id` | — |
| 사용자 | `user` | 로그인한 사용자 계정. 외부 식별자는 UUID `public_id` | — |

## 0-4. 계층별 표기 컨벤션

같은 개념이라도 계층에 따라 표기(casing)가 다릅니다. 다음 표가 기준이며, 계층 간 이름 자체(단어)는 §0-3의 공식 용어를 따릅니다.

| 계층 | 표기 | 예시 |
| --- | --- | --- |
| 클라이언트 REST 와이어(JSON) | camelCase | `storyId`, `aiOutput`, `suggestedInputs` |
| DB 테이블·컬럼 | snake_case | `story_chats`, `turn_number` |
| 구조화 로그 · MDC · Sentry | snake_case | `event_name`, `chat_id`, `error_code` |
| 분석 이벤트명 | `client_{screenName}_{object}_{action}` — 세그먼트 구분 `_`, 세그먼트 내부 camelCase, 동사 과거형 | `client_chat_choiceOption_selected` |
| 분석 프로퍼티 | snake_case | `turn_number`, `creation_id`, `step_name` |
| HTTP 헤더 | `X-Manyak-` 접두 Train-Case | `X-Manyak-Device-Id` |
| enum 값 | UPPER_SNAKE_CASE | `USER`, `ASSISTANT`, `GOOD`, `SUPPORTING_CHARACTER` |
| 프롬프트 버전 키 | UPPER_SNAKE_CASE | `STORYLINES`, `NEXT_ACTIONS` |

추가 규칙:

- **AI 계약의 이원 표기는 공식화된 예외입니다.** story 계열 계약(`/story/*`)은 snake_case, chat SSE `completed` 페이로드는 camelCase입니다. 각 엔드포인트에 필드를 추가할 때 해당 엔드포인트의 기존 규칙을 따릅니다.
- **외부 노출 식별자는 public UUID만 사용합니다.** 내부 Long PK는 FK·조인 전용이며 API, 로그, 분석 프로퍼티에 싣지 않습니다.
- **제작 단계 표기 매핑.** 라우팅 슬러그는 kebab-case(`storyline-select`), 분석 `step_name`은 camelCase(`storylineSelect`)로 변환해 싣습니다.
- **role 변환.** 계약과 저장은 대문자(`USER`/`ASSISTANT`), LLM 호출 직전 소문자 변환은 AI 서버 내부 구현입니다.

## 0-5. 동명이의·예약어 규칙

한 단어가 여러 개념을 가리켜 혼동을 만드는 사례입니다. 다음 규칙으로 의미를 고정합니다.

| 단어 | 규칙 |
| --- | --- |
| 세션(session) | 분석 세션(`session_id`) 전용 예약어. 채팅은 `chat`, 간편 제작 진행은 `creation_id` 계열로 부른다 |
| 스토리(story) | ① 마냑 콘텐츠 단위(기본 의미) ② Jira 이슈 유형 ③ AI 프롬프트 STORY 레이어 — ②③은 "Jira 스토리", "STORY 레이어"처럼 수식어를 붙여 구분한다 |
| USER | AI 레포에서 4중 의미(USER 레이어, `## [USER]` 템플릿 블록, history `role`, `user_input`). 문서·주석에서 "USER 레이어", "`[USER]` 블록"처럼 층위를 명시한다 |
| meta | 컴파일 응답에서 노출 메타(제목 등)는 `stories` 키, 로깅 메타(model·토큰)는 `meta` 키. "메타"라고만 쓰지 않는다 |
| chatCount | 스토리의 채팅 수 전용. 채팅 안의 턴 수는 `turn_count`(개념명 "턴 수")로 부른다 |
| 좋아요 | 스토리 `like` 전용. 스토리라인 GOOD/BAD는 "평가(rating)" |
| 추천 입력 | `suggested_inputs`(첫 입력 후보) 전용. 선택지(`choices`)에 쓰지 않는다 |
| 시드(seed) | 오프닝 시드(History 첫 항목)와 MEMORY의 Seed State(초기 상태값)는 다른 개념. 단독 "시드" 표기를 피한다 |
| 온보딩(onboarding) | 분석 이벤트 네임스페이스와 코드 식별자 전용. UI·문서의 화면 명칭은 "환영 다이얼로그". "온보딩 투어" · "단계별 온보딩"은 미구현 개념이므로 현행 기능 설명에 쓰지 않는다 |

## 0-6. AI 서버 내부 용어

AI 서버와 프롬프트 스펙에서만 쓰는 용어입니다. 상세 정의는 manyak-ai 레포의 `spec/` 문서가 정본이며, 여기서는 다른 레포에서 참조할 때 필요한 수준으로 요약합니다.

| 용어 | 정의 |
| --- | --- |
| 6레이어 | 채팅 프롬프트를 구성하는 레이어 6종: SAFETY · CORE · STORY · CHARACTER · USER · MEMORY |
| PHI (Post-History Instructions) | 생성 직전 최하단에 재주입하는 블록. 내부 순서 CHARACTER → STORY → CORE → SAFETY |
| Depth | 대화 내역 끝 근처의 삽입 슬롯. MEMORY(`summary`) 전담 |
| 희소 입력 | 컴파일의 입력(선택 스토리라인 + 추가 정보 + 태그)을 가리키는 표현 |
| 시점 A-1 / 시점 B | 컴파일 시점(스토리당 1회) / 채팅 턴 런타임 시점. A-2(세션 초기화)는 stateless 확정으로 폐기되어 B에 흡수 |
| 오프닝 시드 | 백엔드가 프롤로그 + 시작 상황을 History 첫 ASSISTANT 항목으로 래핑해 전달하는 것 |
| 부분 재호출(refill) | 컴파일·선택지 생성에서 빈 필수 블록만 다시 채우는 재호출(최대 2회). 관측 필드 `retry_count`가 이 횟수를 담는다 |
| 화자 라벨 / 지문 | `인물명: 대사` 표기 / `*별표*` 행동 묘사 — 프론트·백엔드·AI가 공유하는 와이어 표기 규약 |
| 스토리 명세(StorySpec) | 컴파일의 내부 세분 JSON 산출물. 통글로 렌더링되어 `story_settings`가 된다 |

## 0-7. 참고 근거

공식 용어 선정에 참고한 업계 표준 근거입니다.

| 용어 | 근거 |
| --- | --- |
| 채팅(chat) | Character.AI · SillyTavern · Janitor AI 등 AI 챗 제품군의 공통 명칭. AI Dungeon만 adventure를 사용 |
| 턴(turn) | 대화형 AI 업계 표준(multi-turn conversation) |
| 선택지(choice) | 비주얼 노벨 도메인 표준. 챗봇 UI 관행(suggested reply)보다 서사 제품 성격에 부합 |
| 프롤로그(prologue) | AI 챗 제품군은 first message/greeting을 쓰지만, 시작 장면 서사 텍스트라는 성격은 웹소설·비주얼 노벨 관행인 프롤로그가 더 정확 |
| 태그(tag) | Character.AI · Janitor AI · 제타 · 크랙의 분류 명칭. 트리거형 `keyword_notes` 로드맵과의 충돌 예방 |
| 로어북(lorebook) | SillyTavern · Character Card V2 스펙 · NovelAI로 이어지는 사실상 표준 |
| 익명 사용자(anonymous user) | Segment(`anonymousId`) · Amplitude(`device_id`) 표준 개념 |
| 이벤트 네이밍 | Segment · Amplitude 공통 권장인 Object-Action 프레임워크(동사 과거형) |

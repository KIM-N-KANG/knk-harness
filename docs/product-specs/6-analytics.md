# 6-ANALYTICS

이 문서는 **마냑 서비스에서 사용자가 스토리를 만들고 채팅을 이어가는 흐름**을 측정하기 위한 분석 스펙입니다. 이벤트, 지표, 관측 구현, 검수 기준을 한 파일에서 관리합니다.

```text
§6-1  목적과 범위
§6-2  식별자 정책
§6-3  이벤트 네이밍과 공통 프로퍼티
§6-4  이벤트 카탈로그
§6-5  퍼널과 지표
§6-6  관측 구현
§6-7  개인정보와 원문 수집 원칙
§6-8  검수 체크리스트
```

| 항목      | 값                                                                                                                    |
| --------- | --------------------------------------------------------------------------------------------------------------------- |
| 버전      | v0.33                                                                                                                 |
| 작성일    | 2026-06-30                                                                                                            |
| 수정일    | 2026-08-19                                                                                                            |
| 대상      | 마냑 MVP                                                                                                              |
| 작성 목적 | MVP 출시 후 사용자가 스토리를 만들고 채팅을 이어가는 흐름을 측정하기 위한 이벤트, 지표, 관측, 검수 기준을 정의합니다. |

## 6-1. 목적과 범위

마냑 MVP 분석의 목적은 사용자가 다음 흐름을 자연스럽게 완료하는지 확인하는 것입니다.

1. 스토리 목록에서 스토리 제작을 시작합니다.
2. 키워드 선택, 스토리라인 선택, 추가 정보 입력을 거쳐 스토리를 완성합니다.
3. 완성한 스토리의 상세 화면에서 채팅을 시작합니다.
4. 채팅에서 첫 메시지를 보내고 여러 턴 동안 이야기를 이어갑니다.
5. 불편하거나 아쉬운 점을 피드백으로 남깁니다.

| 핵심 질문                          | 확인 지표                         |
| ---------------------------------- | --------------------------------- |
| 사용자가 스토리 제작을 시작하나요? | 제작 시작률                       |
| 제작 중 어디서 막히나요?           | 제작 단계별 이탈율, 생성 실패율   |
| 스토리 생성이 채팅으로 이어지나요? | 스토리 상세에서 채팅 시작 전환율  |
| 채팅이 실제 몰입으로 이어지나요?   | 첫 메시지 전송률, N턴 이상 도달률 |
| 개선 포인트를 수집하고 있나요?     | 피드백 제출률                     |

MVP 분석은 스토리 제작과 채팅 활성화에 필요한 최소 신호를 우선 수집합니다. 모든 화면 조작을 계측하지 않고, 퍼널과 운영 장애 분석에 필요한 행동과 처리 결과만 수집합니다.

| 포함 범위             | 설명                                            | 원본 섹션              |
| --------------------- | ----------------------------------------------- | ---------------------- |
| 사용자 행동 이벤트    | 화면 진입, CTA 클릭, 선택, 제출, 완료           | `6-4. 이벤트 카탈로그` |
| 서버 처리 결과 이벤트 | 스토리 생성, AI 응답, 피드백 제출의 성공과 실패 | `6-4. 이벤트 카탈로그` |
| 핵심 퍼널과 지표      | 제작 퍼널, 채팅 활성화 퍼널, 전체 활성화 퍼널   | `6-5. 퍼널과 지표`     |
| 운영 관측             | Sentry, CloudWatch, `ai_call_logs`, 실패 코드   | `6-6. 관측 구현`       |
| 릴리스 검수           | P0 이벤트, 식별자, 원문 미수집, 로그 연결 확인  | `6-8. 검수 체크리스트` |

| 제외 범위              | 처리 기준                                                                                                                                           |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 사용자 입력 원문 분석  | MVP 분석 이벤트와 로그에 원문을 넣지 않습니다.                                                                                                      |
| 대시보드 화면 요구사항 | 실제 Amplitude 또는 CloudWatch 대시보드가 정해질 때 별도 문서로 추가합니다.                                                                         |
| 인증 사용자 분석       | 식별자 정책(`setUserId`·`user_id`·`is_logged_in`)은 `Phase 1 · 구현`(§6-2·§6-4-2-8), 로그인 처리·마이그레이션 서버 이벤트는 `Phase 1 · 계획`입니다. |
| 실험 분석              | A/B 테스트 도입 후 `experiment_key`, `variant`를 추가합니다.                                                                                        |

## 6-2. 식별자 정책

현재 MVP는 로그인 기능이 없는 전원 게스트 서비스입니다. 사용자 단위는 익명 `device_id`로 식별합니다.

**식별자의 논리적 의미·타입·금지 데이터·서버 상관관계는 플랫폼 공통 계약**이고, 그 값을 어떤 SDK로 생성·보관·복원하는지는 플랫폼 매핑입니다 — 웹은 Amplitude Browser SDK가 채우는 값에 매핑하고, **Android는 앱이 첫 실행 시 생성한 UUID를 `device_id`로 쓰며 API 헤더와 분석 SDK가 같은 값을 공유합니다**(로그아웃 시 재발급 — [`3-3-android-app.md §3-3-4`](./3-3-android-app.md)). Android도 **동일한 논리적 `device_id`(익명 사용자 단위, string)·`session_id`(방문 흐름, number)·`user_id`(로그인 사용자, string) 의미와 API 헤더 계약(§6-6-2)을 충족해야 합니다.** 게스트 체험 한도·자동 이관은 앱에 게스트가 없어 비적용입니다([`3-3-android-app.md §3-3-1`](./3-3-android-app.md)).

| 식별자           | 분석 이벤트 타입 | 생성·관리                                      | 사용처                            |
| ---------------- | ---------------- | ---------------------------------------------- | --------------------------------- |
| `device_id`      | string           | 논리 식별자 — 웹: Amplitude Browser SDK 자동 수집 / Android: 앱이 생성한 UUID | 익명 사용자 단위 분석             |
| `session_id`     | number           | 논리 식별자 — 웹·Android 모두 Amplitude SDK 자동 수집 | 한 번의 방문 흐름                 |
| `request_id`     | string           | **백엔드 생성**(수신 헤더가 없으면 생성, 응답 헤더로 항상 echo — 클라이언트 앱은 생성·주입하지 않음, §6-6-2) | 서버 로그, Sentry, AI 호출 연결   |
| `device_id_hash` | string           | 백엔드가 `device_id`를 해시                    | 서버 로그, Sentry, `ai_call_logs` |
| `creation_id`(= `analytics_creation_id`) | string | 간편 제작 진행(세션) 식별자 `simpleCreationId`(원본 `story_creation_sessions.id`, Long)를 문자열로 변환 | 스토리 제작 시도 연결. **AI 트레이스의 `trace_creation_id`와 다른 값**(아래 주의) |
| `story_id`       | string           | 스토리 완성 후 서버 발급                       | 스토리 관련 이벤트                |
| `chat_id`        | string           | 채팅 생성 후 서버 발급                         | 채팅 관련 이벤트                  |
| `ai_call_log_id` | string           | AI 호출 기록 생성 시 발급                      | 서버 로그와 `ai_call_logs` 연결   |

분석 이벤트에서 `story_id`는 문자열(공개 UUID 식별자)로 보냅니다. CloudWatch 로그·`ai_call_logs`·DB에서도 동일하게 문자열로 저장합니다.

| 키            | 분석 단위        | 사용                                |
| ------------- | ---------------- | ----------------------------------- |
| `device_id`   | 익명 사용자      | 전체 활성화 퍼널과 장기 행동        |
| `session_id`  | 방문 세션        | 같은 방문 안의 순차 행동            |
| `creation_id`(= `analytics_creation_id`) | 스토리 생성 시도 | 제작 퍼널의 생성 성공 이후 구간(잔여 간극은 §6-8-7 A1~A3) |
| `chat_id`     | 채팅 세션        | 채팅 활성화와 대화 깊이             |
| `request_id`  | API 요청         | 서버 로그, Sentry, AI 호출 상관관계 |

`request_id`는 현재 서버 내부 상관 키입니다. 프론트엔드 `client_*` 이벤트와 백엔드 `server_*` 이벤트를 분석 이벤트 프로퍼티로 직접 연결하는 용도로는 아직 사용하지 않습니다. 현재 제품 퍼널 연결은 `analytics_creation_id`와 `chat_id`를 사용합니다(`analytics_creation_id` 경로의 잔여 간극은 §6-8-7 A1~A3).

> **두 종류의 `creation_id`를 구분합니다.** 제품 분석 이벤트의 `creation_id`는 **`analytics_creation_id`**(진행 세션 식별자 `simpleCreationId`의 문자열 표기)이고, AI 트레이스·`ai_call_logs`·`X-Manyak-Creation-Id`의 `creation_id`는 **`trace_creation_id`**(스토리라인 생성 요청의 클라이언트 생성 UUID `story_creation_requests.request_id`)입니다 — 값도 타입도 다르며(정의: [`0-glossary.md §0-3-2`](./0-glossary.md)) **두 값을 직접 조인하면 안 됩니다.** 제품 퍼널·지표는 `analytics_creation_id`만, AI 호출·Langfuse 트레이스 연결은 `trace_creation_id`만 씁니다. **Android도 같은 규칙을 따릅니다** — `client_*`·`server_*` 분석 이벤트에는 `analytics_creation_id`를, AI 호출 상관 헤더에는 `trace_creation_id`를 싣습니다(§6-6-3·§6-6-8).

스토리 생성 요청은 `analytics_creation_id`가 발급되기 전에도 발생할 수 있습니다. `client_storyCreate_storyGeneration_requested`는 `device_id`와 `session_id` 순차 기준으로 집계합니다. 백엔드는 스토리라인 생성 처리를 시작할 때 가능한 한 먼저 `analytics_creation_id`를 발급합니다. 이후 `server_*` 이벤트의 `analytics_creation_id` 적재는 **목표 계약과 현재 구현이 다릅니다** — 목표 계약은 성공·실패 모두 `string` 필수이지만, **현재 구현은 성공 이벤트만 값을 싣고(타입은 `string`이 아닌 `simpleCreationId` Long) 실패 이벤트는 AI 호출 실패·세션 저장 실패처럼 발급 전 단계에서 끝나면 값 없이 발행될 수 있습니다**(§6-8-7 A1·A3). `creation_id` 발급 전의 malformed request는 분석 이벤트가 아니라 CloudWatch 운영 로그로만 추적합니다.

`Phase 1 · 구현` — 로그인 도입에 따른 식별자 정책은 다음과 같습니다.

- 로그인 성공 시 Amplitude `setUserId`에 사용자 `public_id`를 설정하고 `device_id`는 유지합니다. 같은 기기의 과거 익명 행동은 `device_id`로 자동 연결되므로 별도 `alias`는 사용하지 않습니다.
- 로그아웃 시 `setUserId(null)`와 함께 Amplitude `reset()`으로 `device_id`를 새로 발급합니다. Amplitude는 한 번 연결된 `user_id`↔`device_id`를 이후 익명 이벤트까지 병합하므로, 공용 기기에서 다음 사용자의 행동이 이전 회원에게 귀속되는 것을 막습니다(US-9-5 계정 보호). 개인 기기의 과거 익명 연속성보다 계정 보호를 우선합니다.
- 공통 프로퍼티에 `is_logged_in`(boolean)·`user_id`(public_id 문자열)를 로그인 시점부터 추가합니다(§6-3-2). 서버 분석 이벤트의 사용자 식별도 `user_id`를 사용합니다. 서버 구조화 로그의 `user_id` 필드 추가는 [`4-backend.md §4-7`](./4-backend.md)이 소유합니다.

## 6-3. 이벤트 네이밍과 공통 프로퍼티

### 6-3-1. 이벤트 원칙

이벤트명은 아래 네이밍 기준을 따릅니다.

```text
{platform}_{screenName}(_{objectName})?_{actionType}(_{eventType})?
```

| 원칙                                    | 설명                                                                 | 예시                                     |
| --------------------------------------- | -------------------------------------------------------------------- | ---------------------------------------- |
| 이벤트명에 데이터 값을 넣지 않습니다.   | ID, 선택값, 단계 번호, 리스트 위치, 에러 코드는 프로퍼티로 보냅니다. | `story_id`, `step_number`, `position`    |
| 단계 번호는 screenName에 넣지 않습니다. | 단계는 `step_number`, `step_name` 프로퍼티로 보냅니다.               | `client_storyCreate_step_viewed`         |
| 버튼은 문구보다 역할로 씁니다.          | 버튼 문구가 바뀌어도 이벤트명이 바뀌지 않게 합니다.                  | `nextButton`, `chatStartButton`          |
| 서버 처리 대상은 기능 단위로 씁니다.    | 서버 결과는 `processed`와 `eventType`으로 구분합니다.                | `server_chat_aiMessage_processed_failed` |
| `canceled`는 실제 취소 행동에만 씁니다. | 단순 닫기나 나가기 클릭에는 `clicked`를 씁니다.                      | `client_storyCreate_exitButton_clicked`  |

`actionType`은 아래 값만 사용합니다.

| 그룹        | 값          | 설명                                              |
| ----------- | ----------- | ------------------------------------------------- |
| 사용자 행동 | `viewed`    | 화면 또는 단계에 진입했을 때                      |
| 사용자 행동 | `clicked`   | 클릭 가능한 요소를 눌렀을 때                      |
| 사용자 행동 | `selected`  | 선택지를 선택했을 때                              |
| 사용자 행동 | `focused`   | 입력 영역에 포커스가 들어왔을 때                  |
| 사용자 행동 | `submitted` | 폼이나 입력값을 제출했을 때                       |
| 사용자 행동 | `requested` | 클라이언트가 서버에 생성 또는 처리를 요청했을 때  |
| 사용자 행동 | `completed` | 주요 flow를 끝까지 완료했을 때                    |
| 상태 노출   | `shown`     | 모달, 토스트, 에러, 로딩, 빈 상태가 표시되었을 때 |
| 상태 노출   | `impressed` | item 또는 section이 유효하게 노출되었을 때        |
| 서버 처리   | `processed` | 서버가 생성, 저장, 처리를 수행했을 때             |

`eventType`은 `succeeded`, `failed`, `blocked`, `canceled`만 사용합니다. 단순 클릭, 노출, 포커스, 화면 진입에는 결과 상태를 붙이지 않습니다. `completed`는 결과 상태가 아니라 사용자가 flow를 끝마친 행동이므로 `actionType`으로 씁니다.

### 6-3-2. 공통 프로퍼티

각 이벤트 표에는 고유 프로퍼티만 적습니다. 공통 프로퍼티는 적용 범위에 따라 모든 이벤트에 함께 보냅니다.

| property      | 타입   | 적용 범위         | 설명                                                                           |
| ------------- | ------ | ----------------- | ------------------------------------------------------------------------------ |
| `screen_name` | string | 모든 이벤트       | 이벤트가 발생한 화면입니다. 필터와 세그먼트 편의를 위해 프로퍼티로도 보냅니다. |
| `step_name`   | string | 스토리 제작 퍼널  | `keyword`, `storylineSelect`, `additionalInfo`, `complete` 중 하나입니다.      |
| `step_number` | number | 스토리 제작 퍼널  | 제작 단계 번호입니다.                                                          |
| `creation_id` | string | 스토리 제작 퍼널  | 진행(세션) 식별자 `simpleCreationId`의 문자열 표기입니다(= `analytics_creation_id`, §6-2).                          |
| `story_id`    | string | story 관련 이벤트 | 스토리 식별자입니다.                                                           |
| `chat_id`     | string | chat 관련 이벤트  | 채팅 식별자입니다.                                                             |

다음 값은 Amplitude SDK가 자동으로 채우므로 커스텀 프로퍼티로 다시 만들지 않습니다(웹은 Browser SDK 기준으로 검증됨 — Android SDK 도입 시 동등 수집 여부를 확인하고 차이를 이 절에 기록합니다).

```text
device_id, session_id
platform, os_name, os_version, device_family
app_version
country, region, city, language
event_time, event_id
```

웹·Android 이벤트는 **커스텀 프로퍼티가 아니라 SDK 자동 수집 값으로 구분합니다** — `platform`·`os_name`이 플랫폼 구분 축이고(웹 Browser SDK는 `platform: Web`으로 검증됨, Android 값은 SDK 도입 시 확인해 이 절에 기록), `app_version`은 웹에서는 웹 앱 버전, Android에서는 앱 패키지 버전을 담는 것을 원칙으로 합니다. 이벤트 이름·커스텀 프로퍼티는 플랫폼별로 새로 만들지 않고 공통 카탈로그(§6-4)를 재사용합니다.

다음 프로퍼티는 관련 기능 도입 시점에 추가합니다.

| property                                  | 도입 시점                            | 설명                                                                                      |
| ----------------------------------------- | ------------------------------------ | ----------------------------------------------------------------------------------------- |
| `user_id`                                 | 인증 도입 후 `Phase 1 · 구현`        | 로그인 사용자 식별자(public_id 문자열)입니다. `setUserId`로 설정합니다(§6-2).             |
| `is_logged_in`                            | 인증 도입 후 `Phase 1 · 구현`        | 로그인 여부입니다.                                                                        |
| `membership`                              | 구독·요금제 도입 후                  | 요금제 또는 등급입니다.                                                                   |
| `signup_at`                               | 인증 도입 후 `Phase 1 · 계획`        | 가입 시점입니다.                                                                          |
| `experiment_key` / `variant`              | A/B 테스트 도입 후                   | 실험 키와 분기 값입니다.                                                                  |
| `request_id`                              | 서버 사이드 분석 이벤트 연결 도입 후 | client `requested`와 server `processed`를 분석 이벤트 프로퍼티로 직접 잇는 상관 ID입니다. |
| `item_id` / `section_id` / `section_name` | impression 정밀 계측 시              | 추천 카드 등 노출 분석용 값입니다.                                                        |

현재 `request_id`는 서버 내부 상관 키로 사용합니다. 분석 이벤트 프로퍼티로는 아직 보내지 않습니다. 자세한 기준은 `6-6-3. 요청 식별자와 상관관계`를 따릅니다.

## 6-4. 이벤트 카탈로그

### 6-4-1. MVP 우선순위

P0 이벤트는 출시 전에 반드시 수집합니다. P1 이벤트는 P0가 안정적으로 수집된 뒤 추가합니다. P2 이벤트는 세부 인터랙션 계측으로, P1 이후 필요에 따라 추가합니다.

> **P0·P1·P2는 수집 우선순위이며, 로드맵의 Phase 0~3과 무관합니다.** 로드맵 단계 표기는 3·4·5 스펙 문서와 동일하게 `{로드맵 Phase} · {구현 상태}` 라벨(예: `Phase 1 · 계획`)을 사용합니다([`roadmap.md`](../planning/roadmap.md). 유저 스토리 문서만 `Phase 1` 단축 라벨을 씁니다). Phase 1 기능(계정 · 크레딧 · 제작/채팅 확장)의 이벤트는 Phase 1 스펙 반영에서 이 라벨로 추가합니다.

| 우선순위            | 소유   | 이벤트                                                   |
| ------------------- | ------ | -------------------------------------------------------- |
| P0                  | client | `client_storyList_viewed`                                |
| P0                  | client | `client_storyList_createButton_clicked`                  |
| P0                  | client | `client_storyCreate_viewed`                              |
| P0                  | client | `client_storyCreate_step_viewed`                         |
| P0                  | client | `client_storyCreate_storyGeneration_requested`           |
| P0                  | server | `server_storyCreate_storyGeneration_processed_succeeded` |
| P0                  | server | `server_storyCreate_storyGeneration_processed_failed`    |
| P0                  | client | `client_storyCreate_storylineOption_selected`            |
| P0                  | client | `client_storyCreate_selectedTagsButton_clicked`          |
| P0                  | client | `client_storyCreate_completed`                           |
| P0                  | client | `client_storyDetail_viewed`                              |
| P0                  | client | `client_storyDetail_chatStartButton_clicked`             |
| P0                  | client | `client_chat_viewed`                                     |
| P0                  | client | `client_chat_messageInput_submitted`                     |
| P0                  | server | `server_chat_aiMessage_processed_succeeded`              |
| P0                  | server | `server_chat_aiMessage_processed_failed`                 |
| P0 `Phase 1 · 구현` | client | `client_creditShortageDialog_shown`                      |
| P0 `Phase 1 · 구현` | client | `client_guestLimitDialog_shown`                          |
| P0 `Phase 1 · 구현` | client | `client_login_oauthError_shown`                          |
| P0 `Phase 1 · 구현` | server | `server_login_googleLogin_processed_succeeded`           |
| P0 `Phase 1 · 구현` | server | `server_login_googleLogin_processed_failed`              |
| P0 `Phase 1 · 구현` | server | `server_login_kakaoLogin_processed_succeeded`            |
| P0 `Phase 1 · 구현` | server | `server_login_kakaoLogin_processed_failed`               |
| P1 `Phase 1 · 구현` | server | `server_link_socialLink_processed_succeeded`             |
| P1 `Phase 1 · 구현` | server | `server_link_socialLink_processed_failed`                |
| P0 `Phase 1 · 구현` | server | `server_login_migration_processed_succeeded`             |
| P0 `Phase 1 · 구현` | server | `server_login_migration_processed_failed`                |
| P0                  | client | `client_feedback_viewed`                                 |
| P0                  | client | `client_feedback_form_submitted`                         |
| P1                  | client | `client_onboarding_viewed`                               |
| P1                  | client | `client_onboarding_createButton_clicked`                 |
| P1                  | client | `client_onboarding_skipButton_clicked`                   |
| P1                  | client | `client_storyList_storyCard_clicked`                     |
| P1                  | client | `client_storyList_storyCard_impressed`                   |
| P1 `Phase 1 · 구현` | client | `client_storyList_loginButton_clicked`                   |
| P1                  | client | `client_storyCreate_tagCategory_selected`                |
| P1                  | client | `client_storyCreate_regenerateButton_clicked`            |
| P1                  | client | `client_storyCreate_storylineRating_clicked`             |
| P1 `Phase 1 · 계획` | client | `client_storyCreate_methodOption_selected`               |
| P1 `Phase 1 · 계획` | client | `client_generalCreate_viewed`                            |
| P1 `Phase 1 · 계획` | client | `client_generalCreate_completed`                         |
| P1 `Phase 1 · 계획` | client | `client_storyEdit_viewed`                                |
| P1 `Phase 1 · 계획` | client | `client_storyEdit_completed`                             |
| P1                  | client | `client_storyCreate_storyCompletion_requested`           |
| P1                  | client | `client_storyCreate_completeError_shown`                 |
| P1                  | client | `client_storyCreate_exitButton_clicked`                  |
| P1                  | client | `client_storyCreate_draftSaved`                          |
| P2                  | client | `client_storyCreate_continueBanner_shown`                |
| P1                  | client | `client_storyCreate_continueBanner_clicked`              |
| P2                  | client | `client_storyCreate_continueBanner_dismissed`            |
| P2                  | client | `client_storyCreate_resumeDialog_shown`                  |
| P1                  | client | `client_storyCreate_resumeDialog_continued`              |
| P2                  | client | `client_storyCreate_resumeDialog_discarded`              |
| P1                  | client | `client_chatList_viewed`                                 |
| P1                  | client | `client_chatList_chatCard_clicked`                       |
| P1                  | client | `client_chatList_chatCard_impressed`                     |
| P1                  | client | `client_chat_inputMode_selected`                         |
| P1                  | client | `client_chat_choiceOption_selected`                      |
| P1                  | client | `client_chat_choiceFillButton_clicked`                   |
| P1                  | client | `client_chat_loadError_shown`                            |
| P1                  | client | `client_chat_retryButton_clicked`                        |
| P1                  | client | `client_chat_streamError_shown`                          |
| P1 `Phase 1 · 계획` | client | `client_chat_regenerateButton_clicked`                   |
| P1 `Phase 1 · 계획` | client | `client_chat_chatImage_impressed`                        |
| P1 `Phase 1 · 계획` | client | `client_chat_endingBadge_impressed`                      |
| P1 `Phase 1 · 구현` | client | `client_chatShareDialog_shown`                           |
| P1 `Phase 1 · 구현` | client | `client_chat_shareButton_clicked`                        |
| P1 `Phase 1 · 구현` | client | `client_chatShareDialog_dismissed`                       |
| P1 `Phase 1 · 구현` | client | `client_chatShare_viewed`                                |
| P1 `Phase 1 · 구현` | client | `client_chatShare_ctaButton_clicked`                     |
| P1 `Phase 1 · 구현` | client | `client_guestLimitDialog_loginButton_clicked`            |
| P1 `Phase 1 · 구현` | client | `client_guestLimitDialog_dismissed`                      |
| P1 `Phase 1 · 구현` | client | `client_creditShortageDialog_earnButton_clicked`         |
| P1 `Phase 1 · 구현` | client | `client_creditShortageDialog_attendanceButton_clicked`   |
| P1 `Phase 1 · 구현` | client | `client_creditShortageDialog_dismissed`                  |
| P1 `Phase 1 · 구현` | client | `client_login_viewed`                                    |
| P1 `Phase 1 · 구현` | client | `client_login_googleButton_clicked`                      |
| P1 `Phase 1 · 구현` | client | `client_login_kakaoButton_clicked`                       |
| P1 `Phase 1 · 구현` | client | `client_account_viewed`                                  |
| P1 `Phase 1 · 구현` | client | `client_account_loginButton_clicked`                     |
| P1 `Phase 1 · 구현` | client | `client_account_attendanceButton_clicked`                |
| P1 `Phase 1 · 구현` | client | `client_account_logoutButton_clicked`                    |
| P1 `Phase 1 · 구현` | client | `client_account_linkAccountButton_clicked`               |
| P1 `Phase 1 · 구현` | client | `client_invite_viewed`                                   |
| P1 `Phase 1 · 구현` | client | `client_invite_copyButton_clicked`                       |
| P1 `Phase 1 · 구현` | client | `client_invite_kakaoShareButton_clicked`                 |
| P1                  | server | `server_feedback_submission_processed_succeeded`         |
| P1                  | server | `server_feedback_submission_processed_failed`            |
| P2                  | client | `client_storyCreate_addTag_submitted`                    |
| P2                  | client | `client_storyCreate_storylineTab_selected`               |
| P2                  | client | `client_storyCreate_backToStorylineButton_clicked`       |
| P2                  | client | `client_storyCreate_recommendedInfo_clicked`             |
| P2                  | client | `client_storyCreate_additionalInfoAddButton_clicked`     |
| P2                  | client | `client_storyCreate_additionalInfoRemoveButton_clicked`  |
| P2 `폐기`           | client | `client_chat_settingsButton_clicked`                     |
| P2                  | client | `client_chat_choicesToggle_clicked`                      |
| P2                  | client | `client_chat_addBlockButton_clicked`                     |
| P2                  | client | `client_chat_removeBlockButton_clicked`                  |
| P2                  | client | `client_chat_situationInsertButton_clicked`              |
| P2                  | client | `client_chat_tour_shown`                                 |
| P2                  | client | `client_chat_tourStep_viewed`                            |
| P2                  | client | `client_chat_tour_completed`                             |
| P2                  | client | `client_chat_tourSkipButton_clicked`                     |
| P2                  | client | `client_storyCreate_creditInfoButton_clicked`            |
| P2                  | client | `client_storyDetail_thumbnail_clicked`                   |
| P2                  | client | `client_terms_viewed`                                    |
| P2                  | client | `client_privacy_viewed`                                  |
| P2 `계획`           | client | `client_serviceInfo_viewed`                              |

스토리 상세의 추천 스토리 카드(`client_storyDetail_recommendStoryCard_clicked`, `client_storyDetail_recommendStoryCard_impressed`)는 추천 카드 기능 도입 시 P1으로 추가합니다. 기준은 `6-4-2-4. 스토리 상세`를 따릅니다.

### 6-4-2. 페이지별 이벤트 카탈로그

각 이벤트 표에는 공통 프로퍼티를 제외한 고유 프로퍼티만 적습니다. 필수는 `필수`, 선택은 `선택`으로 표기합니다.

#### 6-4-2-1. 온보딩

홈 최초 진입 시 노출되는 환영 다이얼로그입니다. 사용자는 `스토리 만들기` 버튼을 누르기 전까지 다이얼로그를 닫을 수 없고, 다이얼로그는 최초 1회만 노출됩니다.

| 이벤트                                   | 우선순위 | 발생 시점               | 고유 프로퍼티 |
| ---------------------------------------- | -------- | ----------------------- | ------------- |
| `client_onboarding_viewed`               | P1       | 환영 다이얼로그 노출    | 없음          |
| `client_onboarding_createButton_clicked` | P1       | 스토리 만들기 버튼 클릭 | 없음          |
| `client_onboarding_skipButton_clicked`   | P1       | 나중에 하기 버튼 클릭   | 없음          |

#### 6-4-2-2. 스토리 목록

| 이벤트                                  | 우선순위 | 발생 시점             | 고유 프로퍼티                                        |
| --------------------------------------- | -------- | --------------------- | ---------------------------------------------------- |
| `client_storyList_viewed`               | P0       | 스토리 목록 화면 진입 | 없음                                                 |
| `client_storyList_createButton_clicked` | P0       | 제작하기 CTA 클릭     | `source` (string, 필수: `fab` / `emptyState`)        |
| `client_storyList_storyCard_clicked`    | P1       | 스토리 카드 클릭      | `story_id` (string, 필수), `position` (number, 선택) |
| `client_storyList_storyCard_impressed`  | P1       | 스토리 카드 유효 노출 | `story_id` (string, 필수), `position` (number, 선택) |
| `client_storyList_loginButton_clicked` `Phase 1 · 구현` | P1 | 홈 헤더 로그인 버튼 클릭(게스트) | 없음 |

`client_storyList_loginButton_clicked`는 게스트가 홈 헤더에서 로그인 화면으로 이동한 유입을 구분합니다. 마이발 유입(`client_account_loginButton_clicked`)과 분리해 진입점별 전환을 비교합니다.

제작하기 CTA는 플로팅 버튼과 빈 목록 상태 버튼 두 곳에 있습니다. 버튼 역할이 같으므로 이벤트는 하나로 두고, 어느 CTA에서 제작을 시작했는지는 `source`(`fab`: 플로팅 버튼, `emptyState`: 빈 목록 버튼)로 구분합니다.

#### 6-4-2-3. 스토리 제작

| 이벤트                                                   | 우선순위 | 발생 시점                                                                      | 고유 프로퍼티                                                                                                    |
| -------------------------------------------------------- | -------- | ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| `client_storyCreate_viewed`                              | P0       | 제작 화면 진입                                                                 | 없음                                                                                                             |
| `client_storyCreate_step_viewed`                         | P0       | 각 제작 단계 진입                                                              | `step_name` (string, 필수), `step_number` (number, 필수)                                                         |
| `client_storyCreate_tagCategory_selected`                | P1       | 태그 카테고리 이동(장르 → 주인공 → 주변 인물). 다음/이전 버튼·탭·스와이프 공통 | `from_category` (string, 필수), `to_category` (string, 필수), `direction` (string, 필수: `forward` / `backward`) |
| `client_storyCreate_addTag_submitted`                    | P2       | 태그 직접 추가 제출                                                            | `category` (string, 필수: `GENRE` / `PROTAGONIST` / `SUPPORTING_CHARACTER`)                                      |
| `client_storyCreate_storyGeneration_requested`           | P0       | 스토리라인 생성 요청 전송                                                      | 없음                                                                                                             |
| `server_storyCreate_storyGeneration_processed_succeeded` | P0       | 스토리라인 생성 성공                                                           | `creation_id` (string, 필수)                                                                                     |
| `server_storyCreate_storyGeneration_processed_failed`    | P0       | 스토리라인 생성 실패                                                           | `creation_id` (string, 필수 — 현재 구현은 발급 전 실패에서 누락 가능, §6-8-7 A1), `error_type` (string, 필수)    |
| `client_storyCreate_regenerateButton_clicked`            | P1       | 스토리라인 다시 만들기 클릭                                                    | `creation_id` (string, 필수)                                                                                     |
| `client_storyCreate_storylineTab_selected`               | P2       | 스토리라인 후보 탭 이동                                                        | `creation_id` (string, 필수), `position` (number, 필수)                                                          |
| `client_storyCreate_storylineRating_clicked`             | P1       | 스토리라인 좋아요/싫어요 클릭                                                  | `storyline_id` (string, 필수), `rating` (string, 필수: `GOOD` / `BAD`), `active` (boolean, 필수)                 |
| `client_storyCreate_storylineOption_selected`            | P0       | 스토리라인 선택                                                                | `creation_id` (string, 필수), `position` (number, 선택)                                                          |
| `client_storyCreate_selectedTagsButton_clicked`          | P0       | 선택한 태그 보기 버튼 클릭                                                     | `creation_id` (string, 필수)                                                                                     |
| `client_storyCreate_backToStorylineButton_clicked`       | P2       | 다시 선택하기(스토리라인 선택으로 되돌아감) 클릭                               | 없음                                                                                                             |
| `client_storyCreate_recommendedInfo_clicked`             | P2       | AI 추천 추가 정보 칩 클릭                                                      | `selected` (boolean, 필수)                                                                                       |
| `client_storyCreate_additionalInfoAddButton_clicked`     | P2       | 추가 정보 입력란 추가 클릭                                                     | 없음                                                                                                             |
| `client_storyCreate_additionalInfoRemoveButton_clicked`  | P2       | 추가 정보 입력란 삭제 클릭                                                     | 없음                                                                                                             |
| `client_storyCreate_storyCompletion_requested`           | P1       | 스토리 완성 요청 전송                                                          | `creation_id` (string, 필수)                                                                                     |
| `client_storyCreate_completeError_shown`                 | P1       | 스토리 완성 실패 에러 표시                                                     | `stage` (string, 필수: `story` / `chat`)                                                                         |
| `client_storyCreate_creditInfoButton_clicked`            | P2       | 제작 헤더 크레딧 안내 팝오버 열기(닫힘은 계측하지 않음)                        | 없음                                                                                                             |
| `client_storyCreate_exitButton_clicked`                  | P1       | 제작 이탈 확정(내용 보존 이탈은 뒤로가기 즉시, 소실 이탈은 경고 다이얼로그의 나가기 클릭) | `step_name` (string, 필수), `step_number` (number, 필수)                                                         |
| `client_storyCreate_draftSaved`                          | P1       | 이탈로 제작 상태를 임시 저장                                                   | `step` (string, 필수: `storyline-select` / `additional-info`)                                                    |
| `client_storyCreate_continueBanner_shown`                | P2       | 홈 이어서 만들기 배너 노출(임프레션)                                           | `stage` (string, 필수: `STORYLINE_GENERATION` / `STORY_COMPLETION` / `STORY_DRAFT`)                              |
| `client_storyCreate_continueBanner_clicked`              | P1       | 홈 이어서 만들기 배너의 "이어서 만들기" 클릭                                   | `stage` (string, 필수: `STORYLINE_GENERATION` / `STORY_COMPLETION` / `STORY_DRAFT`)                              |
| `client_storyCreate_continueBanner_dismissed`            | P2       | 홈 이어서 만들기 배너 닫기(X) — 레코드 폐기                                    | `stage` (string, 필수: `STORYLINE_GENERATION` / `STORY_COMPLETION` / `STORY_DRAFT`)                              |
| `client_storyCreate_resumeDialog_shown`                  | P2       | 퍼널 진입 시 임시 저장본 재개 다이얼로그 노출                                  | 없음                                                                                                             |
| `client_storyCreate_resumeDialog_continued`              | P1       | 재개 다이얼로그에서 "이어서 만들기" 선택                                       | 없음                                                                                                             |
| `client_storyCreate_resumeDialog_discarded`              | P2       | 재개 다이얼로그에서 "새로 만들기" 선택 — 임시 저장본 폐기                      | 없음                                                                                                             |
| `client_storyCreate_completed`                           | P0       | 스토리화 완료                                                                  | `story_id` (string, 필수), `chat_id` (string, 필수), `genres` (string[], 선택). **`creation_id`는 포함하지 않습니다** — §6-5 퍼널·지표가 이 이벤트를 `creation_id`로 조인한다고 정의해 간극이 있습니다(§6-8-7 A2) |

`client_storyCreate_storyGeneration_requested`는 `analytics_creation_id` 발급 전 이벤트입니다. `server_storyCreate_storyGeneration_processed_*`는 백엔드가 스토리라인 생성 처리를 시작하며 발급한 `analytics_creation_id`를 싣는 것이 목표 계약이지만, **현재 구현은 성공 이벤트만 항상 포함하고(타입은 문자열이 아닌 Long) 실패 이벤트는 발급 전 실패에서 값이 없을 수 있습니다**(§6-8-7 A1·A3). 이벤트명의 `storyGeneration`은 키워드로 스토리라인 후보를 생성하는 동작(AI feature `storyline_generation`)을 뜻하고, 최종 스토리 완성은 `storyCompletion`(AI feature `story_completion`)으로 구분합니다.

`client_storyCreate_storyCompletion_requested`는 스토리 완성하기 버튼 클릭으로 완성 요청(스토리 생성 또는 실패 후 채팅 생성 재시도)이 실제 전송될 때 발생합니다. 필수 입력이 없어 요청이 전송되지 않는 클릭에는 발생하지 않으며, 완성 실패율(`client_storyCreate_completeError_shown` 대비)의 분모로 사용합니다.

임시 저장 관련 이벤트([`3-1-client.md §3-1-4`](./3-1-client.md) 제작 임시 저장)는 이탈 → 재개까지의 회수 퍼널을 관찰합니다. `client_storyCreate_draftSaved`(저장) → `client_storyCreate_continueBanner_shown`/`_clicked`(홈 배너 회수) 또는 `client_storyCreate_resumeDialog_shown`/`_continued`(퍼널 재진입 회수)로 이어지며, `_dismissed`와 `_discarded`는 저장본을 버린 이탈입니다. 배너 이벤트의 `stage`로 진행 중 요청 복구(`STORYLINE_GENERATION`·`STORY_COMPLETION`)와 임시 저장본(`STORY_DRAFT`) 회수를 구분합니다.

`client_storyCreate_tagCategory_selected`는 키워드 단계의 세 카테고리(장르·주인공·주변 인물) 사이 이동을 다음/이전 버튼·탭·스와이프 공통으로 한 곳에서 계측합니다. `direction`으로 진행(`forward`)과 되돌아감(`backward`)을 구분하고, 카테고리별 이탈 퍼널은 `from_category` + `direction=forward`로 관찰합니다. `Phase 2 · 계획`(KNK-621) — 세계관 탭 개편([`3-1-client.md §3-1-4`](./3-1-client.md))이 구현되면 카테고리 축이 세계관(장르·배경)·주인공·주변 인물로 바뀌므로 `from_category`/`to_category` 값 집합을 함께 갱신합니다.

`client_storyCreate_addTag_submitted`의 `category`는 세 카테고리에서 모두 발생합니다. 세계관 탭 개편(KNK-621)이 구현되면 장르에서 직접 추가가 사라져 `GENRE`가 더 이상 발생하지 않으므로, 그 시점에 값 집합을 함께 갱신합니다. **인물의 이름·성별은 어떤 이벤트에도 싣지 않습니다** — 사용자가 자유 입력하는 값이라 원문 수집 원칙([§6-7](#6-7-개인정보와-원문-수집-원칙))에 걸립니다. 인물 수·성별 선택 여부 같은 파생 지표가 필요해지면 값이 아니라 집계 형태로 따로 설계합니다.

`client_storyCreate_completeError_shown`은 클라이언트가 완성 요청 실패로 에러 상태를 표시할 때 발생하며, `stage`로 스토리 생성(`story`)과 채팅 생성(`chat`) 실패를 구분합니다.

`selectedTagsButton_clicked`는 스토리라인 선택(`storylineSelect`) 단계 탭 우측의 키워드 보기 버튼으로 선택 키워드 드로워를 열 때 발생합니다. 드로워에 노출되는 태그 이름은 이벤트에 넣지 않고 `creation_id`만 보냅니다.

제작 단계 `step_name`은 다음 값만 사용합니다.

| step_number | step_name         |
| ----------- | ----------------- |
| `1`         | `keyword`         |
| `2`         | `storylineSelect` |
| `3`         | `additionalInfo`  |
| `4`         | `complete`        |

#### 6-4-2-4. 스토리 상세

| 이벤트                                       | 우선순위 | 발생 시점                            | 고유 프로퍼티             |
| -------------------------------------------- | -------- | ------------------------------------ | ------------------------- |
| `client_storyDetail_viewed`                  | P0       | 스토리 상세 화면 진입                | `story_id` (string, 필수) |
| `client_storyDetail_chatStartButton_clicked` | P0       | 채팅 시작 버튼 클릭                  | `story_id` (string, 필수) |
| `client_storyDetail_thumbnail_clicked`       | P2       | 스토리 썸네일 클릭(썸네일 뷰어 열기) | `story_id` (string, 필수) |

추천 스토리 카드는 아직 도입되지 않은 기능입니다. 기능 도입 시 `client_storyDetail_recommendStoryCard_clicked`와 `client_storyDetail_recommendStoryCard_impressed`(P1, `story_id` string 필수, `position` number 선택)를 추가합니다. 이때 `story_id`는 현재 보는 스토리가 아니라 추천 카드의 스토리 ID입니다.

#### 6-4-2-5. 채팅 목록

| 이벤트                               | 우선순위 | 발생 시점           | 고유 프로퍼티                                       |
| ------------------------------------ | -------- | ------------------- | --------------------------------------------------- |
| `client_chatList_viewed`             | P1       | 채팅 목록 화면 진입 | 없음                                                |
| `client_chatList_chatCard_clicked`   | P1       | 채팅 카드 클릭      | `chat_id` (string, 필수), `position` (number, 선택) |
| `client_chatList_chatCard_impressed` | P1       | 채팅 카드 유효 노출 | `chat_id` (string, 필수), `position` (number, 선택) |

#### 6-4-2-6. 채팅

| 이벤트                                                  | 우선순위 | 발생 시점                                         | 고유 프로퍼티                                                                                                                                                                               |
| ------------------------------------------------------- | -------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `client_chat_viewed`                                    | P0       | 채팅 화면 진입                                    | `chat_id` (string, 필수)                                                                                                                                                                    |
| `client_chat_settingsButton_clicked` `폐기`             | P2       | (폐기) 채팅 설정 드로어 열기                      | `chat_id` (string, 필수)                                                                                                                                                                    |
| `client_chat_inputMode_selected`                        | P1       | 입력 모드 전환(입력 툴바 메뉴에서 블럭/일반 선택) | `chat_id` (string, 필수), `mode` (string, 필수: `block` / `plain`)                                                                                                                          |
| `client_chat_choicesToggle_clicked`                     | P2       | 추천 입력 켬/끔 전환(입력 툴바 메뉴)              | `chat_id` (string, 필수), `enabled` (boolean, 필수: 전환 후 상태)                                                                                                                           |
| `client_chat_messageInput_submitted`                    | P0       | 사용자 메시지 전송                                | `chat_id` (string, 필수), `turn_number` (number, 필수), `input_mode` (string, 필수: `block` / `plain` / `choice`)                                                                           |
| `client_chat_addBlockButton_clicked`                    | P2       | 블럭 입력 모드에서 상황·대사 블럭 추가 클릭       | `chat_id` (string, 필수), `block_type` (string, 필수: `situation` / `dialogue`)                                                                                                             |
| `client_chat_removeBlockButton_clicked`                 | P2       | 블럭 입력 모드에서 입력 블럭 삭제 클릭            | `chat_id` (string, 필수), `block_type` (string, 필수: `situation` / `dialogue`)                                                                                                             |
| `client_chat_situationInsertButton_clicked`             | P2       | 일반 입력 모드에서 상황 추가(강조 표기 삽입) 클릭 | `chat_id` (string, 필수)                                                                                                                                                                    |
| `server_chat_aiMessage_processed_succeeded`             | P0       | AI 응답 생성 성공                                 | `chat_id` (string, 필수), `turn_number` (number, 필수), `is_regenerated` (boolean, 필수 `Phase 1 · 계획`), `ending_id` (string, 선택 `Phase 1 · 계획`: 도달한 엔딩 식별자 — 엔딩 도달 턴만) |
| `server_chat_aiMessage_processed_failed`                | P0       | AI 응답 생성 실패                                 | `chat_id` (string, 필수), `turn_number` (number, 필수), `error_type` (string, 필수), `is_regenerated` (boolean, 필수 `Phase 1 · 계획`)                                                      |
| `client_chat_regenerateButton_clicked` `Phase 1 · 계획` | P1       | 마지막 AI 응답 다시 생성 버튼 클릭                | `chat_id` (string, 필수), `turn_number` (number, 필수)                                                                                                                                      |
| `client_chat_chatImage_impressed` `Phase 1 · 계획`      | P1       | 채팅 이미지 유효 노출(§6-4-3 기준)                | `chat_id` (string, 필수), `turn_number` (number, 필수), `image_key` (string, 필수)                                                                                                          |
| `client_chat_endingBadge_impressed` `Phase 1 · 계획`    | P1       | 엔딩 도달 배지 유효 노출(§6-4-3 기준)             | `chat_id` (string, 필수), `turn_number` (number, 필수), `ending_id` (string, 필수: 도달한 엔딩 식별자)                                                                                      |
| `client_chat_choiceOption_selected`                     | P1       | 선택지 선택                                       | `chat_id` (string, 필수), `turn_number` (number, 필수), `position` (number, 선택)                                                                                                           |
| `client_chat_choiceFillButton_clicked`                  | P1       | 선택지를 입력창에 넣어 수정 버튼 클릭             | `chat_id` (string, 필수), `turn_number` (number, 필수), `position` (number, 선택)                                                                                                           |
| `client_chat_streamError_shown`                         | P1       | AI 응답 스트리밍 실패 에러 표시                   | `chat_id` (string, 필수), `turn_number` (number, 필수)                                                                                                                                      |
| `client_chat_loadError_shown`                           | P1       | 채팅 화면 로드 실패 에러 표시                     | `chat_id` (string, 필수)                                                                                                                                                                    |
| `client_chat_retryButton_clicked`                       | P1       | 로드 실패 후 다시 시도 버튼 클릭                  | `chat_id` (string, 필수)                                                                                                                                                                    |
| `client_chat_tour_shown`                                | P2       | 첫 진입 안내 투어 노출                            | `chat_id` (string, 필수)                                                                                                                                                                    |
| `client_chat_tourStep_viewed`                           | P2       | 안내 투어의 각 스텝 도달                          | `chat_id` (string, 필수), `step_number` (number, 필수: 0부터), `step_id` (string, 필수: `add-blocks`·`add-emphasis`·`settings`·`random-send`)                                                |
| `client_chat_tour_completed`                            | P2       | 안내 투어 완주(마지막 스텝에서 완료)              | `chat_id` (string, 필수)                                                                                                                                                                    |
| `client_chat_tourSkipButton_clicked`                    | P2       | 안내 투어 건너뛰기 버튼 클릭                      | `chat_id` (string, 필수), `step_number` (number, 필수: 건너뛴 시점의 스텝)                                                                                                                   |
| `client_chatShareDialog_shown` `Phase 1 · 구현`         | P1       | 헤더 공유 버튼 클릭으로 공유 확인 다이얼로그 노출(KNK-715)                       | `chat_id` (string, 필수), `turn_number` (number, 필수)                                                                                                                                      |
| `client_chat_shareButton_clicked` `Phase 1 · 구현`      | P1       | 공유 다이얼로그 "링크 복사하기" 확정 클릭(발급 시도, KNK-715 이전에는 옵션 메뉴 항목 클릭) | `chat_id` (string, 필수), `turn_number` (number, 필수: 발급 시점 턴 수)                                                                                                                     |
| `client_chatShareDialog_dismissed` `Phase 1 · 구현`     | P1       | 공유 다이얼로그를 발급 없이 닫음("나중에 하기"·배경 탭·ESC, KNK-715)             | `chat_id` (string, 필수), `turn_number` (number, 필수)                                                                                                                                      |

채팅 화면은 블럭 입력(상황·대사를 나눠 입력)과 일반 입력(한 입력창에 자유 입력) 두 모드를 제공하며 기본값은 블럭 입력입니다. `client_chat_messageInput_submitted`의 `input_mode`는 메시지가 어떻게 작성·전송됐는지를 뜻하며, `block`(블럭 입력 직접 입력), `plain`(일반 입력 직접 입력), `choice`(AI 선택지 탭 전송) 중 하나입니다. 선택지 탭으로 전송된 메시지는 활성 모드와 무관하게 `choice`로 보내므로, 직접 입력 참여는 `input_mode in (block, plain)`으로, 선택지 기반 전송은 `input_mode = choice`로 바로 구분합니다. 선택지 탭은 이 이벤트와 함께 같은 `chat_id`·`turn_number`로 `client_chat_choiceOption_selected`도 발생시킵니다. `client_chat_inputMode_selected`는 입력 툴바의 모드 메뉴에서 실제로 다른 모드로 전환할 때만 발생하며(같은 모드 재선택 제외), `mode`는 전환 후 모드입니다. 기본값이 블럭 입력이므로 블럭 입력 UX 검증은 일반 입력으로 전환하는 비율로 관찰합니다. 같은 툴바의 추천 입력 켬/끔은 `client_chat_choicesToggle_clicked`로 수집하며(같은 상태 재선택 제외, `enabled`는 전환 후 상태), 기본값이 켬이므로 끄는 비율로 추천 입력의 방해 여부를 관찰합니다.

`client_chat_settingsButton_clicked`는 채팅 설정 드로어 전용 이벤트였으나, 드로어를 걷어내고 입력 툴바 메뉴 + 헤더 옵션 메뉴로 바꾸면서(2026-07-16, KNK-611 — [`3-1-client.md §3-1-5`](./3-1-client.md)) 발화 지점이 사라졌습니다. 과거 수집분 해석을 위해 표에는 `폐기`로 남기고 신규 수집은 하지 않습니다.

`client_chat_choiceFillButton_clicked`는 선택지를 바로 전송하지 않고 입력창에 채워 수정할 때 발생합니다. 선택지 사용률(§6-5-4)은 그대로 전송한 `client_chat_choiceOption_selected`만으로 계산하고, 수정 후 사용 행동은 이 이벤트로 별도 관찰합니다.

안내 투어 4종(KNK-694)은 첫 채팅 진입 안내가 실제로 읽히는지 보는 보조 계측입니다. 완주율은 `client_chat_tour_completed` ÷ `client_chat_tour_shown`으로, 이탈 지점은 `client_chat_tourSkipButton_clicked`의 `step_number` 분포로 봅니다. 투어는 기기별 1회만 노출하고 재열람 진입점이 없으므로 `tour_shown`은 사용자당 사실상 1회입니다(`localStorage` 차단 환경에서는 진입마다 반복될 수 있음 — [`3-1-client.md §3-1-5`](./3-1-client.md)). `step_id`는 단계 번호가 아닌 안내 대상 식별자이며 입력 모드에 따라 첫 스텝이 `add-blocks`(블럭)·`add-emphasis`(일반)로 갈립니다. 같은 화면의 추천 입력 인라인 힌트는 별도 이벤트를 두지 않습니다 — 사용자가 조작하는 UI가 아니라 문구 노출이라 추천 사용률(`client_chat_choiceOption_selected`, §6-5-4)의 변화로 관찰합니다.

`client_chat_loadError_shown`은 채팅 화면 진입 후 대화 내용을 불러오지 못해 에러 상태가 표시될 때 발생합니다. 채팅 진입(`client_chat_viewed`) 대비 로드 실패로 인한 이탈을 구분하는 데 사용합니다. `client_chat_streamError_shown`은 사용자가 메시지를 보낸 뒤 AI 응답 스트리밍이 클라이언트에서 실패(연결 끊김·중단 등)해 에러 토스트가 표시될 때 발생하며, 사용자 취소(abort)로 인한 중단은 제외합니다. 두 이벤트 모두 클라이언트가 체감한 실패이며, 서버가 판단하는 AI 응답 생성 실패는 `server_chat_aiMessage_processed_failed`로 봅니다.

AI 응답 성공·실패는 백엔드가 `server_chat_aiMessage_processed_succeeded` 또는 `server_chat_aiMessage_processed_failed`로 발행합니다. 프론트엔드는 `chat_id`와 `turn_number`로 메시지와 응답을 연결합니다.

`Phase 1 · 계획` — AI 응답 재생성([`4-backend.md §4-3-9`](./4-backend.md))은 별도 서버 이벤트를 만들지 않고 `server_chat_aiMessage_processed_*`에 `is_regenerated` 프로퍼티를 추가해 구분합니다(일반 턴 `false`, 재생성 `true` — 같은 AI 처리라 이벤트를 나누면 AI 응답 성공률 집계가 이원화되기 때문). 재생성은 메시지 전송이 아니므로 `client_chat_messageInput_submitted`를 발생시키지 않고, 요청 트리거는 `client_chat_regenerateButton_clicked`가 담당합니다. 따라서 `messageInput_submitted`를 분모로 쓰는 지표(§6-5-4)의 분자에는 `is_regenerated = false` 필터가 필요하고, 재생성 사용률은 별도 지표로 봅니다. `client_chat_chatImage_impressed`의 `image_key`는 턴 응답·SSE `completed`의 `imageKey` 필드([`4-backend.md §4-3-9`](./4-backend.md))에서 채우며, 이미지 자산 키(팀 프리셋·업로드 키)라 원문 수집 원칙(§6-7)에 저촉되지 않습니다.

`Phase 1 · 계획` — 엔딩 도달([`4-backend.md §4-3-10`](./4-backend.md))도 별도 서버 이벤트 없이 `server_chat_aiMessage_processed_succeeded`의 `ending_id` 프로퍼티로 구분합니다(같은 AI 처리 — 재생성과 동일 근거). 엔딩 도달률은 `ending_id is not null` 필터로 계산하고, 도달의 정본 기록은 이벤트가 아니라 백엔드의 턴 기록·집계 테이블입니다. `client_chat_endingBadge_impressed`는 도달 표시(US-6-13)가 실제로 사용자에게 보였는지를 확인하는 노출 신호이며, `ending_id`는 엔딩 이름 원문이 아니라 식별자라 §6-7에 저촉되지 않습니다.

#### 6-4-2-7. 피드백

| 이벤트                                           | 우선순위 | 발생 시점             | 고유 프로퍼티               |
| ------------------------------------------------ | -------- | --------------------- | --------------------------- |
| `client_feedback_viewed`                         | P0       | 피드백 화면 진입      | 없음                        |
| `client_feedback_form_submitted`                 | P0       | 피드백 제출 버튼 클릭 | 없음                        |
| `server_feedback_submission_processed_succeeded` | P1       | 피드백 제출 처리 성공 | 없음                        |
| `server_feedback_submission_processed_failed`    | P1       | 피드백 제출 처리 실패 | `error_type` (string, 필수) |

server 이벤트의 `error_type`은 `network`, `validation`, `server` 중 하나만 사용합니다. 상세 매핑은 `6-6-7. 서버 분석 이벤트와 실패 타입`을 따릅니다.

#### 6-4-2-8. 로그인·계정 — 클라이언트 이벤트 `Phase 1 · 구현` / 서버 이벤트 `Phase 1 · 계획`

로그인 화면(FE-SCREEN-008)과 게스트 데이터 마이그레이션의 이벤트입니다. 마이그레이션은 로그인 직후 자동 실행되므로 클라이언트 계측 없이 서버 이벤트로 수집합니다.

| 이벤트                                                          | 우선순위 | 발생 시점                                        | 고유 프로퍼티                                                                                                                |
| --------------------------------------------------------------- | -------- | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| `client_login_viewed` `Phase 1 · 구현`                          | P1       | 로그인 화면 진입                                 | 없음                                                                                                                         |
| `client_login_googleButton_clicked` `Phase 1 · 구현`            | P1       | Google 로그인 버튼 클릭                          | 없음                                                                                                                         |
| `client_login_kakaoButton_clicked` `Phase 1 · 구현`             | P1       | 카카오 로그인 버튼 클릭(KNK-721)                 | 없음                                                                                                                         |
| `client_login_oauthError_shown` `Phase 1 · 구현`                | P0       | OAuth 콜백 실패로 `/login` 복귀 시 NextAuth `error` 쿼리 감지(KNK-721) | `error_code` (string, 필수 — NextAuth error 값) · `provider` (string, 시작 provider를 알 수 없으면 null)                     |
| `client_account_viewed` `Phase 1 · 구현`                        | P1       | 마이 페이지 진입                                 | 없음                                                                                                                         |
| `client_account_loginButton_clicked` `Phase 1 · 구현`           | P1       | 마이 페이지 프로필 헤더 로그인 버튼 클릭(게스트) | 없음                                                                                                                         |
| `client_account_logoutButton_clicked` `Phase 1 · 구현`          | P1       | 마이 페이지 로그아웃 클릭                        | 없음                                                                                                                         |
| `client_account_linkAccountButton_clicked` `Phase 1 · 구현`     | P1       | 마이 페이지 계정 연동 버튼 클릭(KNK-740)         | `provider` (string, 필수 — 연동 **대상** provider, `google` · `kakao`)                                                       |
| `server_login_googleLogin_processed_succeeded` `Phase 1 · 구현` | P0       | Google 로그인 처리 성공                          | `is_new_user` (boolean, 필수)                                                                                                |
| `server_login_googleLogin_processed_failed` `Phase 1 · 구현`    | P0       | Google 로그인 처리 실패                          | `error_type` (string, 필수)                                                                                                  |
| `server_login_kakaoLogin_processed_succeeded` `Phase 1 · 구현`  | P0       | Kakao 로그인 처리 성공(KNK-721)                  | `is_new_user` (boolean, 필수)                                                                                                |
| `server_login_kakaoLogin_processed_failed` `Phase 1 · 구현`     | P0       | Kakao 로그인 처리 실패(KNK-721)                  | `error_type` (string, 필수)                                                                                                  |
| `server_link_socialLink_processed_succeeded` `Phase 1 · 구현`   | P1       | 계정 연동 처리 성공(KNK-739)                     | `provider` (string, 필수 — `google` · `kakao`)                                                                               |
| `server_link_socialLink_processed_failed` `Phase 1 · 구현`      | P1       | 계정 연동 처리 실패(KNK-739)                     | `provider` (string, 필수) · `error_type` (string, 필수)                                                                      |
| `server_login_migration_processed_succeeded` `Phase 1 · 구현`   | P0       | 마이그레이션 처리 완료(부분 성공 포함)           | `migrated_story_count` · `migrated_chat_count` · `already_owned_count` · `conflict_count` · `not_found_count` (number, 필수) |
| `server_login_migration_processed_failed` `Phase 1 · 구현`      | P0       | 마이그레이션 요청 자체 실패(400 등)              | `error_type` (string, 필수)                                                                                                  |

**결정 기록 — 서버 로그인 이벤트는 provider별 이름을 유지합니다(2026-07-31, KNK-721).** `server_login_googleLogin_processed_*`는 이미 운영에서 발행 중입니다(서버 `ServerAnalytics` 구현·통합 테스트가 이름을 검증하고, 운영 user-data가 `MANYAK_ANALYTICS_AMPLITUDE_ENABLED=true`로 발행하며, Amplitude 적재를 확인 — 2026-07-31). 따라서 `server_login_socialLogin_*` + `provider` 프로퍼티로의 개명은 지표 이력 단절 또는 전환기 이중 발행(dual-write)·대시보드 이전을 요구해 기각합니다. 카카오는 `server_login_kakaoLogin_processed_*`를 새로 추가하고 고유 프로퍼티는 Google과 동일하게 둡니다. 전체 로그인 성공률·전환은 두 이벤트 합산 차트로, provider 비교는 이벤트별 시리즈로 봅니다. 클라이언트 버튼 클릭도 같은 구조입니다(`client_login_googleButton_clicked` · `client_login_kakaoButton_clicked` — 명명 규칙 `client_{화면}_{요소}_{동작}` 유지).

**서버 `processed_failed`는 백엔드에 로그인 요청이 도달한 이후의 실패만 셉니다.** 토큰 교환 실패(`invalid_client`), 카카오 OIDC 비활성, redirect URI 불일치 같은 OAuth 콜백 단계 실패는 백엔드 호출 전에 끝나므로 서버 이벤트에 잡히지 않습니다 — 콜백 단계에서 로그인이 전면 실패해도 서버 실패율은 정상으로 보입니다. 이 사각지대는 `client_login_oauthError_shown`(NextAuth가 `error` 쿼리와 함께 `/login`으로 복귀시키는 시점에 발행 — [`3-1-client.md`](./3-1-client.md) FE-SCREEN-008)이 커버합니다. 카카오 로그인 릴리스 검수는 서버 실패율과 함께 이 이벤트가 0건에 가깝게 유지되는지 확인하고, 지속 발생 시 콘솔 설정(OIDC 토글·리다이렉트 URI·클라이언트 시크릿)을 점검합니다.

- `is_new_user`는 find-or-create에서 신규 생성이면 `true`입니다.
- 마이그레이션 카운트는 스토리+채팅 합산이 제출 총수와 일치해야 합니다(정합 검증용). 제출 배열이 스토리·채팅 모두 비면 이벤트를 발행하지 않습니다(0건 노이즈 방지).
- 로그아웃은 서버가 refresh를 폐기하지만 분석은 `client_account_logoutButton_clicked` 하나로 충분해 별도 `server_*`를 두지 않습니다. 프론트엔드는 로그아웃 클릭 시 이벤트를 보낸 뒤 analytics `reset()`을 수행합니다(§6-2) — 이벤트 전송이 리셋보다 먼저여야 로그아웃 직전 사용자에게 귀속됩니다.
- `client_account_loginButton_clicked`는 게스트가 마이 페이지에서 로그인 화면으로 이동한 유입을 구분합니다. 로그인 화면 진입 자체는 `client_login_viewed`로 측정합니다.
- 계정 연동(KNK-740)의 클라이언트 이벤트는 시도 시점(`client_account_linkAccountButton_clicked`) 하나뿐입니다. 성공·실패는 서버가 `server_link_socialLink_processed_*`로 이미 잡고 있어 중복이며, 클라이언트에서 결과를 다시 보내면 재인증·연동 2단계를 한 시도로 세기 어려워집니다. 이 이벤트는 인앱 브라우저 차단으로 플로우가 시작되지 않은 경우에도 발화해 차단 빈도를 함께 측정합니다. 링크 코드는 비밀값이라 어떤 이벤트에도 싣지 않습니다(§6-6 관측 금지 규칙).

#### 6-4-2-9. 크레딧 — `Phase 1 · 구현`

마이 페이지의 적립 인터랙션과 크레딧·체험 한도 거절(402) 신호입니다. 소모·환불 자체는 이벤트가 아니라 크레딧 원장(`credit_transactions`)이 정본이고([`4-backend.md §4-3-7`](./4-backend.md)), 분석 이벤트는 사용자 행동과 전환 신호만 수집합니다.

| 이벤트                                           | 우선순위 | 발생 시점                                                                        | 고유 프로퍼티                                                                                                  |
| ------------------------------------------------ | -------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `client_account_attendanceButton_clicked`        | P1       | 마이 페이지 출석체크 클릭                                                        | 없음                                                                                                           |
| `client_invite_viewed`                           | P1       | 친구 초대 페이지(`/my/invite`) 진입                                              | 없음                                                                                                           |
| `client_invite_copyButton_clicked`               | P1       | 친구 초대 페이지 초대 코드 복사 클릭(KNK-567 — 복사 대상이 링크에서 코드로 변경) | 없음                                                                                                           |
| `client_invite_kakaoShareButton_clicked`         | P1       | 친구 초대 페이지 카카오톡 공유 클릭                                              | 없음                                                                                                           |
| `client_invite_codeInput_submitted`              | P1       | 초대 코드 제출(`POST /users/me/invite/redeem` 호출, KNK-567)                     | `source` (string, 필수: `invite_page` / `onboarding`)                                                          |
| `client_invite_codeInput_succeeded`              | P0       | 초대 코드 제출 성공 — 양측 적립(KNK-567, 초대 전환의 종점)                       | `source` (동일)                                                                                                |
| `client_invite_codeInput_failed`                 | P1       | 초대 코드 제출 실패(KNK-567)                                                     | `source` (동일), `error_type` (string, 필수: `not_found` / `self_code` / `already_redeemed` / `network`)       |
| `client_inviteOnboarding_shown`                  | P1       | 신규 가입 온보딩의 초대 코드 스텝 노출(KNK-567)                                  | 없음                                                                                                           |
| `client_inviteOnboarding_skipped`                | P1       | 초대 코드 스텝 건너뛰기 — "나중에 하기" 버튼·배경 탭·ESC 공통(KNK-567, KNK-715)  | 없음                                                                                                           |
| `server_credit_earn_processed_succeeded`         | P1       | 적립 처리 성공(가입 500 · 초대 500, 초대자 월 10회 · 출석 250)                   | `reason` (string, 필수: `signup` / `invite` / `attendance`), `amount` (number, 필수), `balance` (number, 필수) |
| `client_guestLimitDialog_shown`                  | P0       | 로컬 카운터 선차단 또는 서버 402로 게스트 체험 한도 다이얼로그 노출              | `trigger` (string, 필수: `storyline_generate` / `story_create` / `chat_start` / `chat_turn`)                   |
| `client_guestLimitDialog_loginButton_clicked`    | P1       | 게스트 한도 다이얼로그의 로그인 CTA 클릭                                         | `trigger` (동일) · `provider` (string, 필수 — `google` · `kakao`, KNK-728)                                                                                               |
| `client_guestLimitDialog_dismissed`              | P1       | 게스트 한도 다이얼로그 닫기                                                      | `trigger` (동일)                                                                                               |
| `client_creditShortageDialog_shown`              | P0       | 402(INSUFFICIENT_CREDIT)로 크레딧 부족 다이얼로그 노출(회원)                     | `trigger` (동일)                                                                                               |
| `client_creditShortageDialog_earnButton_clicked` | P1       | 크레딧 부족 다이얼로그의 크레딧 받으러 가기 CTA 클릭(친구 초대로 이동)           | `trigger` (동일)                                                                                               |
| `client_creditShortageDialog_attendanceButton_clicked` | P1  | 크레딧 부족 다이얼로그의 출석 보상 받기 버튼 클릭(오늘 미출석일 때만 노출)       | `trigger` (동일)                                                                                               |
| `client_creditShortageDialog_dismissed`          | P1       | 크레딧 부족 다이얼로그 닫기                                                      | `trigger` (동일)                                                                                               |

- `guestLimitDialog`·`creditShortageDialog` 노출은 Phase 1의 핵심 전환 신호입니다 — 게스트 한도 소진 → 가입 전환(US-10-5), 회원 잔액 소진 → 보상 행동·향후 과금(Phase 3) 수요의 선행 지표.
- 두 다이얼로그는 화면 횡단 전역 오버레이라 네이밍 원칙(§6-3-1)의 screenName 자리에 다이얼로그명을 씁니다. 발생 지점은 `trigger`(`storyline_generate`: 스토리라인 생성/재생성, `story_create`: 스토리 완성, `chat_start`: 채팅 시작, `chat_turn`: 채팅 턴)로 구분하며, 이전 개정판의 화면 분리형 이벤트(`client_storyCreate_creditShortage_shown` 등 4종)와 `limit_type`·`chat_id` 프로퍼티를 대체합니다. CTA·닫기 클릭(P1)까지 수집해 전환 다이얼로그의 효과를 관찰합니다.
- 실패성 다이얼로그 노출은 기존 오버레이 관례(`completeError_shown` 등)에 맞춰 `shown`을 씁니다.
- 초대 이벤트는 원래 마이 페이지 복사 버튼 기준으로 `client_account_inviteLinkButton_clicked` 하나였으나, 친구 초대가 전용 페이지(`/my/invite`)로 분리되며 화면 관례에 맞춰 `client_invite_*` 3개로 대체했습니다. 초대 방식 개편(KNK-567 — 링크 어트리뷰션 → 코드 입력, [`4-backend.md §4-3-7`](./4-backend.md) 결정 기록)으로 코드 입력 3종(`codeInput_*`)과 온보딩 2종(`inviteOnboarding_*`)을 추가하고, 복사 버튼의 복사 대상을 링크에서 코드로 재정의했습니다.
- `client_invite_codeInput_failed`의 `error_type`은 redeem 오류 계약의 사유(404 `not_found`, 409 `INVITE_SELF_CODE` → `self_code`, 409 `INVITE_ALREADY_REDEEMED` → `already_redeemed`)와 네트워크 실패를 구분합니다 — 링크 방식과 달리 코드 입력은 타이핑 실패가 전환 손실의 주 요인이라 실패 사유 분포가 개편 효과 판정의 핵심 지표입니다.
- 적립 이벤트는 계정 화면이 아니라 서버 기능 도메인 기준이라 `server_credit_earn_*`으로 두고(가입은 로그인, 출석은 마이 페이지, 초대는 코드 입력(redeem)에서 발생 — KNK-567 전에는 로그인에서 발생) 사유를 `reason`으로 구분합니다.
- 적립 실패는 별도 이벤트 없이 서버 오류 관측(CloudWatch·Sentry)으로 추적합니다(멱등 재요청은 실패가 아니라 `rewarded: false` 성공).

#### 6-4-2-10. 일반 제작·스토리 수정 — `Phase 1 · 계획`

일반 제작 폼(FE-SCREEN-009)과 스토리 수정의 이벤트입니다. AI 처리가 없는 동기 CRUD라 서버 이벤트 없이 클라이언트 계측으로 충분합니다.

| 이벤트                                     | 우선순위 | 발생 시점                 | 고유 프로퍼티                                                                                 |
| ------------------------------------------ | -------- | ------------------------- | --------------------------------------------------------------------------------------------- |
| `client_storyCreate_methodOption_selected` | P1       | 제작 방식 선택(간편/일반) | `method` (string, 필수: `simple` / `general`)                                                 |
| `client_generalCreate_viewed`              | P1       | 일반 제작 폼 진입         | 없음                                                                                          |
| `client_generalCreate_completed`           | P1       | 일반 제작 등록 성공       | `story_id` (string, 필수), `main_event_count` · `ending_count` · `image_count` (number, 필수) |
| `client_storyEdit_viewed`                  | P1       | 수정 화면 진입            | `story_id` (string, 필수)                                                                     |
| `client_storyEdit_completed`               | P1       | 수정 저장 성공            | `story_id` (string, 필수)                                                                     |

- 간편 제작 퍼널 이벤트(`client_storyCreate_*`)는 방식 선택 이후의 간편 경로에서만 발생합니다. 일반 제작 완료율은 `generalCreate_viewed → completed`로 계산합니다.

#### 6-4-2-11. 법적 고지

이용약관·개인정보 처리방침 화면의 진입 이벤트입니다. 유입 경로 분석용 저우선 계측입니다.

| 이벤트                  | 우선순위 | 발생 시점                   | 고유 프로퍼티 |
| ----------------------- | -------- | --------------------------- | ------------- |
| `client_terms_viewed`   | P2       | 이용약관 화면 진입          | 없음          |
| `client_privacy_viewed` | P2       | 개인정보 처리방침 화면 진입 | 없음          |

#### 6-4-2-12. 인앱 브라우저 대응 — `Phase 1 · 계획`(KNK-567·KNK-681)

인앱 브라우저 감지·탈출([`3-2-web-app.md §3-2-5`](./3-2-web-app.md))의 관측 이벤트입니다. 카카오톡 탈출 스킴은 비공식 진입점이라 앱 업데이트로 깨질 수 있고, 이 이벤트가 스킴 생존율(시도 대비 실패 배너 노출 비율)을 관측하는 유일한 수단입니다. 화면 횡단 전역 동작이라 네이밍 원칙(§6-3-1)의 screenName 자리에 `inappBrowser`를 씁니다.

| 이벤트                                | 우선순위 | 발생 시점                                    | 고유 프로퍼티                                               |
| ------------------------------------- | -------- | -------------------------------------------- | ----------------------------------------------------------- |
| `client_inappBrowser_detected`        | P1       | 인앱 브라우저 UA 감지                        | `app` (string, 필수: `kakaotalk` / `instagram` / `threads`) |
| `client_inappBrowser_escapeAttempted` | P1       | 카카오톡 탈출 스킴 호출                      | `app` (string, 필수: `kakaotalk`)                           |
| `client_inappBrowser_bannerShown`     | P1       | 안내 배너 노출(카카오톡 탈출 실패 판정 포함) | `app` (동일 enum)                                           |

- 탈출 성공은 직접 계측할 수 없습니다(스킴 호출에 콜백이 없고 성공 시 페이지가 닫힘). `escapeAttempted` 대비 `bannerShown`(`app=kakaotalk`) 비율을 실패율의 대리 지표로 씁니다.
- 인앱별 유입량(`detected`의 `app` 분포)은 안내 배너만 두는 인스타그램·쓰레드에 자동 탈출 투자를 추가할지 판단하는 근거입니다.

**로그인 핸드오프 퍼널 — `Phase 1 · 계획`(KNK-681)**

인앱 게스트 허용·로그인 핸드오프 개편([`3-2-web-app.md §3-2-5`](./3-2-web-app.md))의 관측 이벤트입니다. 인앱 브라우저와 외부 브라우저는 Amplitude `device_id`가 서로 달라, 서버가 핸드오프 생성 시 발급하는 분석용 `handoff_id`가 두 구간을 잇는 유일한 키입니다. `handoff_id`는 비밀 핸드오프 코드와 별개의 값이며, 비밀 코드는 분석 이벤트·Sentry에 넣지 않습니다.

| 이벤트                                     | 우선순위 | 발생 시점                               | 고유 프로퍼티                                    |
| ------------------------------------------- | -------- | ---------------------------------------- | ------------------------------------------------ |
| `client_inappBrowser_loginHandoffCreated`   | P1       | 로그인 선택으로 핸드오프 생성 성공       | `app` (동일 enum), `handoff_id` (string, 필수)   |
| `client_loginContinue_viewed`               | P1       | 외부 브라우저 핸드오프 랜딩 진입         | `handoff_id` (string, 필수)                      |
| `client_loginContinue_loginButton_clicked`  | P1       | 랜딩에서 소셜 로그인 시작                | `handoff_id` (string, 필수) · `provider` (string, 필수 — `google` · `kakao`, KNK-728) |

- 목표 퍼널은 `인앱 유입(detected) → 스토리 생성 → 첫 채팅 → 핸드오프 생성 → 외부 랜딩 → 로그인 성공 → 이관 성공`입니다. 로그인·이관 구간은 서버 이벤트(§6-4-3)에 `handoff_id`를 실어 연결하며, 서버 측 프로퍼티 추가는 [`4-backend.md`](./4-backend.md) 소유로 협의합니다.
- **카카오톡 인앱의 카카오 로그인은 이 퍼널을 타지 않습니다** (`Phase 1 · 구현`, KNK-721·KNK-728). 같은 브라우저에서 핸드오프 없이 완료되므로([`3-2-web-app.md §3-2-5`](./3-2-web-app.md) 분기 표) 핸드오프 이벤트가 발생하지 않고, `device_id`가 연속이라 연결 키도 필요 없습니다. 카카오 로그인 배포 후 핸드오프 생성 건수 감소는 퍼널 이탈이 아니라 이 경로 전환의 정상 신호이므로, 인앱 로그인 전환은 핸드오프 퍼널과 `client_login_kakaoButton_clicked` → `server_login_kakaoLogin_processed_succeeded`를 합쳐 봅니다.
- 게스트 체험 이중 사용(미결, [`3-2-web-app.md §3-2-5`](./3-2-web-app.md)) 규모 판단을 위해, 개편 배포 시 공통 프로퍼티(§6-3-2)에 인앱 여부(`in_app_browser`: 동일 enum 또는 null)를 추가하는 것을 검토합니다 — 게스트 한도 도달 이벤트의 인앱 분포가 판단 근거입니다.

#### 6-4-2-13. 서비스 안내 — `Phase 1 · 구현`

서비스 안내 화면([`3-1-client.md` FE-SCREEN-011](./3-1-client.md))의 진입 이벤트입니다. 법적 고지(§6-4-2-11)와 같은 유입 경로 분석용 저우선 계측입니다.

| 이벤트                      | 우선순위 | 발생 시점             | 고유 프로퍼티 |
| --------------------------- | -------- | --------------------- | ------------- |
| `client_serviceInfo_viewed` | P2       | 서비스 안내 화면 진입 | 없음          |

#### 6-4-2-14. 채팅 공유 — `Phase 1 · 구현`

채팅 공유 열람 화면([`3-1-client.md` FE-SCREEN-012](./3-1-client.md))의 이벤트입니다. 발급 클릭은 채팅 화면 이벤트(§6-4-2-6의 `client_chat_shareButton_clicked`)가 담당하고, 여기서는 링크를 받은 사람의 열람과 전환만 수집합니다.

| 이벤트                               | 우선순위 | 발생 시점                        | 고유 프로퍼티             |
| ------------------------------------ | -------- | -------------------------------- | ------------------------- |
| `client_chatShare_viewed`            | P1       | 채팅 공유 열람 화면 진입         | `story_id` (string, 필수) |
| `client_chatShare_ctaButton_clicked` | P1       | 열람 화면 하단 CTA 버튼 클릭     | `story_id` (string, 필수) |

- **공유 식별자(`shareId`)는 이벤트·Sentry에 넣지 않습니다.** `shareId`는 곧 열람 토큰이라([`4-backend.md §4-3-11`](./4-backend.md)) 관측 저장소에 실으면 접근 권한이 새는 경로가 됩니다 — 핸드오프 비밀 코드와 동일 원칙(§6-4-2-12). 페이지뷰 자동수집·Sentry가 남기는 URL도 `/share/{shareId}` 경로는 식별자 구간을 마스킹합니다(핸드오프 코드 마스킹과 동일 처리).
- 열람 화면은 원본 `chat_id`도 알 수 없으므로(응답에 비노출) `chat_id` 공통 프로퍼티 대신 `story_id`만 보냅니다.
- CTA 클릭은 공유 링크가 신규 유입으로 이어졌는지를 보는 지표입니다. 열람 대비 클릭(`client_chatShare_viewed` 수 대비 `client_chatShare_ctaButton_clicked` 수)이 공유 열람 화면의 전환율입니다.
- 발급 대비 열람 비율은 건수 집계(`client_chat_shareButton_clicked` 수 대비 `client_chatShare_viewed` 수, 필요 시 `story_id` 단위)로 관찰합니다. 공유 건별 정밀 조인이 필요해지면 비밀 토큰과 분리된 분석용 ID를 서버가 발급하는 핸드오프 `handoff_id` 패턴(§6-4-2-12)을 따라 추가합니다.

### 6-4-3. impression 수집 기준

`impressed`는 특정 item 또는 section이 사용자 화면에 유효하게 노출된 상태를 뜻합니다.

| 항목           | 권장 기준                |
| -------------- | ------------------------ |
| 최소 노출 면적 | 컴포넌트 면적의 50% 이상 |
| 최소 노출 시간 | 1초 이상                 |

중복 노출은 동일 item 기준으로 한 번만 수집합니다. `동일 session_id + 동일 screenName + 동일 objectName + 동일 item_id` 기준으로 30초 이내 재노출은 중복으로 판단합니다. `section_id`, `section_name`, `item_id`는 정밀 계측 도입 시 추가합니다.

### 6-4-4. 전송 예시

```ts
track("client_storyCreate_step_viewed", {
  screen_name: "storyCreate",
  step_name: "keyword",
  step_number: 1,
});
```

```ts
track("client_storyCreate_storylineOption_selected", {
  screen_name: "storyCreate",
  creation_id: simpleCreationId,
  position: selectedIndex,
});
```

생성 성공·실패처럼 서버 결과를 뜻하는 이벤트는 프론트엔드 `client_*` 이벤트로 쓰지 않습니다. 프론트엔드는 `requested` 또는 `submitted` 이벤트를 남기고, 서버 처리 결과는 백엔드가 `server_*` 이벤트로 발행합니다.

## 6-5. 퍼널과 지표

### 6-5-1. 지표 원칙

MVP 지표는 사용자가 스토리를 만들고 채팅을 이어가는지 확인하는 데 집중합니다. 지표 계산의 기준 데이터는 Amplitude 이벤트입니다. 장애 원인, latency, token count, AI 실패 코드는 CloudWatch와 `ai_call_logs`로 보조 분석합니다.

같은 지표를 여러 방식으로 계산하지 않습니다. 지표 이름, 계산식, 집계 단위, 제외 조건은 이 문서를 원본으로 삼습니다.

### 6-5-2. 분석 단위

| 분석 단위        | 기준 키       | 사용 지표                            |
| ---------------- | ------------- | ------------------------------------ |
| 익명 사용자      | `device_id`   | 방문, 제작 시작, 전체 활성화         |
| 방문 세션        | `session_id`  | 같은 방문 안의 화면 흐름             |
| 스토리 생성 시도 | `analytics_creation_id` | 생성 성공 후 제작 완료까지의 흐름(현재 조인 가능 구간은 §6-5-3-1) |
| 채팅 세션        | `chat_id`     | 첫 메시지, 첫 AI 응답, N턴 이상 도달 |
| API 요청         | `request_id`  | 서버 로그, Sentry, AI 호출 상관관계  |

`analytics_creation_id`가 발급되기 전의 `client_storyCreate_viewed`, `client_storyCreate_storyGeneration_requested`는 `device_id`와 `session_id` 순차 기준으로 봅니다. `creation_id`가 포함된 이벤트부터는 `creation_id`를 고정값으로 둡니다.

### 6-5-3. 핵심 퍼널

#### 6-5-3-1. 스토리 제작 퍼널

키워드 입력부터 스토리 완성까지의 이탈과 생성 성공률을 측정합니다.

| 순서 | 단계            | 이벤트                                                   | 고정값        |
| ---- | --------------- | -------------------------------------------------------- | ------------- |
| 1    | 제작 진입       | `client_storyCreate_viewed`                              | device        |
| 2    | 생성 요청       | `client_storyCreate_storyGeneration_requested`           | device        |
| 3    | 생성 성공       | `server_storyCreate_storyGeneration_processed_succeeded` | `analytics_creation_id` |
| 4    | 스토리라인 선택 | `client_storyCreate_storylineOption_selected`            | `analytics_creation_id` |
| 5    | 제작 완료       | `client_storyCreate_completed`                           | `analytics_creation_id` `계획` — 이벤트에 값이 없어 현재는 조인 불가(§6-8-7 A2) |

**구간별 현재 조인 가능 여부** — 1~2단계는 `device_id`·`session_id` 순차 기준이라 영향이 없습니다. **3→4단계(생성 성공 → 스토리라인 선택)는 서버가 Long, 클라이언트가 문자열로 보내 타입이 정렬되지 않아 현재 그대로는 조인되지 않습니다**(§6-8-7 A3). **4→5단계(스토리라인 선택 → 제작 완료)는 완료 이벤트에 값 자체가 없어 조인할 수 없습니다**(A2). 두 간극이 해소되기 전까지 이 퍼널의 3단계 이후 구간은 `analytics_creation_id` 기준으로 계산할 수 없습니다.

화면 단계 이탈은 `client_storyCreate_step_viewed`의 `step_name` 순서(`keyword` -> `storylineSelect` -> `additionalInfo` -> `complete`)로 별도 관찰합니다. 키워드 단계 안의 카테고리별 이탈(장르 -> 주인공 -> 주변 인물)은 `client_storyCreate_tagCategory_selected`의 `from_category` + `direction=forward`로 관찰합니다. 완성 실패율은 `client_storyCreate_completeError_shown`(`client_storyCreate_storyCompletion_requested` 대비), 완성 성공률은 `client_storyCreate_completed`로 봅니다.

#### 6-5-3-2. 채팅 활성화 퍼널

채팅 진입 후 첫 메시지와 첫 AI 응답까지 도달하는지 측정합니다.

| 순서 | 단계       | 이벤트                                                       | 고정값    |
| ---- | ---------- | ------------------------------------------------------------ | --------- |
| 1    | 채팅 진입  | `client_chat_viewed`                                         | `chat_id` |
| 2    | 첫 메시지  | `client_chat_messageInput_submitted` where `turn_number = 1` | `chat_id` |
| 3    | 첫 AI 응답 | `server_chat_aiMessage_processed_succeeded`                  | `chat_id` |

대화 깊이는 퍼널이 아니라 `turn_number` 분포로 봅니다.

#### 6-5-3-3. 전체 활성화 퍼널

방문자가 스토리를 만들고 실제 대화까지 갔는지 측정합니다.

| 순서 | 단계       | 이벤트                                                       | 고정값    |
| ---- | ---------- | ------------------------------------------------------------ | --------- |
| 1    | 메인 방문  | `client_storyList_viewed`                                    | device    |
| 2    | 제작 시작  | `client_storyList_createButton_clicked`                      | device    |
| 3    | 제작 완료  | `client_storyCreate_completed`                               | device    |
| 4    | 첫 메시지  | `client_chat_messageInput_submitted` where `turn_number = 1` | `chat_id` |
| 5    | 첫 AI 응답 | `server_chat_aiMessage_processed_succeeded`                  | `chat_id` |

3단계 `client_storyCreate_completed`에서 발급된 `chat_id`로 4~5단계를 연결합니다.

### 6-5-4. 핵심 지표

| 영역        | 지표                           | 계산식                                                                                                                                                                     |
| ----------- | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 온보딩      | 제작 시작 전환율               | `client_onboarding_createButton_clicked` 수 / `client_onboarding_viewed` 수                                                                                                |
| 스토리 목록 | 스토리 카드 클릭률             | `client_storyList_storyCard_clicked` 수 / `client_storyList_storyCard_impressed` 수                                                                                        |
| 스토리 목록 | 제작 시작률                    | `client_storyList_createButton_clicked` 수 / `client_storyList_viewed` 수                                                                                                  |
| 스토리 제작 | 생성 요청률                    | `client_storyCreate_storyGeneration_requested` 수 / `client_storyCreate_viewed` 수                                                                                         |
| 스토리 제작 | 생성 성공률                    | `server_storyCreate_storyGeneration_processed_succeeded` 수 / `client_storyCreate_storyGeneration_requested` 수                                                            |
| 스토리 제작 | 생성 실패율                    | `server_storyCreate_storyGeneration_processed_failed` 수 / `client_storyCreate_storyGeneration_requested` 수. 이벤트 **수** 기준이라 계산 가능하지만, `analytics_creation_id`로 실패를 개별 시도에 붙이려면 A1·A3가 선행됩니다                                                               |
| 스토리 제작 | 생성 후 완료율 `계획`          | `client_storyCreate_completed` 수 / `server_storyCreate_storyGeneration_processed_succeeded` 수 (`analytics_creation_id` 기준) — **현재 계산 불가**: 완료 이벤트에 값이 없고(§6-8-7 A2) 서버·클라이언트 타입도 정렬되지 않았습니다(A3)                     |
| 스토리 제작 | 완성 실패율                    | `client_storyCreate_completeError_shown` 수 / `client_storyCreate_storyCompletion_requested` 수                                                                            |
| 스토리 제작 | 전체 제작 전환율               | `client_storyCreate_completed` 수 / `client_storyCreate_viewed` 수                                                                                                         |
| 스토리 제작 | 단계별 이탈율                  | `1 - 다음 단계 step_viewed 사용자 수 / 현재 단계 step_viewed 사용자 수`                                                                                                    |
| 스토리 상세 | 상세에서 채팅 시작 전환율      | `client_storyDetail_chatStartButton_clicked` 수 / `client_storyDetail_viewed` 수                                                                                           |
| 채팅 목록   | 채팅 카드 클릭률               | `client_chatList_chatCard_clicked` 수 / `client_chatList_chatCard_impressed` 수                                                                                            |
| 채팅        | 말 거는 비율                   | `client_chat_messageInput_submitted` 사용자 수 where `turn_number = 1` / `client_chat_viewed` 사용자 수                                                                    |
| 채팅        | AI 응답 성공률                 | `server_chat_aiMessage_processed_succeeded` 수 / `client_chat_messageInput_submitted` 수 (`Phase 1 · 계획` — 재생성 도입 후에는 분자에 `is_regenerated = false` 필터 필수) |
| 채팅        | AI 응답 실패율                 | `server_chat_aiMessage_processed_failed` 수 / `client_chat_messageInput_submitted` 수 (`Phase 1 · 계획` — 분자에 `is_regenerated = false` 필터 필수)                       |
| 채팅        | 재생성 사용률 `Phase 1 · 계획` | `client_chat_regenerateButton_clicked` 수 / `is_regenerated = false` `server_chat_aiMessage_processed_succeeded` 수                                                        |
| 채팅        | N턴 이상 도달률                | `turn_number >= N` 채팅 수 / `client_chat_viewed` 채팅 수                                                                                                                  |
| 채팅        | 채팅 로드 실패율               | `client_chat_loadError_shown` 수 / `client_chat_viewed` 수                                                                                                                 |
| 채팅        | 응답 스트리밍 실패율           | `client_chat_streamError_shown` 수 / `client_chat_messageInput_submitted` 수                                                                                               |
| 채팅        | 선택지 사용률                  | `client_chat_choiceOption_selected` 수 / `client_chat_messageInput_submitted` 수                                                                                           |
| 채팅        | 선택지 수정 사용률             | `client_chat_choiceFillButton_clicked` 수 / `client_chat_messageInput_submitted` 수                                                                                        |
| 채팅        | 일반 입력 전환율               | `mode = plain` `client_chat_inputMode_selected` 사용자 수 / `client_chat_viewed` 사용자 수                                                                                 |
| 피드백      | 피드백 제출률                  | `client_feedback_form_submitted` 사용자 수 / `client_feedback_viewed` 사용자 수                                                                                            |
| 피드백      | 제출 성공률                    | `server_feedback_submission_processed_succeeded` 수 / `client_feedback_form_submitted` 수                                                                                  |
| 피드백      | 제출 실패율                    | `server_feedback_submission_processed_failed` 수 / `client_feedback_form_submitted` 수                                                                                     |
| 전체        | 방문에서 활성화 전환율         | `server_chat_aiMessage_processed_succeeded` 도달 사용자 수 / `client_storyList_viewed` 사용자 수                                                                           |

생성, 응답, 제출 실패 사유는 server 이벤트의 `error_type`(`network`, `validation`, `server`) 분포로 봅니다.

### 6-5-5. 운영 지표

운영 지표는 제품 퍼널 지표가 아니라 장애 분석과 성능 관리에 사용합니다.

| 영역        | 지표                    | 계산 기준                                                      |
| ----------- | ----------------------- | -------------------------------------------------------------- |
| API         | API 실패율              | `api_request_failed` 수 / 전체 API 요청 수                     |
| 스토리 생성 | 스토리 생성 서버 실패율 | `story_generation_failed` 수 / `story_generation_requested` 수 |
| AI          | AI 호출 성공률          | `ai_call_logs.status = succeeded` 수 / 전체 AI 호출 수         |
| AI          | AI 호출 실패율          | `ai_call_logs.status = failed` 수 / 전체 AI 호출 수            |
| AI          | 기능별 실패율           | `feature`별 실패 수 / `feature`별 전체 호출 수                 |
| AI          | p50, p95 latency        | `ai_call_logs.latency_ms`의 p50, p95                           |
| AI          | 평균 입력 토큰 수       | `input_token_count` 평균                                       |
| AI          | 평균 출력 토큰 수       | `output_token_count` 평균                                      |
| AI          | 재시도율                | `retry_count > 0` 호출 수 / 전체 호출 수                       |
| 채팅        | 채팅 응답 저장 성공률   | `ai_response_saved` 수 / `user_message_saved` 수               |
| 피드백      | 피드백 제출 성공률      | `feedback_delivery_completed` 수 / 피드백 제출 API 요청 수     |

CloudWatch 이벤트와 `ai_call_logs` 기록 기준은 `6-6. 관측 구현`을 따릅니다.

### 6-5-6. 계산 주의사항

`server_storyCreate_storyGeneration_processed_failed`는 `analytics_creation_id`가 발급된 스토리 생성 처리 실패만 포함하는 것이 **목표 계약**입니다 — **현재 구현은 AI 호출·세션 저장 실패 등 발급 전 실패도 값 없이 발행할 수 있어, `analytics_creation_id` 기준 집계는 그만큼 누락됩니다**(§6-8-7 A1). 요청 형식 자체가 깨져 `creation_id`를 만들 수 없는 malformed request는 CloudWatch의 `api_request_failed`로만 추적합니다.

`client_chat_messageInput_submitted`는 사용자 메시지 전송 시점입니다. AI 응답 성공 여부는 `server_chat_aiMessage_processed_succeeded`로 판단합니다. 사용자가 메시지를 보냈지만 AI 응답이 실패한 경우 말 거는 비율에는 포함되고 AI 응답 성공률에는 포함되지 않습니다.

`client_chat_choiceOption_selected`는 선택지 사용 행동입니다. 선택지가 표시된 횟수 대비 선택률은 MVP 범위에 포함하지 않습니다. MVP에서는 메시지 전송 수 대비 선택지 선택 수로 선택지 사용률을 봅니다.

## 6-6. 관측 구현

### 6-6-1. 도구별 역할

| 도구             | 역할                 | MVP 적용 범위                                              |
| ---------------- | -------------------- | ---------------------------------------------------------- |
| Amplitude        | 사용자 행동 분석     | 퍼널, 전환율, 이탈율, 선택지 사용률                        |
| Meta 픽셀        | 광고 전환 신호       | `PageView`·`StorylinesGenerated`·`StoryCompiled`·`StartTrial` — Meta 캠페인 학습·성과 측정(KNK-616) |
| 브라우저 Sentry  | 웹 프론트엔드 오류 분석 | 렌더링 오류, 라우트 오류, API 실패, 사용자 행동 breadcrumb. Android Sentry 배선은 미정([`3-3-android-app.md §3-3-6`](./3-3-android-app.md)) |
| 서버 분석 이벤트 | 퍼널 결과 계측       | 생성 성공·실패, AI 응답 성공·실패, 피드백 제출 성공·실패   |
| 서버 Sentry      | 백엔드 예외 분석     | API 예외, AI 호출 실패, DB 오류, 외부 연동 실패            |
| CloudWatch       | 운영 로그와 지표     | API 요청 로그, 주요 비즈니스 이벤트, latency, status       |
| AI Sentry        | AI 서비스 오류 분석  | provider 오류, timeout, 파싱 실패, schema 검증 실패        |
| `ai_call_logs`   | AI 호출 이력         | 스토리라인 생성, 스토리 생성, 채팅 응답, 선택지 생성       |
| Langfuse         | AI LLM 트레이싱      | 정상·실패 LLM 호출의 프롬프트·응답 원문·토큰·지연 — AI 프로덕션 활성. 선호 신호 결합은 `Phase 1 · 계획` |

Amplitude 이벤트 수를 제품 지표 계산의 기준으로 사용합니다. Sentry 이벤트 수는 제품 지표 계산에 사용하지 않습니다.

Meta 픽셀도 제품 지표 계산에 사용하지 않습니다 — Meta 광고 최적화·성과 측정 전용이며, 브라우저당 1회 발화 정책과 광고 차단 손실 때문에 Amplitude 퍼널 수치와 정의상 불일치가 정상입니다(정본: 마케팅 전략 문서 "26/07"). 픽셀 이벤트는 프로퍼티 없이 전송하므로 원문 수집 원칙(§6-7)에 저촉되지 않고, `NEXT_PUBLIC_META_PIXEL_ID`가 있는 production에서만 전송합니다(래퍼: `src/observability/marketing/`). 이후 Conversions API 도입을 대비해 발화마다 `eventID`를 부여합니다.

### 6-6-2. 프론트엔드 API 헤더

모든 클라이언트(웹·Android)는 백엔드 API를 호출할 때 익명 사용자와 세션 식별자를 HTTP 헤더로 **best-effort** 전송합니다(플랫폼 공통 계약 — 현재 웹에서 검증됨, Android 배선은 [`3-3-android-app.md §3-3-4`](./3-3-android-app.md)에서 확정). 필수 여부의 정본은 백엔드 수용 계약([`4-backend.md §4-3` 요청·응답 헤더](./4-backend.md)·[`§4-3-7`](./4-backend.md))입니다.

| 헤더                  | 전송 계약 | 값           | 설명                                                                                     |
| --------------------- | --------- | ------------ | ----------------------------------------------------------------------------------------- |
| `X-Manyak-Device-Id`  | best-effort(일부 경로 필수) | 논리 `device_id`  | 일반 요청은 누락해도 거부되지 않고 백엔드가 `unknown`으로 채웁니다. 아래 필수 경로 참조. |
| `X-Manyak-Session-Id` | best-effort | 논리 `session_id` | 누락해도 요청이 거부되지 않습니다. 백엔드가 `unknown`으로 채웁니다.                      |
| `X-Manyak-Request-Id` | 클라이언트 미생성 | `request_id` | 클라이언트 앱은 생성·주입하지 않습니다. 백엔드가 생성해 응답 헤더로 echo합니다(§6-6-3). |

**`X-Manyak-Device-Id`가 정책상 필수인 경로** — ① 게스트 체험 한도 대상 요청(스토리라인 생성·스토리 완성·채팅 턴의 게스트 호출): 누락 시 400([`4-backend.md §4-3-7`](./4-backend.md)). ② 로그인 핸드오프 생성(`POST /auth/handoffs`): 원본 디바이스 ID를 서버에 보관하는 요청 자체의 목적값. ③ 핸드오프 없는 첫 로그인: 회원 체험 시드가 이 헤더를 사용하며 누락 시 소진 시드가 1회성으로 확정됩니다([`4-backend.md §4-3-5`](./4-backend.md)). SDK 초기화 전 첫 요청은 폴백 소스에서 읽고(웹: SDK가 남긴 쿠키), 값이 없으면 헤더를 생략합니다([`3-1-client.md §3-1-7`](./3-1-client.md#3-1-7-api-연동에러-처리-계약)).

프론트엔드는 `device_id` 원본 값을 헤더에 싣습니다. 백엔드는 저장 전 `device_id_hash`로 변환합니다. 프론트엔드는 별도 해시를 만들지 않습니다.

### 6-6-3. 요청 식별자와 상관관계

**관측 계층마다 싣는 상관 키가 다릅니다.** 아래 공통 상관 필드는 요청 단위로 어디서나 이어지지만, `creation_id`는 계층마다 **서로 다른 값**이므로 하나의 전역 필드 표로 묶지 않습니다(§6-2 두 개념 구분).

**공통 상관 필드** — 백엔드가 서버 분석 이벤트·CloudWatch 로그·Sentry scope·AI 호출 요청에 가능한 범위에서 함께 싣습니다.

| 필드             | 설명                                                   |
| ---------------- | ------------------------------------------------------ |
| `request_id`     | API 요청과 AI 호출을 연결하는 서버 내부 상관 ID입니다. |
| `device_id_hash` | 익명 `device_id`를 해시한 값입니다.                    |
| `session_id`     | 프론트엔드 세션 ID입니다.                              |
| `story_id`       | 스토리 ID입니다.                                       |
| `chat_id`        | 채팅 ID입니다.                                         |
| `turn_number`    | 사용자 메시지 기준 턴 번호입니다.                      |
| `ai_call_log_id` | AI 호출 로그 행 ID입니다.                              |

**계층별 `creation_id`** — 와이어 키 이름은 같지만 값이 다릅니다. 계층을 넘어 직접 조인하지 않습니다.

| 관측 계층                                          | 싣는 개념               | 값                                                          | 현재 구현 상태                                                                                             |
| --------------------------------------------------- | ----------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| 제품 분석 이벤트(`client_*`·`server_*`)            | `analytics_creation_id` | `simpleCreationId`(원본 `story_creation_sessions.id`)        | 구현. 단 타입·누락 간극이 있습니다(§6-8-7 A1~A3)                                                           |
| AI 호출 요청 헤더(`X-Manyak-Creation-Id`)·Langfuse | `trace_creation_id`     | 스토리라인 단계 `story_creation_requests.request_id`(UUID)   | 구현([`4-backend.md §4-7`](./4-backend.md))                                                                |
| CloudWatch 구조화 로그                             | `analytics_creation_id` | 제작 로그 이벤트(`story_create_requested` 등)의 `creation_id` 필드에 `simpleCreationId`를 싣습니다 | 구현. 요청 전역 MDC 필드가 아니라 **해당 로그 이벤트의 개별 필드**입니다(MDC 전역 키는 위 공통 상관 필드 중 `request_id`·`session_id`·`device_id_hash` 3종) |
| 서버 Sentry scope                                  | —                       | —                                                            | **현재 `creation_id`를 부착하지 않습니다**(MDC 전역 키만 tag·context로 올림 — §6-6-6)                      |
| `ai_call_logs`                                     | `trace_creation_id`     | 위 AI 호출 상관값                                            | **목표 계약** — 현재 테이블에 `creation_id` 컬럼이 없습니다(§6-6-9)                                        |

`request_id`는 서버 로그, Sentry, `ai_call_logs`를 잇는 서버 내부 상관 키입니다. 프론트엔드 `client_*` 이벤트와 백엔드 `server_*` 이벤트를 제품 분석에서 연결할 때는 현재 `analytics_creation_id`와 `chat_id`를 사용합니다(`analytics_creation_id` 경로의 잔여 간극은 §6-8-7 A1~A3).

### 6-6-4. 프론트엔드 Sentry 기준

수집 기준(최소 context·4xx 제외)은 클라이언트 공통 원칙이고, 아래 배선·`ignoreErrors` 목록은 **웹(브라우저 Sentry) 구현 기준**입니다. Android Sentry 배선은 미정이며 도입 시 같은 원칙을 따릅니다([`3-3-android-app.md §3-3-6`](./3-3-android-app.md)). 프론트엔드 Sentry에는 오류 분석에 필요한 최소 context만 넣습니다.

| 구분       | 수집 내용                                                           |
| ---------- | ------------------------------------------------------------------- |
| Tags       | `screen_name`, `story_id`, `chat_id`, `creation_id`(= `analytics_creation_id` — 분석 이벤트 프로퍼티에서 올림) |
| User       | `id: device_id`, `ip_address: "{{auto}}"`                           |
| Breadcrumb | P0 행동 이벤트 이름, 주요 API 요청 시작과 종료                      |
| Exceptions | 렌더링 오류, 라우트 오류, API 네트워크 오류, 예상하지 못한 5xx 응답 |

4xx 응답이 사용자가 복구할 수 있는 검증 오류라면 Sentry exception으로 보내지 않습니다. 사용자 행동 분석이 필요하면 Amplitude 이벤트로만 기록합니다. 서버 사이드 상관 키 `request_id`를 브라우저 Sentry Tags에 추가하는 것은 추후 도입 항목입니다.

앱 코드와 무관한 외부 노이즈는 `ignoreErrors`로 수집 자체를 차단합니다. 사용자 취소(`AbortError`)·`ResizeObserver` 경고 외에, SNS 인앱 브라우저(인스타그램·쓰레드·카카오톡 등)가 웹뷰에 주입하는 네이티브 브릿지 스크립트(`sendDataToNative`)가 페이지 이탈 시점에 던지는 오류(`window.webkit.messageHandlers` undefined, `Java object is gone`)도 여기에 해당합니다 — 웹 레포에서 고칠 수 없는 주입 스크립트 오류인데 사용자 영향 1위 이슈로 잡혀 실제 오류를 가렸기 때문입니다. 정본 목록은 `src/observability/monitoring/sentry.ts`의 `SENTRY_IGNORE_ERRORS`입니다.

### 6-6-5. 백엔드 CloudWatch 로그

모든 백엔드 로그는 JSON 형태로 남깁니다. CloudWatch `event_name`은 운영 로그 이름이며, `6-4. 이벤트 카탈로그`의 분석 이벤트 네이밍 컨벤션을 강제하지 않습니다.

```json
{
  "timestamp": "2026-06-23T12:00:00.000Z",
  "level": "INFO",
  "service": "manyak-server",
  "event_name": "story_created",
  "request_id": "req_...",
  "device_id_hash": "device_hash_...",
  "session_id": "session_...",
  "creation_id": "creation_...",
  "story_id": "story_...",
  "chat_id": null,
  "endpoint": "/api/v1/stories",
  "http_method": "POST",
  "status_code": 201,
  "duration_ms": 842
}
```

| 이벤트                        | 발생 시점                     | 핵심 필드                                                             |
| ----------------------------- | ----------------------------- | --------------------------------------------------------------------- |
| `api_request_completed`       | API 요청 정상 종료            | `endpoint`, `http_method`, `status_code`, `duration_ms`               |
| `api_request_failed`          | API 요청 실패                 | `endpoint`, `http_method`, `status_code`, `duration_ms`, `error_code` |
| `story_generation_requested`  | 스토리라인 생성 API 요청 수신 | `request_id`, `session_id`                                            |
| `story_generated`             | 스토리라인 생성 완료          | `creation_id`(= `analytics_creation_id`, §6-6-3), `duration_ms`                                          |
| `story_generation_failed`     | 스토리라인 생성 실패          | `creation_id`(= `analytics_creation_id`, §6-6-3), `error_code`, `duration_ms`                            |
| `story_created`               | 스토리 저장 완료              | `story_id`, `chat_id`, `duration_ms`                                  |
| `user_message_saved`          | 사용자 메시지 저장 완료       | `chat_id`, `story_id`, `turn_number`                                  |
| `ai_response_saved`           | AI 응답 저장 완료             | `chat_id`, `story_id`, `turn_number`, `ai_call_log_id`                |
| `feedback_delivery_completed` | 피드백 저장 또는 전달 완료    | `has_email`                                                           |

### 6-6-6. 백엔드 Sentry 기준

백엔드는 예상하지 못한 장애와 운영자가 확인해야 하는 실패만 Sentry에 보냅니다.

| 구분       | 수집 내용                                                                                                  |
| ---------- | ---------------------------------------------------------------------------------------------------------- |
| Tags       | `endpoint`, `http_method`, `status_code`, `error_code`, `story_id`, `chat_id`, `request_id`. `creation_id`는 **목표 계약** — 현재 서버 Sentry는 MDC 전역 키(`request_id`·`session_id`·`device_id_hash`)만 올리고 `creation_id`를 부착하지 않습니다(§6-6-3). 도입 시 어느 개념(`analytics_creation_id` / `trace_creation_id`)을 올릴지 함께 결정합니다 |
| Context    | `session_id`, `device_id_hash`, `feature`, `duration_ms`, `ai_call_log_id`                                 |
| Breadcrumb | API 요청 시작, DB 저장 완료, AI 호출 시작과 종료                                                           |
| Exceptions | 5xx 예외, DB 예외, AI 호출 timeout, AI 응답 검증 실패, Slack 피드백 webhook 실패                           |

사용자 입력 검증 실패처럼 예상 가능한 4xx 오류는 기본적으로 Sentry exception으로 보내지 않습니다. 같은 4xx 오류가 짧은 시간에 반복되어 운영 문제가 의심될 때만 warning 수준의 CloudWatch 로그로 확인합니다.

### 6-6-7. 서버 분석 이벤트와 실패 타입

서버 분석 이벤트의 전체 목록은 `6-4-2. 페이지별 이벤트 카탈로그`에 있습니다. 백엔드는 퍼널의 결과 단계를 채우는 `server_*` 분석 이벤트를 발행합니다.

`error_type`은 사용자·퍼널 분석용 거친 분류이며 `network`, `validation`, `server`만 사용합니다. 내부 상세 실패 코드(`ai_call_logs.error_code`)는 다음 기준으로 `error_type`에 매핑합니다.

| error_type   | 의미                              | 매핑되는 내부 error_code                                                                            |
| ------------ | --------------------------------- | --------------------------------------------------------------------------------------------------- |
| `network`    | 네트워크, 연결, timeout 실패      | `provider_timeout`, `provider_unavailable`                                                          |
| `validation` | 입력값, 응답 검증, 안전 정책 실패 | `provider_bad_request`, `schema_validation_failed`, `invalid_ai_response`, `content_filter_blocked` |
| `server`     | 서버 내부 처리 실패               | `provider_rate_limited`, `unexpected_error`                                                         |

`Phase 1 · 계획` — 로그인·마이그레이션 실패의 `error_type` 매핑입니다.

| error_type   | 로그인·마이그레이션 실패 사례                                                                      |
| ------------ | -------------------------------------------------------------------------------------------------- |
| `network`    | 소셜 인증 서버(Google·Kakao) 연결·timeout 실패                                                     |
| `validation` | 소셜 ID 토큰 서명·만료·issuer·audience 검증 실패(provider 미허용·client ID 목록 비어 있음 포함), 마이그레이션 요청 UUID 형식 오류·배열 100개 초과(400) |
| `server`     | 사용자 저장·소유권 이관 중 내부 처리 실패                                                          |

### 6-6-8. AI 기능과 요청 context

MVP에서 분석 대상이 되는 AI 기능은 다음 네 가지입니다.

| feature                 | 설명                                                                                      | 사용자 퍼널 연결                                                                                                  |
| ----------------------- | ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `storyline_generation`  | 선택 키워드로 스토리라인 후보 생성                                                        | `client_storyCreate_storyGeneration_requested`, `server_storyCreate_storyGeneration_processed_*`                  |
| `story_completion`      | 선택 스토리라인과 추가 정보로 스토리 상세 생성                                            | `client_storyCreate_storyCompletion_requested`, `client_storyCreate_completed`                                    |
| `chat_response`         | 사용자 메시지에 대한 AI 응답 생성(`Phase 1 · 계획` 재생성 포함 — `is_regenerated`로 구분) | `client_chat_messageInput_submitted`, `client_chat_regenerateButton_clicked`, `server_chat_aiMessage_processed_*` |
| `choice_generation`     | 선택지 생성 — 현행은 `chat_response` 내부 호출로 합산 적재. `Phase 1 · 계획`(KNK-622) 선택지 전용 엔드포인트 분리 후 별도 행 적재 시작(백엔드 feature enum `CHOICE_GENERATION` 기정의 — [`4-backend.md §4-7`](./4-backend.md)) | `client_chat_choiceOption_selected`                                                                               |

AI feature는 프론트엔드 이벤트명에 넣지 않습니다. 상세 원인은 `feature`와 `error_code`로 구분합니다.

백엔드는 AI 서비스 호출 시 다음 값을 전달합니다. AI 서비스는 값을 그대로 로그, Sentry scope, `ai_call_logs`에 연결합니다.

| 필드                      | 필수 여부 | 설명                                                 |
| ------------------------- | --------- | ---------------------------------------------------- |
| `request_id`              | 필수      | 백엔드와 AI 로그를 연결하는 서버 내부 상관 ID입니다. |
| `device_id_hash`          | 필수      | 익명 `device_id` 해시입니다.                         |
| `session_id`              | 필수      | 프론트엔드 세션 ID입니다.                            |
| `feature`                 | 필수      | AI 기능명입니다.                                     |
| `prompt_template_version` | 필수      | 프롬프트 템플릿 버전입니다.                          |
| `creation_id`             | 조건부    | 스토리라인 생성과 스토리 완성 시 필수입니다. 값은 **`trace_creation_id`**입니다(§6-2). |
| `story_id`                | 조건부    | 스토리 완성 후 또는 채팅 중 필수입니다.              |
| `chat_id`                 | 조건부    | 채팅 응답 생성 시 필수입니다.                        |
| `turn_number`             | 조건부    | 채팅 응답 생성 시 필수입니다.                        |

AI 서비스 응답에는 다음 메타데이터를 포함합니다.

| 필드                 | 설명                        |
| -------------------- | --------------------------- |
| `ai_call_log_id`     | `ai_call_logs` 행 ID입니다. |
| `model`              | 사용 모델입니다.            |
| `latency_ms`         | AI 호출 소요 시간입니다.    |
| `input_token_count`  | 입력 토큰 수입니다.         |
| `output_token_count` | 출력 토큰 수입니다.         |
| `error_code`         | 실패 시 오류 코드입니다.    |

### 6-6-9. `ai_call_logs` 기록 기준

AI 호출 1회당 `ai_call_logs`에 1행을 기록합니다. 재시도가 발생하면 같은 `request_id` 아래에서 `retry_count`를 증가시킵니다. 여러 모델을 순차 호출하는 기능이 생기면 provider 호출별로 행을 분리합니다. `Phase 1 · 계획`(KNK-622) — 선택지 전용 엔드포인트 분리 후에는 한 턴이 `chat_response`(본문+판정)와 `choice_generation`(선택지) 두 행으로 적재되고, `chat_id` + `turn_number`로 조인합니다.

| 컬럼                      | 타입 예시      | 설명                                               |
| ------------------------- | -------------- | -------------------------------------------------- |
| `id`                      | UUID           | AI 호출 로그 ID입니다.                             |
| `request_id`              | VARCHAR        | API 요청과 연결되는 ID입니다.                      |
| `caller_service`          | VARCHAR        | 호출 서비스입니다. MVP 값은 `manyak-server`입니다. |
| `feature`                 | VARCHAR        | AI 기능명입니다.                                   |
| `device_id_hash`          | VARCHAR        | 익명 `device_id` 해시입니다.                       |
| `session_id`              | VARCHAR        | 세션 ID입니다.                                     |
| `creation_id`             | VARCHAR NULL   | **`trace_creation_id`**입니다(스토리라인 생성 요청 UUID — §6-2). 분석 이벤트의 `analytics_creation_id`와 다른 값입니다. **목표 계약이며 현재 `ai_call_logs` 스키마에는 이 컬럼이 없습니다**(§6-6-3 계층별 표). |
| `story_id`                | VARCHAR NULL   | 연결된 스토리 ID입니다.                            |
| `chat_id`                 | VARCHAR NULL   | 연결된 채팅 ID입니다.                              |
| `turn_number`             | INTEGER NULL   | 사용자 메시지 기준 턴 번호입니다.                  |
| `provider`                | VARCHAR        | AI provider입니다.                                 |
| `model`                   | VARCHAR        | 모델명입니다.                                      |
| `prompt_template_version` | VARCHAR        | 프롬프트 템플릿 버전입니다.                        |
| `status`                  | VARCHAR        | `started`, `succeeded`, `failed` 중 하나입니다.    |
| `latency_ms`              | INTEGER        | AI 호출 소요 시간입니다.                           |
| `input_token_count`       | INTEGER NULL   | 입력 토큰 수입니다.                                |
| `output_token_count`      | INTEGER NULL   | 출력 토큰 수입니다.                                |
| `retry_count`             | INTEGER        | 재시도 횟수입니다.                                 |
| `error_code`              | VARCHAR NULL   | 내부 실패 코드입니다.                              |
| `sentry_event_id`         | VARCHAR NULL   | Sentry 이벤트 ID입니다.                            |
| `created_at`              | TIMESTAMP      | 생성 시각입니다.                                   |
| `completed_at`            | TIMESTAMP NULL | 완료 시각입니다.                                   |

실패 코드는 적게 유지합니다.

| error_code                 | 의미                                | error_type   |
| -------------------------- | ----------------------------------- | ------------ |
| `provider_timeout`         | provider 응답 시간 초과             | `network`    |
| `provider_rate_limited`    | provider rate limit                 | `server`     |
| `provider_bad_request`     | provider 요청 거부                  | `validation` |
| `provider_unavailable`     | provider 장애 또는 일시적 연결 실패 | `network`    |
| `invalid_ai_response`      | 응답이 서비스 기대 형식과 다름      | `validation` |
| `schema_validation_failed` | Pydantic 또는 응답 schema 검증 실패 | `validation` |
| `content_filter_blocked`   | 안전 정책 또는 필터에 의해 차단     | `validation` |
| `unexpected_error`         | 분류되지 않은 예외                  | `server`     |

### 6-6-10. AI CloudWatch와 Sentry 기준

AI 서비스 로그도 JSON 형태로 남깁니다.

```json
{
  "timestamp": "2026-06-23T12:00:00.000Z",
  "level": "INFO",
  "service": "manyak-ai",
  "event_name": "ai_call_completed",
  "request_id": "req_...",
  "ai_call_log_id": "ai_log_...",
  "feature": "chat_response",
  "creation_id": null,
  "story_id": "story_...",
  "chat_id": "chat_...",
  "turn_number": 2,
  "provider": "openai",
  "model": "model-name",
  "status": "succeeded",
  "latency_ms": 1280,
  "input_token_count": 1024,
  "output_token_count": 320,
  "retry_count": 0
}
```

| 이벤트                          | 발생 시점                         | 핵심 필드                                                                            |
| ------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------ |
| `ai_call_started`               | provider 호출 직전                | `feature`, `request_id`, `prompt_template_version`, `model`                          |
| `ai_call_completed`             | provider 호출과 응답 검증 성공    | `feature`, `ai_call_log_id`, `latency_ms`, `input_token_count`, `output_token_count` |
| `ai_call_failed`                | provider 호출 또는 응답 검증 실패 | `feature`, `ai_call_log_id`, `latency_ms`, `error_code`, `retry_count`               |
| `ai_response_validation_failed` | 응답 schema 검증 실패             | `feature`, `error_code`, `prompt_template_version`                                   |

| 구분       | 수집 내용                                                                                                                          |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Tags       | `feature`, `provider`, `model`, `prompt_template_version`, `error_code`, `request_id`                                              |
| Context    | `ai_call_log_id`, `session_id`, `device_id_hash`, `creation_id`(= `trace_creation_id`, §6-6-3), `story_id`, `chat_id`, `turn_number`, `latency_ms`, `retry_count` |
| Breadcrumb | AI 호출 시작, provider 응답 수신, schema 검증, DB 기록                                                                             |
| Exceptions | timeout, provider 오류, 파싱 실패, schema 검증 실패, 예상하지 못한 예외                                                            |

### 6-6-11. AI 품질 평가 로깅과 자가개선 루프 수집 기준 — `Phase 1 · 계획`

평가 지표의 정의·루프 규칙은 [`5-ai-server.md §5-6`](./5-ai-server.md)이 소유합니다. 이 절은 평가 결과의 로깅 계약과, 자가개선 루프가 사용할 수 있는 데이터의 수집 기준을 고정합니다.

**평가 로그 이벤트** — 평가 에이전트가 벤치 실행 결과를 JSON 로그로 남깁니다. Amplitude 이벤트가 아닙니다(사용자 행동이 아니라 내부 품질 실측이므로 CloudWatch 로그 축).

| 이벤트                         | 발생 시점                 | 핵심 필드                                                                                                                                          |
| ------------------------------ | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ai_evaluation_completed`      | 벤치 케이스 1건 채점 완료 | `benchmark_id`(벤치 세트 식별자), `case_id`, `feature`, `metric`(지표 키), `score`(1~5 정수), `prompt_versions`, `model`, `judge_model`(채점 모델) |
| `ai_evaluation_run_summarized` | 벤치 세트 1회 실행 완료   | `benchmark_id`, `run_id`, `feature`, 지표별 평균 점수, `case_count`, `prompt_versions`, `model`                                                    |

- 점수는 항상 `prompt_versions`·`model`과 함께 남깁니다 — 버전별 품질 추적과 회귀 게이트 판정의 근거입니다.
- 벤치 입력·산출 원문은 로그에 싣지 않습니다. 원문은 manyak-ai 레포의 벤치 자산(합성 시나리오)으로만 관리합니다.

**자가개선 루프가 쓸 수 있는 데이터** — 원문 수집 원칙(§6-7)을 유지한 채 다음만 사용합니다.

| 데이터                       | 출처                                                                                                       | 용도                                        |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| 벤치 지표 점수               | `ai_evaluation_*` 로그                                                                                     | 프롬프트 버전 간 품질 비교, 회귀 게이트     |
| `output_char_count`          | `ai_call_completed` 로그에 필드 추가(채팅 본문 문자 수 — 원문이 아니라 길이, `message_length_bucket` 선례) | 분량 고정(약 600자) 준수 분포 실측          |
| 폴백·빈 블록 발동 로그       | AI 형식 보정 로그([`5-ai-server.md §5-5`](./5-ai-server.md))                                               | 프롬프트 점검 신호                          |
| `retry_count` · `error_code` | `ai_call_logs`                                                                                             | 형식 위반·실패 추세                         |
| 스토리라인 GOOD/BAD 평가     | `story_creation_storyline_ratings`([`4-backend.md §4-3-2`](./4-backend.md))                                | 운영 품질의 사용자 신호(원문 없이 평가값만) |

**수집하지 않는 것** — 운영 채팅·생성 원문, 프롬프트 전문, 사용자 입력 원문은 위 표의 수집 경로(로그·이벤트)에 싣지 않습니다. 운영 원문이 필요한 작업은 §6-7의 Langfuse 예외 경로로만 수행합니다 — 개인정보처리방침 v1.2(2026-07-28 시행)로 트레이스 원문의 AI 모델 학습·개선 활용이 고지되었으며, **실서비스에 반영되는 모델의 학습 데이터는 방침 시행 이후 수집분만** 사용하고 시행 전 수집분(2026-07-23~27)은 내부 실험에 한정합니다. 벤치 평가 자산은 여전히 합성 데이터로 관리합니다.

### 6-6-12. AI LLM 트레이싱과 선호 신호 (Langfuse) — 트레이싱 `Phase 1 · 구현` · 선호 신호 `Phase 1 · 계획`

- **무엇.** AI 프로덕션 호출의 원문은 Langfuse trace에 축적하고, 사용자의 평가·재생성·완주·선택지 행동은 해당 생성 결과의 Langfuse score로 붙입니다. 이번 범위는 행동 신호 기록까지이며 대시보드·목표치·평가 계산식·알림은 만들지 않습니다.
- **왜.** Sentry와 `ai_call_logs`에는 오류·토큰·지연만 있고 원문이 없으며, Amplitude에는 행동만 있고 어떤 AI 결과에 대한 반응인지 확정할 생성 버전 연결이 없습니다. 행동 라벨은 나중에 소급 복원하기 어렵지만, 지표와 계산식은 라벨이 쌓인 뒤 다시 설계할 수 있습니다. 따라서 지표를 정하기 전에 생성 결과와 반응의 정확한 연결부터 저장합니다.
- **어떻게.** AI는 요청마다 별도 trace를 유지하고 구조화된 요청 입력과 제품 연결 metadata를 기록합니다([`5-ai-server.md §5-6`](./5-ai-server.md)). 백엔드는 `request_id`와 버전별 생성 연결로 정확한 trace를 지목해 아래 score를 발행합니다([`4-backend.md §4-7`](./4-backend.md)).

  | score 이름 | 타입·값 | 붙이는 생성 결과 | 필수 metadata |
  | --- | --- | --- | --- |
  | `storyline_rating` | `CATEGORICAL`: `GOOD`·`BAD` | 후보 3개를 만든 스토리라인 trace | `creation_id`, `storyline_id`, `storyline_order` |
  | `storylines_regenerated` | `BOOLEAN`: `true` | 새 생성이 아니라 버린 이전 스토리라인 trace | `creation_id`, `regenerated_by_creation_id` |
  | `chat_response_regenerated` | `BOOLEAN`: `true` | 새 답변이 아니라 버린 이전 채팅 응답 trace | `story_id`, `chat_id`, `turn_id`, `turn_number` |
  | `ending_reached` | `BOOLEAN`: `true` | 엔딩 본문을 만든 마지막 채팅 응답 trace | `story_id`, `chat_id`, `turn_id`, `turn_number`, `ending_id` |
  | `choice_presented` | `BOOLEAN`: `true` | 시작 추천 입력은 컴파일 trace, 턴 선택지는 선택지 생성 trace | `choice_source`, `story_id`, `chat_id`, `choice_id`, `choice_order` |
  | `choice_selected` | `CATEGORICAL`: `FILL`·`SEND`·`RANDOM` | 위와 같음 | `choice_source`, `story_id`, `chat_id`, `choice_id`, `choice_order`, `selection_attempt_id` |
  | `choice_applied` | `BOOLEAN`: `true` | 위와 같음 | `choice_source`, `story_id`, `chat_id`, `choice_id`, `choice_order`, `next_turn_id`, `choice_edited`, `selection_attempt_id` |
  | `choice_submission_failed` | `BOOLEAN`: `true` | 위와 같음 | `choice_source`, `story_id`, `chat_id`, `choice_id`, `choice_order`, `choice_edited`, `selection_attempt_id` |
  | `choice_set_skipped` | `BOOLEAN`: `true` | 노출됐지만 쓰지 않은 시작 추천 입력 또는 턴 선택지 묶음의 생성 trace | `choice_source`, `story_id`, `chat_id`, `input_attempt_id` |

  `choice_source`는 `START_SUGGESTION|TURN_CHOICE`입니다. `TURN_CHOICE`에는 `source_turn_id`, `START_SUGGESTION`에는 `start_setting_id`를 추가합니다. `RANDOM`은 사용자가 특정 문장을 직접 고른 행동이 아니므로 `FILL`·`SEND`와 분리합니다. score metadata에는 사용자 입력·선택지 문장·프롬프트·AI 출력 원문을 추가하지 않습니다.

  `storyline_rating`은 후보별 고정 `score_id`를 사용합니다. GOOD↔BAD 변경은 같은 score를 덮어쓰고 취소는 삭제하며, 최초 평가 시각을 유지합니다. 재생성 score는 새 결과가 저장된 뒤 버린 이전 결과에만 붙이고 실패하거나 롤백된 재생성에는 붙이지 않습니다. `choice_selected`는 클릭 사실이므로 다음 턴 실패와 무관하게 유지하고, `choice_applied`는 다음 턴 저장 성공 뒤에만 만듭니다. 백엔드가 실패를 확정한 경우에만 `choice_submission_failed`를 만들며, 클라이언트 단절로 결과를 모르면 성공·실패를 추정하지 않습니다. `choice_set_skipped`는 실제 노출 기록 뒤 직접 입력이 왔을 때만 만듭니다.

  score는 행동 저장 트랜잭션과 같은 트랜잭션의 outbox에 넣고 커밋 뒤 별도 작업자가 보냅니다. 신호 종류·대상 제품 ID·`selection_attempt_id`·`next_turn_id`·`input_attempt_id` 등 신호별 고유 재료로 결정적 `score_id`를 만들어 재시도 중복을 막습니다. 전송 실패는 제한 재시도하며 재시도 소진과 대기 건수는 원문 없는 운영 로그로 관측합니다. PR1 검수에서는 요청별 trace 분리, 호출별 metadata 구분, 임의 ID 미생성, 같은 문장의 다른 `choice_id` 구분, 행동 시점 분리, 버려진 이전 결과의 재생성 score, 중복 재전송 멱등성, 장애 격리, score·metadata의 원문 미포함을 자동 검증하고, 운영 trace와 score가 제품 ID로 연결되는지는 실제 Langfuse에서 확인합니다.

  아직 정하지 않은 구현 세부사항은 담당 레포가 결정합니다. manyak-ai는 KNK-752에서 합의한 `request_id`를 Langfuse trace metadata에 기록하며 추가 연결 정책을 결정하지 않습니다. manyak-server는 `request_id`로 정확한 trace ID를 조회·보관하는 방식, API 세부 계약, 공개 ID와 저장 스키마, score 갱신·삭제 호출, outbox와 재시도, 백엔드 Langfuse 설정을 결정합니다. manyak-web은 `selectionAttemptId`의 생성·수명과 노출·선택 상태 보존 방식을 결정합니다. `inputAttemptId`의 생성 주체·형식·수명은 manyak-server와 manyak-web이 함께 확정합니다. manyak-terraform과 manyak-infra는 백엔드 키 주입·재기동·롤백 배선을 결정합니다. 이미 정한 score 의미와 행동 시점은 이 구현 결정으로 바꾸지 않습니다.
- **왜 이 방법.** 서로 다른 API 요청을 하나의 trace로 합치면 실패·재시도 경계가 사라지므로 trace는 요청 단위로 유지하고 검증된 제품 ID로 조인합니다. 반응이 며칠 뒤 발생할 수 있어 AI 서버를 다시 거치지 않고 도메인 상태를 가진 백엔드가 직접 score를 발행합니다. 노출·선택·반영·실패를 나누면 사용자가 볼 수 있었는지, 눌렀는지, 실제 채팅에 반영됐는지를 섞지 않습니다. outbox는 사용자 기능과 Langfuse 장애를 분리하면서 커밋된 행동의 유실을 막습니다. 원문은 기존 Langfuse 예외 저장소에만 두고 score에는 비원문 식별자만 추가해 §6-7의 수집 경계를 유지합니다.

**트레이스 분석 차원.** 현재 AI가 기록하는 분석 차원은 장르 라벨·프롬프트 버전 맵·`retry_count`·`request_id`이며, KNK-762에서 생성·스토리·채팅·턴 연결 식별자와 선택적인 `user_source`를 추가합니다([`5-ai-server.md §5-6`](./5-ai-server.md)). 장르 라벨은 사전 정의 장르와 직접 입력 장르(`customTags` category `GENRE`)를 구분하지 않고 모두 `genre:*`로 저장하는 KNK-669 임시 정책을 유지합니다. 적용 범위는 스토리 제작의 장르뿐이며, 주인공·주변 인물의 직접 입력값은 라벨이나 metadata에 올리지 않습니다. KNK-621이 장르 직접 입력을 차단하면 이 예외는 종료됩니다. 장르 라벨은 채팅 trace에는 달지 않습니다(KNK-652).

### 6-6-13. Sentry 오류 일일 요약 (슬랙) — `Phase 1 · 구현`

**배경.** Sentry는 오류를 모아 두지만 사람이 대시보드를 열어야 압니다. 슬랙 제보([`slack-report.md`](../templates/slack-report.md))도 사람이 요청해야 움직입니다. 오류를 알아채는 일이 사람의 습관에 달려 있어, 아무도 열어 보지 않은 날은 장애가 있었는지조차 모릅니다.

**문제와 결정.**

- **알림을 자동으로 받되, 건마다 보내지는 않습니다.** 7일 기준 미해결 오류가 20건 수준이고 그중 절반 이상이 웹의 같은 네트워크 끊김입니다. 발생할 때마다 보내면 소음이 되어 아무도 읽지 않습니다. 그래서 **하루 한 번, 한 통으로 묶어** 보냅니다. 매일 오전 10시(KST) claude.ai 클라우드 루틴이 지난 24시간 오류를 세 서비스(`python-fastapi`·`java-spring-boot`·`typescript-nextjs`) 통틀어 요약해 슬랙 전용 채널 `#센트리-데일리-리포트`에 올립니다(KNK-711).
- **오류가 없는 날에도 보냅니다.** 안 보내면 조용한 날과 파이프라인이 끊긴 날이 구분되지 않습니다. 매일 무언가 오게 두면 끊겼을 때 사람이 알아채므로, 파이프라인이 살아 있는지 감시하는 장치를 따로 만들지 않습니다.
- **조회가 실패한 것과 오류가 없는 것을 구분합니다.** 이 파이프라인의 가장 나쁜 실패는 장애가 난 날을 조용한 날로 보고하는 것입니다. 판정 근거는 조회 호출의 성패입니다. 호출이 실패하면(HTTP 400·타임아웃) 요약 대신 조회가 실패했다는 사실을 보내고, 호출이 성공했는데 결과가 비면 "오류 없음"으로 봅니다.
- **심각도가 아니라 서비스별로 나눕니다.** AI·서버는 사용자 컨텍스트를 붙이지 않아 영향 인원이 항상 0으로 나옵니다(§6-6-8·§6-6-10 대비). 사용자 수로 정렬하거나 임계값을 걸면 백엔드 오류가 매일 바닥에 깔려 보이지 않습니다.
- **급한지 아닌지는 판정하지 않습니다.** 정말 급한 것은 오류 때문에 사용자가 떠나는 상황인데, Sentry는 몇 번 났고 몇 명이 겪었는지까지만 압니다. 그 사람들이 떠났는지는 Amplitude에 있고 이 요약은 거기까지 보지 않습니다. 기준 없이 심각도를 매기면 같은 데이터에도 매일 다른 값이 나오므로, 판단 재료(오류가 난 화면과 건수)만 싣고 판정은 읽는 사람이 합니다.

**구현.** 조회식·분류 기준·메시지 형식·결정 이력의 정본은 manyak-ai 레포의 `.agents/skills/daily-sentry-report/`입니다. 이 절은 관측 계약으로 고정할 것만 적습니다.

| 고정하는 것 | 값 |
| --- | --- |
| 대상 | 세 Sentry 프로젝트 전부 |
| 창 | 지난 24시간 |
| 환경 | `prod`와 `production` 둘 다. 서비스마다 이름이 달라 하나만 걸면 백엔드가 통째로 빠집니다 |
| 신규 판정 | 절대 시각 조회식으로 따로 조회합니다. 응답의 `First seen` 표시값은 조회 창에 따라 달라져 쓰지 않습니다 |
| 발생 횟수·영향 인원·마지막 시각 | 집계 조회로 받습니다. 영향 인원은 조회 창 기준 값(`count_unique(user)`)만 씁니다. 이슈 목록이 주는 사용자 수는 누적이라 매일 부풀려집니다 |
| 0건인 날 | 침묵하지 않고 "오류 없음"을 보냅니다 |

**제품 지표로 쓰지 않습니다.** Sentry 이벤트 수를 지표 계산에 사용하지 않는 원칙(§6-6-1)은 그대로입니다.

**원문 비수집 유지(§6-7).** Sentry 이슈 상세 응답에는 프롬프트 원문·지역변수·`device_id_hash`가 들어 있습니다. **요약은 이슈 상세를 열지 않습니다.** 필요한 값은 위 집계 조회로 모두 나옵니다. 상세를 열고 "슬랙에 옮기지 않는다"고만 정하면, 옮기지 않아도 그 내용이 요약을 만드는 에이전트의 실행 기록에 남습니다. 슬랙 메시지에도 사용자 입력 원문·채팅 원문·식별자를 싣지 않습니다.

## 6-7. 개인정보와 원문 수집 원칙

MVP 분석 이벤트, CloudWatch 로그, Sentry context, `ai_call_logs`에는 사용자가 입력한 원문을 직접 넣지 않습니다.

| 데이터                | 분석 이벤트   | 운영 로그와 Sentry | 대체 값                             |
| --------------------- | ------------- | ------------------ | ----------------------------------- |
| 채팅 메시지 원문      | 수집하지 않음 | 저장 금지          | `turn_number`, token count          |
| 피드백 본문           | 수집하지 않음 | 로그 저장 금지     | 저장 또는 전달 성공 여부, 본문 길이 |
| 이메일                | 수집하지 않음 | 로그 저장 금지     | `has_email`                         |
| 키워드·추가 정보 원문 | 수집하지 않음 | 저장 금지          | 관리되는 ID 또는 선택값             |
| 프롬프트 전문         | 수집하지 않음 | 저장 금지          | `prompt_template_version`           |
| AI 생성 결과 원문     | 수집하지 않음 | 저장 금지          | 응답 성공 여부, token count         |

원문 디버깅이 필요하면 별도 보안 정책과 제한된 저장소를 먼저 정의한 뒤 사용합니다. 이 문서의 MVP 분석 범위에는 원문 저장소를 포함하지 않습니다.

**AI LLM 트레이싱(Langfuse) 예외 — `Phase 1 · 구현`.** 위 표의 "저장 금지"는 운영 로그·Sentry·`ai_call_logs`·분석 이벤트에 대한 규칙입니다. AI 서버의 LLM 트레이싱(Langfuse)은 이 원칙의 **명시적 예외**로, 정상·실패 LLM 호출의 프롬프트·응답 원문을 별도 관측 저장소(Langfuse Cloud)에 남깁니다. 위 문단이 요구하는 "별도 보안 정책과 제한된 저장소"에 해당하며, 확정된 조건은 다음과 같습니다:

- **저장 리전**: 일본(JP) — HOST `https://jp.cloud.langfuse.com`. 운영에서 반드시 이 값을 주입합니다. 활성화 가드가 실린 릴리스에서는 HOST가 JP가 아니면(누락 포함) 켜지지 않아 원문이 다른 리전으로 갈 경로가 막히지만, 가드 이전 릴리스에서는 코드 기본값(JP 아님)으로 전송될 수 있습니다([`5-ai-server.md §5-6`](./5-ai-server.md)).
- **접근·삭제·권한 책임**: AI 담당자로 한정.
- **보존 기간**: 수집일로부터 1년(개인정보처리방침 v1.2와 동일 값 — Langfuse 프로젝트 retention 설정에 반영하고, 설정이 불가한 플랜이면 주기 삭제 운영으로 보장).
- **범위**: 프로덕션 전용(실험·로컬 제외).
- **학습 활용**: 저장된 원문은 AI 모델의 학습·개선에 활용할 수 있습니다(개인정보처리방침 v1.2·이용약관 v1.1, 2026-07-28 시행으로 고지). 실서비스에 반영되는 모델의 학습 데이터는 **방침 시행 이후 수집분만** 사용하며, 시행 전 수집분(2026-07-23~27)은 내부 실험에 한정합니다. 이용자가 학습 제외·삭제를 요청하면 해당 트레이스를 학습 셋에서 제외·삭제합니다(방침 13조).
- **조건의 코드 강제**: 위 "prod 전용·JP 리전" 조건은 문서 규칙에 그치지 않고 코드가 막습니다 — 키가 있어도 HOST가 JP가 아니거나 환경이 `prod`가 아니면 켜지지 않습니다(활성화 가드, [`5-ai-server.md §5-6`](./5-ai-server.md)). 가드는 KNK-652로 구현돼 AI `v0.2.1`(2026-07-22)에 실렸습니다. 키 주입은 가드가 실린 릴리스가 배포된 뒤에 합니다([`7-deployment.md §7-9`](./7-deployment.md)).

사용자 식별은 원본이 아니라 기기 해시(`device_id_hash`)로만 싣습니다. 사용자 자유입력(`user_input`·`additional_info`·커스텀 태그)은 LLM 프롬프트의 일부라 Langfuse 요청 원문에 저장됩니다. 원칙적으로 tags·metadata 같은 색인 차원에는 올리지 않습니다. 다만 **직접 입력 장르는 사용자 수요 관측을 위해 `genre:*` 필터용 라벨로 임시 저장합니다**(KNK-669). 이 예외는 장르에만 적용하고, KNK-621이 장르 직접 입력을 차단하면 종료합니다. 평가 벤치는 이 예외와 무관하게 합성 데이터를 사용하며, 트레이스 원문의 학습·개선 활용 조건은 위 예외 조건의 "학습 활용" 항목을 따릅니다(§6-6-11). 구현은 [`5-ai-server.md §5-6`](./5-ai-server.md), 선호 신호 결합은 §6-6-12입니다.

## 6-8. 검수 체크리스트

### 6-8-1. 검수 원칙

검수는 "이벤트가 발생한다"에서 끝나지 않습니다. 이벤트명, 프로퍼티 타입, 식별자 연결, 지표 계산 가능성, 원문 미수집까지 함께 확인합니다.

| 원칙             | 확인 방법                                                                                                            |
| ---------------- | -------------------------------------------------------------------------------------------------------------------- |
| P0 이벤트 우선   | 출시 전에는 `6-4-1. MVP 우선순위`의 P0 이벤트를 모두 확인합니다.                                                     |
| 원본 섹션 기준   | 이벤트는 `6-4. 이벤트 카탈로그`, 지표는 `6-5. 퍼널과 지표`, 관측 구현은 `6-6. 관측 구현`을 기준으로 확인합니다.      |
| 식별자 연결 확인 | `device_id`, `session_id`, `chat_id`, `request_id`, `ai_call_log_id`가 각 계층에서 이어지는지 봅니다. `analytics_creation_id`(분석 이벤트의 `creation_id`) 경로는 §6-8-7 A1~A3 해소 전까지 구간별로만 확인합니다(§6-8-3). `trace_creation_id`(AI 트레이스·헤더의 `creation_id`)는 다른 값이므로 두 값을 직접 조인하지 않습니다(§6-2·§6-6-3). |
| 원문 수집 금지   | 채팅·피드백·이메일·키워드·프롬프트·AI 생성 결과 원문이 **Amplitude·CloudWatch·Sentry·`ai_call_logs`** payload에 없는지 확인합니다(Langfuse는 §6-7 예외 — 아래 별도 항목).                             |
| Langfuse 원문 예외 | Langfuse가 §6-7 확정 조건(JP 리전·AI 담당자 한정 접근·prod 전용)대로 동작하는지 확인합니다. 직접 입력 장르는 KNK-669 임시 예외에 따라 `genre:*` 라벨로 저장하고, 그 밖의 사용자 자유입력은 tags·metadata에 색인하지 않습니다(`Phase 1 · 구현`). |

### 6-8-2. 문서 변경 체크리스트

분석 스펙을 변경할 때는 다음 항목을 확인합니다.

- 새 이벤트를 추가하면 `6-4. 이벤트 카탈로그`에 이벤트명, 발생 시점, 고유 프로퍼티, 우선순위를 추가합니다.
- 새 이벤트가 지표에 쓰이면 `6-5. 퍼널과 지표`에 계산식과 집계 단위를 추가합니다.
- 새 이벤트가 Sentry breadcrumb 또는 CloudWatch 로그와 연결되면 `6-6. 관측 구현`에 연결 기준을 추가합니다.
- P0 이벤트가 바뀌면 이 문서의 출시 전 P0 체크리스트를 업데이트합니다.
- 원문 수집 가능성이 있는 프로퍼티를 추가하면 `6-7. 개인정보와 원문 수집 원칙`과 `6-8-5. 개인정보 검수 기준`을 함께 확인합니다.
- 같은 표를 여러 섹션에 복사하지 않고 원본 섹션을 참조합니다.

### 6-8-3. 출시 전 P0 체크리스트

| 영역                  | 체크 항목                                                                                                                                                                          |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 이벤트 수집           | `client_storyList_viewed`, `client_storyList_createButton_clicked`가 Amplitude에서 수집됩니다.                                                                                     |
| 이벤트 수집           | `client_storyCreate_viewed`, `client_storyCreate_step_viewed`, `client_storyCreate_storyGeneration_requested`가 수집됩니다.                                                        |
| 이벤트 수집           | `server_storyCreate_storyGeneration_processed_succeeded`, `server_storyCreate_storyGeneration_processed_failed`가 수집됩니다.                                                      |
| 이벤트 수집           | `client_storyCreate_storylineOption_selected`, `client_storyCreate_selectedTagsButton_clicked`, `client_storyCreate_completed`가 수집됩니다.                                       |
| 이벤트 수집           | `client_storyDetail_viewed`, `client_storyDetail_chatStartButton_clicked`가 수집됩니다.                                                                                            |
| 이벤트 수집           | `client_chat_viewed`, `client_chat_messageInput_submitted`가 수집됩니다.                                                                                                           |
| 이벤트 수집           | `server_chat_aiMessage_processed_succeeded`, `server_chat_aiMessage_processed_failed`가 수집됩니다.                                                                                |
| 이벤트 수집           | `client_feedback_viewed`, `client_feedback_form_submitted`가 수집됩니다.                                                                                                           |
| 식별자                | `device_id`와 `session_id`가 SDK 자동 수집으로 채워지고 커스텀 프로퍼티로 재정의되지 않습니다.                                                                                     |
| 식별자                | 스토리 제작 퍼널 1~2단계(제작 진입 → 생성 요청)를 `device_id`·`session_id` 순차 기준으로 계산할 수 있습니다.                                                                       |
| 식별자 `계획`         | **실패 조인** — `server_*` 실패 이벤트를 `analytics_creation_id`로 개별 시도에 연결합니다. **§6-8-7 A1·A3 해소 전까지 통과 항목으로 요구하지 않습니다**(발급 전 실패는 값 없음·타입 불일치). |
| 식별자 `계획`         | **생성 성공 → 스토리라인 선택** — `analytics_creation_id`로 조인합니다. **A3 해소 전까지 통과 항목으로 요구하지 않습니다**(서버 Long ↔ 클라이언트 문자열).                        |
| 식별자 `계획`         | **생성 성공 → 제작 완료** — `analytics_creation_id`로 조인합니다. **A2·A3 해소 전까지 통과 항목으로 요구하지 않습니다**(완료 이벤트에 값 없음·타입 불일치).                       |
| 식별자                | 채팅 첫 메시지와 AI 응답을 `chat_id`, `turn_number`로 연결할 수 있습니다.                                                                                                          |
| 로그 연결             | 서버 로그, Sentry, `ai_call_logs`를 `request_id`로 연결할 수 있습니다.                                                                                                             |
| 개인정보              | 채팅 메시지, 피드백 본문, 이메일, 키워드 원문, 프롬프트 전문이 payload에 없습니다.                                                                                                 |
| 이벤트 수집 `Phase 1` | `server_login_googleLogin_processed_succeeded`·`_failed`, `server_login_kakaoLogin_processed_succeeded`·`_failed`, `server_login_migration_processed_succeeded`·`_failed`가 수집되고, `client_login_oauthError_shown`이 `error_code`와 함께 수집됩니다(§6-4-3 — 콜백 단계 실패는 서버 이벤트가 못 잡음). |
| 식별자 `Phase 1`      | 로그인 시 `setUserId`로 `user_id`가 설정되고, 로그아웃 시 `reset()`으로 `device_id`가 재발급됩니다.                                                                                |
| 이벤트 수집 `Phase 1` | `client_guestLimitDialog_shown`·`client_creditShortageDialog_shown`이 `trigger`와 함께 수집됩니다.                                                                                 |
| 이벤트 수집 `Phase 1` | `client_storyCreate_methodOption_selected`, `client_generalCreate_viewed`, `client_generalCreate_completed`, `client_storyEdit_viewed`, `client_storyEdit_completed`가 수집됩니다. |
| 이벤트 수집 `Phase 1` | `client_chat_regenerateButton_clicked`, `client_chat_chatImage_impressed`가 수집되고, `server_chat_aiMessage_processed_*`에 `is_regenerated`가 실립니다.                           |

### 6-8-4. 계층별 검수 기준

#### 6-8-4-1. 프론트엔드

- Amplitude 디버그 모드에서 P0 `client_*` 이벤트가 한 번씩 발생합니다.
- 이벤트명이 `{platform}_{screenName}(_{objectName})?_{actionType}(_{eventType})?` 형식을 따릅니다.
- 프로퍼티는 `snake_case`로 전송합니다.
- 같은 사용자 행동에서 Amplitude event, Sentry breadcrumb, 상관 키(`chat_id`)가 연결됩니다. **`analytics_creation_id` 경로는 §6-8-7 A1~A3 해소 전까지 통과 항목이 아닙니다**(§6-8-3 구간별 기준과 동일).
- API 요청 헤더에 `X-Manyak-Device-Id`, `X-Manyak-Session-Id`가 포함됩니다.
- `X-Manyak-Request-Id`가 없을 때 백엔드가 `request_id`를 생성합니다.

#### 6-8-4-2. 백엔드

- 모든 API 로그에 `request_id`, `session_id`, `device_id_hash`가 있습니다.
- 생성, AI 응답, 피드백 결과가 `server_*` 분석 이벤트로 발행됩니다.
- `server_*` 이벤트가 `chat_id`로 client 이벤트와 연결됩니다. **`analytics_creation_id` 경로는 §6-8-7 A1~A3 해소 전까지 통과 항목으로 요구하지 않습니다**(실패 이벤트 누락 가능·완료 이벤트에 값 없음·타입 불일치 — §6-8-3 구간별 기준과 동일).
- 5xx 오류가 Sentry에 생성되고 CloudWatch 로그의 `request_id`로 연결됩니다.
- 서버 분석 이벤트의 `error_type`이 `6-6-7. 서버 분석 이벤트와 실패 타입` 기준을 따릅니다.
- 스토리 생성 실패율, API 실패율, 피드백 제출 성공률을 계산할 수 있습니다.

#### 6-8-4-3. AI 서비스

- 성공 호출과 실패 호출이 모두 `ai_call_logs`에 기록됩니다.
- CloudWatch 로그에서 `request_id`로 백엔드 로그와 AI 로그를 연결할 수 있습니다.
- AI 호출 결과가 `server_storyCreate_storyGeneration_processed_*` 또는 `server_chat_aiMessage_processed_*` 이벤트로 연결됩니다.
- `error_code`가 `6-6-9. ai_call_logs 기록 기준` 기준으로 `error_type`에 매핑됩니다.
- Sentry 이벤트에 `feature`, `model`, `prompt_template_version`, `error_code`가 있습니다.
- `storyline_generation`, `story_completion`, `chat_response`의 성공률과 p95 latency를 계산할 수 있습니다.

### 6-8-5. 개인정보 검수 기준

| 데이터                | 확인 기준                                                          |
| --------------------- | ------------------------------------------------------------------ |
| 채팅 메시지 원문      | Amplitude, CloudWatch, Sentry, `ai_call_logs` payload에 없습니다.  |
| 피드백 본문           | 분석 이벤트와 로그 payload에 없습니다.                             |
| 이메일                | 분석 이벤트와 로그 payload에 없습니다. `has_email`만 허용합니다.   |
| 키워드·추가 정보 원문 | 관리되는 ID 또는 선택값만 허용합니다.                              |
| 프롬프트 전문         | CloudWatch, Sentry, `ai_call_logs`에 없습니다.                     |
| AI 생성 결과 원문     | CloudWatch, Sentry, `ai_call_logs`에 없습니다.                     |
| 익명 ID               | 서버 계층에는 원본 `device_id`가 없고 `device_id_hash`만 있습니다. |

### 6-8-6. 검증 쿼리 예시

아래 쿼리는 운영 검수용 예시입니다. 실제 로그 그룹, 테이블명, 시간 범위는 배포 환경에 맞춥니다.

CloudWatch에서 최근 API 실패를 확인합니다.

```text
fields @timestamp, event_name, request_id, endpoint, status_code, error_code, duration_ms
| filter event_name = "api_request_failed"
| sort @timestamp desc
| limit 50
```

CloudWatch에서 한 요청의 백엔드 흐름을 확인합니다.

```text
fields @timestamp, event_name, request_id, creation_id, story_id, chat_id, duration_ms
| filter request_id = "req_..."
| sort @timestamp asc
| limit 100
```

AI 호출 실패 분포를 확인합니다.

```sql
select
  feature,
  error_code,
  count(*) as failed_count
from ai_call_logs
where status = 'failed'
  and created_at >= current_date - interval '7 days'
group by feature, error_code
order by failed_count desc;
```

AI latency p95를 확인합니다.

```sql
select
  feature,
  percentile_cont(0.95) within group (order by latency_ms) as p95_latency_ms
from ai_call_logs
where status = 'succeeded'
  and created_at >= current_date - interval '7 days'
group by feature;
```

### 6-8-7. `creation_id` 계약과 현재 구현의 간극 — `확인 필요`

Android도 같은 이벤트 카탈로그를 구현해야 하므로(§6-2), 아래 간극을 먼저 정리해야 웹·Android가 같은 계약을 구현할 수 있습니다. **현재 구현과 목표 계약이 다른 구간이며, 팀 결정 전까지 어느 쪽도 정본으로 확정하지 않습니다.** 인접 서비스 레포의 코드는 이 문서에서 바꾸지 않습니다.

| #   | 항목                                                          | 목표 계약(이 문서)                                                            | 현재 구현                                                                                                        | 영향                                                                                                                     | 처리 방향                                                                                                     |
| --- | ------------------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| A1  | `server_storyCreate_storyGeneration_processed_failed`의 `creation_id` | `creation_id` (string, 필수) — §6-4-2-3                                        | 서버는 `creation_id` 없이도 발행할 수 있습니다(발급 전 실패 경로에서 프로퍼티 생략)                              | `creation_id` 기준 실패 조인이 일부 누락됩니다. `device_id`·`session_id` 기준 집계는 영향 없음                            | 필수를 유지하고 발급 전 실패를 별도 이벤트·로그로 분리할지, `creation_id`를 선택으로 완화할지 **결정 필요**    |
| A2  | `client_storyCreate_completed`의 `creation_id`                | §6-5-3-1 퍼널 5단계와 "생성 후 완료율"이 `creation_id`로 조인한다고 정의       | 이벤트 프로퍼티에 `creation_id`가 없습니다(§6-4-2-3 정의·웹 타입·웹 발행 모두 없음)                              | **"생성 후 완료율(`creation_id` 기준)"은 현재 계산할 수 없습니다** — 현 상태에서는 `device_id`·`session_id` 순차 근사치만 가능 | 이벤트에 `creation_id`를 추가할지, 지표 정의를 device 기준으로 바꿀지 **결정 필요**. 결정 전까지 이 지표는 `계획` |
| A3  | `creation_id` 타입                                            | `string`(§6-2 — 분석 이벤트는 문자열)                                          | 웹 클라이언트 이벤트는 문자열로 변환해 보내고, 서버 성공 이벤트(`..._succeeded`)는 `Long` 값을 그대로 전달합니다 | 같은 프로퍼티가 이벤트 출처에 따라 문자열·숫자로 섞여 조인·필터가 어긋날 수 있습니다                                      | 서버 전송 시 문자열 변환과 계약 변경 중 하나로 정렬 **결정 필요**. 임의 변경 금지                              |
| A4  | `creation_id` 이름의 의미 충돌                                | 개념 이름을 분리해 `analytics_creation_id`(분석)와 `trace_creation_id`(AI 트레이스)로 구분(§6-2·[`0-glossary.md`](./0-glossary.md)) | **와이어 키는 양쪽 다 `creation_id`입니다** — 분석 이벤트는 진행 세션 ID(`simpleCreationId`, Long 원본), AI 트레이스·`ai_call_logs`·`X-Manyak-Creation-Id`는 스토리라인 요청 UUID | 두 값을 같은 연결 키로 오인하면 조인 결과가 전부 비거나 잘못 붙습니다. Android가 어느 값을 실을지 혼동할 위험도 같습니다 | 문서 개념 분리는 전파 완료(용어집 §0-3-2 · §6-2 · §6-6-3 계층별 표 · `3-1-client.md` · `4-backend.md §4-3·§4-7` · `5-ai-server.md §5-6`). **와이어 키·헤더·DB 컬럼 이름 변경은 배포된 계약이라 팀 결정 필요**(임의 개명 금지) — 이름이 같은 한 오인 위험은 남으므로 항목을 닫지 않습니다 |

Android 구현 시에도 이 간극이 해소되기 전까지는 `creation_id` 관련 프로퍼티를 임의로 추가하지 않고 웹과 동일한 현재 계약을 따릅니다(이벤트 이름·기존 프로퍼티 재사용 원칙은 §6-3-2). **Android가 실을 값은 문맥으로 갈립니다** — `client_*`·`server_*` 분석 이벤트의 `creation_id`에는 `analytics_creation_id`를, AI 호출 상관 헤더(`X-Manyak-Creation-Id`)에는 `trace_creation_id`를 싣습니다(A4).

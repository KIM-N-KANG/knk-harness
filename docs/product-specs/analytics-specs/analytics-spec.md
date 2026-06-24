# AN-1-ANALYTICS-SPEC

이 문서는 **마냑 서비스에서 사용자가 스토리를 만들고 채팅을 이어가는 흐름**을 측정하기 위한 최상위 분석 스펙입니다. 프론트엔드 이벤트, 백엔드 서버 이벤트, AI 호출 로그를 같은 식별자와 네이밍 컨벤션으로 연결하는 기준 문서로 사용합니다.

이 문서는 긴 설명서가 아니라 분석 스펙의 지도 역할을 하며, 세부 구현 계약은 프론트엔드·백엔드·AI 서비스 문서로 나눕니다.

```text
§AN-1-1   분석 목적            MVP 핵심 흐름과 분석 질문
§AN-1-2   식별자 정책          device_id · creation_id · story_id · chat_id
§AN-1-3   이벤트 네이밍 컨벤션  platform · screenName · objectName · actionType · eventType
§AN-1-4   이벤트 공통 프로퍼티  핵심 프로퍼티 · SDK 자동 수집 · 추후 도입
§AN-1-5   핵심 퍼널 정의       제작 · 채팅 활성화 · 전체 활성화 퍼널
§AN-1-6   핵심 지표 정의       제작 · 채팅 · 피드백 지표 계산식
§AN-1-7   페이지별 이벤트 스펙  화면별 이벤트 카탈로그
§AN-1-8   개인정보와 원문 수집 원칙  원문 수집 금지와 대체 프로퍼티
§AN-1-9   MVP 우선 적용 이벤트  P0 · P1 적용 순서
```

---

| 항목 | 값 |
| --- | --- |
| 버전 | v0.5 |
| 작성일 | 2026-06-25 |
| 대상 | 마냑 서비스 |
| 작성 목적 | MVP 출시 후 사용자가 스토리를 만들고 채팅을 이어가는 흐름을 측정하기 위한 최소 이벤트 스펙을 정의한다. |

| 세부 문서 | 역할 |
| --- | --- |
| [`analytics-frontend-spec.md`](./analytics-frontend-spec.md) | Amplitude 이벤트와 브라우저 Sentry 수집 기준 |
| [`analytics-backend-spec.md`](./analytics-backend-spec.md) | CloudWatch API 로그, 서버 분석 이벤트, 서버 Sentry, `ai_call_logs` 연결 기준 |
| [`analytics-ai-spec.md`](./analytics-ai-spec.md) | AI 호출 로그, 실패 코드, 토큰·latency 운영 지표 |

## AN-1-1 분석 목적

마냑 MVP 분석의 목적은 사용자가 다음 흐름을 자연스럽게 완료하는지 확인하는 것이다.

1. 스토리 목록에서 스토리 제작을 시작한다.
2. 키워드 선택, 스토리라인 선택, 추가 정보 입력을 거쳐 스토리를 완성한다.
3. 완성한 스토리의 상세 화면에서 채팅을 시작한다.
4. 채팅에서 첫 메시지를 보내고 여러 턴 동안 이야기를 이어간다.
5. 불편하거나 아쉬운 점을 피드백으로 남긴다.

핵심 질문과 지표는 다음과 같다.

| 핵심 질문 | 확인 지표 |
| --- | --- |
| 사용자가 스토리 제작을 시작하는가? | 제작 시작률 |
| 제작 중 어디서 막히는가? | 제작 단계별 이탈율, 생성 실패율 |
| 스토리 생성이 채팅으로 이어지는가? | 스토리 상세 → 채팅 시작 전환율 |
| 채팅이 실제 몰입으로 이어지는가? | 첫 메시지 전송률, N턴 이상 도달률 |
| 개선 포인트를 수집하고 있는가? | 피드백 제출률 |

## AN-1-2 식별자 정책

현재 MVP는 로그인 기능이 없는 **전원 게스트(익명)** 서비스다. 따라서 `user_id`는 사용하지 않고, 익명 식별자를 기준으로 분석한다. 사용자 단위는 Amplitude SDK가 자동으로 채우는 `device_id`로 식별한다.

| 식별자 | 타입 | 의미 | 생성 방식 |
| --- | --- | --- | --- |
| `device_id` | string | 같은 브라우저 사용자를 묶는 익명 단위 | Amplitude Browser SDK 자동 수집 |
| `session_id` | number | 한 번의 방문 흐름 | Amplitude SDK 자동 수집 |
| `creation_id` | string | 한 번의 스토리 생성 시도 | 스토리라인 생성 시 발급되는 `simpleCreationId` |
| `story_id` | number | 스토리 식별자 | 스토리 완성 후 서버에서 발급한다. |
| `chat_id` | string | 채팅 식별자 | 채팅 생성 후 서버에서 발급한다. |

분석 단위는 다음 join key로 잡는다.

| 키 | 의미 | 사용 |
| --- | --- | --- |
| `device_id` | 익명 사용자 단위 (SDK 자동) | 전체·장기 퍼널의 기본 단위 |
| `creation_id` | 한 번의 스토리 생성 시도 | 제작 퍼널의 생성 성공 ~ 완료 구간 고정값 |
| `chat_id` | 한 채팅 세션 | 채팅 퍼널, 제작 완료 후 첫 대화 연결 |

`requested`·`viewed`처럼 ID 발급 이전 단계는 고정값 없이 `device_id` 순차 기준으로 집계한다. 로그인 기능을 도입하면 `device_id`는 계속 유지하고, 로그인 시점부터 `user_id`를 추가한다. Amplitude의 `identify` 또는 `alias` 기능으로 기존 익명 행동과 로그인 사용자를 연결한다.

## AN-1-3 이벤트 네이밍 컨벤션

이벤트명은 platform, screenName, objectName, actionType, eventType을 언더스코어로 연결해 만든다. 각 항목 내부는 camelCase로 쓰고, 프로퍼티는 `snake_case`로 쓴다.

```text
{platform}_{screenName}(_{objectName})?_{actionType}(_{eventType})?
```

```text
client_storyList_viewed
client_storyList_storyCard_clicked
client_storyList_storyCard_impressed
client_storyCreate_nextButton_clicked
client_storyCreate_storyGeneration_requested
server_storyCreate_storyGeneration_processed_succeeded
server_storyCreate_storyGeneration_processed_failed
```

### AN-1-3-1 구성 항목

| 항목 | 필수 여부 | 설명 |
| --- | --- | --- |
| `platform` | 필수 | 이벤트가 발생한 주체. `client`(프론트엔드 행동) 또는 `server`(서버·AI·DB 처리 결과) |
| `screenName` | 필수 | 이벤트가 발생한 화면 또는 주요 flow. 예: `onboarding`, `storyList`, `storyCreate`, `storyDetail`, `chatList`, `chat`, `feedback` |
| `objectName` | 조건부 필수 | 사용자가 보거나 조작한 대상, 또는 서버가 처리한 대상. 화면 진입처럼 대상이 화면 자체이면 생략한다. |
| `actionType` | 필수 | 사용자 행동 또는 사용자에게 노출된 상태 |
| `eventType` | 선택 | 결과 상태. 성공·실패·차단·취소를 구분해야 할 때만 사용한다. |

`actionType`은 아래 값으로 제한해 사용한다.

| 그룹 | 값 | 설명 |
| --- | --- | --- |
| 사용자 행동 (client) | `viewed` | 화면 또는 단계에 진입했을 때 |
| 사용자 행동 (client) | `clicked` | 클릭 가능한 요소를 눌렀을 때 |
| 사용자 행동 (client) | `selected` | 선택지를 선택했을 때 |
| 사용자 행동 (client) | `focused` | 입력 영역에 포커스가 들어왔을 때 |
| 사용자 행동 (client) | `submitted` | 폼이나 입력값을 제출했을 때 |
| 사용자 행동 (client) | `requested` | 클라이언트가 서버에 생성·처리를 요청했을 때 |
| 사용자 행동 (client) | `completed` | 주요 flow를 끝까지 완료했을 때 |
| 상태 노출 (client) | `shown` | 모달, 토스트, 에러, 로딩, 빈 상태가 표시되었을 때 |
| 상태 노출 (client) | `impressed` | 특정 item 또는 section이 유효하게 노출되었을 때 |
| 서버 처리 (server) | `processed` | 서버가 생성·저장·처리를 수행했을 때. eventType으로 결과를 구분한다. |

`eventType`은 `succeeded`, `failed`, `blocked`, `canceled`만 사용한다. 단순 클릭·노출·포커스·화면 진입에는 결과 상태를 붙이지 않는다. `completed`는 결과 상태가 아니라 사용자가 flow를 끝마친 행동이므로 eventType이 아니라 actionType으로 쓴다.

### AN-1-3-2 이벤트명 작성 원칙

| 원칙 | 설명 | 예시 |
| --- | --- | --- |
| 이벤트명에 데이터 값을 넣지 않는다. | ID, 선택값, 에러 코드, 단계 번호, 리스트 위치는 프로퍼티로 보낸다. | `story_id`, `step_number`, `position` |
| 단계 번호는 screenName에 넣지 않는다. | 단계는 `step_number`, `step_name` 프로퍼티로 보낸다. | `client_storyCreate_step_viewed` |
| 버튼은 문구보다 역할·의도로 쓴다. | `nextButton`, `completeButton`, `chatStartButton`, `skipButton` 등 | `client_storyCreate_nextButton_clicked` |
| 서버 처리 대상은 기능 단위로 쓴다. | `storyGeneration`, `aiMessage`, `submission` 등 | `server_chat_aiMessage_processed_failed` |
| `canceled`는 실제 취소 행동에만 붙인다. | 단순 닫기·나가기 클릭에는 `clicked`만 쓴다. | `client_storyCreate_exitButton_clicked` |

### AN-1-3-3 impression 가이드

`impressed`는 특정 item 또는 section이 사용자 화면에 유효하게 노출된 상태를 의미한다. 유효 노출 여부는 다음 기준으로 판단한다.

| 항목 | 권장 기준 |
| --- | --- |
| 최소 노출 면적 | 컴포넌트 면적의 50% 이상 |
| 최소 노출 시간 | 1초 이상 |

중복 노출은 동일 item 기준으로 한 번만 수집한다. `동일 session_id + 동일 screenName + 동일 objectName + 동일 item_id` 기준으로 30초 이내 재노출은 중복으로 판단한다(cooling time 30초). section, item 세부 정보는 `section_id`, `section_name`, `item_id`, `position` 프로퍼티로 보낸다.

## AN-1-4 이벤트 공통 프로퍼티

각 이벤트 표에는 고유 프로퍼티만 나열하고, 공통 프로퍼티는 전 이벤트에 자동 부착한다. 프로퍼티 타입은 API 응답 모델과 일치시킨다. `story_id`는 number, `chat_id`는 string이고, boolean은 문자열이 아닌 boolean으로 보낸다.

### AN-1-4-1 MVP 핵심 프로퍼티

현재 서비스의 핵심 동선은 **스토리 제작 → 채팅**이다. 이 퍼널 추적에 필요한 최소 프로퍼티만 정의한다.

| property | 타입 | 적용 범위 | 설명 |
| --- | --- | --- | --- |
| `screen_name` | string | 모든 이벤트 | 이벤트가 발생한 화면. 필터·세그먼트 편의를 위해 프로퍼티로도 보낸다. |
| `step_name` | string | 스토리 제작 퍼널 | 제작 단계. `keyword`, `storylineSelect`, `additionalInfo`, `complete` |
| `step_number` | number | 스토리 제작 퍼널 | 제작 단계 번호 |
| `creation_id` | string | 스토리 제작 퍼널 | 스토리라인 생성 시 발급되는 `simpleCreationId` |
| `story_id` | number | story 관련 이벤트 | 스토리 식별자 |
| `chat_id` | string | chat 관련 이벤트 | 채팅 식별자 |

### AN-1-4-2 자동 수집 (재정의 금지)

다음 값은 Amplitude Browser SDK가 자동으로 채우므로 커스텀 프로퍼티로 다시 만들지 않는다. 익명 사용자 식별도 `device_id`로 처리한다.

```text
device_id, session_id
platform, os_name, os_version, device_family
app_version
country, region, city, language
event_time, event_id
```

### AN-1-4-3 추후 도입

다음 프로퍼티는 관련 기능 도입 시점에 함께 추가한다.

| property | 도입 시점 | 설명 |
| --- | --- | --- |
| `user_id` | 인증 도입 후 | 로그인 사용자 식별자 (`identify`로 설정) |
| `is_logged_in` | 인증 도입 후 | 로그인 여부 (게스트 구분) |
| `membership` | 구독·요금제 도입 후 | 요금제·등급 |
| `signup_at` | 인증 도입 후 | 가입 시점 |
| `experiment_key` / `variant` | A/B 테스트 도입 후 | 실험 키와 분기 값 |
| `request_id` | 서버 사이드 이벤트 계측 시 | client `requested` ↔ server `processed` 연결용 상관 ID. 현재는 `creation_id`로 대체한다. |
| `item_id` / `section_id` / `section_name` | impression 정밀 계측 시 | 추천 카드 등 노출 분석용 |

## AN-1-5 핵심 퍼널 정의

익명 서비스라 사용자 단위는 `device_id`(SDK 자동)를 쓰고, 한 번의 시도·세션은 `creation_id`·`chat_id`를 단계 간 고정값(hold constant)으로 쓴다.

### AN-1-5-1 스토리 제작 퍼널

키워드 입력부터 스토리 완성까지 어디서 이탈하는지와 생성 성공률을 측정한다.

| 순서 | 단계 | 이벤트 | 고정값 |
| --- | --- | --- | --- |
| 1 | 제작 진입 | `client_storyCreate_viewed` | device |
| 2 | 생성 요청 | `client_storyCreate_storyGeneration_requested` | device |
| 3 | 생성 성공 | `server_storyCreate_storyGeneration_processed_succeeded` | creation_id |
| 4 | 스토리라인 선택 | `client_storyCreate_storylineOption_selected` | creation_id |
| 5 | 제작 완료 | `client_storyCreate_completed` | creation_id |

- 핵심 지표: 전체 전환율(1 → 5), 생성 성공률(2 → 3), 생성 후 완료율(3 → 5), 최대 이탈 단계 식별
- 고정값 주의: 1~2단계는 `creation_id` 발급 전이라 device 순차 기준, 3단계부터 `creation_id` 고정으로 한 생성 건의 완주를 측정한다.
- UI 단계 렌즈: `client_storyCreate_step_viewed`의 `step_name`(keyword → storylineSelect → additionalInfo → complete)으로 화면 단계 이탈을 별도 퍼널로 관찰한다.

### AN-1-5-2 채팅 활성화 퍼널

채팅 진입 후 첫 메시지·첫 응답까지 도달하는지와 대화 깊이를 측정한다. 채팅은 메시지↔응답이 반복되므로 **활성화 퍼널 + 인게이지먼트 깊이**로 나눠서 본다.

활성화 퍼널(고정값 `chat_id`)

| 순서 | 단계 | 이벤트 |
| --- | --- | --- |
| 1 | 채팅 진입 | `client_chat_viewed` |
| 2 | 첫 메시지 | `client_chat_messageInput_submitted` |
| 3 | 첫 AI 응답 | `server_chat_aiMessage_processed_succeeded` |

- 핵심 지표: 말 거는 비율(1 → 2), AI 응답 성공률(2 → 3), 진입 경로(`client_storyDetail_chatStartButton_clicked` → 1)
- 인게이지먼트 깊이: `client_chat_messageInput_submitted`의 `turn_number` 분포로 N턴 이상 도달률을 보고, 선택지 사용률은 `client_chat_choiceOption_selected` / 턴 수로 본다.

### AN-1-5-3 전체 활성화 퍼널 (north-star)

방문자가 스토리를 만들고 실제 대화까지 갔는지 측정한다. 페이지를 가로지르는 퍼널이다.

| 순서 | 단계 | 이벤트 | 고정값 |
| --- | --- | --- | --- |
| 1 | 메인 방문 | `client_storyList_viewed` | device |
| 2 | 제작 시작 | `client_storyList_createButton_clicked` | device |
| 3 | 제작 완료 | `client_storyCreate_completed` | device |
| 4 | 첫 메시지 | `client_chat_messageInput_submitted` | chat_id |
| 5 | 첫 AI 응답 | `server_chat_aiMessage_processed_succeeded` | chat_id |

- 핵심 지표: 방문 → 활성화(첫 대화) 전환율(1 → 5), 구간별 이탈
- 3단계 `client_storyCreate_completed`에서 발급된 `chat_id`로 4~5를 연결한다.

## AN-1-6 핵심 지표 정의

지표는 페이지별 이벤트 카탈로그(AN-1-7)에 정의된 이벤트만으로 계산한다.

| 영역 | 지표 | 계산식 |
| --- | --- | --- |
| 온보딩 | 온보딩 완료율 | `client_onboarding_completed` 수 / `client_onboarding_viewed` 수 |
| 온보딩 | 온보딩 건너뛰기율 | `client_onboarding_skipButton_clicked` 수 / `client_onboarding_viewed` 수 |
| 스토리 목록 | 스토리 카드 클릭률 | `client_storyList_storyCard_clicked` 수 / `client_storyList_storyCard_impressed` 수 |
| 스토리 목록 | 제작 시작률 | `client_storyList_createButton_clicked` 수 / `client_storyList_viewed` 수 |
| 스토리 제작 | 생성 요청률 | `client_storyCreate_storyGeneration_requested` 수 / `client_storyCreate_viewed` 수 |
| 스토리 제작 | 생성 성공률 | `server_storyCreate_storyGeneration_processed_succeeded` 수 / `client_storyCreate_storyGeneration_requested` 수 |
| 스토리 제작 | 생성 실패율 | `server_storyCreate_storyGeneration_processed_failed` 수 / `client_storyCreate_storyGeneration_requested` 수 |
| 스토리 제작 | 생성 후 완료율 | `client_storyCreate_completed` 수 / `server_storyCreate_storyGeneration_processed_succeeded` 수 (creation_id 기준) |
| 스토리 제작 | 전체 제작 전환율 | `client_storyCreate_completed` 수 / `client_storyCreate_viewed` 수 |
| 스토리 제작 | 단계별 이탈율 | `1 - 다음 단계 step_viewed 사용자 수 / 현재 단계 step_viewed 사용자 수` (`client_storyCreate_step_viewed`의 `step_name` 기준) |
| 스토리 상세 | 상세 → 채팅 시작 전환율 | `client_storyDetail_chatStartButton_clicked` 수 / `client_storyDetail_viewed` 수 |
| 스토리 상세 | 추천 카드 클릭률 | `client_storyDetail_recommendStoryCard_clicked` 수 / `client_storyDetail_recommendStoryCard_impressed` 수 |
| 채팅 목록 | 채팅 카드 클릭률 | `client_chatList_chatCard_clicked` 수 / `client_chatList_chatCard_impressed` 수 |
| 채팅 | 말 거는 비율(첫 메시지 전송률) | `client_chat_messageInput_submitted` 사용자 수 where `turn_number=1` / `client_chat_viewed` 사용자 수 |
| 채팅 | AI 응답 성공률 | `server_chat_aiMessage_processed_succeeded` 수 / `client_chat_messageInput_submitted` 수 |
| 채팅 | AI 응답 실패율 | `server_chat_aiMessage_processed_failed` 수 / `client_chat_messageInput_submitted` 수 |
| 채팅 | N턴 이상 도달률 | `turn_number >= N` 채팅 수 / `client_chat_viewed` 채팅 수 (`turn_number` 분포) |
| 채팅 | 선택지 사용률 | `client_chat_choiceOption_selected` 수 / `client_chat_messageInput_submitted` 수 |
| 피드백 | 피드백 제출률 | `client_feedback_form_submitted` 사용자 수 / `client_feedback_viewed` 사용자 수 |
| 피드백 | 제출 성공률 | `server_feedback_submission_processed_succeeded` 수 / `client_feedback_form_submitted` 수 |
| 피드백 | 제출 실패율 | `server_feedback_submission_processed_failed` 수 / `client_feedback_form_submitted` 수 |
| 전체 | 방문 → 활성화 전환율 (north-star) | `server_chat_aiMessage_processed_succeeded` 도달 사용자 수 / `client_storyList_viewed` 사용자 수 |

생성·응답·제출 실패 사유는 server 이벤트의 `error_type`(`network` / `validation` / `server`)으로 분포를 본다.

## AN-1-7 페이지별 이벤트 스펙

각 이벤트 표에는 공통 프로퍼티(AN-1-4)를 제외한 고유 프로퍼티만 적는다. 필수는 ✅, 선택은 — 로 표기한다.

### AN-1-7-1 온보딩

목적은 신규 진입 사용자의 온보딩 투어 노출·완료·이탈률을 파악하는 것이다.

| 이벤트 | 발생 시점 | platform | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_onboarding_viewed` | 투어 첫 스텝 노출 | client | `step_number` (number, —) |
| `client_onboarding_completed` | 투어 마지막 스텝 완료 | client | 없음 |
| `client_onboarding_skipButton_clicked` | 건너뛰기 클릭 | client | `step_number` (number, ✅) — 이탈 지점 분석용 |

### AN-1-7-2 스토리 목록

목적은 메인에서 스토리 탐색·진입과 제작 진입을 파악하는 것이다.

| 이벤트 | 발생 시점 | platform | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_storyList_viewed` | 화면 진입 | client | 없음 |
| `client_storyList_storyCard_clicked` | 스토리 카드 클릭 | client | `story_id` (number, ✅), `position` (number, —) |
| `client_storyList_storyCard_impressed` | 카드 유효 노출 | client | `story_id` (number, ✅), `position` (number, —) |
| `client_storyList_createButton_clicked` | 제작하기 CTA 클릭 | client | 없음 |

### AN-1-7-3 스토리 제작

목적은 키워드 입력부터 생성 완료까지 단계별 이탈·생성 성공률을 측정하는 것이다.

| 이벤트 | 발생 시점 | platform | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_storyCreate_viewed` | 제작 화면 진입 | client | 없음 |
| `client_storyCreate_step_viewed` | 각 단계 진입 | client | `step_name` (string, ✅), `step_number` (number, ✅) |
| `client_storyCreate_nextButton_clicked` | 다음 버튼 클릭 | client | `step_name` (string, ✅), `step_number` (number, ✅) |
| `client_storyCreate_storyGeneration_requested` | 스토리라인 생성 요청 전송 | client | 없음 (`creation_id` 발급 전) |
| `server_storyCreate_storyGeneration_processed_succeeded` | 생성 성공 응답 | server | `creation_id` (string, ✅) |
| `server_storyCreate_storyGeneration_processed_failed` | 생성 실패 | server | `creation_id` (string, ✅), `error_type` (string, ✅) |
| `client_storyCreate_storylineOption_selected` | 스토리라인 선택 | client | `creation_id` (string, ✅), `position` (number, —) |
| `client_storyCreate_completed` | 스토리화 완료 | client | `story_id` (number, ✅), `chat_id` (string, ✅), `genre` (string[], —) |

제작 단계 `step_name`은 다음 값만 사용한다.

| step_number | step_name |
| --- | --- |
| `1` | `keyword` |
| `2` | `storylineSelect` |
| `3` | `additionalInfo` |
| `4` | `complete` |

### AN-1-7-4 스토리 상세

목적은 스토리 상세에서 채팅 시작 전환율을 파악하는 것이다.

| 이벤트 | 발생 시점 | platform | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_storyDetail_viewed` | 화면 진입 | client | `story_id` (number, ✅) |
| `client_storyDetail_chatStartButton_clicked` | 채팅 시작 버튼 클릭 | client | `story_id` (number, ✅) |
| `client_storyDetail_recommendStoryCard_clicked` | 추천 스토리 카드 클릭 | client | `story_id` (number, ✅) — 클릭한 추천 카드의 스토리 id, `position` (number, —) |
| `client_storyDetail_recommendStoryCard_impressed` | 추천 카드 유효 노출 | client | `story_id` (number, ✅) — 노출된 추천 카드의 스토리 id, `position` (number, —) |

`recommendStoryCard`의 `story_id`는 현재 보고 있는 스토리가 아니라 추천 카드의 스토리 id다.

### AN-1-7-5 채팅 목록

목적은 채팅 목록에서 기존 채팅 재진입을 파악하는 것이다.

| 이벤트 | 발생 시점 | platform | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_chatList_viewed` | 화면 진입 | client | 없음 |
| `client_chatList_chatCard_clicked` | 채팅 카드 클릭 | client | `chat_id` (string, ✅), `position` (number, —) |
| `client_chatList_chatCard_impressed` | 카드 유효 노출 | client | `chat_id` (string, ✅), `position` (number, —) |

### AN-1-7-6 채팅

목적은 채팅 진입·메시지 전송·AI 응답 성공률을 파악하는 것이다.

| 이벤트 | 발생 시점 | platform | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_chat_viewed` | 화면 진입 | client | `chat_id` (string, ✅) |
| `client_chat_messageInput_submitted` | 메시지 전송 | client | `chat_id` (string, ✅), `turn_number` (number, ✅) |
| `server_chat_aiMessage_processed_succeeded` | AI 응답 성공 | server | `chat_id` (string, ✅), `turn_number` (number, ✅) |
| `server_chat_aiMessage_processed_failed` | AI 응답 실패 | server | `chat_id` (string, ✅), `turn_number` (number, ✅), `error_type` (string, ✅) |
| `client_chat_choiceOption_selected` | 선택지(choices) 선택 | client | `chat_id` (string, ✅), `turn_number` (number, ✅), `position` (number, —) |

### AN-1-7-7 피드백

목적은 피드백 진입에서 제출 전환을 파악하는 것이다.

| 이벤트 | 발생 시점 | platform | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_feedback_viewed` | 화면 진입 | client | 없음 |
| `client_feedback_form_submitted` | 제출 버튼 클릭(전송) | client | 없음 |
| `server_feedback_submission_processed_succeeded` | 제출 성공 | server | 없음 |
| `server_feedback_submission_processed_failed` | 제출 실패 | server | `error_type` (string, ✅) |

server 이벤트의 `error_type`은 `network`, `validation`, `server` 중 하나만 사용한다.

## AN-1-8 개인정보와 원문 수집 원칙

MVP 분석 이벤트에는 사용자가 입력한 원문을 직접 넣지 않는다.

| 데이터 | 이벤트 포함 여부 | 처리 방식 |
| --- | --- | --- |
| 피드백 본문 | 포함하지 않음 | 별도 저장소에 저장한다. |
| 이메일 | 포함하지 않음 | 별도 저장소에 저장한다. |
| 채팅 메시지 원문 | 포함하지 않음 | 분석 이벤트에는 `turn_number`만 남긴다. |
| 키워드·추가 정보 원문 | 포함하지 않음 | 관리되는 ID 또는 선택값만 남긴다. |
| 프롬프트 전문 | 포함하지 않음 | 로그와 Sentry에 넣지 않는다. |

## AN-1-9 MVP 우선 적용 이벤트

처음부터 모든 이벤트를 심기 어렵다면 핵심 퍼널(AN-1-5)에 쓰이는 이벤트를 P0로 먼저 적용하고, 보조 분석용 이벤트를 P1로 추가한다.

| 우선순위 | 이벤트 |
| --- | --- |
| P0 | `client_storyList_viewed` |
| P0 | `client_storyList_createButton_clicked` |
| P0 | `client_storyCreate_viewed` |
| P0 | `client_storyCreate_step_viewed` |
| P0 | `client_storyCreate_storyGeneration_requested` |
| P0 | `server_storyCreate_storyGeneration_processed_succeeded` |
| P0 | `server_storyCreate_storyGeneration_processed_failed` |
| P0 | `client_storyCreate_storylineOption_selected` |
| P0 | `client_storyCreate_completed` |
| P0 | `client_storyDetail_viewed` |
| P0 | `client_storyDetail_chatStartButton_clicked` |
| P0 | `client_chat_viewed` |
| P0 | `client_chat_messageInput_submitted` |
| P0 | `server_chat_aiMessage_processed_succeeded` |
| P0 | `server_chat_aiMessage_processed_failed` |
| P0 | `client_feedback_viewed` |
| P0 | `client_feedback_form_submitted` |
| P1 | `client_onboarding_viewed` |
| P1 | `client_onboarding_completed` |
| P1 | `client_onboarding_skipButton_clicked` |
| P1 | `client_storyList_storyCard_clicked` |
| P1 | `client_storyList_storyCard_impressed` |
| P1 | `client_storyCreate_nextButton_clicked` |
| P1 | `client_storyDetail_recommendStoryCard_clicked` |
| P1 | `client_storyDetail_recommendStoryCard_impressed` |
| P1 | `client_chatList_viewed` |
| P1 | `client_chatList_chatCard_clicked` |
| P1 | `client_chatList_chatCard_impressed` |
| P1 | `client_chat_choiceOption_selected` |
| P1 | `server_feedback_submission_processed_succeeded` |
| P1 | `server_feedback_submission_processed_failed` |

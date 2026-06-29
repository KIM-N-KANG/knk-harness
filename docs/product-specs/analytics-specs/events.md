# AN-2-ANALYTICS-EVENTS

이 문서는 마냑 MVP 분석 이벤트의 원본 카탈로그입니다. 이벤트명, 발생 조건, 고유 프로퍼티, 우선순위는 이 문서에서 관리합니다.

```text
§AN-2-1  이벤트 원칙
§AN-2-2  공통 프로퍼티
§AN-2-3  MVP 우선순위
§AN-2-4  페이지별 이벤트 카탈로그
§AN-2-5  impression 수집 기준
§AN-2-6  전송 예시
```

| 항목 | 값 |
| --- | --- |
| 버전 | v0.8 |
| 작성일 | 2026-06-30 |
| 대상 | 마냑 MVP 분석 이벤트 |
| 관련 문서 | [`analytics-spec.md`](./analytics-spec.md), [`metrics.md`](./metrics.md), [`observability.md`](./observability.md), [`qa.md`](./qa.md) |

## AN-2-1 이벤트 원칙

이벤트명은 [`analytics-spec.md`](./analytics-spec.md) AN-1-7의 네이밍 기준을 따릅니다.

```text
{platform}_{screenName}(_{objectName})?_{actionType}(_{eventType})?
```

| 원칙 | 설명 | 예시 |
| --- | --- | --- |
| 이벤트명에 데이터 값을 넣지 않습니다. | ID, 선택값, 단계 번호, 리스트 위치, 에러 코드는 프로퍼티로 보냅니다. | `story_id`, `step_number`, `position` |
| 단계 번호는 screenName에 넣지 않습니다. | 단계는 `step_number`, `step_name` 프로퍼티로 보냅니다. | `client_storyCreate_step_viewed` |
| 버튼은 문구보다 역할로 씁니다. | 버튼 문구가 바뀌어도 이벤트명이 바뀌지 않게 합니다. | `nextButton`, `chatStartButton` |
| 서버 처리 대상은 기능 단위로 씁니다. | 서버 결과는 `processed`와 `eventType`으로 구분합니다. | `server_chat_aiMessage_processed_failed` |
| `canceled`는 실제 취소 행동에만 씁니다. | 단순 닫기나 나가기 클릭에는 `clicked`를 씁니다. | `client_storyCreate_exitButton_clicked` |

`actionType`은 아래 값만 사용합니다.

| 그룹 | 값 | 설명 |
| --- | --- | --- |
| 사용자 행동 | `viewed` | 화면 또는 단계에 진입했을 때 |
| 사용자 행동 | `clicked` | 클릭 가능한 요소를 눌렀을 때 |
| 사용자 행동 | `selected` | 선택지를 선택했을 때 |
| 사용자 행동 | `focused` | 입력 영역에 포커스가 들어왔을 때 |
| 사용자 행동 | `submitted` | 폼이나 입력값을 제출했을 때 |
| 사용자 행동 | `requested` | 클라이언트가 서버에 생성 또는 처리를 요청했을 때 |
| 사용자 행동 | `completed` | 주요 flow를 끝까지 완료했을 때 |
| 상태 노출 | `shown` | 모달, 토스트, 에러, 로딩, 빈 상태가 표시되었을 때 |
| 상태 노출 | `impressed` | item 또는 section이 유효하게 노출되었을 때 |
| 서버 처리 | `processed` | 서버가 생성, 저장, 처리를 수행했을 때 |

`eventType`은 `succeeded`, `failed`, `blocked`, `canceled`만 사용합니다. 단순 클릭, 노출, 포커스, 화면 진입에는 결과 상태를 붙이지 않습니다. `completed`는 결과 상태가 아니라 사용자가 flow를 끝마친 행동이므로 `actionType`으로 씁니다.

## AN-2-2 공통 프로퍼티

각 이벤트 표에는 고유 프로퍼티만 적습니다. 공통 프로퍼티는 적용 범위에 따라 모든 이벤트에 함께 보냅니다.

| property | 타입 | 적용 범위 | 설명 |
| --- | --- | --- | --- |
| `screen_name` | string | 모든 이벤트 | 이벤트가 발생한 화면입니다. 필터와 세그먼트 편의를 위해 프로퍼티로도 보냅니다. |
| `step_name` | string | 스토리 제작 퍼널 | `keyword`, `storylineSelect`, `additionalInfo`, `complete` 중 하나입니다. |
| `step_number` | number | 스토리 제작 퍼널 | 제작 단계 번호입니다. |
| `creation_id` | string | 스토리 제작 퍼널 | 스토리라인 생성 시 발급되는 `simpleCreationId`입니다. |
| `story_id` | number | story 관련 이벤트 | 스토리 식별자입니다. |
| `chat_id` | string | chat 관련 이벤트 | 채팅 식별자입니다. |

다음 값은 Amplitude Browser SDK가 자동으로 채우므로 커스텀 프로퍼티로 다시 만들지 않습니다.

```text
device_id, session_id
platform, os_name, os_version, device_family
app_version
country, region, city, language
event_time, event_id
```

다음 프로퍼티는 관련 기능 도입 시점에 추가합니다.

| property | 도입 시점 | 설명 |
| --- | --- | --- |
| `user_id` | 인증 도입 후 | 로그인 사용자 식별자입니다. |
| `is_logged_in` | 인증 도입 후 | 로그인 여부입니다. |
| `membership` | 구독·요금제 도입 후 | 요금제 또는 등급입니다. |
| `signup_at` | 인증 도입 후 | 가입 시점입니다. |
| `experiment_key` / `variant` | A/B 테스트 도입 후 | 실험 키와 분기 값입니다. |
| `request_id` | 서버 사이드 분석 이벤트 연결 도입 후 | client `requested`와 server `processed`를 분석 이벤트 프로퍼티로 직접 잇는 상관 ID입니다. |
| `item_id` / `section_id` / `section_name` | impression 정밀 계측 시 | 추천 카드 등 노출 분석용 값입니다. |

현재 `request_id`는 서버 내부 상관 키로 사용합니다. 분석 이벤트 프로퍼티로는 아직 보내지 않습니다. 자세한 기준은 [`observability.md`](./observability.md) AN-4-3을 따릅니다.

## AN-2-3 MVP 우선순위

P0 이벤트는 출시 전에 반드시 수집합니다. P1 이벤트는 P0가 안정적으로 수집된 뒤 추가합니다.

| 우선순위 | 소유 | 이벤트 |
| --- | --- | --- |
| P0 | client | `client_storyList_viewed` |
| P0 | client | `client_storyList_createButton_clicked` |
| P0 | client | `client_storyCreate_viewed` |
| P0 | client | `client_storyCreate_step_viewed` |
| P0 | client | `client_storyCreate_storyGeneration_requested` |
| P0 | server | `server_storyCreate_storyGeneration_processed_succeeded` |
| P0 | server | `server_storyCreate_storyGeneration_processed_failed` |
| P0 | client | `client_storyCreate_storylineOption_selected` |
| P0 | client | `client_storyCreate_selectedKeywordsButton_clicked` |
| P0 | client | `client_storyCreate_completed` |
| P0 | client | `client_storyDetail_viewed` |
| P0 | client | `client_storyDetail_chatStartButton_clicked` |
| P0 | client | `client_chat_viewed` |
| P0 | client | `client_chat_messageInput_submitted` |
| P0 | server | `server_chat_aiMessage_processed_succeeded` |
| P0 | server | `server_chat_aiMessage_processed_failed` |
| P0 | client | `client_feedback_viewed` |
| P0 | client | `client_feedback_form_submitted` |
| P1 | client | `client_onboarding_viewed` |
| P1 | client | `client_onboarding_createButton_clicked` |
| P1 | client | `client_storyList_storyCard_clicked` |
| P1 | client | `client_storyList_storyCard_impressed` |
| P1 | client | `client_storyCreate_nextButton_clicked` |
| P1 | client | `client_storyDetail_recommendStoryCard_clicked` |
| P1 | client | `client_storyDetail_recommendStoryCard_impressed` |
| P1 | client | `client_chatList_viewed` |
| P1 | client | `client_chatList_chatCard_clicked` |
| P1 | client | `client_chatList_chatCard_impressed` |
| P1 | client | `client_chat_choiceOption_selected` |
| P1 | server | `server_feedback_submission_processed_succeeded` |
| P1 | server | `server_feedback_submission_processed_failed` |

## AN-2-4 페이지별 이벤트 카탈로그

각 이벤트 표에는 공통 프로퍼티를 제외한 고유 프로퍼티만 적습니다. 필수는 `필수`, 선택은 `선택`으로 표기합니다.

### AN-2-4-1 온보딩

홈 최초 진입 시 노출되는 환영 다이얼로그입니다. 사용자는 `스토리 만들기` 버튼을 누르기 전까지 다이얼로그를 닫을 수 없고, 다이얼로그는 최초 1회만 노출됩니다.

| 이벤트 | 우선순위 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_onboarding_viewed` | P1 | 환영 다이얼로그 노출 | 없음 |
| `client_onboarding_createButton_clicked` | P1 | 스토리 만들기 버튼 클릭 | 없음 |

### AN-2-4-2 스토리 목록

| 이벤트 | 우선순위 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_storyList_viewed` | P0 | 스토리 목록 화면 진입 | 없음 |
| `client_storyList_createButton_clicked` | P0 | 제작하기 CTA 클릭 | 없음 |
| `client_storyList_storyCard_clicked` | P1 | 스토리 카드 클릭 | `story_id` (number, 필수), `position` (number, 선택) |
| `client_storyList_storyCard_impressed` | P1 | 스토리 카드 유효 노출 | `story_id` (number, 필수), `position` (number, 선택) |

### AN-2-4-3 스토리 제작

| 이벤트 | 우선순위 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_storyCreate_viewed` | P0 | 제작 화면 진입 | 없음 |
| `client_storyCreate_step_viewed` | P0 | 각 제작 단계 진입 | `step_name` (string, 필수), `step_number` (number, 필수) |
| `client_storyCreate_storyGeneration_requested` | P0 | 스토리라인 생성 요청 전송 | 없음 |
| `server_storyCreate_storyGeneration_processed_succeeded` | P0 | 스토리라인 생성 성공 | `creation_id` (string, 필수) |
| `server_storyCreate_storyGeneration_processed_failed` | P0 | 스토리라인 생성 실패 | `creation_id` (string, 필수), `error_type` (string, 필수) |
| `client_storyCreate_storylineOption_selected` | P0 | 스토리라인 선택 | `creation_id` (string, 필수), `position` (number, 선택) |
| `client_storyCreate_selectedKeywordsButton_clicked` | P0 | 선택한 키워드 보기 버튼 클릭 | `creation_id` (string, 필수) |
| `client_storyCreate_completed` | P0 | 스토리화 완료 | `story_id` (number, 필수), `chat_id` (string, 필수), `genre` (string[], 선택) |
| `client_storyCreate_nextButton_clicked` | P1 | 다음 버튼 클릭 | `step_name` (string, 필수), `step_number` (number, 필수) |

`client_storyCreate_storyGeneration_requested`는 `creation_id` 발급 전 이벤트입니다. `server_storyCreate_storyGeneration_processed_*`는 백엔드가 스토리라인 생성 처리를 시작하며 발급한 `creation_id`를 포함합니다.

`selectedKeywordsButton_clicked`는 스토리라인 선택(`storylineSelect`) 단계 탭 우측의 키워드 보기 버튼으로 선택 키워드 드로워를 열 때 발생합니다. 드로워에 노출되는 키워드 이름은 이벤트에 넣지 않고 `creation_id`만 보냅니다.

제작 단계 `step_name`은 다음 값만 사용합니다.

| step_number | step_name |
| --- | --- |
| `1` | `keyword` |
| `2` | `storylineSelect` |
| `3` | `additionalInfo` |
| `4` | `complete` |

### AN-2-4-4 스토리 상세

| 이벤트 | 우선순위 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_storyDetail_viewed` | P0 | 스토리 상세 화면 진입 | `story_id` (number, 필수) |
| `client_storyDetail_chatStartButton_clicked` | P0 | 채팅 시작 버튼 클릭 | `story_id` (number, 필수) |
| `client_storyDetail_recommendStoryCard_clicked` | P1 | 추천 스토리 카드 클릭 | `story_id` (number, 필수), `position` (number, 선택) |
| `client_storyDetail_recommendStoryCard_impressed` | P1 | 추천 스토리 카드 유효 노출 | `story_id` (number, 필수), `position` (number, 선택) |

`recommendStoryCard`의 `story_id`는 현재 보는 스토리가 아니라 추천 카드의 스토리 ID입니다.

### AN-2-4-5 채팅 목록

| 이벤트 | 우선순위 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_chatList_viewed` | P1 | 채팅 목록 화면 진입 | 없음 |
| `client_chatList_chatCard_clicked` | P1 | 채팅 카드 클릭 | `chat_id` (string, 필수), `position` (number, 선택) |
| `client_chatList_chatCard_impressed` | P1 | 채팅 카드 유효 노출 | `chat_id` (string, 필수), `position` (number, 선택) |

### AN-2-4-6 채팅

| 이벤트 | 우선순위 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_chat_viewed` | P0 | 채팅 화면 진입 | `chat_id` (string, 필수) |
| `client_chat_messageInput_submitted` | P0 | 사용자 메시지 전송 | `chat_id` (string, 필수), `turn_number` (number, 필수) |
| `server_chat_aiMessage_processed_succeeded` | P0 | AI 응답 생성 성공 | `chat_id` (string, 필수), `turn_number` (number, 필수) |
| `server_chat_aiMessage_processed_failed` | P0 | AI 응답 생성 실패 | `chat_id` (string, 필수), `turn_number` (number, 필수), `error_type` (string, 필수) |
| `client_chat_choiceOption_selected` | P1 | 선택지 선택 | `chat_id` (string, 필수), `turn_number` (number, 필수), `position` (number, 선택) |

AI 응답 성공·실패는 백엔드가 `server_chat_aiMessage_processed_succeeded` 또는 `server_chat_aiMessage_processed_failed`로 발행합니다. 프론트엔드는 `chat_id`와 `turn_number`로 메시지와 응답을 연결합니다.

### AN-2-4-7 피드백

| 이벤트 | 우선순위 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_feedback_viewed` | P0 | 피드백 화면 진입 | 없음 |
| `client_feedback_form_submitted` | P0 | 피드백 제출 버튼 클릭 | 없음 |
| `server_feedback_submission_processed_succeeded` | P1 | 피드백 제출 처리 성공 | 없음 |
| `server_feedback_submission_processed_failed` | P1 | 피드백 제출 처리 실패 | `error_type` (string, 필수) |

server 이벤트의 `error_type`은 `network`, `validation`, `server` 중 하나만 사용합니다. 상세 매핑은 [`observability.md`](./observability.md) AN-4-7을 따릅니다.

## AN-2-5 impression 수집 기준

`impressed`는 특정 item 또는 section이 사용자 화면에 유효하게 노출된 상태를 뜻합니다.

| 항목 | 권장 기준 |
| --- | --- |
| 최소 노출 면적 | 컴포넌트 면적의 50% 이상 |
| 최소 노출 시간 | 1초 이상 |

중복 노출은 동일 item 기준으로 한 번만 수집합니다. `동일 session_id + 동일 screenName + 동일 objectName + 동일 item_id` 기준으로 30초 이내 재노출은 중복으로 판단합니다. `section_id`, `section_name`, `item_id`는 정밀 계측 도입 시 추가합니다.

## AN-2-6 전송 예시

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

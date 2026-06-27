# AN-2-ANALYTICS-FRONTEND-SPEC

이 문서는 **마냑 MVP 웹 프론트엔드가 Amplitude와 Sentry로 남겨야 하는 분석 신호**를 정리합니다. 사용자가 스토리를 만들고 채팅을 이어가는 행동은 Amplitude로 측정하고, 브라우저 오류와 API 실패 재현 단서는 Sentry로 확인합니다.

프론트엔드는 에이전트와 운영자가 직접 읽을 수 있는 관측 경계입니다. 화면 이벤트, breadcrumb, 상관 키를 같은 흐름 안에 묶어 프론트엔드 행동과 서버 로그가 끊기지 않게 합니다.

```text
§AN-2-1   목적              프론트엔드 분석 책임과 제외 범위
§AN-2-2   도구별 역할       Amplitude · Sentry 역할 분리
§AN-2-3   식별자 정책       device_id · session_id · creation_id · chat_id
§AN-2-4   공통 이벤트 규칙  네이밍 컨벤션 · 핵심 프로퍼티 · SDK 자동 수집
§AN-2-5   MVP 우선 이벤트   출시 전 P0 · 안정화 후 P1 이벤트
§AN-2-6   퍼널 정의         제작 · 채팅 활성화 · 전체 활성화 퍼널
§AN-2-7   페이지별 이벤트   온보딩 · 목록 · 제작 · 상세 · 채팅 목록 · 채팅 · 피드백
§AN-2-8   Sentry 수집 기준  Tags · User · Breadcrumb · Exceptions
§AN-2-9   개인정보 원칙     원문 수집 금지와 대체 프로퍼티
§AN-2-10  검수 체크리스트   출시 전 확인 항목
```

---

| 항목 | 값 |
| --- | --- |
| 버전 | v0.7 |
| 작성일 | 2026-06-25 |
| 대상 | 마냑 MVP 웹 프론트엔드 |
| 적용 도구 | Amplitude, Sentry |

| 관련 문서 | 연결 지점 |
| --- | --- |
| [`analytics-spec.md`](./analytics-spec.md) | 전체 이벤트·지표·퍼널 기준 |
| [`analytics-backend-spec.md`](./analytics-backend-spec.md) | 서버 분석 이벤트(`server_*`)와 API 상관 키 |
| [`analytics-ai-spec.md`](./analytics-ai-spec.md) | AI 응답 성공·실패 이벤트와 AI 호출 로그 연결 |

## AN-2-1 목적

프론트엔드 분석의 목적은 사용자가 스토리를 만들고 채팅을 시작한 뒤 이야기를 이어가는지 측정하는 것이다. MVP에서는 모든 화면과 클릭을 추적하지 않고, 핵심 퍼널에 필요한 화면 진입과 클릭만 측정한다.

프론트엔드는 다음 데이터를 담당한다.

- Amplitude로 `client_*` 사용자 행동 이벤트를 수집한다.
- Sentry로 브라우저 오류와 사용자 행동 breadcrumb를 수집한다.
- 백엔드 API 호출에 상관 키(`creation_id`, `chat_id`)를 전달해 `server_*` 이벤트·서버 로그와 연결한다.
- 사용자가 입력한 원문, 이메일, 채팅 메시지는 분석 이벤트에 넣지 않는다.

`server_*` 이벤트(생성·AI 응답·피드백 제출 결과)는 백엔드가 발행한다. 프론트엔드는 client `requested`·`submitted` 이벤트를 남기고, 서버 처리 결과는 [`analytics-backend-spec.md`](./analytics-backend-spec.md)에서 계측한다.

## AN-2-2 도구별 역할

| 도구 | 역할 | MVP 적용 범위 |
| --- | --- | --- |
| Amplitude | 사용자 행동 분석 | 퍼널, 전환율, 이탈율, 선택지 사용률 |
| Sentry | 프론트엔드 오류 분석 | 렌더링 오류, 라우트 오류, API 실패, 사용자 행동 breadcrumb |

Amplitude는 사용자 행동의 기준 데이터로 사용한다. Sentry는 오류 재현과 장애 원인 파악에 사용한다. Sentry 이벤트 수는 지표 계산의 기준으로 쓰지 않는다.

## AN-2-3 식별자 정책

MVP는 로그인 기능이 없는 전원 게스트 서비스다. 사용자 단위 식별은 Amplitude Browser SDK가 자동으로 채우는 `device_id`로 처리한다. 프론트엔드가 익명 ID를 직접 생성·저장하지 않는다.

| 식별자 | 타입 | 생성·관리 | 설명 |
| --- | --- | --- | --- |
| `device_id` | string | Amplitude SDK 자동 | 같은 브라우저 사용자를 묶는 익명 단위 |
| `session_id` | number | Amplitude SDK 자동 | 한 번의 방문 흐름 |
| `creation_id` | string | 서버 발급(`simpleCreationId`) | client `requested` ↔ server `processed`를 잇는 상관 키 |
| `story_id` | number | 서버 발급 | 스토리 식별자 |
| `chat_id` | string | 서버 발급 | 채팅 식별자 |

로그인 기능을 도입하면 `device_id`는 유지하고, 로그인 시점부터 `user_id`를 추가한다. Amplitude의 `identify`로 기존 익명 행동과 로그인 사용자를 연결한다. 서버 사이드 이벤트를 정밀하게 연결할 `request_id`는 추후 도입하며, 현재는 `creation_id`로 대체한다.

## AN-2-4 공통 이벤트 규칙

모든 Amplitude 이벤트명은 `{platform}_{screenName}(_{objectName})?_{actionType}(_{eventType})?` 형식을 따른다. 프론트엔드는 platform을 `client`로 쓴다. 각 항목 내부는 camelCase, 프로퍼티는 `snake_case`로 쓴다. 자세한 규칙은 [`analytics-spec.md`](./analytics-spec.md) AN-1-3을 따른다.

### AN-2-4-1 이벤트명과 프로퍼티 분리

이벤트명에는 사용자가 한 행동 또는 노출된 상태만 표현한다. ID, 선택값, 단계 번호, 에러 정보, 리스트 위치는 이벤트명이 아니라 프로퍼티로 보낸다.

| 구분 | 기준 | 예시 |
| --- | --- | --- |
| 이벤트명 | 사용자가 화면을 보거나 UI를 조작한 행동 | `client_storyCreate_step_viewed`, `client_storyList_storyCard_clicked` |
| 프로퍼티 | 행동이 일어난 순간의 ID, 단계, 선택값 | `step_name`, `step_number`, `story_id`, `position` |

생성 성공·실패처럼 서버 결과를 뜻하는 이벤트는 프론트엔드 `client_*` 이벤트로 쓰지 않는다. 생성 성공은 사용자가 다음 화면을 본 이벤트로, 생성 실패는 server `processed_failed` 이벤트로 측정한다.

### AN-2-4-2 핵심 프로퍼티

각 이벤트 표에는 고유 프로퍼티만 적는다. 다음 핵심 프로퍼티를 적용 범위에 따라 함께 보낸다.

| property | 타입 | 적용 범위 | 설명 |
| --- | --- | --- | --- |
| `screen_name` | string | 모든 이벤트 | 이벤트가 발생한 화면 |
| `step_name` | string | 스토리 제작 퍼널 | `keyword`, `storylineSelect`, `additionalInfo`, `complete` |
| `step_number` | number | 스토리 제작 퍼널 | 제작 단계 번호 |
| `creation_id` | string | 스토리 제작 퍼널 | 스토리라인 생성 시 발급되는 `simpleCreationId` |
| `story_id` | number | story 관련 이벤트 | 스토리 식별자 |
| `chat_id` | string | chat 관련 이벤트 | 채팅 식별자 |

### AN-2-4-3 SDK 자동 수집 (재정의 금지)

다음 값은 Amplitude Browser SDK가 자동으로 채우므로 커스텀 프로퍼티로 다시 만들지 않는다.

```text
device_id, session_id
platform, os_name, os_version, device_family
app_version
country, region, city, language
event_time, event_id
```

## AN-2-5 MVP 우선 이벤트

P0 이벤트는 출시 전에 반드시 심는다. P1 이벤트는 P0가 안정적으로 수집된 뒤 추가한다. 아래 표는 프론트엔드가 직접 발행하는 `client_*` 이벤트만 적는다. `server_*` 이벤트는 백엔드 스펙을 따른다.

| 우선순위 | 이벤트 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- | --- |
| P0 | `client_storyList_viewed` | 스토리 목록 진입 | 없음 |
| P0 | `client_storyList_createButton_clicked` | 제작하기 CTA 클릭 | 없음 |
| P0 | `client_storyCreate_viewed` | 제작 화면 진입 | 없음 |
| P0 | `client_storyCreate_step_viewed` | 제작 단계 진입 | `step_name`, `step_number` |
| P0 | `client_storyCreate_storyGeneration_requested` | 스토리라인 생성 요청 전송 | 없음 |
| P0 | `client_storyCreate_storylineOption_selected` | 스토리라인 선택 | `creation_id`, `position` |
| P0 | `client_storyCreate_selectedKeywordsButton_clicked` | 선택한 키워드 보기 버튼 클릭(드로워 열기) | `creation_id` |
| P0 | `client_storyCreate_completed` | 스토리화 완료 | `story_id`, `chat_id`, `genre` |
| P0 | `client_storyDetail_viewed` | 스토리 상세 진입 | `story_id` |
| P0 | `client_storyDetail_chatStartButton_clicked` | 채팅 시작 버튼 클릭 | `story_id` |
| P0 | `client_chat_viewed` | 채팅 진입 | `chat_id` |
| P0 | `client_chat_messageInput_submitted` | 메시지 전송 | `chat_id`, `turn_number` |
| P0 | `client_feedback_viewed` | 피드백 화면 진입 | 없음 |
| P0 | `client_feedback_form_submitted` | 피드백 제출(전송) | 없음 |
| P1 | `client_onboarding_viewed` | 환영 다이얼로그 노출 | 없음 |
| P1 | `client_onboarding_createButton_clicked` | 스토리 만들기 버튼 클릭 | 없음 |
| P1 | `client_storyList_storyCard_clicked` | 스토리 카드 클릭 | `story_id`, `position` |
| P1 | `client_storyList_storyCard_impressed` | 스토리 카드 유효 노출 | `story_id`, `position` |
| P1 | `client_storyCreate_nextButton_clicked` | 다음 버튼 클릭 | `step_name`, `step_number` |
| P1 | `client_storyDetail_recommendStoryCard_clicked` | 추천 카드 클릭 | `story_id`, `position` |
| P1 | `client_storyDetail_recommendStoryCard_impressed` | 추천 카드 유효 노출 | `story_id`, `position` |
| P1 | `client_chatList_viewed` | 채팅 목록 진입 | 없음 |
| P1 | `client_chatList_chatCard_clicked` | 채팅 카드 클릭 | `chat_id`, `position` |
| P1 | `client_chatList_chatCard_impressed` | 채팅 카드 유효 노출 | `chat_id`, `position` |
| P1 | `client_chat_choiceOption_selected` | 선택지 선택 | `chat_id`, `turn_number`, `position` |

## AN-2-6 퍼널 정의

퍼널 전체 정의는 [`analytics-spec.md`](./analytics-spec.md) AN-1-5를 따른다. 프론트엔드는 client 이벤트로 구간을 측정하고, 생성 성공·AI 응답 성공처럼 결과 상태는 server 이벤트로 연결한다.

### AN-2-6-1 스토리 제작 퍼널

| 순서 | 단계 | 이벤트 | 고정값 |
| --- | --- | --- | --- |
| 1 | 제작 진입 | `client_storyCreate_viewed` | device |
| 2 | 생성 요청 | `client_storyCreate_storyGeneration_requested` | device |
| 3 | 생성 성공 | `server_storyCreate_storyGeneration_processed_succeeded` | creation_id |
| 4 | 스토리라인 선택 | `client_storyCreate_storylineOption_selected` | creation_id |
| 5 | 제작 완료 | `client_storyCreate_completed` | creation_id |

화면 단계 이탈은 `client_storyCreate_step_viewed`의 `step_name`(keyword → storylineSelect → additionalInfo → complete)으로 별도 퍼널로 본다.

### AN-2-6-2 채팅 활성화 퍼널

| 순서 | 단계 | 이벤트 | 고정값 |
| --- | --- | --- | --- |
| 1 | 채팅 진입 | `client_chat_viewed` | chat_id |
| 2 | 첫 메시지 | `client_chat_messageInput_submitted` (`turn_number=1`) | chat_id |
| 3 | 첫 AI 응답 | `server_chat_aiMessage_processed_succeeded` | chat_id |

진입 경로는 `client_storyDetail_chatStartButton_clicked` → 1로 본다. 대화 깊이는 `turn_number` 분포로 N턴 이상 도달률을 본다.

### AN-2-6-3 전체 활성화 퍼널 (north-star)

| 순서 | 단계 | 이벤트 | 고정값 |
| --- | --- | --- | --- |
| 1 | 메인 방문 | `client_storyList_viewed` | device |
| 2 | 제작 시작 | `client_storyList_createButton_clicked` | device |
| 3 | 제작 완료 | `client_storyCreate_completed` | device |
| 4 | 첫 메시지 | `client_chat_messageInput_submitted` | chat_id |
| 5 | 첫 AI 응답 | `server_chat_aiMessage_processed_succeeded` | chat_id |

3단계 `client_storyCreate_completed`에서 발급된 `chat_id`로 4~5를 연결한다.

## AN-2-7 페이지별 이벤트

각 이벤트 표에는 공통 프로퍼티 외에 이벤트별 고유 프로퍼티만 적는다. 필수는 ✅, 선택은 — 로 표기한다.

### AN-2-7-1 온보딩

홈 최초 진입 시 노출되는 환영 다이얼로그다. '스토리 만들기' 버튼을 누르기 전까지 닫을 수 없고, 최초 1회만 노출된다.

| 이벤트 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- |
| `client_onboarding_viewed` | 환영 다이얼로그 노출 | 없음 |
| `client_onboarding_createButton_clicked` | 스토리 만들기 버튼 클릭 | 없음 |

### AN-2-7-2 스토리 목록

| 이벤트 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- |
| `client_storyList_viewed` | 화면 진입 | 없음 |
| `client_storyList_storyCard_clicked` | 스토리 카드 클릭 | `story_id` (number, ✅), `position` (number, —) |
| `client_storyList_storyCard_impressed` | 카드 유효 노출 | `story_id` (number, ✅), `position` (number, —) |
| `client_storyList_createButton_clicked` | 제작하기 CTA 클릭 | 없음 |

### AN-2-7-3 스토리 제작

스토리 제작 이벤트에는 단계 정보를 `step_name`, `step_number`로 함께 보낸다. 단계 번호를 이벤트명이나 screenName에 넣지 않는다.

| 이벤트 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- |
| `client_storyCreate_viewed` | 제작 화면 진입 | 없음 |
| `client_storyCreate_step_viewed` | 각 단계 진입 | `step_name` (string, ✅), `step_number` (number, ✅) |
| `client_storyCreate_nextButton_clicked` | 다음 버튼 클릭 | `step_name` (string, ✅), `step_number` (number, ✅) |
| `client_storyCreate_storyGeneration_requested` | 스토리라인 생성 요청 전송 | 없음 |
| `client_storyCreate_storylineOption_selected` | 스토리라인 선택 | `creation_id` (string, ✅), `position` (number, —) |
| `client_storyCreate_selectedKeywordsButton_clicked` | 선택한 키워드 보기 버튼 클릭(드로워 열기) | `creation_id` (string, ✅) |
| `client_storyCreate_completed` | 스토리화 완료 | `story_id` (number, ✅), `chat_id` (string, ✅), `genre` (string[], —) |

`selectedKeywordsButton_clicked`는 스토리라인 선택(`storylineSelect`) 단계 탭 우측의 키워드 보기 버튼으로 선택 키워드 드로워를 열 때 발생한다. 드로워에 노출되는 키워드 이름은 이벤트에 넣지 않고 `creation_id`만 보낸다.

제작 단계 `step_name`은 다음 값만 사용한다.

| step_number | step_name |
| --- | --- |
| `1` | `keyword` |
| `2` | `storylineSelect` |
| `3` | `additionalInfo` |
| `4` | `complete` |

전송 예시는 다음과 같다.

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

생성 요청 후 성공·실패 결과는 백엔드가 `server_storyCreate_storyGeneration_processed_succeeded` 또는 `..._failed`로 발행한다. 프론트엔드는 `creation_id`로 두 흐름을 연결한다.

### AN-2-7-4 스토리 상세

| 이벤트 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- |
| `client_storyDetail_viewed` | 화면 진입 | `story_id` (number, ✅) |
| `client_storyDetail_chatStartButton_clicked` | 채팅 시작 버튼 클릭 | `story_id` (number, ✅) |
| `client_storyDetail_recommendStoryCard_clicked` | 추천 스토리 카드 클릭 | `story_id` (number, ✅), `position` (number, —) |
| `client_storyDetail_recommendStoryCard_impressed` | 추천 카드 유효 노출 | `story_id` (number, ✅), `position` (number, —) |

`recommendStoryCard`의 `story_id`는 현재 보는 스토리가 아니라 추천 카드의 스토리 id다.

### AN-2-7-5 채팅 목록

| 이벤트 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- |
| `client_chatList_viewed` | 화면 진입 | 없음 |
| `client_chatList_chatCard_clicked` | 채팅 카드 클릭 | `chat_id` (string, ✅), `position` (number, —) |
| `client_chatList_chatCard_impressed` | 카드 유효 노출 | `chat_id` (string, ✅), `position` (number, —) |

### AN-2-7-6 채팅

| 이벤트 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- |
| `client_chat_viewed` | 화면 진입 | `chat_id` (string, ✅) |
| `client_chat_messageInput_submitted` | 메시지 전송 | `chat_id` (string, ✅), `turn_number` (number, ✅) |
| `client_chat_choiceOption_selected` | 선택지 선택 | `chat_id` (string, ✅), `turn_number` (number, ✅), `position` (number, —) |

AI 응답 성공·실패는 백엔드가 `server_chat_aiMessage_processed_succeeded` 또는 `..._failed`로 발행한다. 프론트엔드는 `chat_id`와 `turn_number`로 메시지·응답을 연결한다.

### AN-2-7-7 피드백

| 이벤트 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- |
| `client_feedback_viewed` | 화면 진입 | 없음 |
| `client_feedback_form_submitted` | 제출 버튼 클릭(전송) | 없음 |

제출 성공·실패는 백엔드가 `server_feedback_submission_processed_succeeded` 또는 `..._failed`로 발행한다.

## AN-2-8 Sentry 수집 기준

Sentry에는 오류 분석에 필요한 최소 context만 넣는다.

| 구분 | 수집 내용 |
| --- | --- |
| Tags | `screen_name`, `story_id`, `chat_id`, `creation_id` |
| User | `id: device_id`, `ip_address: "{{auto}}"` |
| Breadcrumb | P0 행동 이벤트 이름, 주요 API 요청 시작과 종료 |
| Exceptions | 렌더링 오류, 라우트 오류, API 네트워크 오류, 예상하지 못한 5xx 응답 |

4xx 응답은 사용자가 복구할 수 있는 검증 오류라면 Sentry exception으로 보내지 않는다. 사용자 행동 분석이 필요하면 Amplitude 이벤트로만 기록한다. 서버 사이드 상관 키 `request_id`를 도입하면 Tags에 추가한다.

## AN-2-9 개인정보 원칙

프론트엔드 분석 이벤트에는 원문을 넣지 않는다.

| 데이터 | 처리 방식 |
| --- | --- |
| 채팅 메시지 | `turn_number`만 전송 |
| 피드백 본문 | 분석 이벤트에 미포함. 별도 저장소에 저장 |
| 이메일 | 분석 이벤트에 미포함. 별도 저장소에 저장 |
| 직접 추가 키워드·추가 정보 | 관리되는 ID 또는 선택값만 전송 |
| 장르 | 관리되는 태그(`genre`)만 전송 |

## AN-2-10 검수 체크리스트

- Amplitude 디버그 모드에서 P0 이벤트가 한 번씩 발생한다.
- `client_storyList_viewed`, `client_storyCreate_step_viewed`, `client_storyCreate_completed`, `client_chat_viewed`, `client_chat_messageInput_submitted`, `client_feedback_form_submitted`가 P0 이벤트로 수집된다.
- `device_id`와 `session_id`가 SDK 자동 수집으로 채워지고, 커스텀 프로퍼티로 재정의되지 않는다.
- 같은 사용자 행동에서 Amplitude event, Sentry breadcrumb, 상관 키(`creation_id`, `chat_id`)가 연결된다.
- 채팅 메시지, 피드백 본문, 이메일, 키워드 원문이 이벤트 payload에 없다.
- `client_storyCreate_viewed`부터 `client_storyCreate_completed`까지 스토리 제작 퍼널을 `creation_id`로 계산할 수 있다.
- 채팅 첫 메시지 전송률과 N턴 이상 도달률을 Amplitude에서 계산할 수 있다.
- 이벤트명이 `{platform}_{screenName}(_{objectName})?_{actionType}(_{eventType})?` 형식을 따르고, 프로퍼티는 `snake_case`다.

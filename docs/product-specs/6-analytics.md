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

| 항목 | 값 |
| --- | --- |
| 버전 | v0.10 |
| 작성일 | 2026-06-30 |
| 수정일 | 2026-07-02 |
| 대상 | 마냑 MVP |
| 작성 목적 | MVP 출시 후 사용자가 스토리를 만들고 채팅을 이어가는 흐름을 측정하기 위한 이벤트, 지표, 관측, 검수 기준을 정의합니다. |

## 6-1. 목적과 범위

마냑 MVP 분석의 목적은 사용자가 다음 흐름을 자연스럽게 완료하는지 확인하는 것입니다.

1. 스토리 목록에서 스토리 제작을 시작합니다.
2. 키워드 선택, 스토리라인 선택, 추가 정보 입력을 거쳐 스토리를 완성합니다.
3. 완성한 스토리의 상세 화면에서 채팅을 시작합니다.
4. 채팅에서 첫 메시지를 보내고 여러 턴 동안 이야기를 이어갑니다.
5. 불편하거나 아쉬운 점을 피드백으로 남깁니다.

| 핵심 질문 | 확인 지표 |
| --- | --- |
| 사용자가 스토리 제작을 시작하나요? | 제작 시작률 |
| 제작 중 어디서 막히나요? | 제작 단계별 이탈율, 생성 실패율 |
| 스토리 생성이 채팅으로 이어지나요? | 스토리 상세에서 채팅 시작 전환율 |
| 채팅이 실제 몰입으로 이어지나요? | 첫 메시지 전송률, N턴 이상 도달률 |
| 개선 포인트를 수집하고 있나요? | 피드백 제출률 |

MVP 분석은 스토리 제작과 채팅 활성화에 필요한 최소 신호를 우선 수집합니다. 모든 화면 조작을 계측하지 않고, 퍼널과 운영 장애 분석에 필요한 행동과 처리 결과만 수집합니다.

| 포함 범위 | 설명 | 원본 섹션 |
| --- | --- | --- |
| 사용자 행동 이벤트 | 화면 진입, CTA 클릭, 선택, 제출, 완료 | `6-4. 이벤트 카탈로그` |
| 서버 처리 결과 이벤트 | 스토리 생성, AI 응답, 피드백 제출의 성공과 실패 | `6-4. 이벤트 카탈로그` |
| 핵심 퍼널과 지표 | 제작 퍼널, 채팅 활성화 퍼널, 전체 활성화 퍼널 | `6-5. 퍼널과 지표` |
| 운영 관측 | Sentry, CloudWatch, `ai_call_logs`, 실패 코드 | `6-6. 관측 구현` |
| 릴리스 검수 | P0 이벤트, 식별자, 원문 미수집, 로그 연결 확인 | `6-8. 검수 체크리스트` |

| 제외 범위 | 처리 기준 |
| --- | --- |
| 사용자 입력 원문 분석 | MVP 분석 이벤트와 로그에 원문을 넣지 않습니다. |
| 대시보드 화면 요구사항 | 실제 Amplitude 또는 CloudWatch 대시보드가 정해질 때 별도 문서로 추가합니다. |
| 인증 사용자 분석 | 로그인 기능 도입 후 `user_id`, `identify`, `is_logged_in`을 추가합니다. |
| 실험 분석 | A/B 테스트 도입 후 `experiment_key`, `variant`를 추가합니다. |

## 6-2. 식별자 정책

현재 MVP는 로그인 기능이 없는 전원 게스트 서비스입니다. 사용자 단위는 Amplitude Browser SDK가 자동으로 채우는 `device_id`로 식별합니다.

| 식별자 | 분석 이벤트 타입 | 생성·관리 | 사용처 |
| --- | --- | --- | --- |
| `device_id` | string | Amplitude Browser SDK 자동 수집 | 익명 사용자 단위 분석 |
| `session_id` | number | Amplitude Browser SDK 자동 수집 | 한 번의 방문 흐름 |
| `request_id` | string | 프론트엔드 전달 또는 백엔드 생성 | 서버 로그, Sentry, AI 호출 연결 |
| `device_id_hash` | string | 백엔드가 `device_id`를 해시 | 서버 로그, Sentry, `ai_call_logs` |
| `creation_id` | string | 스토리라인 생성 시 발급되는 `simpleCreationId` | 스토리 제작 시도 연결 |
| `story_id` | string | 스토리 완성 후 서버 발급 | 스토리 관련 이벤트 |
| `chat_id` | string | 채팅 생성 후 서버 발급 | 채팅 관련 이벤트 |
| `ai_call_log_id` | string | AI 호출 기록 생성 시 발급 | 서버 로그와 `ai_call_logs` 연결 |

분석 이벤트에서 `story_id`는 문자열(공개 UUID 식별자)로 보냅니다. CloudWatch 로그·`ai_call_logs`·DB에서도 동일하게 문자열로 저장합니다.

| 키 | 분석 단위 | 사용 |
| --- | --- | --- |
| `device_id` | 익명 사용자 | 전체 활성화 퍼널과 장기 행동 |
| `session_id` | 방문 세션 | 같은 방문 안의 순차 행동 |
| `creation_id` | 스토리 생성 시도 | 제작 퍼널의 생성 성공 이후 구간 |
| `chat_id` | 채팅 세션 | 채팅 활성화와 대화 깊이 |
| `request_id` | API 요청 | 서버 로그, Sentry, AI 호출 상관관계 |

`request_id`는 현재 서버 내부 상관 키입니다. 프론트엔드 `client_*` 이벤트와 백엔드 `server_*` 이벤트를 분석 이벤트 프로퍼티로 직접 연결하는 용도로는 아직 사용하지 않습니다. 현재 제품 퍼널 연결은 `creation_id`와 `chat_id`를 사용합니다.

스토리 생성 요청은 `creation_id`가 발급되기 전에도 발생할 수 있습니다. `client_storyCreate_storyGeneration_requested`는 `device_id`와 `session_id` 순차 기준으로 집계합니다. 백엔드는 스토리라인 생성 처리를 시작할 때 가능한 한 먼저 `creation_id`를 발급하고, 이후 성공·실패 `server_*` 이벤트에는 `creation_id`를 포함합니다. `creation_id` 발급 전의 malformed request는 분석 이벤트가 아니라 CloudWatch 운영 로그로만 추적합니다.

로그인 기능을 도입하면 `device_id`는 유지하고 로그인 시점부터 `user_id`를 추가합니다. Amplitude의 `identify` 또는 `alias` 기능으로 기존 익명 행동과 로그인 사용자를 연결합니다.

## 6-3. 이벤트 네이밍과 공통 프로퍼티

### 6-3-1. 이벤트 원칙

이벤트명은 아래 네이밍 기준을 따릅니다.

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

### 6-3-2. 공통 프로퍼티

각 이벤트 표에는 고유 프로퍼티만 적습니다. 공통 프로퍼티는 적용 범위에 따라 모든 이벤트에 함께 보냅니다.

| property | 타입 | 적용 범위 | 설명 |
| --- | --- | --- | --- |
| `screen_name` | string | 모든 이벤트 | 이벤트가 발생한 화면입니다. 필터와 세그먼트 편의를 위해 프로퍼티로도 보냅니다. |
| `step_name` | string | 스토리 제작 퍼널 | `keyword`, `storylineSelect`, `additionalInfo`, `complete` 중 하나입니다. |
| `step_number` | number | 스토리 제작 퍼널 | 제작 단계 번호입니다. |
| `creation_id` | string | 스토리 제작 퍼널 | 스토리라인 생성 시 발급되는 `simpleCreationId`입니다. |
| `story_id` | string | story 관련 이벤트 | 스토리 식별자입니다. |
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

현재 `request_id`는 서버 내부 상관 키로 사용합니다. 분석 이벤트 프로퍼티로는 아직 보내지 않습니다. 자세한 기준은 `6-6-3. 요청 식별자와 상관관계`를 따릅니다.

## 6-4. 이벤트 카탈로그

### 6-4-1. MVP 우선순위

P0 이벤트는 출시 전에 반드시 수집합니다. P1 이벤트는 P0가 안정적으로 수집된 뒤 추가합니다. P2 이벤트는 세부 인터랙션 계측으로, P1 이후 필요에 따라 추가합니다.

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
| P1 | client | `client_storyCreate_keywordCategory_selected` |
| P1 | client | `client_storyCreate_regenerateButton_clicked` |
| P1 | client | `client_storyCreate_storylineRating_clicked` |
| P1 | client | `client_storyCreate_storyCompletion_requested` |
| P1 | client | `client_storyCreate_completeError_shown` |
| P1 | client | `client_storyCreate_exitButton_clicked` |
| P1 | client | `client_chatList_viewed` |
| P1 | client | `client_chatList_chatCard_clicked` |
| P1 | client | `client_chatList_chatCard_impressed` |
| P1 | client | `client_chat_choiceOption_selected` |
| P1 | client | `client_chat_loadError_shown` |
| P1 | client | `client_chat_retryButton_clicked` |
| P1 | server | `server_feedback_submission_processed_succeeded` |
| P1 | server | `server_feedback_submission_processed_failed` |
| P2 | client | `client_storyCreate_addKeyword_submitted` |
| P2 | client | `client_storyCreate_storylineTab_selected` |
| P2 | client | `client_storyCreate_backToStorylineButton_clicked` |
| P2 | client | `client_storyCreate_recommendedInfo_clicked` |
| P2 | client | `client_storyCreate_additionalInfoAddButton_clicked` |
| P2 | client | `client_storyCreate_additionalInfoRemoveButton_clicked` |

스토리 상세의 추천 스토리 카드(`client_storyDetail_recommendStoryCard_clicked`, `client_storyDetail_recommendStoryCard_impressed`)는 추천 카드 기능 도입 시 P1으로 추가합니다. 기준은 `6-4-2-4. 스토리 상세`를 따릅니다.

### 6-4-2. 페이지별 이벤트 카탈로그

각 이벤트 표에는 공통 프로퍼티를 제외한 고유 프로퍼티만 적습니다. 필수는 `필수`, 선택은 `선택`으로 표기합니다.

#### 6-4-2-1. 온보딩

홈 최초 진입 시 노출되는 환영 다이얼로그입니다. 사용자는 `스토리 만들기` 버튼을 누르기 전까지 다이얼로그를 닫을 수 없고, 다이얼로그는 최초 1회만 노출됩니다.

| 이벤트 | 우선순위 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_onboarding_viewed` | P1 | 환영 다이얼로그 노출 | 없음 |
| `client_onboarding_createButton_clicked` | P1 | 스토리 만들기 버튼 클릭 | 없음 |

#### 6-4-2-2. 스토리 목록

| 이벤트 | 우선순위 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_storyList_viewed` | P0 | 스토리 목록 화면 진입 | 없음 |
| `client_storyList_createButton_clicked` | P0 | 제작하기 CTA 클릭 | `source` (string, 필수: `fab` / `emptyState`) |
| `client_storyList_storyCard_clicked` | P1 | 스토리 카드 클릭 | `story_id` (string, 필수), `position` (number, 선택) |
| `client_storyList_storyCard_impressed` | P1 | 스토리 카드 유효 노출 | `story_id` (string, 필수), `position` (number, 선택) |

제작하기 CTA는 플로팅 버튼과 빈 목록 상태 버튼 두 곳에 있습니다. 버튼 역할이 같으므로 이벤트는 하나로 두고, 어느 CTA에서 제작을 시작했는지는 `source`(`fab`: 플로팅 버튼, `emptyState`: 빈 목록 버튼)로 구분합니다.

#### 6-4-2-3. 스토리 제작

| 이벤트 | 우선순위 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_storyCreate_viewed` | P0 | 제작 화면 진입 | 없음 |
| `client_storyCreate_step_viewed` | P0 | 각 제작 단계 진입 | `step_name` (string, 필수), `step_number` (number, 필수) |
| `client_storyCreate_keywordCategory_selected` | P1 | 키워드 카테고리 이동(장르 → 주인공 → 주변 인물). 다음/이전 버튼·탭·스와이프 공통 | `from_category` (string, 필수), `to_category` (string, 필수), `direction` (string, 필수: `forward` / `backward`) |
| `client_storyCreate_addKeyword_submitted` | P2 | 키워드 직접 추가 제출 | `category` (string, 필수) |
| `client_storyCreate_storyGeneration_requested` | P0 | 스토리라인 생성 요청 전송 | 없음 |
| `server_storyCreate_storyGeneration_processed_succeeded` | P0 | 스토리라인 생성 성공 | `creation_id` (string, 필수) |
| `server_storyCreate_storyGeneration_processed_failed` | P0 | 스토리라인 생성 실패 | `creation_id` (string, 필수), `error_type` (string, 필수) |
| `client_storyCreate_regenerateButton_clicked` | P1 | 스토리라인 다시 만들기 클릭 | `creation_id` (string, 필수) |
| `client_storyCreate_storylineTab_selected` | P2 | 스토리라인 후보 탭 이동 | `creation_id` (string, 필수), `position` (number, 필수) |
| `client_storyCreate_storylineRating_clicked` | P1 | 스토리라인 좋아요/싫어요 클릭 | `storyline_id` (string, 필수), `rating` (string, 필수: `GOOD` / `BAD`), `active` (boolean, 필수) |
| `client_storyCreate_storylineOption_selected` | P0 | 스토리라인 선택 | `creation_id` (string, 필수), `position` (number, 선택) |
| `client_storyCreate_selectedKeywordsButton_clicked` | P0 | 선택한 키워드 보기 버튼 클릭 | `creation_id` (string, 필수) |
| `client_storyCreate_backToStorylineButton_clicked` | P2 | 다시 선택하기(스토리라인 선택으로 되돌아감) 클릭 | 없음 |
| `client_storyCreate_recommendedInfo_clicked` | P2 | AI 추천 추가 정보 칩 클릭 | `selected` (boolean, 필수) |
| `client_storyCreate_additionalInfoAddButton_clicked` | P2 | 추가 정보 입력란 추가 클릭 | 없음 |
| `client_storyCreate_additionalInfoRemoveButton_clicked` | P2 | 추가 정보 입력란 삭제 클릭 | 없음 |
| `client_storyCreate_storyCompletion_requested` | P1 | 스토리 완성 요청 전송 | `creation_id` (string, 필수) |
| `client_storyCreate_completeError_shown` | P1 | 스토리 완성 실패 에러 표시 | `stage` (string, 필수: `story` / `chat`) |
| `client_storyCreate_exitButton_clicked` | P1 | 제작 이탈 확인(나가기) 클릭 | `step_name` (string, 필수), `step_number` (number, 필수) |
| `client_storyCreate_completed` | P0 | 스토리화 완료 | `story_id` (string, 필수), `chat_id` (string, 필수), `genre` (string[], 선택) |

`client_storyCreate_storyGeneration_requested`는 `creation_id` 발급 전 이벤트입니다. `server_storyCreate_storyGeneration_processed_*`는 백엔드가 스토리라인 생성 처리를 시작하며 발급한 `creation_id`를 포함합니다. 이벤트명의 `storyGeneration`은 키워드로 스토리라인 후보를 생성하는 동작(AI feature `storyline_generation`)을 뜻하고, 최종 스토리 완성은 `storyCompletion`(AI feature `story_completion`)으로 구분합니다.

`client_storyCreate_storyCompletion_requested`는 스토리 완성하기 버튼 클릭으로 완성 요청(스토리 생성 또는 실패 후 채팅 생성 재시도)이 실제 전송될 때 발생합니다. 필수 입력이 없어 요청이 전송되지 않는 클릭에는 발생하지 않으며, 완성 실패율(`client_storyCreate_completeError_shown` 대비)의 분모로 사용합니다.

`client_storyCreate_keywordCategory_selected`는 키워드 단계의 세 카테고리(장르·주인공·주변 인물) 사이 이동을 다음/이전 버튼·탭·스와이프 공통으로 한 곳에서 계측합니다. `direction`으로 진행(`forward`)과 되돌아감(`backward`)을 구분하고, 카테고리별 이탈 퍼널은 `from_category` + `direction=forward`로 관찰합니다. `client_storyCreate_completeError_shown`은 클라이언트가 완성 요청 실패로 에러 상태를 표시할 때 발생하며, `stage`로 스토리 생성(`story`)과 채팅 생성(`chat`) 실패를 구분합니다.

`selectedKeywordsButton_clicked`는 스토리라인 선택(`storylineSelect`) 단계 탭 우측의 키워드 보기 버튼으로 선택 키워드 드로워를 열 때 발생합니다. 드로워에 노출되는 키워드 이름은 이벤트에 넣지 않고 `creation_id`만 보냅니다.

제작 단계 `step_name`은 다음 값만 사용합니다.

| step_number | step_name |
| --- | --- |
| `1` | `keyword` |
| `2` | `storylineSelect` |
| `3` | `additionalInfo` |
| `4` | `complete` |

#### 6-4-2-4. 스토리 상세

| 이벤트 | 우선순위 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_storyDetail_viewed` | P0 | 스토리 상세 화면 진입 | `story_id` (string, 필수) |
| `client_storyDetail_chatStartButton_clicked` | P0 | 채팅 시작 버튼 클릭 | `story_id` (string, 필수) |

추천 스토리 카드는 아직 도입되지 않은 기능입니다. 기능 도입 시 `client_storyDetail_recommendStoryCard_clicked`와 `client_storyDetail_recommendStoryCard_impressed`(P1, `story_id` string 필수, `position` number 선택)를 추가합니다. 이때 `story_id`는 현재 보는 스토리가 아니라 추천 카드의 스토리 ID입니다.

#### 6-4-2-5. 채팅 목록

| 이벤트 | 우선순위 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_chatList_viewed` | P1 | 채팅 목록 화면 진입 | 없음 |
| `client_chatList_chatCard_clicked` | P1 | 채팅 카드 클릭 | `chat_id` (string, 필수), `position` (number, 선택) |
| `client_chatList_chatCard_impressed` | P1 | 채팅 카드 유효 노출 | `chat_id` (string, 필수), `position` (number, 선택) |

#### 6-4-2-6. 채팅

| 이벤트 | 우선순위 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_chat_viewed` | P0 | 채팅 화면 진입 | `chat_id` (string, 필수) |
| `client_chat_messageInput_submitted` | P0 | 사용자 메시지 전송 | `chat_id` (string, 필수), `turn_number` (number, 필수) |
| `server_chat_aiMessage_processed_succeeded` | P0 | AI 응답 생성 성공 | `chat_id` (string, 필수), `turn_number` (number, 필수) |
| `server_chat_aiMessage_processed_failed` | P0 | AI 응답 생성 실패 | `chat_id` (string, 필수), `turn_number` (number, 필수), `error_type` (string, 필수) |
| `client_chat_choiceOption_selected` | P1 | 선택지 선택 | `chat_id` (string, 필수), `turn_number` (number, 필수), `position` (number, 선택) |
| `client_chat_loadError_shown` | P1 | 채팅 화면 로드 실패 에러 표시 | `chat_id` (string, 필수) |
| `client_chat_retryButton_clicked` | P1 | 로드 실패 후 다시 시도 버튼 클릭 | `chat_id` (string, 필수) |

`client_chat_loadError_shown`은 채팅 화면 진입 후 대화 내용을 불러오지 못해 에러 상태가 표시될 때 발생합니다. 채팅 진입(`client_chat_viewed`) 대비 로드 실패로 인한 이탈을 구분하는 데 사용합니다. AI 응답 생성 실패는 이 이벤트가 아니라 `server_chat_aiMessage_processed_failed`로 봅니다.

AI 응답 성공·실패는 백엔드가 `server_chat_aiMessage_processed_succeeded` 또는 `server_chat_aiMessage_processed_failed`로 발행합니다. 프론트엔드는 `chat_id`와 `turn_number`로 메시지와 응답을 연결합니다.

#### 6-4-2-7. 피드백

| 이벤트 | 우선순위 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- | --- |
| `client_feedback_viewed` | P0 | 피드백 화면 진입 | 없음 |
| `client_feedback_form_submitted` | P0 | 피드백 제출 버튼 클릭 | 없음 |
| `server_feedback_submission_processed_succeeded` | P1 | 피드백 제출 처리 성공 | 없음 |
| `server_feedback_submission_processed_failed` | P1 | 피드백 제출 처리 실패 | `error_type` (string, 필수) |

server 이벤트의 `error_type`은 `network`, `validation`, `server` 중 하나만 사용합니다. 상세 매핑은 `6-6-7. 서버 분석 이벤트와 실패 타입`을 따릅니다.

### 6-4-3. impression 수집 기준

`impressed`는 특정 item 또는 section이 사용자 화면에 유효하게 노출된 상태를 뜻합니다.

| 항목 | 권장 기준 |
| --- | --- |
| 최소 노출 면적 | 컴포넌트 면적의 50% 이상 |
| 최소 노출 시간 | 1초 이상 |

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

| 분석 단위 | 기준 키 | 사용 지표 |
| --- | --- | --- |
| 익명 사용자 | `device_id` | 방문, 제작 시작, 전체 활성화 |
| 방문 세션 | `session_id` | 같은 방문 안의 화면 흐름 |
| 스토리 생성 시도 | `creation_id` | 생성 성공 후 제작 완료까지의 흐름 |
| 채팅 세션 | `chat_id` | 첫 메시지, 첫 AI 응답, N턴 이상 도달 |
| API 요청 | `request_id` | 서버 로그, Sentry, AI 호출 상관관계 |

`creation_id`가 발급되기 전의 `client_storyCreate_viewed`, `client_storyCreate_storyGeneration_requested`는 `device_id`와 `session_id` 순차 기준으로 봅니다. `creation_id`가 포함된 이벤트부터는 `creation_id`를 고정값으로 둡니다.

### 6-5-3. 핵심 퍼널

#### 6-5-3-1. 스토리 제작 퍼널

키워드 입력부터 스토리 완성까지의 이탈과 생성 성공률을 측정합니다.

| 순서 | 단계 | 이벤트 | 고정값 |
| --- | --- | --- | --- |
| 1 | 제작 진입 | `client_storyCreate_viewed` | device |
| 2 | 생성 요청 | `client_storyCreate_storyGeneration_requested` | device |
| 3 | 생성 성공 | `server_storyCreate_storyGeneration_processed_succeeded` | `creation_id` |
| 4 | 스토리라인 선택 | `client_storyCreate_storylineOption_selected` | `creation_id` |
| 5 | 제작 완료 | `client_storyCreate_completed` | `creation_id` |

화면 단계 이탈은 `client_storyCreate_step_viewed`의 `step_name` 순서(`keyword` -> `storylineSelect` -> `additionalInfo` -> `complete`)로 별도 관찰합니다. 키워드 단계 안의 카테고리별 이탈(장르 -> 주인공 -> 주변 인물)은 `client_storyCreate_keywordCategory_selected`의 `from_category` + `direction=forward`로 관찰합니다. 완성 실패율은 `client_storyCreate_completeError_shown`(`client_storyCreate_storyCompletion_requested` 대비), 완성 성공률은 `client_storyCreate_completed`로 봅니다.

#### 6-5-3-2. 채팅 활성화 퍼널

채팅 진입 후 첫 메시지와 첫 AI 응답까지 도달하는지 측정합니다.

| 순서 | 단계 | 이벤트 | 고정값 |
| --- | --- | --- | --- |
| 1 | 채팅 진입 | `client_chat_viewed` | `chat_id` |
| 2 | 첫 메시지 | `client_chat_messageInput_submitted` where `turn_number = 1` | `chat_id` |
| 3 | 첫 AI 응답 | `server_chat_aiMessage_processed_succeeded` | `chat_id` |

대화 깊이는 퍼널이 아니라 `turn_number` 분포로 봅니다.

#### 6-5-3-3. 전체 활성화 퍼널

방문자가 스토리를 만들고 실제 대화까지 갔는지 측정합니다.

| 순서 | 단계 | 이벤트 | 고정값 |
| --- | --- | --- | --- |
| 1 | 메인 방문 | `client_storyList_viewed` | device |
| 2 | 제작 시작 | `client_storyList_createButton_clicked` | device |
| 3 | 제작 완료 | `client_storyCreate_completed` | device |
| 4 | 첫 메시지 | `client_chat_messageInput_submitted` where `turn_number = 1` | `chat_id` |
| 5 | 첫 AI 응답 | `server_chat_aiMessage_processed_succeeded` | `chat_id` |

3단계 `client_storyCreate_completed`에서 발급된 `chat_id`로 4~5단계를 연결합니다.

### 6-5-4. 핵심 지표

| 영역 | 지표 | 계산식 |
| --- | --- | --- |
| 온보딩 | 제작 시작 전환율 | `client_onboarding_createButton_clicked` 수 / `client_onboarding_viewed` 수 |
| 스토리 목록 | 스토리 카드 클릭률 | `client_storyList_storyCard_clicked` 수 / `client_storyList_storyCard_impressed` 수 |
| 스토리 목록 | 제작 시작률 | `client_storyList_createButton_clicked` 수 / `client_storyList_viewed` 수 |
| 스토리 제작 | 생성 요청률 | `client_storyCreate_storyGeneration_requested` 수 / `client_storyCreate_viewed` 수 |
| 스토리 제작 | 생성 성공률 | `server_storyCreate_storyGeneration_processed_succeeded` 수 / `client_storyCreate_storyGeneration_requested` 수 |
| 스토리 제작 | 생성 실패율 | `server_storyCreate_storyGeneration_processed_failed` 수 / `client_storyCreate_storyGeneration_requested` 수 |
| 스토리 제작 | 생성 후 완료율 | `client_storyCreate_completed` 수 / `server_storyCreate_storyGeneration_processed_succeeded` 수 (`creation_id` 기준) |
| 스토리 제작 | 완성 실패율 | `client_storyCreate_completeError_shown` 수 / `client_storyCreate_storyCompletion_requested` 수 |
| 스토리 제작 | 전체 제작 전환율 | `client_storyCreate_completed` 수 / `client_storyCreate_viewed` 수 |
| 스토리 제작 | 단계별 이탈율 | `1 - 다음 단계 step_viewed 사용자 수 / 현재 단계 step_viewed 사용자 수` |
| 스토리 상세 | 상세에서 채팅 시작 전환율 | `client_storyDetail_chatStartButton_clicked` 수 / `client_storyDetail_viewed` 수 |
| 채팅 목록 | 채팅 카드 클릭률 | `client_chatList_chatCard_clicked` 수 / `client_chatList_chatCard_impressed` 수 |
| 채팅 | 말 거는 비율 | `client_chat_messageInput_submitted` 사용자 수 where `turn_number = 1` / `client_chat_viewed` 사용자 수 |
| 채팅 | AI 응답 성공률 | `server_chat_aiMessage_processed_succeeded` 수 / `client_chat_messageInput_submitted` 수 |
| 채팅 | AI 응답 실패율 | `server_chat_aiMessage_processed_failed` 수 / `client_chat_messageInput_submitted` 수 |
| 채팅 | N턴 이상 도달률 | `turn_number >= N` 채팅 수 / `client_chat_viewed` 채팅 수 |
| 채팅 | 채팅 로드 실패율 | `client_chat_loadError_shown` 수 / `client_chat_viewed` 수 |
| 채팅 | 선택지 사용률 | `client_chat_choiceOption_selected` 수 / `client_chat_messageInput_submitted` 수 |
| 피드백 | 피드백 제출률 | `client_feedback_form_submitted` 사용자 수 / `client_feedback_viewed` 사용자 수 |
| 피드백 | 제출 성공률 | `server_feedback_submission_processed_succeeded` 수 / `client_feedback_form_submitted` 수 |
| 피드백 | 제출 실패율 | `server_feedback_submission_processed_failed` 수 / `client_feedback_form_submitted` 수 |
| 전체 | 방문에서 활성화 전환율 | `server_chat_aiMessage_processed_succeeded` 도달 사용자 수 / `client_storyList_viewed` 사용자 수 |

생성, 응답, 제출 실패 사유는 server 이벤트의 `error_type`(`network`, `validation`, `server`) 분포로 봅니다.

### 6-5-5. 운영 지표

운영 지표는 제품 퍼널 지표가 아니라 장애 분석과 성능 관리에 사용합니다.

| 영역 | 지표 | 계산 기준 |
| --- | --- | --- |
| API | API 실패율 | `api_request_failed` 수 / 전체 API 요청 수 |
| 스토리 생성 | 스토리 생성 서버 실패율 | `story_generation_failed` 수 / `story_generation_requested` 수 |
| AI | AI 호출 성공률 | `ai_call_logs.status = succeeded` 수 / 전체 AI 호출 수 |
| AI | AI 호출 실패율 | `ai_call_logs.status = failed` 수 / 전체 AI 호출 수 |
| AI | 기능별 실패율 | `feature`별 실패 수 / `feature`별 전체 호출 수 |
| AI | p50, p95 latency | `ai_call_logs.latency_ms`의 p50, p95 |
| AI | 평균 입력 토큰 수 | `input_token_count` 평균 |
| AI | 평균 출력 토큰 수 | `output_token_count` 평균 |
| AI | 재시도율 | `retry_count > 0` 호출 수 / 전체 호출 수 |
| 채팅 | 채팅 응답 저장 성공률 | `ai_response_saved` 수 / `user_message_saved` 수 |
| 피드백 | 피드백 제출 성공률 | `feedback_delivery_completed` 수 / 피드백 제출 API 요청 수 |

CloudWatch 이벤트와 `ai_call_logs` 기록 기준은 `6-6. 관측 구현`을 따릅니다.

### 6-5-6. 계산 주의사항

`server_storyCreate_storyGeneration_processed_failed`는 `creation_id`가 발급된 스토리 생성 처리 실패만 포함합니다. 요청 형식 자체가 깨져 `creation_id`를 만들 수 없는 malformed request는 CloudWatch의 `api_request_failed`로만 추적합니다.

`client_chat_messageInput_submitted`는 사용자 메시지 전송 시점입니다. AI 응답 성공 여부는 `server_chat_aiMessage_processed_succeeded`로 판단합니다. 사용자가 메시지를 보냈지만 AI 응답이 실패한 경우 말 거는 비율에는 포함되고 AI 응답 성공률에는 포함되지 않습니다.

`client_chat_choiceOption_selected`는 선택지 사용 행동입니다. 선택지가 표시된 횟수 대비 선택률은 MVP 범위에 포함하지 않습니다. MVP에서는 메시지 전송 수 대비 선택지 선택 수로 선택지 사용률을 봅니다.

## 6-6. 관측 구현

### 6-6-1. 도구별 역할

| 도구 | 역할 | MVP 적용 범위 |
| --- | --- | --- |
| Amplitude | 사용자 행동 분석 | 퍼널, 전환율, 이탈율, 선택지 사용률 |
| 브라우저 Sentry | 프론트엔드 오류 분석 | 렌더링 오류, 라우트 오류, API 실패, 사용자 행동 breadcrumb |
| 서버 분석 이벤트 | 퍼널 결과 계측 | 생성 성공·실패, AI 응답 성공·실패, 피드백 제출 성공·실패 |
| 서버 Sentry | 백엔드 예외 분석 | API 예외, AI 호출 실패, DB 오류, 외부 연동 실패 |
| CloudWatch | 운영 로그와 지표 | API 요청 로그, 주요 비즈니스 이벤트, latency, status |
| AI Sentry | AI 서비스 오류 분석 | provider 오류, timeout, 파싱 실패, schema 검증 실패 |
| `ai_call_logs` | AI 호출 이력 | 스토리라인 생성, 스토리 생성, 채팅 응답, 추천 입력 생성 |

Amplitude 이벤트 수를 제품 지표 계산의 기준으로 사용합니다. Sentry 이벤트 수는 제품 지표 계산에 사용하지 않습니다.

### 6-6-2. 프론트엔드 API 헤더

프론트엔드는 백엔드 API를 호출할 때 익명 사용자와 세션 식별자를 HTTP 헤더로 함께 보냅니다.

| 헤더 | 필수 여부 | 값 | 설명 |
| --- | --- | --- | --- |
| `X-Manyak-Device-Id` | 필수 | `device_id` | Amplitude SDK가 채운 익명 사용자 ID입니다. |
| `X-Manyak-Session-Id` | 필수 | `session_id` | Amplitude SDK가 채운 세션 ID입니다. |
| `X-Manyak-Request-Id` | 권장 | `request_id` | 요청 단위 ID입니다. 없으면 백엔드가 생성합니다. |

프론트엔드는 `device_id` 원본 값을 헤더에 싣습니다. 백엔드는 저장 전 `device_id_hash`로 변환합니다. 프론트엔드는 별도 해시를 만들지 않습니다.

### 6-6-3. 요청 식별자와 상관관계

백엔드는 모든 서버 분석 이벤트, CloudWatch 로그, Sentry scope, AI 호출 요청에 다음 값을 가능한 범위에서 포함합니다.

| 필드 | 설명 |
| --- | --- |
| `request_id` | API 요청과 AI 호출을 연결하는 서버 내부 상관 ID입니다. |
| `device_id_hash` | 익명 `device_id`를 해시한 값입니다. |
| `session_id` | 프론트엔드 세션 ID입니다. |
| `creation_id` | 스토리 생성 시도 ID입니다. |
| `story_id` | 스토리 ID입니다. |
| `chat_id` | 채팅 ID입니다. |
| `turn_number` | 사용자 메시지 기준 턴 번호입니다. |
| `ai_call_log_id` | AI 호출 로그 행 ID입니다. |

`request_id`는 서버 로그, Sentry, `ai_call_logs`를 잇는 서버 내부 상관 키입니다. 프론트엔드 `client_*` 이벤트와 백엔드 `server_*` 이벤트를 제품 분석에서 연결할 때는 현재 `creation_id`와 `chat_id`를 사용합니다.

### 6-6-4. 프론트엔드 Sentry 기준

프론트엔드 Sentry에는 오류 분석에 필요한 최소 context만 넣습니다.

| 구분 | 수집 내용 |
| --- | --- |
| Tags | `screen_name`, `story_id`, `chat_id`, `creation_id` |
| User | `id: device_id`, `ip_address: "{{auto}}"` |
| Breadcrumb | P0 행동 이벤트 이름, 주요 API 요청 시작과 종료 |
| Exceptions | 렌더링 오류, 라우트 오류, API 네트워크 오류, 예상하지 못한 5xx 응답 |

4xx 응답이 사용자가 복구할 수 있는 검증 오류라면 Sentry exception으로 보내지 않습니다. 사용자 행동 분석이 필요하면 Amplitude 이벤트로만 기록합니다. 서버 사이드 상관 키 `request_id`를 브라우저 Sentry Tags에 추가하는 것은 추후 도입 항목입니다.

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

| 이벤트 | 발생 시점 | 핵심 필드 |
| --- | --- | --- |
| `api_request_completed` | API 요청 정상 종료 | `endpoint`, `http_method`, `status_code`, `duration_ms` |
| `api_request_failed` | API 요청 실패 | `endpoint`, `http_method`, `status_code`, `duration_ms`, `error_code` |
| `story_generation_requested` | 스토리라인 생성 API 요청 수신 | `request_id`, `session_id` |
| `story_generated` | 스토리라인 생성 완료 | `creation_id`, `duration_ms` |
| `story_generation_failed` | 스토리라인 생성 실패 | `creation_id`, `error_code`, `duration_ms` |
| `story_created` | 스토리 저장 완료 | `story_id`, `chat_id`, `duration_ms` |
| `user_message_saved` | 사용자 메시지 저장 완료 | `chat_id`, `story_id`, `turn_number` |
| `ai_response_saved` | AI 응답 저장 완료 | `chat_id`, `story_id`, `turn_number`, `ai_call_log_id` |
| `feedback_delivery_completed` | 피드백 저장 또는 전달 완료 | `has_email` |

### 6-6-6. 백엔드 Sentry 기준

백엔드는 예상하지 못한 장애와 운영자가 확인해야 하는 실패만 Sentry에 보냅니다.

| 구분 | 수집 내용 |
| --- | --- |
| Tags | `endpoint`, `http_method`, `status_code`, `error_code`, `creation_id`, `story_id`, `chat_id`, `request_id` |
| Context | `session_id`, `device_id_hash`, `feature`, `duration_ms`, `ai_call_log_id` |
| Breadcrumb | API 요청 시작, DB 저장 완료, AI 호출 시작과 종료 |
| Exceptions | 5xx 예외, DB 예외, AI 호출 timeout, AI 응답 검증 실패, Slack 피드백 webhook 실패 |

사용자 입력 검증 실패처럼 예상 가능한 4xx 오류는 기본적으로 Sentry exception으로 보내지 않습니다. 같은 4xx 오류가 짧은 시간에 반복되어 운영 문제가 의심될 때만 warning 수준의 CloudWatch 로그로 확인합니다.

### 6-6-7. 서버 분석 이벤트와 실패 타입

서버 분석 이벤트의 전체 목록은 `6-4-2. 페이지별 이벤트 카탈로그`에 있습니다. 백엔드는 퍼널의 결과 단계를 채우는 `server_*` 분석 이벤트를 발행합니다.

`error_type`은 사용자·퍼널 분석용 거친 분류이며 `network`, `validation`, `server`만 사용합니다. 내부 상세 실패 코드(`ai_call_logs.error_code`)는 다음 기준으로 `error_type`에 매핑합니다.

| error_type | 의미 | 매핑되는 내부 error_code |
| --- | --- | --- |
| `network` | 네트워크, 연결, timeout 실패 | `provider_timeout`, `provider_unavailable` |
| `validation` | 입력값, 응답 검증, 안전 정책 실패 | `provider_bad_request`, `schema_validation_failed`, `invalid_ai_response`, `content_filter_blocked` |
| `server` | 서버 내부 처리 실패 | `provider_rate_limited`, `unexpected_error` |

### 6-6-8. AI 기능과 요청 context

MVP에서 분석 대상이 되는 AI 기능은 다음 네 가지입니다.

| feature | 설명 | 사용자 퍼널 연결 |
| --- | --- | --- |
| `storyline_generation` | 선택 키워드로 스토리라인 후보 생성 | `client_storyCreate_storyGeneration_requested`, `server_storyCreate_storyGeneration_processed_*` |
| `story_completion` | 선택 스토리라인과 추가 정보로 스토리 상세 생성 | `client_storyCreate_storyCompletion_requested`, `client_storyCreate_completed` |
| `chat_response` | 사용자 메시지에 대한 AI 응답 생성 | `client_chat_messageInput_submitted`, `server_chat_aiMessage_processed_*` |
| `suggestion_generation` | 다음 입력 추천 선택지 생성 | `client_chat_choiceOption_selected` |

AI feature는 프론트엔드 이벤트명에 넣지 않습니다. 상세 원인은 `feature`와 `error_code`로 구분합니다.

백엔드는 AI 서비스 호출 시 다음 값을 전달합니다. AI 서비스는 값을 그대로 로그, Sentry scope, `ai_call_logs`에 연결합니다.

| 필드 | 필수 여부 | 설명 |
| --- | --- | --- |
| `request_id` | 필수 | 백엔드와 AI 로그를 연결하는 서버 내부 상관 ID입니다. |
| `device_id_hash` | 필수 | 익명 `device_id` 해시입니다. |
| `session_id` | 필수 | 프론트엔드 세션 ID입니다. |
| `feature` | 필수 | AI 기능명입니다. |
| `prompt_template_version` | 필수 | 프롬프트 템플릿 버전입니다. |
| `creation_id` | 조건부 | 스토리라인 생성과 스토리 완성 시 필수입니다. |
| `story_id` | 조건부 | 스토리 완성 후 또는 채팅 중 필수입니다. |
| `chat_id` | 조건부 | 채팅 응답 생성 시 필수입니다. |
| `turn_number` | 조건부 | 채팅 응답 생성 시 필수입니다. |

AI 서비스 응답에는 다음 메타데이터를 포함합니다.

| 필드 | 설명 |
| --- | --- |
| `ai_call_log_id` | `ai_call_logs` 행 ID입니다. |
| `model` | 사용 모델입니다. |
| `latency_ms` | AI 호출 소요 시간입니다. |
| `input_token_count` | 입력 토큰 수입니다. |
| `output_token_count` | 출력 토큰 수입니다. |
| `error_code` | 실패 시 오류 코드입니다. |

### 6-6-9. `ai_call_logs` 기록 기준

AI 호출 1회당 `ai_call_logs`에 1행을 기록합니다. 재시도가 발생하면 같은 `request_id` 아래에서 `retry_count`를 증가시킵니다. 여러 모델을 순차 호출하는 기능이 생기면 provider 호출별로 행을 분리합니다.

| 컬럼 | 타입 예시 | 설명 |
| --- | --- | --- |
| `id` | UUID | AI 호출 로그 ID입니다. |
| `request_id` | VARCHAR | API 요청과 연결되는 ID입니다. |
| `caller_service` | VARCHAR | 호출 서비스입니다. MVP 값은 `manyak-server`입니다. |
| `feature` | VARCHAR | AI 기능명입니다. |
| `device_id_hash` | VARCHAR | 익명 `device_id` 해시입니다. |
| `session_id` | VARCHAR | 세션 ID입니다. |
| `creation_id` | VARCHAR NULL | 스토리 생성 시도 ID입니다. |
| `story_id` | VARCHAR NULL | 연결된 스토리 ID입니다. |
| `chat_id` | VARCHAR NULL | 연결된 채팅 ID입니다. |
| `turn_number` | INTEGER NULL | 사용자 메시지 기준 턴 번호입니다. |
| `provider` | VARCHAR | AI provider입니다. |
| `model` | VARCHAR | 모델명입니다. |
| `prompt_template_version` | VARCHAR | 프롬프트 템플릿 버전입니다. |
| `status` | VARCHAR | `started`, `succeeded`, `failed` 중 하나입니다. |
| `latency_ms` | INTEGER | AI 호출 소요 시간입니다. |
| `input_token_count` | INTEGER NULL | 입력 토큰 수입니다. |
| `output_token_count` | INTEGER NULL | 출력 토큰 수입니다. |
| `retry_count` | INTEGER | 재시도 횟수입니다. |
| `error_code` | VARCHAR NULL | 내부 실패 코드입니다. |
| `sentry_event_id` | VARCHAR NULL | Sentry 이벤트 ID입니다. |
| `created_at` | TIMESTAMP | 생성 시각입니다. |
| `completed_at` | TIMESTAMP NULL | 완료 시각입니다. |

실패 코드는 적게 유지합니다.

| error_code | 의미 | error_type |
| --- | --- | --- |
| `provider_timeout` | provider 응답 시간 초과 | `network` |
| `provider_rate_limited` | provider rate limit | `server` |
| `provider_bad_request` | provider 요청 거부 | `validation` |
| `provider_unavailable` | provider 장애 또는 일시적 연결 실패 | `network` |
| `invalid_ai_response` | 응답이 서비스 기대 형식과 다름 | `validation` |
| `schema_validation_failed` | Pydantic 또는 응답 schema 검증 실패 | `validation` |
| `content_filter_blocked` | 안전 정책 또는 필터에 의해 차단 | `validation` |
| `unexpected_error` | 분류되지 않은 예외 | `server` |

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

| 이벤트 | 발생 시점 | 핵심 필드 |
| --- | --- | --- |
| `ai_call_started` | provider 호출 직전 | `feature`, `request_id`, `prompt_template_version`, `model` |
| `ai_call_completed` | provider 호출과 응답 검증 성공 | `feature`, `ai_call_log_id`, `latency_ms`, `input_token_count`, `output_token_count` |
| `ai_call_failed` | provider 호출 또는 응답 검증 실패 | `feature`, `ai_call_log_id`, `latency_ms`, `error_code`, `retry_count` |
| `ai_response_validation_failed` | 응답 schema 검증 실패 | `feature`, `error_code`, `prompt_template_version` |

| 구분 | 수집 내용 |
| --- | --- |
| Tags | `feature`, `provider`, `model`, `prompt_template_version`, `error_code`, `request_id` |
| Context | `ai_call_log_id`, `session_id`, `device_id_hash`, `creation_id`, `story_id`, `chat_id`, `turn_number`, `latency_ms`, `retry_count` |
| Breadcrumb | AI 호출 시작, provider 응답 수신, schema 검증, DB 기록 |
| Exceptions | timeout, provider 오류, 파싱 실패, schema 검증 실패, 예상하지 못한 예외 |

## 6-7. 개인정보와 원문 수집 원칙

MVP 분석 이벤트, CloudWatch 로그, Sentry context, `ai_call_logs`에는 사용자가 입력한 원문을 직접 넣지 않습니다.

| 데이터 | 분석 이벤트 | 운영 로그와 Sentry | 대체 값 |
| --- | --- | --- | --- |
| 채팅 메시지 원문 | 수집하지 않음 | 저장 금지 | `turn_number`, token count |
| 피드백 본문 | 수집하지 않음 | 로그 저장 금지 | 저장 또는 전달 성공 여부, 본문 길이 |
| 이메일 | 수집하지 않음 | 로그 저장 금지 | `has_email` |
| 키워드·추가 정보 원문 | 수집하지 않음 | 저장 금지 | 관리되는 ID 또는 선택값 |
| 프롬프트 전문 | 수집하지 않음 | 저장 금지 | `prompt_template_version` |
| AI 생성 결과 원문 | 수집하지 않음 | 저장 금지 | 응답 성공 여부, token count |

원문 디버깅이 필요하면 별도 보안 정책과 제한된 저장소를 먼저 정의한 뒤 사용합니다. 이 문서의 MVP 분석 범위에는 원문 저장소를 포함하지 않습니다.

## 6-8. 검수 체크리스트

### 6-8-1. 검수 원칙

검수는 "이벤트가 발생한다"에서 끝나지 않습니다. 이벤트명, 프로퍼티 타입, 식별자 연결, 지표 계산 가능성, 원문 미수집까지 함께 확인합니다.

| 원칙 | 확인 방법 |
| --- | --- |
| P0 이벤트 우선 | 출시 전에는 `6-4-1. MVP 우선순위`의 P0 이벤트를 모두 확인합니다. |
| 원본 섹션 기준 | 이벤트는 `6-4. 이벤트 카탈로그`, 지표는 `6-5. 퍼널과 지표`, 관측 구현은 `6-6. 관측 구현`을 기준으로 확인합니다. |
| 식별자 연결 확인 | `device_id`, `session_id`, `creation_id`, `chat_id`, `request_id`, `ai_call_log_id`가 각 계층에서 이어지는지 봅니다. |
| 원문 수집 금지 | 채팅, 피드백, 이메일, 키워드, 프롬프트, AI 생성 결과 원문이 payload에 없는지 확인합니다. |

### 6-8-2. 문서 변경 체크리스트

분석 스펙을 변경할 때는 다음 항목을 확인합니다.

- 새 이벤트를 추가하면 `6-4. 이벤트 카탈로그`에 이벤트명, 발생 시점, 고유 프로퍼티, 우선순위를 추가합니다.
- 새 이벤트가 지표에 쓰이면 `6-5. 퍼널과 지표`에 계산식과 집계 단위를 추가합니다.
- 새 이벤트가 Sentry breadcrumb 또는 CloudWatch 로그와 연결되면 `6-6. 관측 구현`에 연결 기준을 추가합니다.
- P0 이벤트가 바뀌면 이 문서의 출시 전 P0 체크리스트를 업데이트합니다.
- 원문 수집 가능성이 있는 프로퍼티를 추가하면 `6-7. 개인정보와 원문 수집 원칙`과 `6-8-5. 개인정보 검수 기준`을 함께 확인합니다.
- 같은 표를 여러 섹션에 복사하지 않고 원본 섹션을 참조합니다.

### 6-8-3. 출시 전 P0 체크리스트

| 영역 | 체크 항목 |
| --- | --- |
| 이벤트 수집 | `client_storyList_viewed`, `client_storyList_createButton_clicked`가 Amplitude에서 수집됩니다. |
| 이벤트 수집 | `client_storyCreate_viewed`, `client_storyCreate_step_viewed`, `client_storyCreate_storyGeneration_requested`가 수집됩니다. |
| 이벤트 수집 | `server_storyCreate_storyGeneration_processed_succeeded`, `server_storyCreate_storyGeneration_processed_failed`가 수집됩니다. |
| 이벤트 수집 | `client_storyCreate_storylineOption_selected`, `client_storyCreate_selectedKeywordsButton_clicked`, `client_storyCreate_completed`가 수집됩니다. |
| 이벤트 수집 | `client_storyDetail_viewed`, `client_storyDetail_chatStartButton_clicked`가 수집됩니다. |
| 이벤트 수집 | `client_chat_viewed`, `client_chat_messageInput_submitted`가 수집됩니다. |
| 이벤트 수집 | `server_chat_aiMessage_processed_succeeded`, `server_chat_aiMessage_processed_failed`가 수집됩니다. |
| 이벤트 수집 | `client_feedback_viewed`, `client_feedback_form_submitted`가 수집됩니다. |
| 식별자 | `device_id`와 `session_id`가 SDK 자동 수집으로 채워지고 커스텀 프로퍼티로 재정의되지 않습니다. |
| 식별자 | 스토리 제작 퍼널을 `creation_id`로 계산할 수 있습니다. |
| 식별자 | 채팅 첫 메시지와 AI 응답을 `chat_id`, `turn_number`로 연결할 수 있습니다. |
| 로그 연결 | 서버 로그, Sentry, `ai_call_logs`를 `request_id`로 연결할 수 있습니다. |
| 개인정보 | 채팅 메시지, 피드백 본문, 이메일, 키워드 원문, 프롬프트 전문이 payload에 없습니다. |

### 6-8-4. 계층별 검수 기준

#### 6-8-4-1. 프론트엔드

- Amplitude 디버그 모드에서 P0 `client_*` 이벤트가 한 번씩 발생합니다.
- 이벤트명이 `{platform}_{screenName}(_{objectName})?_{actionType}(_{eventType})?` 형식을 따릅니다.
- 프로퍼티는 `snake_case`로 전송합니다.
- 같은 사용자 행동에서 Amplitude event, Sentry breadcrumb, 상관 키(`creation_id`, `chat_id`)가 연결됩니다.
- API 요청 헤더에 `X-Manyak-Device-Id`, `X-Manyak-Session-Id`가 포함됩니다.
- `X-Manyak-Request-Id`가 없을 때 백엔드가 `request_id`를 생성합니다.

#### 6-8-4-2. 백엔드

- 모든 API 로그에 `request_id`, `session_id`, `device_id_hash`가 있습니다.
- 생성, AI 응답, 피드백 결과가 `server_*` 분석 이벤트로 발행됩니다.
- `server_*` 이벤트가 `creation_id` 또는 `chat_id`로 client 이벤트와 연결됩니다.
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

| 데이터 | 확인 기준 |
| --- | --- |
| 채팅 메시지 원문 | Amplitude, CloudWatch, Sentry, `ai_call_logs` payload에 없습니다. |
| 피드백 본문 | 분석 이벤트와 로그 payload에 없습니다. |
| 이메일 | 분석 이벤트와 로그 payload에 없습니다. `has_email`만 허용합니다. |
| 키워드·추가 정보 원문 | 관리되는 ID 또는 선택값만 허용합니다. |
| 프롬프트 전문 | CloudWatch, Sentry, `ai_call_logs`에 없습니다. |
| AI 생성 결과 원문 | CloudWatch, Sentry, `ai_call_logs`에 없습니다. |
| 익명 ID | 서버 계층에는 원본 `device_id`가 없고 `device_id_hash`만 있습니다. |

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

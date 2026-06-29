# AN-3-ANALYTICS-METRICS

이 문서는 마냑 MVP의 퍼널과 핵심 지표 계산식을 정의합니다. 지표는 [`events.md`](./events.md)에 정의된 이벤트만으로 계산합니다.

```text
§AN-3-1  지표 원칙
§AN-3-2  분석 단위
§AN-3-3  핵심 퍼널
§AN-3-4  핵심 지표
§AN-3-5  운영 지표
§AN-3-6  계산 주의사항
```

| 항목 | 값 |
| --- | --- |
| 버전 | v0.8 |
| 작성일 | 2026-06-30 |
| 대상 | 마냑 MVP 퍼널과 지표 |
| 관련 문서 | [`analytics-spec.md`](./analytics-spec.md), [`events.md`](./events.md), [`observability.md`](./observability.md), [`qa.md`](./qa.md) |

## AN-3-1 지표 원칙

MVP 지표는 사용자가 스토리를 만들고 채팅을 이어가는지 확인하는 데 집중합니다. 지표 계산의 기준 데이터는 Amplitude 이벤트입니다. 장애 원인, latency, token count, AI 실패 코드는 CloudWatch와 `ai_call_logs`로 보조 분석합니다.

같은 지표를 여러 방식으로 계산하지 않습니다. 지표 이름, 계산식, 집계 단위, 제외 조건은 이 문서를 원본으로 삼습니다.

## AN-3-2 분석 단위

| 분석 단위 | 기준 키 | 사용 지표 |
| --- | --- | --- |
| 익명 사용자 | `device_id` | 방문, 제작 시작, 전체 활성화 |
| 방문 세션 | `session_id` | 같은 방문 안의 화면 흐름 |
| 스토리 생성 시도 | `creation_id` | 생성 성공 후 제작 완료까지의 흐름 |
| 채팅 세션 | `chat_id` | 첫 메시지, 첫 AI 응답, N턴 이상 도달 |
| API 요청 | `request_id` | 서버 로그, Sentry, AI 호출 상관관계 |

`creation_id`가 발급되기 전의 `client_storyCreate_viewed`, `client_storyCreate_storyGeneration_requested`는 `device_id`와 `session_id` 순차 기준으로 봅니다. `creation_id`가 포함된 이벤트부터는 `creation_id`를 고정값으로 둡니다.

## AN-3-3 핵심 퍼널

### AN-3-3-1 스토리 제작 퍼널

키워드 입력부터 스토리 완성까지의 이탈과 생성 성공률을 측정합니다.

| 순서 | 단계 | 이벤트 | 고정값 |
| --- | --- | --- | --- |
| 1 | 제작 진입 | `client_storyCreate_viewed` | device |
| 2 | 생성 요청 | `client_storyCreate_storyGeneration_requested` | device |
| 3 | 생성 성공 | `server_storyCreate_storyGeneration_processed_succeeded` | `creation_id` |
| 4 | 스토리라인 선택 | `client_storyCreate_storylineOption_selected` | `creation_id` |
| 5 | 제작 완료 | `client_storyCreate_completed` | `creation_id` |

화면 단계 이탈은 `client_storyCreate_step_viewed`의 `step_name` 순서(`keyword` -> `storylineSelect` -> `additionalInfo` -> `complete`)로 별도 관찰합니다.

### AN-3-3-2 채팅 활성화 퍼널

채팅 진입 후 첫 메시지와 첫 AI 응답까지 도달하는지 측정합니다.

| 순서 | 단계 | 이벤트 | 고정값 |
| --- | --- | --- | --- |
| 1 | 채팅 진입 | `client_chat_viewed` | `chat_id` |
| 2 | 첫 메시지 | `client_chat_messageInput_submitted` where `turn_number = 1` | `chat_id` |
| 3 | 첫 AI 응답 | `server_chat_aiMessage_processed_succeeded` | `chat_id` |

대화 깊이는 퍼널이 아니라 `turn_number` 분포로 봅니다.

### AN-3-3-3 전체 활성화 퍼널

방문자가 스토리를 만들고 실제 대화까지 갔는지 측정합니다.

| 순서 | 단계 | 이벤트 | 고정값 |
| --- | --- | --- | --- |
| 1 | 메인 방문 | `client_storyList_viewed` | device |
| 2 | 제작 시작 | `client_storyList_createButton_clicked` | device |
| 3 | 제작 완료 | `client_storyCreate_completed` | device |
| 4 | 첫 메시지 | `client_chat_messageInput_submitted` where `turn_number = 1` | `chat_id` |
| 5 | 첫 AI 응답 | `server_chat_aiMessage_processed_succeeded` | `chat_id` |

3단계 `client_storyCreate_completed`에서 발급된 `chat_id`로 4~5단계를 연결합니다.

## AN-3-4 핵심 지표

| 영역 | 지표 | 계산식 |
| --- | --- | --- |
| 온보딩 | 제작 시작 전환율 | `client_onboarding_createButton_clicked` 수 / `client_onboarding_viewed` 수 |
| 스토리 목록 | 스토리 카드 클릭률 | `client_storyList_storyCard_clicked` 수 / `client_storyList_storyCard_impressed` 수 |
| 스토리 목록 | 제작 시작률 | `client_storyList_createButton_clicked` 수 / `client_storyList_viewed` 수 |
| 스토리 제작 | 생성 요청률 | `client_storyCreate_storyGeneration_requested` 수 / `client_storyCreate_viewed` 수 |
| 스토리 제작 | 생성 성공률 | `server_storyCreate_storyGeneration_processed_succeeded` 수 / `client_storyCreate_storyGeneration_requested` 수 |
| 스토리 제작 | 생성 실패율 | `server_storyCreate_storyGeneration_processed_failed` 수 / `client_storyCreate_storyGeneration_requested` 수 |
| 스토리 제작 | 생성 후 완료율 | `client_storyCreate_completed` 수 / `server_storyCreate_storyGeneration_processed_succeeded` 수 (`creation_id` 기준) |
| 스토리 제작 | 전체 제작 전환율 | `client_storyCreate_completed` 수 / `client_storyCreate_viewed` 수 |
| 스토리 제작 | 단계별 이탈율 | `1 - 다음 단계 step_viewed 사용자 수 / 현재 단계 step_viewed 사용자 수` |
| 스토리 상세 | 상세에서 채팅 시작 전환율 | `client_storyDetail_chatStartButton_clicked` 수 / `client_storyDetail_viewed` 수 |
| 스토리 상세 | 추천 카드 클릭률 | `client_storyDetail_recommendStoryCard_clicked` 수 / `client_storyDetail_recommendStoryCard_impressed` 수 |
| 채팅 목록 | 채팅 카드 클릭률 | `client_chatList_chatCard_clicked` 수 / `client_chatList_chatCard_impressed` 수 |
| 채팅 | 말 거는 비율 | `client_chat_messageInput_submitted` 사용자 수 where `turn_number = 1` / `client_chat_viewed` 사용자 수 |
| 채팅 | AI 응답 성공률 | `server_chat_aiMessage_processed_succeeded` 수 / `client_chat_messageInput_submitted` 수 |
| 채팅 | AI 응답 실패율 | `server_chat_aiMessage_processed_failed` 수 / `client_chat_messageInput_submitted` 수 |
| 채팅 | N턴 이상 도달률 | `turn_number >= N` 채팅 수 / `client_chat_viewed` 채팅 수 |
| 채팅 | 선택지 사용률 | `client_chat_choiceOption_selected` 수 / `client_chat_messageInput_submitted` 수 |
| 피드백 | 피드백 제출률 | `client_feedback_form_submitted` 사용자 수 / `client_feedback_viewed` 사용자 수 |
| 피드백 | 제출 성공률 | `server_feedback_submission_processed_succeeded` 수 / `client_feedback_form_submitted` 수 |
| 피드백 | 제출 실패율 | `server_feedback_submission_processed_failed` 수 / `client_feedback_form_submitted` 수 |
| 전체 | 방문에서 활성화 전환율 | `server_chat_aiMessage_processed_succeeded` 도달 사용자 수 / `client_storyList_viewed` 사용자 수 |

생성, 응답, 제출 실패 사유는 server 이벤트의 `error_type`(`network`, `validation`, `server`) 분포로 봅니다.

## AN-3-5 운영 지표

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

CloudWatch 이벤트와 `ai_call_logs` 기록 기준은 [`observability.md`](./observability.md)를 따릅니다.

## AN-3-6 계산 주의사항

`server_storyCreate_storyGeneration_processed_failed`는 `creation_id`가 발급된 스토리 생성 처리 실패만 포함합니다. 요청 형식 자체가 깨져 `creation_id`를 만들 수 없는 malformed request는 CloudWatch의 `api_request_failed`로만 추적합니다.

`client_chat_messageInput_submitted`는 사용자 메시지 전송 시점입니다. AI 응답 성공 여부는 `server_chat_aiMessage_processed_succeeded`로 판단합니다. 사용자가 메시지를 보냈지만 AI 응답이 실패한 경우 말 거는 비율에는 포함되고 AI 응답 성공률에는 포함되지 않습니다.

`client_chat_choiceOption_selected`는 선택지 사용 행동입니다. 선택지가 표시된 횟수 대비 선택률은 MVP 범위에 포함하지 않습니다. MVP에서는 메시지 전송 수 대비 선택지 선택 수로 선택지 사용률을 봅니다.

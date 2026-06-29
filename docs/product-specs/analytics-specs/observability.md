# AN-4-ANALYTICS-OBSERVABILITY

이 문서는 마냑 MVP의 분석 관측 구현 계약을 정의합니다. Amplitude, Sentry, CloudWatch, `ai_call_logs`, `request_id`, 실패 코드는 이 문서에서 관리합니다.

```text
§AN-4-1  도구별 역할
§AN-4-2  프론트엔드 API 헤더
§AN-4-3  요청 식별자와 상관관계
§AN-4-4  프론트엔드 Sentry 기준
§AN-4-5  백엔드 CloudWatch 로그
§AN-4-6  백엔드 Sentry 기준
§AN-4-7  서버 분석 이벤트와 실패 타입
§AN-4-8  AI 기능과 요청 context
§AN-4-9  ai_call_logs 기록 기준
§AN-4-10 AI CloudWatch와 Sentry 기준
§AN-4-11 개인정보 원칙
```

| 항목 | 값 |
| --- | --- |
| 버전 | v0.8 |
| 작성일 | 2026-06-30 |
| 대상 | 마냑 MVP 관측 구현 |
| 관련 문서 | [`analytics-spec.md`](./analytics-spec.md), [`events.md`](./events.md), [`metrics.md`](./metrics.md), [`qa.md`](./qa.md) |

## AN-4-1 도구별 역할

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

## AN-4-2 프론트엔드 API 헤더

프론트엔드는 백엔드 API를 호출할 때 익명 사용자와 세션 식별자를 HTTP 헤더로 함께 보냅니다.

| 헤더 | 필수 여부 | 값 | 설명 |
| --- | --- | --- | --- |
| `X-Manyak-Device-Id` | 필수 | `device_id` | Amplitude SDK가 채운 익명 사용자 ID입니다. |
| `X-Manyak-Session-Id` | 필수 | `session_id` | Amplitude SDK가 채운 세션 ID입니다. |
| `X-Manyak-Request-Id` | 권장 | `request_id` | 요청 단위 ID입니다. 없으면 백엔드가 생성합니다. |

프론트엔드는 `device_id` 원본 값을 헤더에 싣습니다. 백엔드는 저장 전 `device_id_hash`로 변환합니다. 프론트엔드는 별도 해시를 만들지 않습니다.

## AN-4-3 요청 식별자와 상관관계

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

## AN-4-4 프론트엔드 Sentry 기준

프론트엔드 Sentry에는 오류 분석에 필요한 최소 context만 넣습니다.

| 구분 | 수집 내용 |
| --- | --- |
| Tags | `screen_name`, `story_id`, `chat_id`, `creation_id` |
| User | `id: device_id`, `ip_address: "{{auto}}"` |
| Breadcrumb | P0 행동 이벤트 이름, 주요 API 요청 시작과 종료 |
| Exceptions | 렌더링 오류, 라우트 오류, API 네트워크 오류, 예상하지 못한 5xx 응답 |

4xx 응답이 사용자가 복구할 수 있는 검증 오류라면 Sentry exception으로 보내지 않습니다. 사용자 행동 분석이 필요하면 Amplitude 이벤트로만 기록합니다. 서버 사이드 상관 키 `request_id`를 브라우저 Sentry Tags에 추가하는 것은 추후 도입 항목입니다.

## AN-4-5 백엔드 CloudWatch 로그

모든 백엔드 로그는 JSON 형태로 남깁니다. CloudWatch `event_name`은 운영 로그 이름이며, [`events.md`](./events.md)의 분석 이벤트 네이밍 컨벤션을 강제하지 않습니다.

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

## AN-4-6 백엔드 Sentry 기준

백엔드는 예상하지 못한 장애와 운영자가 확인해야 하는 실패만 Sentry에 보냅니다.

| 구분 | 수집 내용 |
| --- | --- |
| Tags | `endpoint`, `http_method`, `status_code`, `error_code`, `creation_id`, `story_id`, `chat_id`, `request_id` |
| Context | `session_id`, `device_id_hash`, `feature`, `duration_ms`, `ai_call_log_id` |
| Breadcrumb | API 요청 시작, DB 저장 완료, AI 호출 시작과 종료 |
| Exceptions | 5xx 예외, DB 예외, AI 호출 timeout, AI 응답 검증 실패, Slack 피드백 webhook 실패 |

사용자 입력 검증 실패처럼 예상 가능한 4xx 오류는 기본적으로 Sentry exception으로 보내지 않습니다. 같은 4xx 오류가 짧은 시간에 반복되어 운영 문제가 의심될 때만 warning 수준의 CloudWatch 로그로 확인합니다.

## AN-4-7 서버 분석 이벤트와 실패 타입

서버 분석 이벤트의 전체 목록은 [`events.md`](./events.md) AN-2-4에 있습니다. 백엔드는 퍼널의 결과 단계를 채우는 `server_*` 분석 이벤트를 발행합니다.

`error_type`은 사용자·퍼널 분석용 거친 분류이며 `network`, `validation`, `server`만 사용합니다. 내부 상세 실패 코드(`ai_call_logs.error_code`)는 다음 기준으로 `error_type`에 매핑합니다.

| error_type | 의미 | 매핑되는 내부 error_code |
| --- | --- | --- |
| `network` | 네트워크, 연결, timeout 실패 | `provider_timeout`, `provider_unavailable` |
| `validation` | 입력값, 응답 검증, 안전 정책 실패 | `provider_bad_request`, `schema_validation_failed`, `invalid_ai_response`, `content_filter_blocked` |
| `server` | 서버 내부 처리 실패 | `provider_rate_limited`, `unexpected_error` |

## AN-4-8 AI 기능과 요청 context

MVP에서 분석 대상이 되는 AI 기능은 다음 네 가지입니다.

| feature | 설명 | 사용자 퍼널 연결 |
| --- | --- | --- |
| `storyline_generation` | 선택 키워드로 스토리라인 후보 생성 | `client_storyCreate_storyGeneration_requested`, `server_storyCreate_storyGeneration_processed_*` |
| `story_completion` | 선택 스토리라인과 추가 정보로 스토리 상세 생성 | `client_storyCreate_completed`, `client_storyDetail_viewed` |
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

## AN-4-9 `ai_call_logs` 기록 기준

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

## AN-4-10 AI CloudWatch와 Sentry 기준

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

## AN-4-11 개인정보 원칙

| 데이터 | 처리 방식 |
| --- | --- |
| 채팅 메시지 | 원문 로그 금지. `turn_number`와 token count만 기록합니다. |
| 피드백 본문 | 별도 저장소 또는 Slack 전송만 허용합니다. 로그에는 길이만 기록합니다. |
| 이메일 | 로그 저장 금지. `has_email`만 기록합니다. |
| 프롬프트 전문 | CloudWatch, Sentry, `ai_call_logs` 저장 금지입니다. |
| AI 생성 결과 원문 | CloudWatch, Sentry, `ai_call_logs` 저장 금지입니다. |
| 직접 추가 키워드 원문 | 저장 금지입니다. |
| 익명 ID | 서버 계층에서는 `device_id_hash`만 저장합니다. |

# AN-3-ANALYTICS-BACKEND-SPEC

이 문서는 **마냑 MVP 백엔드가 서버 분석 이벤트, CloudWatch, Sentry, `ai_call_logs`로 남겨야 하는 서버 분석 신호**를 정리합니다. 프론트엔드 행동 이벤트만으로 확인하기 어려운 API 처리 결과, 장애 원인, AI 호출 상관관계를 서버 관측 기준으로 고정합니다.

백엔드는 프론트엔드 이벤트와 AI 호출 로그 사이의 허브입니다. 모든 요청에 `request_id`, `session_id`, `device_id_hash`를 싣고, 생성·채팅 결과를 `server_*` 분석 이벤트로 발행해, 서버 로그·Sentry·AI 호출 이력이 같은 사건을 가리키도록 만듭니다.

```text
§AN-3-1  목적                      백엔드 분석 책임과 제외 범위
§AN-3-2  도구별 역할               서버 분석 이벤트 · Sentry · CloudWatch · ai_call_logs
§AN-3-3  요청 식별자와 상관관계     프론트엔드 헤더와 서버 context
§AN-3-4  서버 분석 이벤트           server_* 이벤트와 error_type 매핑
§AN-3-5  CloudWatch 구조화 로그     JSON 로그 양식과 운영 이벤트
§AN-3-6  Sentry 수집 기준          Tags · Context · Breadcrumb · Exceptions
§AN-3-7  ai_call_logs 테이블        AI 호출 이력 컬럼과 연결 규칙
§AN-3-8  MVP 운영 지표             API · 스토리 · AI · 피드백 운영 지표
§AN-3-9  개인정보 원칙             원문 로그 금지와 대체 프로퍼티
§AN-3-10 검수 체크리스트           출시 전 확인 항목
```

---

| 항목 | 값 |
| --- | --- |
| 버전 | v0.3 |
| 작성일 | 2026-06-25 |
| 대상 | 마냑 MVP 백엔드 |
| 적용 도구 | 서버 분석 이벤트, Sentry, `ai_call_logs` 테이블, CloudWatch |

| 관련 문서 | 연결 지점 |
| --- | --- |
| [`analytics-spec.md`](./analytics-spec.md) | 전체 이벤트·지표·퍼널 기준 |
| [`analytics-frontend-spec.md`](./analytics-frontend-spec.md) | API 요청에 실리는 `device_id`, `session_id`, `creation_id` |
| [`analytics-ai-spec.md`](./analytics-ai-spec.md) | AI 서비스 호출 context와 `ai_call_logs` 기록 기준 |

## AN-3-1 목적

백엔드 분석의 목적은 프론트엔드 행동 이벤트만으로 확인하기 어려운 서버 처리 결과와 장애 원인을 추적하는 것이다. MVP에서는 별도 서버 사이드 제품 분석 도구를 붙이지 않고, 서버 분석 이벤트, Sentry, CloudWatch, `ai_call_logs`로 운영 분석에 필요한 최소 데이터를 남긴다.

백엔드는 다음 데이터를 담당한다.

- 스토리 생성, AI 응답, 피드백 제출 결과를 `server_*` 분석 이벤트로 발행한다.
- API 요청의 성공, 실패, 처리 시간을 CloudWatch 구조화 로그로 남긴다.
- AI 서비스 호출 전후의 상관관계 정보를 `ai_call_logs`와 연결한다.
- 예외와 장애 context를 Sentry에 남긴다.
- 사용자가 입력한 원문, 피드백 본문, 이메일 원문, 프롬프트 전문은 로그와 Sentry에 넣지 않는다.

## AN-3-2 도구별 역할

| 도구 | 역할 | MVP 적용 범위 |
| --- | --- | --- |
| 서버 분석 이벤트 | 퍼널 결과 계측 | 생성 성공·실패, AI 응답 성공·실패, 피드백 제출 성공·실패 |
| Sentry | 서버 예외 분석 | API 예외, AI 호출 실패, DB 오류, 외부 연동 실패 |
| CloudWatch | 운영 로그와 지표 | API 요청 로그, 주요 비즈니스 이벤트, latency, status |
| `ai_call_logs` | AI 호출 이력 | 스토리라인 생성, 스토리 생성, 채팅 응답, 추천 입력 생성 |

서버 분석 이벤트는 프론트엔드 client 이벤트와 같은 퍼널에서 결과 단계를 채운다. CloudWatch는 운영 상태를 빠르게 확인하는 기준이고, Sentry는 stack trace와 예외 context를 확인하는 기준이며, `ai_call_logs`는 AI 호출 품질과 비용 추정 기준이다.

## AN-3-3 요청 식별자와 상관관계

프론트엔드는 모든 API 요청에 다음 값을 전달한다. 백엔드는 값을 검증한 뒤 요청 context와 로그에 넣는다.

| 헤더 | 필수 여부 | 설명 |
| --- | --- | --- |
| `X-Manyak-Device-Id` | 필수 | 프론트엔드 Amplitude SDK의 익명 사용자 ID(`device_id`) |
| `X-Manyak-Session-Id` | 필수 | 프론트엔드 세션 ID |
| `X-Manyak-Request-Id` | 권장 | 요청 단위 ID. 없으면 백엔드에서 생성한다. |

백엔드는 모든 서버 분석 이벤트, CloudWatch 로그, Sentry scope, AI 호출 요청에 다음 값을 포함한다.

| 필드 | 설명 |
| --- | --- |
| `device_id_hash` | 익명 `device_id`를 해시한 값. 원본 ID는 필요한 곳에만 제한적으로 사용한다. |
| `session_id` | 프론트엔드 세션 ID |
| `request_id` | API 요청과 AI 호출을 연결하는 서버 내부 상관 ID |
| `creation_id` | 스토리라인 생성 시 발급되는 `simpleCreationId` |
| `story_id` | 스토리 완성 후 발급된 ID |
| `chat_id` | 채팅 생성 후 발급된 ID |

`request_id`는 서버 로그·Sentry·`ai_call_logs`를 잇는 서버 내부 상관 키다. 프론트엔드 client `requested` ↔ server `processed` 연결은 현재 `creation_id`로 한다.

## AN-3-4 서버 분석 이벤트

백엔드는 퍼널의 결과 단계를 채우는 `server_*` 분석 이벤트를 발행한다. 이벤트명은 프론트엔드와 같은 네이밍 컨벤션(`{platform}_{screenName}_{objectName}_{actionType}_{eventType}`)을 따르고, platform은 `server`, actionType은 `processed`를 쓴다. 이 이벤트는 CloudWatch 운영 로그(AN-3-5)와 별개이며, `ai_call_logs`·서버 로그와는 `creation_id`, `chat_id`, `request_id`로 연결한다.

| 이벤트 | 발생 시점 | 고유 프로퍼티 |
| --- | --- | --- |
| `server_storyCreate_storyGeneration_processed_succeeded` | 스토리라인 생성 성공 | `creation_id` (string, ✅) |
| `server_storyCreate_storyGeneration_processed_failed` | 스토리라인 생성 실패 | `creation_id` (string, ✅), `error_type` (string, ✅) |
| `server_chat_aiMessage_processed_succeeded` | AI 응답 생성 성공 | `chat_id` (string, ✅), `turn_number` (number, ✅) |
| `server_chat_aiMessage_processed_failed` | AI 응답 생성 실패 | `chat_id` (string, ✅), `turn_number` (number, ✅), `error_type` (string, ✅) |
| `server_feedback_submission_processed_succeeded` | 피드백 제출 처리 성공 | 없음 |
| `server_feedback_submission_processed_failed` | 피드백 제출 처리 실패 | `error_type` (string, ✅) |

`error_type`은 사용자·퍼널 분석용 거친 분류이며 `network`, `validation`, `server`만 사용한다. 내부 상세 실패 코드(`ai_call_logs.error_code`)는 다음 기준으로 `error_type`에 매핑한다.

| error_type | 의미 | 매핑되는 내부 error_code 예시 |
| --- | --- | --- |
| `network` | 네트워크·연결·timeout 실패 | `provider_timeout`, `provider_unavailable` |
| `validation` | 입력값·응답 검증 실패 | `provider_bad_request`, `schema_validation_failed`, `invalid_ai_response`, `content_filter_blocked` |
| `server` | 서버 내부·처리 실패 | `provider_rate_limited`, `unexpected_error` |

## AN-3-5 CloudWatch 구조화 로그

모든 로그는 JSON 형태로 남긴다.

CloudWatch `event_name`은 서버 처리 결과를 나타내는 운영 로그이며, AN-3-4의 서버 분석 이벤트명이나 프론트엔드 사용자 이벤트명과 같은 네이밍 컨벤션을 강제하지 않는다. 운영 로그와 분석 이벤트는 `request_id`, `session_id`, `device_id_hash`, `creation_id`, `story_id`, `chat_id`로 연결한다.

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

MVP에서 반드시 남길 운영 로그 이벤트는 다음과 같다.

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

## AN-3-6 Sentry 수집 기준

백엔드는 예상하지 못한 장애와 운영자가 확인해야 하는 실패만 Sentry에 보낸다.

| 구분 | 수집 내용 |
| --- | --- |
| Tags | `endpoint`, `http_method`, `status_code`, `error_code`, `creation_id`, `story_id`, `chat_id`, `request_id` |
| Context | `session_id`, `device_id_hash`, `feature`, `duration_ms`, `ai_call_log_id` |
| Breadcrumb | API 요청 시작, DB 저장 완료, AI 호출 시작과 종료 |
| Exceptions | 5xx 예외, DB 예외, AI 호출 timeout, AI 응답 검증 실패, Slack 피드백 webhook 실패 |

사용자 입력 검증 실패처럼 예상 가능한 4xx 오류는 기본적으로 Sentry exception으로 보내지 않는다. 같은 4xx 오류가 짧은 시간에 반복되어 운영 문제가 의심될 때만 warning 수준의 CloudWatch 로그로 확인한다.

## AN-3-7 `ai_call_logs` 테이블

`ai_call_logs`는 AI 호출 단위 이력을 남기는 테이블이다. 백엔드는 AI 서비스에 `request_id`, `device_id_hash`, `session_id`, `creation_id`, `story_id`, `chat_id`, `turn_number`, `feature`를 전달한다. AI 서비스는 실행 결과를 기록하고, 백엔드는 응답의 `ai_call_log_id`를 서버 로그와 저장 데이터에 연결한다.

MVP 최소 컬럼은 다음과 같다.

| 컬럼 | 타입 예시 | 설명 |
| --- | --- | --- |
| `id` | UUID | AI 호출 로그 ID |
| `request_id` | VARCHAR | API 요청과 연결되는 ID |
| `caller_service` | VARCHAR | 호출 서비스. MVP 값은 `manyak-server` |
| `feature` | VARCHAR | `storyline_generation`, `story_completion`, `chat_response`, `suggestion_generation` |
| `device_id_hash` | VARCHAR | 익명 `device_id` 해시 |
| `session_id` | VARCHAR | 세션 ID |
| `creation_id` | VARCHAR NULL | 스토리 생성 시도 ID(`simpleCreationId`) |
| `story_id` | VARCHAR NULL | 연결된 스토리 ID |
| `chat_id` | VARCHAR NULL | 연결된 채팅 ID |
| `turn_number` | INTEGER NULL | 사용자 메시지 기준 턴 번호 |
| `provider` | VARCHAR | AI provider |
| `model` | VARCHAR | 모델명 |
| `prompt_template_version` | VARCHAR | 프롬프트 템플릿 버전 |
| `status` | VARCHAR | `started`, `succeeded`, `failed` |
| `latency_ms` | INTEGER | AI 호출 소요 시간 |
| `input_token_count` | INTEGER NULL | 입력 토큰 수 |
| `output_token_count` | INTEGER NULL | 출력 토큰 수 |
| `retry_count` | INTEGER | 재시도 횟수 |
| `error_code` | VARCHAR NULL | 내부 실패 코드 |
| `sentry_event_id` | VARCHAR NULL | Sentry 이벤트 ID |
| `created_at` | TIMESTAMP | 생성 시각 |
| `completed_at` | TIMESTAMP NULL | 완료 시각 |

프롬프트 원문, 채팅 원문, 생성 결과 원문은 `ai_call_logs`에 저장하지 않는다. 디버깅에 원문이 필요하면 별도 보안 정책을 정한 뒤 제한된 저장소를 사용한다.

## AN-3-8 MVP 운영 지표

CloudWatch와 `ai_call_logs`로 다음 지표를 본다.

| 지표 | 계산 기준 |
| --- | --- |
| API 실패율 | `api_request_failed` 수 / 전체 API 요청 수 |
| 스토리 생성 서버 실패율 | `story_generation_failed` 수 / `story_generation_requested` 수 |
| AI 호출 실패율 | `ai_call_logs.status = failed` 수 / 전체 AI 호출 수 |
| AI 응답 p95 latency | `ai_call_logs.latency_ms` p95 |
| 채팅 응답 저장 성공률 | `ai_response_saved` 수 / `user_message_saved` 수 |
| 피드백 제출 성공률 | `feedback_delivery_completed` 수 / 피드백 제출 API 요청 수 |

서버 분석 이벤트로 보는 퍼널 결과 지표(생성 실패율, AI 응답 성공률 등)는 [`analytics-spec.md`](./analytics-spec.md) AN-1-6을 따른다.

## AN-3-9 개인정보 원칙

| 데이터 | 처리 방식 |
| --- | --- |
| 채팅 메시지 | 원문 로그 금지. `turn_number`만 기록 |
| 피드백 본문 | 별도 저장소 또는 Slack 전송만 허용. 로그에는 길이만 기록 |
| 이메일 | 로그 금지. `has_email`만 기록 |
| 프롬프트 전문 | 로그와 Sentry 저장 금지 |
| 익명 ID | 로그에는 `device_id_hash` 사용 |

## AN-3-10 검수 체크리스트

- 모든 API 로그에 `request_id`, `session_id`, `device_id_hash`가 있다.
- 생성·AI 응답·피드백 결과가 `server_*` 분석 이벤트로 발행되고, `creation_id` 또는 `chat_id`로 client 이벤트와 연결된다.
- 5xx 오류가 Sentry에 생성되고 CloudWatch 로그의 `request_id`로 연결된다.
- AI 호출 성공과 실패가 `ai_call_logs`에 남고, 서버 로그에 `ai_call_log_id`가 연결된다.
- `server_*` 이벤트의 `error_type`이 `ai_call_logs.error_code`와 AN-3-4 기준으로 매핑된다.
- 채팅 메시지, 피드백 본문, 이메일, 프롬프트 원문이 CloudWatch와 Sentry payload에 없다.
- 스토리 생성 실패율, AI 호출 실패율, AI 응답 p95 latency를 계산할 수 있다.

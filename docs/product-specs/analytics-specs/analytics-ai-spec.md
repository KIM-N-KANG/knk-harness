# AN-4-ANALYTICS-AI-SPEC

이 문서는 **마냑 MVP AI 서비스가 CloudWatch, Sentry, `ai_call_logs`로 남겨야 하는 AI 호출 분석 신호**를 정리합니다. 스토리 제작과 채팅 흐름에서 AI 호출이 성공했는지, 실패했다면 어느 feature와 오류 코드에서 실패했는지 확인하는 기준입니다.

AI 서비스는 사용자 행동 퍼널의 내부 피드백 루프입니다. provider 호출, 응답 검증, 토큰 사용량, retry, Sentry 이벤트를 호출 단위로 남겨 운영자가 비용·latency·실패 원인을 추적할 수 있게 합니다.

```text
§AN-4-1   목적                       AI 분석 책임과 제외 범위
§AN-4-2   도구별 역할                Sentry · CloudWatch · ai_call_logs
§AN-4-3   AI 기능 범위               storyline_generation · story_completion · chat_response · suggestion_generation
§AN-4-4   요청 context 계약          백엔드가 전달하는 필드와 AI 응답 메타데이터
§AN-4-5   CloudWatch 구조화 로그      JSON 로그 양식과 AI 이벤트
§AN-4-6   ai_call_logs 기록 기준      호출 단위 기록과 최소 컬럼
§AN-4-7   실패 코드                  provider · schema · safety · unexpected 오류 분류
§AN-4-8   Sentry 수집 기준           Tags · Context · Breadcrumb · Exceptions
§AN-4-9   MVP 운영 지표              성공률 · 실패율 · p50/p95 latency · token · retry
§AN-4-10  개인정보 원칙              프롬프트·채팅·생성 결과 원문 저장 금지
§AN-4-11  검수 체크리스트            출시 전 확인 항목
```

---

| 항목 | 값 |
| --- | --- |
| 버전 | v0.4 |
| 작성일 | 2026-06-25 |
| 대상 | 마냑 MVP AI 서비스 |
| 적용 도구 | Sentry, `ai_call_logs` 테이블, CloudWatch |

| 관련 문서 | 연결 지점 |
| --- | --- |
| [`analytics-spec.md`](./analytics-spec.md) | 전체 이벤트·지표·퍼널 기준 |
| [`analytics-frontend-spec.md`](./analytics-frontend-spec.md) | AI 성공·실패가 사용자 행동 이벤트로 노출되는 기준 |
| [`analytics-backend-spec.md`](./analytics-backend-spec.md) | 백엔드가 AI 호출에 전달하는 `request_id`와 `server_*` 이벤트 연결 |

## AN-4-1 목적

AI 분석의 목적은 스토리 제작과 채팅 흐름에서 AI 호출이 성공적으로 응답하는지, 실패한다면 어디서 실패하는지 확인하는 것이다. MVP에서는 사용자 행동 분석보다 AI 호출 품질, 응답 시간, 실패 원인, 토큰 사용량을 우선 측정한다.

AI 서비스는 다음 데이터를 담당한다.

- AI 호출 시작, 성공, 실패를 CloudWatch 구조화 로그로 남긴다.
- AI 호출 결과를 `ai_call_logs`에 기록한다.
- provider 오류, timeout, 응답 파싱 실패, schema 검증 실패를 Sentry에 보낸다.
- 프롬프트 원문, 채팅 원문, 생성 결과 원문은 로그와 Sentry에 넣지 않는다.

AI 호출 결과는 백엔드가 `server_storyCreate_storyGeneration_processed_*`, `server_chat_aiMessage_processed_*` 같은 서버 분석 이벤트로 퍼널에 반영한다. AI 서비스의 상세 실패 코드(AN-4-7)는 그 이벤트의 `error_type`으로 거칠게 매핑된다([`analytics-backend-spec.md`](./analytics-backend-spec.md) AN-3-4).

## AN-4-2 도구별 역할

| 도구 | 역할 | MVP 적용 범위 |
| --- | --- | --- |
| Sentry | AI 서비스 오류 분석 | provider 오류, timeout, 파싱 실패, schema 검증 실패 |
| CloudWatch | 운영 로그와 지표 | 호출 시작과 종료, latency, status, token count, retry count |
| `ai_call_logs` | AI 호출 이력 | 스토리라인 생성, 스토리 생성, 채팅 응답, 추천 입력 생성 |

CloudWatch는 실시간 운영 확인에 사용한다. `ai_call_logs`는 호출 단위 분석과 비용 추정에 사용한다. Sentry는 코드 레벨 오류와 재현 정보를 확인하는 데 사용한다.

## AN-4-3 AI 기능 범위

MVP에서 분석 대상이 되는 AI 기능은 다음 네 가지다.

| feature | 설명 | 사용자 퍼널 연결 |
| --- | --- | --- |
| `storyline_generation` | 선택 키워드로 스토리라인 후보 생성 | `client_storyCreate_storyGeneration_requested`, `server_storyCreate_storyGeneration_processed_succeeded`, `server_storyCreate_storyGeneration_processed_failed` |
| `story_completion` | 선택 스토리라인과 추가 정보로 스토리 상세 생성 | `client_storyCreate_completed`, `client_storyDetail_viewed` |
| `chat_response` | 사용자 메시지에 대한 AI 응답 생성 | `client_chat_messageInput_submitted`, `server_chat_aiMessage_processed_succeeded`, `server_chat_aiMessage_processed_failed` |
| `suggestion_generation` | 다음 입력 추천 선택지 생성 | `client_chat_choiceOption_selected` |

AI feature는 프론트엔드 이벤트명에 넣지 않는다. 스토리라인 생성 실패와 채팅 응답 실패는 각각 `server_storyCreate_storyGeneration_processed_failed`, `server_chat_aiMessage_processed_failed`로 노출되고, 상세 원인은 `feature`와 `error_code`로 구분한다.

## AN-4-4 요청 context 계약

백엔드는 AI 서비스 호출 시 다음 값을 전달한다. AI 서비스는 값을 그대로 로그, Sentry scope, `ai_call_logs`에 연결한다.

| 필드 | 필수 여부 | 설명 |
| --- | --- | --- |
| `request_id` | 필수 | 백엔드, AI 로그를 연결하는 서버 내부 상관 ID |
| `device_id_hash` | 필수 | 익명 `device_id` 해시 |
| `session_id` | 필수 | 프론트엔드 세션 ID |
| `feature` | 필수 | AI 기능명 |
| `creation_id` | 조건부 | 스토리라인 생성·완성 시 필수 |
| `story_id` | 조건부 | 스토리 완성 후 또는 채팅 중 필수 |
| `chat_id` | 조건부 | 채팅 응답 생성 시 필수 |
| `turn_number` | 조건부 | 채팅 응답 생성 시 필수 |
| `prompt_template_version` | 필수 | 프롬프트 템플릿 버전 |

AI 서비스 응답에는 다음 메타데이터를 포함한다.

| 필드 | 설명 |
| --- | --- |
| `ai_call_log_id` | `ai_call_logs` 행 ID |
| `model` | 사용 모델 |
| `latency_ms` | AI 호출 소요 시간 |
| `input_token_count` | 입력 토큰 수 |
| `output_token_count` | 출력 토큰 수 |
| `error_code` | 실패 시 오류 코드 |

## AN-4-5 CloudWatch 구조화 로그

모든 로그는 JSON 형태로 남긴다.

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

MVP에서 반드시 남길 AI 이벤트는 다음과 같다.

| 이벤트 | 발생 시점 | 핵심 필드 |
| --- | --- | --- |
| `ai_call_started` | provider 호출 직전 | `feature`, `request_id`, `prompt_template_version`, `model` |
| `ai_call_completed` | provider 호출과 응답 검증 성공 | `feature`, `ai_call_log_id`, `latency_ms`, `input_token_count`, `output_token_count` |
| `ai_call_failed` | provider 호출 또는 응답 검증 실패 | `feature`, `ai_call_log_id`, `latency_ms`, `error_code`, `retry_count` |
| `ai_response_validation_failed` | 응답 schema 검증 실패 | `feature`, `error_code`, `prompt_template_version` |

## AN-4-6 `ai_call_logs` 기록 기준

AI 호출 1회당 `ai_call_logs`에 1행을 기록한다. 재시도가 발생하면 같은 `request_id` 아래에서 `retry_count`를 증가시킨다. 여러 모델을 순차 호출하는 기능이 생기면 provider 호출별로 행을 분리한다.

MVP 최소 컬럼은 다음과 같다.

| 컬럼 | 설명 |
| --- | --- |
| `id` | AI 호출 로그 ID |
| `request_id` | 백엔드, AI 로그 연결 ID |
| `caller_service` | 호출 서비스. MVP 값은 `manyak-server` |
| `feature` | AI 기능명 |
| `device_id_hash` | 익명 `device_id` 해시 |
| `session_id` | 세션 ID |
| `creation_id` | 스토리 생성 시도 ID(`simpleCreationId`) |
| `story_id` | 연결된 스토리 ID |
| `chat_id` | 연결된 채팅 ID |
| `turn_number` | 사용자 메시지 기준 턴 번호 |
| `provider` | AI provider |
| `model` | 모델명 |
| `prompt_template_version` | 프롬프트 템플릿 버전 |
| `status` | `started`, `succeeded`, `failed` |
| `latency_ms` | provider 호출과 응답 검증까지 걸린 시간 |
| `input_token_count` | 입력 토큰 수 |
| `output_token_count` | 출력 토큰 수 |
| `retry_count` | 재시도 횟수 |
| `error_code` | 실패 코드 |
| `sentry_event_id` | Sentry 이벤트 ID |
| `created_at` | 호출 시작 시각 |
| `completed_at` | 호출 종료 시각 |

## AN-4-7 실패 코드

MVP에서는 실패 코드를 적게 유지한다. 아래 `error_code`는 내부 상세 코드이며, 분석 이벤트의 `error_type`(`network` / `validation` / `server`)으로 매핑된다([`analytics-backend-spec.md`](./analytics-backend-spec.md) AN-3-4).

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

프론트엔드와 백엔드에는 사용자에게 노출 가능한 메시지 코드만 전달한다. 내부 오류 상세는 CloudWatch와 Sentry에서 확인한다.

## AN-4-8 Sentry 수집 기준

| 구분 | 수집 내용 |
| --- | --- |
| Tags | `feature`, `provider`, `model`, `prompt_template_version`, `error_code`, `request_id` |
| Context | `ai_call_log_id`, `session_id`, `device_id_hash`, `creation_id`, `story_id`, `chat_id`, `turn_number`, `latency_ms`, `retry_count` |
| Breadcrumb | AI 호출 시작, provider 응답 수신, schema 검증, DB 기록 |
| Exceptions | timeout, provider 오류, 파싱 실패, schema 검증 실패, 예상하지 못한 예외 |

Sentry에는 프롬프트 전문, 사용자 메시지, AI 생성 결과를 넣지 않는다. 필요하면 길이, 토큰 수, 템플릿 버전, 모델명만 남긴다.

## AN-4-9 MVP 운영 지표

| 지표 | 계산 기준 |
| --- | --- |
| AI 호출 성공률 | `status = succeeded` 수 / 전체 AI 호출 수 |
| AI 호출 실패율 | `status = failed` 수 / 전체 AI 호출 수 |
| 기능별 실패율 | `feature`별 실패 수 / `feature`별 전체 호출 수 |
| p50, p95 latency | `latency_ms`의 p50, p95 |
| 채팅 응답 실패율 | `chat_response` 실패 수 / `chat_response` 전체 호출 수 |
| 평균 입력 토큰 수 | `input_token_count` 평균 |
| 평균 출력 토큰 수 | `output_token_count` 평균 |
| 재시도율 | `retry_count > 0` 호출 수 / 전체 호출 수 |

## AN-4-10 개인정보 원칙

| 데이터 | 처리 방식 |
| --- | --- |
| 프롬프트 전문 | 저장 금지 |
| 사용자 채팅 원문 | 저장 금지 |
| AI 생성 결과 원문 | 저장 금지 |
| 직접 추가 키워드 원문 | 저장 금지 |
| 입력과 출력 크기 | token count만 저장 |
| 익명 ID | `device_id_hash`만 저장 |

## AN-4-11 검수 체크리스트

- 성공 호출과 실패 호출이 모두 `ai_call_logs`에 기록된다.
- CloudWatch 로그에서 `request_id`로 백엔드 로그와 AI 로그를 연결할 수 있다.
- AI 호출 결과가 `server_storyCreate_storyGeneration_processed_*` 또는 `server_chat_aiMessage_processed_*` 이벤트로 연결되고, `error_code`가 AN-4-7 기준으로 `error_type`에 매핑된다.
- Sentry 이벤트에 `feature`, `model`, `prompt_template_version`, `error_code`가 있다.
- 프롬프트 전문, 채팅 원문, AI 생성 결과 원문이 CloudWatch, Sentry, `ai_call_logs`에 없다.
- `storyline_generation`, `story_completion`, `chat_response`의 성공률과 p95 latency를 계산할 수 있다.

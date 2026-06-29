# AN-5-ANALYTICS-QA

이 문서는 마냑 MVP 분석 스펙의 검수 기준을 정의합니다. 출시 전에는 이 문서의 체크리스트로 이벤트, 지표, 로그, 개인정보 원칙을 확인합니다.

```text
§AN-5-1  검수 원칙
§AN-5-2  문서 변경 체크리스트
§AN-5-3  출시 전 P0 체크리스트
§AN-5-4  계층별 검수 기준
§AN-5-5  개인정보 검수 기준
§AN-5-6  검증 쿼리 예시
```

| 항목 | 값 |
| --- | --- |
| 버전 | v0.8 |
| 작성일 | 2026-06-30 |
| 대상 | 마냑 MVP 분석 검수 |
| 관련 문서 | [`analytics-spec.md`](./analytics-spec.md), [`events.md`](./events.md), [`metrics.md`](./metrics.md), [`observability.md`](./observability.md) |

## AN-5-1 검수 원칙

검수는 "이벤트가 발생한다"에서 끝나지 않습니다. 이벤트명, 프로퍼티 타입, 식별자 연결, 지표 계산 가능성, 원문 미수집까지 함께 확인합니다.

| 원칙 | 확인 방법 |
| --- | --- |
| P0 이벤트 우선 | 출시 전에는 [`events.md`](./events.md) AN-2-3의 P0 이벤트를 모두 확인합니다. |
| 원본 문서 기준 | 이벤트는 `events.md`, 지표는 `metrics.md`, 관측 구현은 `observability.md`를 기준으로 확인합니다. |
| 식별자 연결 확인 | `device_id`, `session_id`, `creation_id`, `chat_id`, `request_id`, `ai_call_log_id`가 각 계층에서 이어지는지 봅니다. |
| 원문 수집 금지 | 채팅, 피드백, 이메일, 키워드, 프롬프트, AI 생성 결과 원문이 payload에 없는지 확인합니다. |

## AN-5-2 문서 변경 체크리스트

분석 스펙을 변경할 때는 다음 항목을 확인합니다.

- 새 이벤트를 추가하면 [`events.md`](./events.md)에 이벤트명, 발생 시점, 고유 프로퍼티, 우선순위를 추가합니다.
- 새 이벤트가 지표에 쓰이면 [`metrics.md`](./metrics.md)에 계산식과 집계 단위를 추가합니다.
- 새 이벤트가 Sentry breadcrumb 또는 CloudWatch 로그와 연결되면 [`observability.md`](./observability.md)에 연결 기준을 추가합니다.
- P0 이벤트가 바뀌면 이 문서의 출시 전 P0 체크리스트를 업데이트합니다.
- 원문 수집 가능성이 있는 프로퍼티를 추가하면 [`analytics-spec.md`](./analytics-spec.md) AN-1-8과 이 문서 AN-5-5를 함께 확인합니다.
- 같은 표를 여러 문서에 복사하지 않고 원본 문서를 링크합니다.

## AN-5-3 출시 전 P0 체크리스트

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

## AN-5-4 계층별 검수 기준

### AN-5-4-1 프론트엔드

- Amplitude 디버그 모드에서 P0 `client_*` 이벤트가 한 번씩 발생합니다.
- 이벤트명이 `{platform}_{screenName}(_{objectName})?_{actionType}(_{eventType})?` 형식을 따릅니다.
- 프로퍼티는 `snake_case`로 전송합니다.
- 같은 사용자 행동에서 Amplitude event, Sentry breadcrumb, 상관 키(`creation_id`, `chat_id`)가 연결됩니다.
- API 요청 헤더에 `X-Manyak-Device-Id`, `X-Manyak-Session-Id`가 포함됩니다.
- `X-Manyak-Request-Id`가 없을 때 백엔드가 `request_id`를 생성합니다.

### AN-5-4-2 백엔드

- 모든 API 로그에 `request_id`, `session_id`, `device_id_hash`가 있습니다.
- 생성, AI 응답, 피드백 결과가 `server_*` 분석 이벤트로 발행됩니다.
- `server_*` 이벤트가 `creation_id` 또는 `chat_id`로 client 이벤트와 연결됩니다.
- 5xx 오류가 Sentry에 생성되고 CloudWatch 로그의 `request_id`로 연결됩니다.
- 서버 분석 이벤트의 `error_type`이 [`observability.md`](./observability.md) AN-4-7 기준을 따릅니다.
- 스토리 생성 실패율, API 실패율, 피드백 제출 성공률을 계산할 수 있습니다.

### AN-5-4-3 AI 서비스

- 성공 호출과 실패 호출이 모두 `ai_call_logs`에 기록됩니다.
- CloudWatch 로그에서 `request_id`로 백엔드 로그와 AI 로그를 연결할 수 있습니다.
- AI 호출 결과가 `server_storyCreate_storyGeneration_processed_*` 또는 `server_chat_aiMessage_processed_*` 이벤트로 연결됩니다.
- `error_code`가 [`observability.md`](./observability.md) AN-4-9 기준으로 `error_type`에 매핑됩니다.
- Sentry 이벤트에 `feature`, `model`, `prompt_template_version`, `error_code`가 있습니다.
- `storyline_generation`, `story_completion`, `chat_response`의 성공률과 p95 latency를 계산할 수 있습니다.

## AN-5-5 개인정보 검수 기준

| 데이터 | 확인 기준 |
| --- | --- |
| 채팅 메시지 원문 | Amplitude, CloudWatch, Sentry, `ai_call_logs` payload에 없습니다. |
| 피드백 본문 | 분석 이벤트와 로그 payload에 없습니다. |
| 이메일 | 분석 이벤트와 로그 payload에 없습니다. `has_email`만 허용합니다. |
| 키워드·추가 정보 원문 | 관리되는 ID 또는 선택값만 허용합니다. |
| 프롬프트 전문 | CloudWatch, Sentry, `ai_call_logs`에 없습니다. |
| AI 생성 결과 원문 | CloudWatch, Sentry, `ai_call_logs`에 없습니다. |
| 익명 ID | 서버 계층에는 원본 `device_id`가 없고 `device_id_hash`만 있습니다. |

## AN-5-6 검증 쿼리 예시

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

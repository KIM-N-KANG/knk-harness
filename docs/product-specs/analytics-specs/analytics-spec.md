# AN-1-ANALYTICS-SPEC

이 문서는 **마냑 MVP에서 사용자가 스토리를 만들고 채팅을 이어가는 흐름**을 측정하기 위한 대표 분석 스펙입니다. 세부 이벤트, 지표, 관측 구현, 검수 기준은 역할별 문서로 분리합니다.

```text
§AN-1-1  문서 목적과 원본 책임
§AN-1-2  분석 문서 구조
§AN-1-3  분석 목적과 핵심 질문
§AN-1-4  MVP 분석 범위
§AN-1-5  전체 분석 흐름
§AN-1-6  식별자 정책
§AN-1-7  이벤트 네이밍 기준
§AN-1-8  개인정보와 원문 수집 원칙
§AN-1-9  변경 관리 원칙
```

| 항목 | 값 |
| --- | --- |
| 버전 | v0.8 |
| 작성일 | 2026-06-30 |
| 대상 | 마냑 MVP |
| 작성 목적 | 분석 스펙의 목적, 범위, 공통 용어, 식별자, 문서 소유 경계를 정의합니다. |

## AN-1-1 문서 목적과 원본 책임

`analytics-spec.md`는 분석 문서의 입구입니다. 이 문서는 분석 목적, MVP 범위, 전체 흐름, 식별자, 네이밍 기준처럼 모든 구현자가 공유해야 하는 기준만 담습니다.

이벤트 목록, 지표 계산식, Sentry와 CloudWatch 설정, `ai_call_logs` 컬럼, 릴리스 검수 항목은 이 문서에 중복해서 적지 않습니다. 각 세부 항목은 아래 역할 문서를 원본으로 삼습니다.

## AN-1-2 분석 문서 구조

| 문서 | 원본으로 관리하는 내용 | 주 독자 |
| --- | --- | --- |
| [`analytics-spec.md`](./analytics-spec.md) | 분석 목적, 범위, 용어, 전체 흐름, 식별자, 문서 링크 | 기획자, 개발자, 운영자 |
| [`events.md`](./events.md) | 이벤트명, 발생 조건, 고유 프로퍼티, P0/P1 우선순위 | 프론트엔드, 백엔드 |
| [`metrics.md`](./metrics.md) | 퍼널, 핵심 지표, 계산식, 집계 단위, 제외 조건 | 기획자, 데이터 분석자, 운영자 |
| [`observability.md`](./observability.md) | Amplitude, Sentry, CloudWatch, `ai_call_logs`, `request_id`, 실패 코드 | 프론트엔드, 백엔드, AI 서버 |
| [`qa.md`](./qa.md) | 검수 체크리스트, 릴리스 전 확인, 검증 쿼리 | QA, 개발자, 운영자 |

## AN-1-3 분석 목적과 핵심 질문

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

## AN-1-4 MVP 분석 범위

MVP 분석은 스토리 제작과 채팅 활성화에 필요한 최소 신호를 우선 수집합니다. 모든 화면 조작을 계측하지 않고, 퍼널과 운영 장애 분석에 필요한 행동과 처리 결과만 수집합니다.

| 포함 범위 | 설명 | 원본 문서 |
| --- | --- | --- |
| 사용자 행동 이벤트 | 화면 진입, CTA 클릭, 선택, 제출, 완료 | [`events.md`](./events.md) |
| 서버 처리 결과 이벤트 | 스토리 생성, AI 응답, 피드백 제출의 성공과 실패 | [`events.md`](./events.md) |
| 핵심 퍼널과 지표 | 제작 퍼널, 채팅 활성화 퍼널, 전체 활성화 퍼널 | [`metrics.md`](./metrics.md) |
| 운영 관측 | Sentry, CloudWatch, `ai_call_logs`, 실패 코드 | [`observability.md`](./observability.md) |
| 릴리스 검수 | P0 이벤트, 식별자, 원문 미수집, 로그 연결 확인 | [`qa.md`](./qa.md) |

| 제외 범위 | 처리 기준 |
| --- | --- |
| 사용자 입력 원문 분석 | MVP 분석 이벤트와 로그에 원문을 넣지 않습니다. |
| 대시보드 화면 요구사항 | 실제 Amplitude 또는 CloudWatch 대시보드가 정해질 때 별도 문서로 추가합니다. |
| 인증 사용자 분석 | 로그인 기능 도입 후 `user_id`, `identify`, `is_logged_in`을 추가합니다. |
| 실험 분석 | A/B 테스트 도입 후 `experiment_key`, `variant`를 추가합니다. |

## AN-1-5 전체 분석 흐름

분석 신호는 사용자 행동 이벤트, 서버 처리 결과, AI 호출 로그를 같은 식별자로 연결해 해석합니다.

```text
브라우저
  client_* 이벤트 -> Amplitude
  Sentry breadcrumb -> 브라우저 Sentry
  X-Manyak-Device-Id / X-Manyak-Session-Id / X-Manyak-Request-Id -> 백엔드 API

백엔드
  server_* 이벤트 -> 분석 이벤트
  API 로그 -> CloudWatch
  예외 context -> 서버 Sentry
  AI 호출 context -> AI 서비스

AI 서비스
  ai_call_logs 1행 -> 호출 단위 이력
  AI 로그 -> CloudWatch
  AI 예외 -> AI Sentry
```

Amplitude 이벤트는 제품 퍼널과 전환율의 기준 데이터입니다. Sentry와 CloudWatch는 오류 재현, 장애 원인, 운영 상태 확인에 사용합니다. `ai_call_logs`는 AI 호출 품질, latency, 토큰 사용량, 비용 추정에 사용합니다.

## AN-1-6 식별자 정책

현재 MVP는 로그인 기능이 없는 전원 게스트 서비스입니다. 사용자 단위는 Amplitude Browser SDK가 자동으로 채우는 `device_id`로 식별합니다.

| 식별자 | 분석 이벤트 타입 | 생성·관리 | 사용처 |
| --- | --- | --- | --- |
| `device_id` | string | Amplitude Browser SDK 자동 수집 | 익명 사용자 단위 분석 |
| `session_id` | number | Amplitude Browser SDK 자동 수집 | 한 번의 방문 흐름 |
| `request_id` | string | 프론트엔드 전달 또는 백엔드 생성 | 서버 로그, Sentry, AI 호출 연결 |
| `device_id_hash` | string | 백엔드가 `device_id`를 해시 | 서버 로그, Sentry, `ai_call_logs` |
| `creation_id` | string | 스토리라인 생성 시 발급되는 `simpleCreationId` | 스토리 제작 시도 연결 |
| `story_id` | number | 스토리 완성 후 서버 발급 | 스토리 관련 이벤트 |
| `chat_id` | string | 채팅 생성 후 서버 발급 | 채팅 관련 이벤트 |
| `ai_call_log_id` | string | AI 호출 기록 생성 시 발급 | 서버 로그와 `ai_call_logs` 연결 |

분석 이벤트에서 `story_id`는 number로 보냅니다. CloudWatch 로그와 `ai_call_logs`에서는 저장소 제약에 맞춰 문자열로 저장할 수 있습니다. 타입 차이는 저장 계층 차이이며 같은 값을 가리킵니다.

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

## AN-1-7 이벤트 네이밍 기준

이벤트명은 `platform`, `screenName`, `objectName`, `actionType`, `eventType`을 언더스코어로 연결합니다. 각 항목 내부는 camelCase로 쓰고, 프로퍼티는 `snake_case`로 씁니다.

```text
{platform}_{screenName}(_{objectName})?_{actionType}(_{eventType})?
```

| 항목 | 필수 여부 | 설명 |
| --- | --- | --- |
| `platform` | 필수 | 이벤트 주체입니다. `client` 또는 `server`를 사용합니다. |
| `screenName` | 필수 | 화면 또는 주요 flow입니다. 예: `storyList`, `storyCreate`, `chat` |
| `objectName` | 조건부 | 사용자가 보거나 조작한 대상, 또는 서버가 처리한 대상입니다. |
| `actionType` | 필수 | 사용자 행동, 상태 노출, 서버 처리를 나타냅니다. |
| `eventType` | 선택 | 성공, 실패, 차단, 취소처럼 결과 상태가 필요할 때만 사용합니다. |

```text
client_storyList_viewed
client_storyList_storyCard_clicked
client_storyCreate_storyGeneration_requested
server_storyCreate_storyGeneration_processed_succeeded
server_chat_aiMessage_processed_failed
```

이벤트명과 프로퍼티의 상세 계약은 [`events.md`](./events.md)를 따릅니다.

## AN-1-8 개인정보와 원문 수집 원칙

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

## AN-1-9 변경 관리 원칙

분석 스펙을 바꿀 때는 변경 성격에 맞는 원본 문서를 먼저 수정합니다.

| 변경 유형 | 먼저 수정할 문서 | 함께 확인할 문서 |
| --- | --- | --- |
| 이벤트 추가·삭제·이름 변경 | [`events.md`](./events.md) | [`metrics.md`](./metrics.md), [`qa.md`](./qa.md) |
| 프로퍼티 추가·타입 변경 | [`events.md`](./events.md) | [`observability.md`](./observability.md), [`qa.md`](./qa.md) |
| 지표 계산식 변경 | [`metrics.md`](./metrics.md) | [`events.md`](./events.md), [`qa.md`](./qa.md) |
| Sentry, CloudWatch, `ai_call_logs` 변경 | [`observability.md`](./observability.md) | [`qa.md`](./qa.md) |
| 릴리스 검수 기준 변경 | [`qa.md`](./qa.md) | 관련 원본 문서 |

같은 표를 여러 문서에 복사하지 않습니다. 다른 문서에서 필요한 경우 원본 문서의 섹션을 링크합니다.

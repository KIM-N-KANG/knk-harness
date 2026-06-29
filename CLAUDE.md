# KNK Workspace LLM Working Harness

- 아래 경로는 `knk-harness/` 루트 기준입니다.
- 세부 규칙은 이 문서에 반복하지 않고, 아래의 레포지토리 문서를 기준으로 확인합니다.

## Knowledge Base

| 작업 상황 | 먼저 확인할 문서 |
| --- | --- |
| 서비스 배경, 타겟 사용자, MVP 범위 확인 | `docs/product-specs/1-background.md` |
| 화면·기능별 사용자 요구(유저 스토리) 확인 | `docs/product-specs/2-user-stories.md` |
| 분석 목적, 범위, 식별자, 문서 구조 확인 | `docs/product-specs/analytics-specs/analytics-spec.md` |
| 이벤트명, 발생 조건, 프로퍼티, P0/P1 확인 | `docs/product-specs/analytics-specs/events.md` |
| 퍼널, 핵심 지표, 계산식, 집계 기준 확인 | `docs/product-specs/analytics-specs/metrics.md` |
| Amplitude, Sentry, CloudWatch, `ai_call_logs`, 실패 코드 확인 | `docs/product-specs/analytics-specs/observability.md` |
| 릴리스 전 분석 검수, 테스트 기준, 검증 쿼리 확인 | `docs/product-specs/analytics-specs/qa.md` |

## Working Principle

- 레포지토리에 없는 제품 정책, 이벤트 이름, 로그 필드, API 계약은 추측하지 않습니다.
- 제품 동작이나 분석 기준을 바꾸는 작업은 관련 `docs/product-specs/` 문서를 함께 확인합니다.
- 실제 secret, 로컬 전용 파일, 사용자 입력 원문, 프롬프트 전문, 채팅 원문은 문서나 예시에 넣지 않습니다.

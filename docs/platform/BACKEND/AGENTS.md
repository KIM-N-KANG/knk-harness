# 백엔드 플랫폼 기반

기능별 계약과 구조는 도메인 세트에서 관리한다. 과거 통합 Design의 기능 설명을 현재 계약으로 사용하지 않는다.

<br>

### 1 문서와 도메인

| 공통 기반 | 위치 |
|---|---|
| 기술 환경과 요청 경계 | [ARCHITECTURE.md](ARCHITECTURE.md) |
| 메트릭 수집과 집계 | [OBSERVABILITY.md](OBSERVABILITY.md) |
| 런타임 설정 | [CONFIGURATION.md](CONFIGURATION.md) |
| 공통 API와 상태 확인 | [서비스 인터페이스](../../reference/SERVICE-INTERFACES.md) |
| 환경과 배포 | [배포](../../operations/DEPLOYMENT.md) |
| 기존 BE 결정 원문 | [백엔드 결정 기록](../../reference/decisions/BACKEND.md) |

| 도메인 | 현재 구조 |
|---|---|
| ACCOUNT | [저장 구조](../../domain/ACCOUNT/BACKEND/3-2-DB-SCHEMA.md), [실행](../../domain/ACCOUNT/BACKEND/4-1-PIPELINES.md), [세트 안내](../../domain/ACCOUNT/BACKEND/AGENTS.md) |
| PAYMENT | [저장 구조](../../domain/PAYMENT/BACKEND/3-2-DB-SCHEMA.md), [실행](../../domain/PAYMENT/BACKEND/4-1-PIPELINES.md), [세트 안내](../../domain/PAYMENT/BACKEND/AGENTS.md) |
| CHAT | [저장 구조](../../domain/CHAT/BACKEND/3-2-DB-SCHEMA.md), [실행](../../domain/CHAT/BACKEND/4-1-PIPELINES.md), [세트 안내](../../domain/CHAT/BACKEND/AGENTS.md) |
| STORY | [저장 구조](../../domain/STORY/BACKEND/3-2-DB-SCHEMA.md), [실행](../../domain/STORY/BACKEND/4-1-PIPELINES.md), [세트 안내](../../domain/STORY/BACKEND/AGENTS.md) |
| MODERATION | [저장 구조](../../domain/MODERATION/BACKEND/3-2-DB-SCHEMA.md), [실행](../../domain/MODERATION/BACKEND/4-1-PIPELINES.md), [세트 안내](../../domain/MODERATION/BACKEND/AGENTS.md) |
| NOTIFICATION | [저장 구조](../../domain/NOTIFICATION/BACKEND/3-2-DB-SCHEMA.md), [실행](../../domain/NOTIFICATION/BACKEND/4-1-PIPELINES.md), [세트 안내](../../domain/NOTIFICATION/BACKEND/AGENTS.md) |

<br>

### 2 코드 위치

[서버 안내](../../../../manyak-server/CLAUDE.md), [Flyway](../../../../manyak-server/src/main/resources/db/migration), [DB 문서](../../../../manyak-server/dbdoc)에서 코드와 스키마를 대조한다.

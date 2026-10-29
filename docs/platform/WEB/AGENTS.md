# WEB 플랫폼 기반

여러 도메인이 사용하는 컴포넌트, 데이터 상태, 실행, 관측과 빌드 규칙을 관리한다. 사용자 기능은 [도메인 목록](../../domain/AGENTS.md)에서 선택하고 앱 셸과 진입은 [공통 사용자 경험 WEB](../../experience/WEB/AGENTS.md)에서 확인한다.

<br>

### 문서 역할

| 문서 | 내용 |
|---|---|
| [CONTRACT.md](CONTRACT.md) | 웹 공용 연동 |
| [COMPONENT-ARCHITECTURE.md](COMPONENT-ARCHITECTURE.md) | 웹 공용 구성 |
| [STATE-MANAGEMENT.md](STATE-MANAGEMENT.md) | 웹 기반 상태 관리 |
| [EXECUTION.md](EXECUTION.md) | 웹 기반 실행 |
| [VERIFICATION.md](VERIFICATION.md) | 웹 기반 검증 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | 웹 공용 배포 |
| [DECISIONS.md](DECISIONS.md) | WEB 결정 기록 |

공통 전송 계약은 [공통 연동 계약](../CLIENT-CONTRACT.md), 공통 배포 절차는 [운영 문서](../../operations/AGENTS.md)를 따른다. 위 표의 계약, 구현, 검증과 배포 순서로 읽으며 사용자 목표를 새로 정의하지 않는다.

<br>

### 코드 위치

- [package.json](../../../../manyak-web/package.json)
- [pnpm-lock.yaml](../../../../manyak-web/pnpm-lock.yaml)
- [AGENTS.md](../../../../manyak-web/AGENTS.md)
- [tools/orval/stabilize-operation-ids.ts](../../../../manyak-web/tools/orval/stabilize-operation-ids.ts)
- [src/api/mutator/custom-instance.ts](../../../../manyak-web/src/api/mutator/custom-instance.ts)
- [src/lib/query-client.ts](../../../../manyak-web/src/lib/query-client.ts)
- [src/lib/contained-image.ts](../../../../manyak-web/src/lib/contained-image.ts)
- [src/lib/image-zoom.ts](../../../../manyak-web/src/lib/image-zoom.ts)
- [next.config.ts](../../../../manyak-web/next.config.ts)
- [src/observability/analytics/share-id-redaction.ts](../../../../manyak-web/src/observability/analytics/share-id-redaction.ts)
- [playwright.config.ts](../../../../manyak-web/playwright.config.ts)
- [e2e](../../../../manyak-web/e2e)

# WEB 플랫폼 기반

여러 도메인이 사용하는 컴포넌트, 데이터 상태, 실행, 관측과 빌드 규칙을 관리한다. 사용자 기능은 [도메인 목록](../../domain/AGENTS.md)에서 선택하고 앱 셸과 진입은 [공통 UI WEB](../../ui/WEB/AGENTS.md)에서 확인한다.

<br>

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [4-1-CONTRACT.md](4-1-CONTRACT.md) | 4-1 연동 계약: 웹 |
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 컴포넌트 구조: 웹 |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 상태 관리: 웹 |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 실행: 웹 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 검증: 웹 |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 6 배포: 웹 |
| [DECISIONS.md](DECISIONS.md) | WEB 결정 기록 |

공통 전송 계약은 [CLIENT 기반](../CLIENT/AGENTS.md), 공통 배포 절차는 [운영 문서](../../operations/AGENTS.md)를 따른다. 이 폴더에서 사용자 목표를 새로 정의하지 않는다.

<br>

### 2 코드 위치

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

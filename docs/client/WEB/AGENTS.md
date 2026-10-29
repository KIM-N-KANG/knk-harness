# 공용 WEB 클라이언트

단계마다 [공통](../AGENTS.md) 다음 이 플랫폼의 같은 단계 문서를 읽는다. 도메인 기능은 해당 CLIENT 세트가 기준이다.

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 웹 공용 요구사항 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 웹 공용 경로 |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 웹 공용 이동 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 웹 공용 표현 |
| [4-1-CONTRACT.md](4-1-CONTRACT.md) | 4-1 웹 공용 연동 |
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 웹 공용 구성 |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 웹 공용 상태 관리 |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 웹 공용 실행 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 웹 공용 검증 |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 6 웹 공용 배포 |
| [DECISIONS.md](DECISIONS.md) | 확정 결정과 적용 범위 이력 |

### 2 코드 위치

- [package.json](../../../../manyak-web/package.json)
- [pnpm-lock.yaml](../../../../manyak-web/pnpm-lock.yaml)
- [AGENTS.md](../../../../manyak-web/AGENTS.md)
- [tools/orval/stabilize-operation-ids.ts](../../../../manyak-web/tools/orval/stabilize-operation-ids.ts)
- [src/api/mutator/custom-instance.ts](../../../../manyak-web/src/api/mutator/custom-instance.ts)
- [src/lib/query-client.ts](../../../../manyak-web/src/lib/query-client.ts)
- [src/lib/contained-image.ts](../../../../manyak-web/src/lib/contained-image.ts)
- [src/lib/image-zoom.ts](../../../../manyak-web/src/lib/image-zoom.ts)
- [src/constants/site.ts](../../../../manyak-web/src/constants/site.ts)
- [src/components/providers/in-app-navigation-tracker.tsx](../../../../manyak-web/src/components/providers/in-app-navigation-tracker.tsx)
- [src/lib/in-app-navigation.ts](../../../../manyak-web/src/lib/in-app-navigation.ts)
- [src/lib/return-to-main-tab.ts](../../../../manyak-web/src/lib/return-to-main-tab.ts)
- [src/hooks/use-scroll-restoration.ts](../../../../manyak-web/src/hooks/use-scroll-restoration.ts)
- [src/lib/history-layer-stack.ts](../../../../manyak-web/src/lib/history-layer-stack.ts)
- [src/lib/history-layers.ts](../../../../manyak-web/src/lib/history-layers.ts)
- [src/hooks/use-back-layer.ts](../../../../manyak-web/src/hooks/use-back-layer.ts)
- [src/hooks/use-prevent-page-leave.ts](../../../../manyak-web/src/hooks/use-prevent-page-leave.ts)
- [src/components/layout/ios-input-zoom-lock.tsx](../../../../manyak-web/src/components/layout/ios-input-zoom-lock.tsx)
- [src/components/common/snap-strip.tsx](../../../../manyak-web/src/components/common/snap-strip.tsx)
- [src/hooks/use-drag-scroll.ts](../../../../manyak-web/src/hooks/use-drag-scroll.ts)
- [src/components/layout/app-banner.tsx](../../../../manyak-web/src/components/layout/app-banner.tsx)
- [src/lib/app-banner.ts](../../../../manyak-web/src/lib/app-banner.ts)
- [src/lib/in-app-browser.ts](../../../../manyak-web/src/lib/in-app-browser.ts)
- [src/lib/external-browser-escape.ts](../../../../manyak-web/src/lib/external-browser-escape.ts)
- [src/constants/app-banner.ts](../../../../manyak-web/src/constants/app-banner.ts)
- [src/app/(share)/app/page.tsx](../../../../manyak-web/src/app/(share)/app/page.tsx)
- [src/features/app/components/app-share-screen.tsx](../../../../manyak-web/src/features/app/components/app-share-screen.tsx)
- [src/lib/app-share.ts](../../../../manyak-web/src/lib/app-share.ts)
- [src/features/app/constants.ts](../../../../manyak-web/src/features/app/constants.ts)
- [src/components/layout/main-header.tsx](../../../../manyak-web/src/components/layout/main-header.tsx)
- [src/components/common/go-back-button.tsx](../../../../manyak-web/src/components/common/go-back-button.tsx)
- [src/constants/not-found.ts](../../../../manyak-web/src/constants/not-found.ts)
- [src/app/globals.css](../../../../manyak-web/src/app/globals.css)
- [src/hooks/use-delayed-loading.ts](../../../../manyak-web/src/hooks/use-delayed-loading.ts)
- [next.config.ts](../../../../manyak-web/next.config.ts)
- [src/components/layout/in-app-scroll-anchor.tsx](../../../../manyak-web/src/components/layout/in-app-scroll-anchor.tsx)
- [src/observability/analytics/share-id-redaction.ts](../../../../manyak-web/src/observability/analytics/share-id-redaction.ts)
- [playwright.config.ts](../../../../manyak-web/playwright.config.ts)
- [e2e](../../../../manyak-web/e2e)

정확한 라이브러리와 React Compiler 설정, 생성 및 검사 명령은 [package.json](../../../../manyak-web/package.json), [웹 지침](../../../../manyak-web/AGENTS.md)과 lockfile을 기준으로 한다.

### 3 작업 규칙

번호 문서에는 현재 계약과 구조를, 실행 결과는 PR 및 CI에 남긴다. 원문 QA의 과거 기대와 현재 계약이 다르면 차이를 명시한다. 문서 작성과 검토를 서브에이전트에 맡기지 않는다.

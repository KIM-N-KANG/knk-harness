# APP WEB

단계마다 [APP 공통](../AGENTS.md) 다음 이 플랫폼의 같은 단계 문서를 읽는다. 네트워크, 공통 상태와 검증 도구는 [WEB 기반](../../../../platform/WEB/AGENTS.md)에 둔다.

<br>

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 웹 공용 요구사항 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 웹 공용 경로 |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 웹 공용 이동 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 웹 공용 표현 |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 웹 공용 상태 관리 |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 웹 앱 실행 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 웹 공용 검증 |
| [DECISIONS.md](DECISIONS.md) | WEB 결정 기록 |

<br>

### 2 코드 위치

- [src/constants/site.ts](../../../../../../manyak-web/src/constants/site.ts)
- [src/components/providers/in-app-navigation-tracker.tsx](../../../../../../manyak-web/src/components/providers/in-app-navigation-tracker.tsx)
- [src/lib/in-app-navigation.ts](../../../../../../manyak-web/src/lib/in-app-navigation.ts)
- [src/lib/return-to-main-tab.ts](../../../../../../manyak-web/src/lib/return-to-main-tab.ts)
- [src/hooks/use-scroll-restoration.ts](../../../../../../manyak-web/src/hooks/use-scroll-restoration.ts)
- [src/lib/history-layer-stack.ts](../../../../../../manyak-web/src/lib/history-layer-stack.ts)
- [src/lib/history-layers.ts](../../../../../../manyak-web/src/lib/history-layers.ts)
- [src/hooks/use-back-layer.ts](../../../../../../manyak-web/src/hooks/use-back-layer.ts)
- [src/hooks/use-prevent-page-leave.ts](../../../../../../manyak-web/src/hooks/use-prevent-page-leave.ts)
- [src/components/layout/ios-input-zoom-lock.tsx](../../../../../../manyak-web/src/components/layout/ios-input-zoom-lock.tsx)
- [src/components/common/snap-strip.tsx](../../../../../../manyak-web/src/components/common/snap-strip.tsx)
- [src/hooks/use-drag-scroll.ts](../../../../../../manyak-web/src/hooks/use-drag-scroll.ts)
- [src/components/layout/app-banner.tsx](../../../../../../manyak-web/src/components/layout/app-banner.tsx)
- [src/lib/app-banner.ts](../../../../../../manyak-web/src/lib/app-banner.ts)
- [src/lib/in-app-browser.ts](../../../../../../manyak-web/src/lib/in-app-browser.ts)
- [src/lib/external-browser-escape.ts](../../../../../../manyak-web/src/lib/external-browser-escape.ts)
- [src/constants/app-banner.ts](../../../../../../manyak-web/src/constants/app-banner.ts)
- [src/app/(share)/app/page.tsx](../../../../../../manyak-web/src/app/(share)/app/page.tsx)
- [src/features/app/components/app-share-screen.tsx](../../../../../../manyak-web/src/features/app/components/app-share-screen.tsx)
- [src/lib/app-share.ts](../../../../../../manyak-web/src/lib/app-share.ts)
- [src/features/app/constants.ts](../../../../../../manyak-web/src/features/app/constants.ts)
- [src/components/layout/main-header.tsx](../../../../../../manyak-web/src/components/layout/main-header.tsx)
- [src/components/common/go-back-button.tsx](../../../../../../manyak-web/src/components/common/go-back-button.tsx)
- [src/constants/not-found.ts](../../../../../../manyak-web/src/constants/not-found.ts)
- [src/app/globals.css](../../../../../../manyak-web/src/app/globals.css)
- [src/hooks/use-delayed-loading.ts](../../../../../../manyak-web/src/hooks/use-delayed-loading.ts)
- [src/components/layout/in-app-scroll-anchor.tsx](../../../../../../manyak-web/src/components/layout/in-app-scroll-anchor.tsx)

공통 실행과 검증 도구의 확인 항목은 [플랫폼 검증](../../../../platform/WEB/5-1-VERIFICATION.md)을 함께 확인한다.

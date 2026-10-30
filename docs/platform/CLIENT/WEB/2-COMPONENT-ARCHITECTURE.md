# 2 컴포넌트 구조: 웹

기준: [표현](../../../ui/WEB/3-3-LAYOUT.md), [웹 연동](1-CONTRACT.md).

<br>

### 2-1 구성과 의존

| 경계 | 책임 |
|---|---|
| 렌더링 | Next.js와 React, TypeScript. 서버 메타데이터와 클라이언트 상호작용 분리 |
| 데이터 | TanStack Query, Orval 생성 클라이언트와 Zod 입력 검증 |
| UI | Base UI와 shadcn, CVA, Tailwind, Motion, Sonner와 next-themes |
| 루트 | Query, 관측, Motion과 테마 Provider, 토스트와 동의 게이트. 게이트 안에서 회원 부수 효과 실행 |
| 라우트 그룹 | 권한이 아닌 셸 구분. 메인만 헤더와 탭 공유, 상세와 채팅은 루트 상속, 다른 화면은 자체 헤더 |
| HTTP | 브라우저는 같은 출처 BFF를 사용하고 서버가 백엔드에 연결. 인증과 타임아웃은 ACCOUNT 경계 |
| 오버레이 | Drawer는 앱 프레임 포털, 투어는 body 포털. 레이어 상태와 브라우저 이벤트 어댑터를 분리 |
| 관측 | 화면별 수동 호출을 공용 진입점 하나로 모아 screen_name, Sentry breadcrumb와 활성 Amplitude로 전달 |

브라우저 이벤트가 도메인 API의 제품 정책을 결정하지 않는다. 화면별 컴포넌트와 경로 원본은 안내 문서에서 찾는다.

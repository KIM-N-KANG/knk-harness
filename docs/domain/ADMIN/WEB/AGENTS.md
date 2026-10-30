# AGENTS.md

ADMIN 도메인 웹 명세를 읽고 수정할 때 필요한 문서와 코드 위치를 안내한다. 관리자 페이지의 사이드바와 워드마크, 대시보드 그룹의 개요와 성장, 스토리, 채팅, 결제, 운영 지표 화면, 관리 목록과 지표 화면의 상호 링크, 이프 내역 화면, 검수 제출 화면, 스토리 목록과 상세의 공개 중단, 채팅 상세의 요약 끝 턴, 캠페인 상세의 열람을 다룬다. 회원, 스토리, 오리지널, 채팅, 결제, 공지, 감사 로그, 알림 화면 전체는 이 세트에 아직 없다.

명세 본문과 설정값은 이 문서에 복사하지 않는다.

<br>

### 1. 문서의 역할과 읽는 순서

| 문서 | 정하는 것 |
|---|---|
| [1-1-BACKGROUND.md](1-1-BACKGROUND.md) | 화면이 필요한 이유, 대상 사용자, 용어 |
| [1-2-REQUIREMENTS.md](1-2-REQUIREMENTS.md) | 지원 범위, 화면 크기, 접근성과 성능 목표 |
| [2-1-INFORMATION-ARCHITECTURE.md](2-1-INFORMATION-ARCHITECTURE.md) | 메뉴와 경로, 예전 경로 이동, 화면별 탭과 영역, 요약 수치, 차트, 기본 선택, 화면 문구 |
| [2-2-LAYOUT.md](2-2-LAYOUT.md) | 화면별 배치 순서와 격자 |
| [2-3-UI-DESIGN-SYSTEM.md](2-3-UI-DESIGN-SYSTEM.md) | 디자인 기준 문서와의 관계, 차트 규칙, 계열 순서와 색, 숫자 표기 |
| [2-4-COMPONENT-ARCHITECTURE.md](2-4-COMPONENT-ARCHITECTURE.md) | 공용 구성 요소와 화면별 구성 요소의 책임 |
| [2-5-STATE-MANAGEMENT.md](2-5-STATE-MANAGEMENT.md) | URL 상태, 서버 상태, 브라우저 저장 |
| [3-1-CONTRACT.md](3-1-CONTRACT.md) | 화면이 부르는 BFF 경로와 서버 계약의 대응, 보내는 쿼리 |
| [3-2-DATA-INTEGRATION.md](3-2-DATA-INTEGRATION.md) | 조회, 캐시, 재요청, 데이터 모드 |
| [3-4-INTERACTION-FLOWS.md](3-4-INTERACTION-FLOWS.md) | 화면 진입, 탭 전환, 기간 변경, 광고 캠페인 선택, 준비 중 재요청, 전환 퍼널 카드, 스토리 공개 중단의 흐름 |
| [4-1-ERROR-HANDLING.md](4-1-ERROR-HANDLING.md) | 불러오는 중, 실패, 사용 불가, 준비 중, 값 없음, 기간 오류의 표시와 복귀 |
| [4-2-QUALITY.md](4-2-QUALITY.md) | 접근성, 인증 상태, 분석 이벤트 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 화면별 테스트 케이스와 검증 명령 |
| [5-2-DEPLOYMENT.md](5-2-DEPLOYMENT.md) | 배포 경로, 환경 변수, 배포 조건, 되돌리기 |
| [DECISIONS.md](DECISIONS.md) | 결정의 이력 |

- 처음 읽을 때는 1-1부터 3-4까지 순서대로 읽는다. 4는 품질, 5는 검증과 배포다.
- 서버 계약의 기준은 BACKEND 세트의 4-2다. 이 세트는 웹이 쓰는 범위와 화면 규칙만 정한다. ([BACKEND 4-2 계약](../BACKEND/4-2-CONTRACT.md))
- 색, 글꼴, 간격 같은 디자인 토큰의 기준은 관리자 저장소의 디자인 문서다. ([manyak-admin DESIGN.md](https://github.com/KIM-N-KANG/manyak-admin/blob/dev/docs/DESIGN.md))

<br>

### 2. 작업별 참조

| 하려는 일 | 먼저 볼 곳 | 함께 볼 곳 |
|---|---|---|
| 지표 화면에 지표나 차트 추가 | [2-1 정보 구조](2-1-INFORMATION-ARCHITECTURE.md)의 그 도메인 화면 절과 [2-1-17 지표 정의](2-1-INFORMATION-ARCHITECTURE.md#2-1-17-지표-정의) | [2-3-3 계열 순서와 모양](2-3-UI-DESIGN-SYSTEM.md#2-3-3-계열-순서와-모양)<br>[3-1 계약](3-1-CONTRACT.md)<br>[5-1 검증](5-1-VERIFICATION.md) |
| 탭의 플랫폼이나 대상 지원 변경 | [2-1-2 분석 화면 공통 요소](2-1-INFORMATION-ARCHITECTURE.md#2-1-2-분석-화면-공통-요소)의 플랫폼과 대상 | [3-1-2 보내는 쿼리](3-1-CONTRACT.md#3-1-2-보내는-쿼리)<br>[5-1 검증](5-1-VERIFICATION.md) |
| 기간 상한이나 기본 기간 변경 | [2-1-2 분석 화면 공통 요소](2-1-INFORMATION-ARCHITECTURE.md#2-1-2-분석-화면-공통-요소)의 기간과 화면 절의 탭과 영역 표 | [BACKEND 4-1-20 Amplitude 조회 공통](../BACKEND/4-1-PIPELINES.md#4-1-20-amplitude-조회-공통)<br>[3-4 흐름](3-4-INTERACTION-FLOWS.md) |
| 상태 문구 변경 | [4-1 오류 처리](4-1-ERROR-HANDLING.md) | [2-1 정보 구조](2-1-INFORMATION-ARCHITECTURE.md)의 화면 문구 |
| 메뉴 추가나 경로 변경 | [2-1-1 메뉴와 경로](2-1-INFORMATION-ARCHITECTURE.md#2-1-1-메뉴와-경로)의 메뉴와 예전 경로 이동 | [2-5 상태](2-5-STATE-MANAGEMENT.md) |
| 서버 응답 필드가 바뀜 | [3-1 계약](3-1-CONTRACT.md) | [5-2-3 배포 조건](5-2-DEPLOYMENT.md#5-2-3-배포-조건) |
| 이미 내린 결정인지 확인 | [DECISIONS.md](DECISIONS.md) | [BACKEND DECISIONS.md](../BACKEND/DECISIONS.md) |

<br>

### 3. 명세와 코드의 대응

코드 경로는 `manyak-admin` 저장소 루트 아래 `src/`다.

| 구성 요소 | 구현 위치 (`manyak-admin` 기준) | 사용 범위 |
|---|---|---|
| 사이드바와 메뉴 | `features/navigation/`, `components/admin/` | 2-1-1 |
| 워드마크 | `components/admin/` | 2-1-1 |
| 기간 선택기 | `features/dashboard/` | 2-1-2, 2-5 |
| 개요, 분포 카드 | `features/dashboard/` | 2-1-3, 2-1-10 |
| 성장, 스토리, 채팅, 결제, 운영 화면 | `features/analytics/` | 2-1-4~2-1-8, 2-1-10 |
| 이프 내역, 프로모션 | `features/credits/` | 2-1-9 |
| 검수 제출 목록과 상세 | `features/moderation/` | 2-1-11 |
| 공지 태그, 게시, 알림 보내기 | `features/notices/` | 2-1-13, 5-1-11 |
| 캠페인 작성의 이동 대상 | `features/notifications/` | 2-1-20, 5-1-17 |
| 캠페인 상세의 공지 알림 실패 사유 | `features/notifications/` | 2-1-21, 5-1-18 |
| 회원 목록과 상세의 누적 턴 | `features/shared/`, `features/members/` | 2-1-12, 5-1-8 |
| 스토리 상세의 스토리 설정 | `features/stories/` | 2-1-14, 5-1-12 |
| 스토리와 채팅의 삭제 필터와 삭제 표시 | `features/shared/` | 2-1-15, 5-1-13 |
| 스토리 공개 중단 | `features/stories/` | 2-1-16, 3-4-5, 5-1-14 |
| 채팅 상세의 요약 끝 턴 | `features/shared/`, `features/chats/` | 2-1-18, 5-1-15 |
| 캠페인 상세의 열람 | `features/notifications/` | 2-1-19, 5-1-16 |
| 화면 경로 | `app/(admin)/` | 2-1-1 |
| BFF route handler와 서버 전달 | `app/api/`, `api/` | 3-1, 3-2 |
| 생성 Zod와 연산 목록 | `api/generated/` | 3-1 |
| 고정 데이터 | `fixtures/` | 3-2 |
| 테스트 | `tests/` | 5-1 |

<br>

### 4. 작성 규칙과 검증 명령

| 항목 | 위치 |
|---|---|
| 문서별 작성 기준 | [클라이언트 명세 작성 가이드](../../../reference/CLIENT-SPEC-WRITING-GUIDE.md) |
| 문체와 파일명 | [제품 Spec 작성 가이드](../../../reference/PRODUCT-SPEC-WRITING-GUIDE.md) |
| 화면 용어 | [용어집](../../../reference/GLOSSARY.md)과 [BACKEND DECISIONS](../BACKEND/DECISIONS.md) 결정 11 |
| 코드 규칙과 명령 | `manyak-admin`의 `AGENTS.md` |
| 문서 변경 뒤 검사 | `git diff --check` 실행<br>링크, 앵커, 참조한 절 번호 확인 |
| 코드 검증 | 관리자 저장소에서 `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build` |

- 명세의 작성, 수정, 검토를 서브에이전트에 맡기지 않는다.
- 화면 문구에 em dash와 가운뎃점 나열을 쓰지 않는다. 안내 문장은 "해 주세요"로 끝내고 상태 제목은 명사형으로 끝낸다.
- 화면에 늘 보이는 설명 문장을 두지 않는다. 꼭 필요한 설명은 그 대상의 제목 옆 "?" 툴팁으로 둔다. ([2-3-5 문구 표기](2-3-UI-DESIGN-SYSTEM.md#2-3-5-문구-표기))
- 절의 제목이나 위치를 바꾸면 이 문서와 다른 문서의 링크도 고친다.

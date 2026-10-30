# AGENTS.md

ADMIN 도메인 백엔드 명세를 읽고 수정할 때 필요한 문서와 코드 위치를 안내한다. 관리자 로그인과 토큰, 관리자 판정 필터, 감사 로그, 대시보드 요약과 차트, 스토리와 채팅과 회원과 결제의 목록과 상세, 스토리 설정, 이프 내역, Amplitude 분석 지표와 캠페인 분석과 푸시 열람과 캠페인 열람, 사용자와 전환과 기능 지표, Play 설치 지표, 인프라 지표와 DB 테이블 크기를 다룬다. 다른 도메인의 관리자 API는 그 도메인 세트가 정한다.

명세 본문과 설정값은 이 문서에 복사하지 않는다.

<br>

### 1. 문서의 역할과 읽는 순서

| 문서 | 정하는 것 |
|---|---|
| [1-BACKGROUND.md](1-BACKGROUND.md) | 배경, 역할, 주체, 용어 |
| [2-REQUIREMENTS.md](2-REQUIREMENTS.md) | 요구 주체, 기대하는 동작, 다른 주체와의 역할 분담, 제품 제약, 대시보드 지표와 분포 차트 정의, 데이터 보존 |
| [3-1-SOFTWARE-ARCHITECTURE.md](3-1-SOFTWARE-ARCHITECTURE.md) | 개요, 배경과 목표, 품질 속성, 배포 단위, 모듈 구조, 의존 방향, 도메인 모델 |
| [3-2-DB-SCHEMA.md](3-2-DB-SCHEMA.md) | 테이블, 컬럼, 제약, 인덱스, 감사 로그 작업 이름, Amplitude 조회 값 저장, 데이터 수명 |
| [3-3-CONVENTIONS.md](3-3-CONVENTIONS.md) | 이름, 계층 책임, 검증, 이벤트, 테스트 규칙 |
| [4-1-PIPELINES.md](4-1-PIPELINES.md) | 공통 처리, 로그인, 판정, 감사 기록, 목록 공통, 대시보드, 스토리, 채팅, 회원, 결제, 이프 내역, 감사 로그 조회, 분석 지표, 설치 지표, 캠페인 분석, 사용자와 전환과 기능 지표, Amplitude 조회 공통, 인프라 지표, DB 테이블 크기 |
| [4-2-CONTRACT.md](4-2-CONTRACT.md) | 관리자 API 공통 규칙과 토큰, 페이지와 검색 규칙, 엔드포인트, 다른 도메인과의 경계 |
| [5-1-SECURITY.md](5-1-SECURITY.md) | 인증 수준과 토큰, 권한 판정, 계정 상태, 감사와 접속 기록, 입력 검증, 비밀값과 개인정보, 수용한 한계 |
| [5-2-CONCURRENCY.md](5-2-CONCURRENCY.md) | 감사 기록 트랜잭션, 멱등, 역할 변경과의 경쟁, 수용한 경쟁 |
| [5-3-ERROR-HANDLING.md](5-3-ERROR-HANDLING.md) | 응답 규칙, 오류 분류, 복구, 시간 한도 |
| [5-4-OBSERVABILITY.md](5-4-OBSERVABILITY.md) | 관측 스택, 식별자, 로그, 지표, 트레이스, 알림 |
| [5-5-TEST-CASES.md](5-5-TEST-CASES.md) | 테스트 범위와 케이스<br>관리자 경로 회귀 테스트 |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 배포 단위, 환경 변수와 분석 도구와 설치 보고서 시크릿, 조건, 역할 부여, 되돌리기 |
| [DECISIONS.md](DECISIONS.md) | 결정의 이력 |

- 처음 읽을 때는 1부터 4-2까지 순서대로 읽어 배경, 요구사항, 설계, 계약을 확인한다. 5는 품질과 검증, 6은 배포를 다룬다.
- 앞 단계의 결정이 뒤 단계의 기준이다. 구현에 맞추기 위해 앞 단계의 결정을 임의로 바꾸지 않는다.
- 다른 도메인의 관리자 API는 그 도메인 세트의 4-2에 있고 인증 수준과 토큰 규칙만 이 세트의 4-2-1을 따른다. 관리자 화면의 알림 통계도 NOTIFICATION 세트의 4-2에서 정한다.
- 다른 도메인과의 경계는 계약 문서의 마지막 절에 있다. ([4-2-43 다른 도메인과의 경계](4-2-CONTRACT.md#4-2-43-다른-도메인과의-경계))

<br>

### 2. 작업별 참조

| 하려는 일 | 먼저 볼 곳 | 함께 볼 곳 |
|---|---|---|
| 요청과 응답 필드 변경 | [4-2 계약](4-2-CONTRACT.md) | [4-1 처리 흐름](4-1-PIPELINES.md)<br>[6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 테이블과 컬럼 변경 | [3-2 DB 스키마](3-2-DB-SCHEMA.md) | [3-3-5 테스트와 검증 도구](3-3-CONVENTIONS.md#3-3-5-테스트와-검증-도구)<br>[6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 다른 도메인에 관리자 API 추가 | [4-2-1 공통 규칙과 헤더](4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더) | [4-1-4 감사 기록](4-1-PIPELINES.md#4-1-4-감사-기록), [3-2-4 감사 로그](3-2-DB-SCHEMA.md#3-2-4-감사-로그)의 작업 이름, [5-5-3 권한 판정과 회귀](5-5-TEST-CASES.md#5-5-3-권한-판정과-회귀) |
| 토큰 정책 변경 | [5-1-1 인증 수준과 토큰](5-1-SECURITY.md#5-1-1-인증-수준과-토큰) | [5-3-5 재시도와 시간 한도](5-3-ERROR-HANDLING.md#5-3-5-재시도와-시간-한도)<br>[DECISIONS.md](DECISIONS.md) |
| 분석 도구 지표 변경 | [2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약)의 캠페인 분석 지표, 푸시 열람 지표, 사용자와 전환과 기능과 품질 지표 | [4-1-20 Amplitude 조회 공통](4-1-PIPELINES.md#4-1-20-amplitude-조회-공통)의 비용 산식과 엔드포인트별 비용 표<br>[DECISIONS.md](DECISIONS.md) 결정 12, 13, 15, 28, 35, 36, 46~54 |
| 지표나 분포 차트 추가 | [2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약) | [4-1-7 대시보드 차트](4-1-PIPELINES.md#4-1-7-대시보드-차트)<br>[4-2-4 대시보드 차트](4-2-CONTRACT.md#4-2-4-대시보드-차트)의 목록 링크<br>[3-2-6 참조하는 다른 도메인의 컬럼](3-2-DB-SCHEMA.md#3-2-6-참조하는-다른-도메인의-컬럼) |
| 목록 필터나 정렬 추가 | [4-2-1 공통 규칙과 헤더](4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더)의 페이지와 검색 규칙 | [4-1-5 목록 공통 처리](4-1-PIPELINES.md#4-1-5-목록-공통-처리)<br>[5-1-4 감사와 접속 기록](5-1-SECURITY.md#5-1-4-감사와-접속-기록) |
| 관리자 역할 부여와 회수 | [6-5 설정 변경](6-DEPLOYMENT.md#6-5-설정-변경) | [5-1-2 권한 판정](5-1-SECURITY.md#5-1-2-권한-판정) |
| 동시 요청 문제 | [5-2 동시성](5-2-CONCURRENCY.md) | [4-1 처리 흐름](4-1-PIPELINES.md) |
| 로그나 지표 추가 | [5-4 관측](5-4-OBSERVABILITY.md) | [5-4-8 수집 조건과 실패 처리](5-4-OBSERVABILITY.md#5-4-8-수집-조건과-실패-처리) |
| 이미 내린 결정인지 확인 | [DECISIONS.md](DECISIONS.md) | 해당 결정에서 연결한 명세 절 |

<br>

### 3. 명세와 코드의 대응

코드 경로는 `manyak-server` 저장소 루트 아래 `src/main/kotlin/com/knk/manyak/`이다. 관리자 패키지는 이 명세로 새로 만든다. 신원 검증기와 보안 필터 사슬은 ACCOUNT 세트에 속한다.

| 구성 요소 | 구현 위치 (`manyak-server` 기준) | 사용 범위 |
|---|---|---|
| 관리자 API 계층 | `admin/controller/` | 4-2-2~4-2-42 |
| 로그인, 토큰, 감사 기록, 대시보드, 목록과 상세 | `admin/service/`<br>`admin/repository/`의 조회 쿼리 | 4-1-2~4-1-13 |
| 분석 도구 클라이언트, 캠페인과 사용자와 전환과 기능 지표, 비용 예산, 값 저장 | `admin/analytics/` | 4-1-14, 4-1-16~4-1-20, 4-1-24, 4-1-25, 3-2-5 |
| 설치 보고서 클라이언트, 해석기, 캐시 | `admin/playstats/` | 4-1-15 |
| CloudWatch와 ECS 클라이언트, 인프라 지표 조립, DB 테이블 크기 조회 | `admin/infra/` | 4-1-21, 4-1-22 |
| 관리자 판정 필터와 앱 토큰 검증 보강 | `admin/security/`<br>[global/config/SecurityConfig.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/config/SecurityConfig.kt) | 4-1-1, 4-1-3, 5-1-1 |
| 신원 검증기 | [auth/social/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/auth/social/) | 4-1-2 |
| 토큰 발급 기반 | [auth/jwt/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/auth/jwt/)<br>[auth/config/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/auth/config/) | 4-2-1 관리자 토큰 |
| 모델과 저장 계층 | `admin/entity/`<br>`admin/repository/` | 3-2 DB 스키마 |
| 오류 | [global/error/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/error/) | 5-3 |
| 관측 | [global/observability/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/observability/) | 5-4 관측 |
| 마이그레이션 | [db/migration/](../../../../../manyak-server/src/main/resources/db/migration/)<br>[dbdoc/](../../../../../manyak-server/dbdoc/) | 3-2 DB 스키마 |
| 테스트 | `src/test/kotlin/com/knk/manyak/admin/`<br>`http/admin/` | 5-5 테스트 케이스 |
| 배포 | [.github/workflows/](../../../../../manyak-server/.github/workflows/)<br>[Dockerfile](../../../../../manyak-server/Dockerfile) | 6 배포 |

<br>

### 4. 작성 규칙과 검증 명령

| 항목 | 위치 |
|---|---|
| 문서별 작성 기준 | [백엔드 명세 작성 가이드](../../../REFERENCE/BACKEND-SPEC-WRITING-GUIDE.md) |
| 문체와 파일명 | [제품 Spec 작성 가이드](../../../REFERENCE/PRODUCT-SPEC-WRITING-GUIDE.md) |
| 하네스 전체 지침 | 하네스 루트의 `AGENTS.md` |
| 코드 규칙 | `manyak-server`의 `CLAUDE.md` |
| 문서 변경 뒤 검사 | `git diff --check` 실행<br>링크, 앵커, 참조한 절 번호 확인 |
| 테스트 실행 | 서버 저장소에서 `./gradlew test` 실행<br>DB 제약은 `scripts/gen-db-docs.sh`로 실제 PostgreSQL에서 검증 |
| 관리자 경로 회귀 테스트 | 등록된 핸들러 매핑을 수집하는 통합 테스트 1개<br>새 관리자 엔드포인트마다 수집 수가 늘어나는지 확인 |

- 명세의 작성, 수정, 검토를 서브에이전트에 맡기지 않는다.
- 실제 비밀값, 신원 증명, 관리자 토큰을 문서에 넣지 않는다.
- 코드와 설정에서 확인할 수 없는 정책, 필드, 계약을 추측해 적지 않는다.
- 절의 제목이나 위치를 바꾸면 이 문서와 다른 문서의 링크도 고친다.

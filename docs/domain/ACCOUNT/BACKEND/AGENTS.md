# AGENTS.md

ACCOUNT 도메인 백엔드 명세를 읽고 수정할 때 필요한 문서와 코드 위치를 안내한다. 소셜 인증과 동의, 세션과 토큰, 게스트 이관, 계정 연동, 프로필, 페르소나, 탈퇴와 재가입, 초대, 내 콘텐츠 목록, 관리자의 계정 정지와 해제를 다룬다.

명세 본문과 설정값은 이 문서에 복사하지 않는다.

<br>

### 1. 문서의 역할

| 문서 | 정하는 것 |
|---|---|
| [1-BACKGROUND.md](1-BACKGROUND.md) | 배경, 역할, 주체, 용어 |
| [2-REQUIREMENTS.md](2-REQUIREMENTS.md) | 요구 주체, 기대하는 동작, 다른 주체와의 역할 분담, 제품 제약, 데이터 보존 |
| [3-1-SOFTWARE-ARCHITECTURE.md](3-1-SOFTWARE-ARCHITECTURE.md) | 개요, 배경과 목표, 품질 속성, 배포 단위, 모듈 구조, 의존 방향, 도메인 모델 |
| [3-2-DB-SCHEMA.md](3-2-DB-SCHEMA.md) | 테이블, 컬럼, 제약, 인덱스, Redis 키, 데이터 수명 |
| [3-3-CONVENTIONS.md](3-3-CONVENTIONS.md) | 이름, 계층 책임, 검증, 이벤트, 테스트 규칙 |
| [4-1-PIPELINES.md](4-1-PIPELINES.md) | 공통 처리, 신원 검증, 엔드포인트별 처리 흐름, 로그인 후속 처리, 계정 생성과 재가입, 계정 정지와 해제 |
| [4-2-CONTRACT.md](4-2-CONTRACT.md) | 클라이언트, 관리자 페이지, 다른 도메인과의 계약 |
| [5-1-SECURITY.md](5-1-SECURITY.md) | 인증 수준과 토큰, 접근 판정, 계정 상태와 동의 게이트, 신원 증명 검증, 입력 검증, 비밀값과 개인정보, 수용한 한계 |
| [5-2-CONCURRENCY.md](5-2-CONCURRENCY.md) | 사용자 행 잠금, 멱등, 유니크 위반, 토큰 회전 원자성, 수용한 경쟁 |
| [5-3-ERROR-HANDLING.md](5-3-ERROR-HANDLING.md) | 응답 규칙, 앱 코드, 오류 분류, 복구, 시간 한도 |
| [5-4-OBSERVABILITY.md](5-4-OBSERVABILITY.md) | 관측 스택, 식별자, 로그, 지표, 트레이스, 알림, 분석 이벤트 |
| [5-5-TEST-CASES.md](5-5-TEST-CASES.md) | 테스트 범위와 케이스 |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 배포 단위, 환경 변수, 조건, 되돌리기 |
| [DECISIONS.md](DECISIONS.md) | 결정의 이력 |

- 앞 단계의 결정이 뒤 단계의 기준이다. 구현에 맞추기 위해 앞 단계의 결정을 임의로 바꾸지 않는다.
- 미정으로 표시된 항목을 추측으로 채우지 않는다.
- 관리자 인증 수준과 토큰은 ADMIN 세트가 정한다.
- 다른 도메인과의 경계는 계약 문서의 마지막 절에 있다. ([4-2-28 다른 도메인과의 경계](4-2-CONTRACT.md#4-2-28-다른-도메인과의-경계))

<br>

### 2. 작업별 참조

| 하려는 일 | 먼저 볼 곳 | 함께 볼 곳 |
|---|---|---|
| 요청, 응답 필드 변경 | [4-2 계약](4-2-CONTRACT.md) | [4-1 처리 흐름](4-1-PIPELINES.md), [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 테이블, 컬럼, Redis 키 변경 | [3-2 DB 스키마](3-2-DB-SCHEMA.md) | [3-3-5 테스트와 검증 도구](3-3-CONVENTIONS.md#3-3-5-테스트와-검증-도구), [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 새 엔드포인트 | [4-2-1 공통 규칙과 헤더](4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더) | [3-3-2 계층 책임](3-3-CONVENTIONS.md#3-3-2-계층-책임), 서버 저장소 `http/auth/`, `http/user/`, `http/invite/`의 수동 호출 파일과 통합 테스트 |
| 로그인 흐름, 보상, 체험 변경 | [4-1-5 로그인 후속 처리](4-1-PIPELINES.md#4-1-5-로그인-후속-처리) | [5-2-2 멱등과 1회 처리](5-2-CONCURRENCY.md#5-2-2-멱등과-1회-처리), PAYMENT 세트 |
| 탈퇴, 재가입, 승계 변경 | [4-1-6 계정 생성과 재가입](4-1-PIPELINES.md#4-1-6-계정-생성과-재가입), [4-1-14 탈퇴](4-1-PIPELINES.md#4-1-14-탈퇴) | [5-2-1 사용자 행 잠금](5-2-CONCURRENCY.md#5-2-1-사용자-행-잠금), [DECISIONS.md](DECISIONS.md) |
| 계정 정지와 해제 | [4-2-26 계정 정지](4-2-CONTRACT.md#4-2-26-계정-정지) | [4-1-17 계정 정지와 해제](4-1-PIPELINES.md#4-1-17-계정-정지와-해제)<br>[ADMIN 4-2-1 공통 규칙과 헤더](../../ADMIN/BACKEND/4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더) |
| 토큰 정책 변경 | [5-1-1 인증 수준과 토큰](5-1-SECURITY.md#5-1-1-인증-수준과-토큰) | [5-2-4 토큰 회전의 원자성](5-2-CONCURRENCY.md#5-2-4-토큰-회전의-원자성), [5-3-5 재시도와 시간 한도](5-3-ERROR-HANDLING.md#5-3-5-재시도와-시간-한도) |
| 동의 문서 개정, 게이트 변경 | [5-1-3 계정 상태와 동의](5-1-SECURITY.md#5-1-3-계정-상태와-동의) | [6-5 설정 변경](6-DEPLOYMENT.md#6-5-설정-변경) |
| 제공자 추가, client ID 변경 | [5-1-4 신원 증명 검증](5-1-SECURITY.md#5-1-4-신원-증명-검증) | [6-3 환경 변수와 시크릿](6-DEPLOYMENT.md#6-3-환경-변수와-시크릿) |
| 오류 코드 추가 | [5-3-2 앱 코드](5-3-ERROR-HANDLING.md#5-3-2-앱-코드) | [3-3-3 요청 검증과 오류](3-3-CONVENTIONS.md#3-3-3-요청-검증과-오류) |
| 동시 요청 문제 | [5-2 동시성](5-2-CONCURRENCY.md) | [4-1 처리 흐름](4-1-PIPELINES.md) |
| 로그나 이벤트 추가 | [5-4 관측](5-4-OBSERVABILITY.md) | [5-4-8 수집 조건과 실패 처리](5-4-OBSERVABILITY.md#5-4-8-수집-조건과-실패-처리) |
| 이미 내린 결정인지 확인 | [DECISIONS.md](DECISIONS.md) | 해당 결정에서 연결한 명세 절 |

<br>

### 3. 명세와 코드의 대응

코드 경로는 `manyak-server` 저장소 루트 아래 `src/main/kotlin/com/knk/manyak/`이다. 푸시 토큰과 수신 동의는 NOTIFICATION 세트, 초안은 STORY 세트에 속한다.

| 구성 요소 | 구현 위치 (`manyak-server` 기준) | 사용 범위 |
|---|---|---|
| 인증 API 계층 | [auth/controller/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/auth/controller/), [auth/consent/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/auth/consent/), [auth/link/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/auth/link/) | 4-2-2~4-2-9 |
| 신원 검증, 소셜 인증, 계정 등록 | [auth/social/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/auth/social/), [auth/config/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/auth/config/) | 4-1-1 신원 검증, 4-1-4~4-1-6, 5-1-4 |
| 토큰 | [auth/jwt/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/auth/jwt/), [auth/token/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/auth/token/) | 4-1-8, 5-1-1, 5-2-4 |
| 세션 응답 조립 | [auth/service/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/auth/service/) | 4-1-7, 4-2-1 공통 응답 구조 |
| 이관 | [migration/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/migration/) | 4-1-10, 4-2-10 |
| 프로필, 페르소나, 탈퇴, 내 콘텐츠, 관리자 정지와 해제 | [user/controller/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/user/controller/)<br>[user/service/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/user/service/) | 4-1-11, 4-1-12, 4-1-14, 4-1-16, 4-1-17, 4-2-11~4-2-16, 4-2-21~4-2-23, 4-2-26, 4-2-27 |
| 동의 | [user/consent/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/user/consent/) | 4-1-13, 4-2-17~4-2-20, 5-1-3 |
| 초대 | [invite/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/invite/) | 4-1-15, 4-2-24, 4-2-25 |
| 모델 | [user/entity/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/user/entity/), [auth/entity/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/auth/entity/) | 3-2 DB 스키마, 3-1-7 도메인 모델 |
| 보안 필터, 오류 | [global/security/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/security/), [global/config/SecurityConfig.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/config/SecurityConfig.kt), [global/error/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/error/) | 4-1-1 공통 처리, 5-1, 5-3 |
| 관측 | [global/observability/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/observability/) | 5-4 관측 |
| 프리셋 자산 | [static/profile-presets/](../../../../../manyak-server/src/main/resources/static/profile-presets/) | 4-1-6, 4-2-12 |
| 마이그레이션 | [db/migration/](../../../../../manyak-server/src/main/resources/db/migration/), [dbdoc/](../../../../../manyak-server/dbdoc/) | 3-2 DB 스키마 |
| 테스트 | [src/test/kotlin/com/knk/manyak/auth/](../../../../../manyak-server/src/test/kotlin/com/knk/manyak/auth/), [user/](../../../../../manyak-server/src/test/kotlin/com/knk/manyak/user/), [migration/](../../../../../manyak-server/src/test/kotlin/com/knk/manyak/migration/), [invite/](../../../../../manyak-server/src/test/kotlin/com/knk/manyak/invite/), [http/auth/](../../../../../manyak-server/http/auth/), [http/user/](../../../../../manyak-server/http/user/), [http/invite/](../../../../../manyak-server/http/invite/) | 5-5 테스트 케이스 |
| 배포 | [.github/workflows/](../../../../../manyak-server/.github/workflows/), [Dockerfile](../../../../../manyak-server/Dockerfile) | 6 배포 |

<br>

### 4. 작성 규칙과 검증 명령

| 항목 | 위치 |
|---|---|
| 문서별 작성 기준 | [백엔드 명세 작성 가이드](../../../reference/BACKEND-SPEC-WRITING-GUIDE.md) |
| 문체와 파일명 | [제품 Spec 작성 가이드](../../../reference/PRODUCT-SPEC-WRITING-GUIDE.md) |
| 하네스 전체 지침 | 하네스 루트의 `AGENTS.md` |
| 코드 규칙 | `manyak-server`의 `CLAUDE.md` |
| 문서 변경 뒤 검사 | `git diff --check` 실행<br>링크, 앵커, 참조한 절 번호 확인 |
| 테스트 실행 | 서버 저장소에서 `./gradlew test` 실행<br>DB 제약은 `scripts/gen-db-docs.sh`로 실제 PostgreSQL에서 검증 |

- 명세의 작성, 수정, 검토를 서브에이전트에 맡기지 않는다.
- 실제 비밀값, 신원 증명, 코드 원문, 이메일, 사용자 입력 원문을 문서에 넣지 않는다.
- 코드와 설정에서 확인할 수 없는 정책, 필드, 계약을 추측해 적지 않는다. 결정되지 않은 항목은 미정으로, 확인하지 못한 항목은 미확인으로 표시해 구분한다.
- 절의 제목이나 위치를 바꾸면 이 문서와 다른 문서의 링크도 고친다.

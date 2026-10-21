# AGENTS.md

PAYMENT 도메인 백엔드 명세를 읽고 수정할 때 필요한 문서와 코드 위치를 안내한다. 지갑과 원장, 로트 만료, 보상 적립, 선차감과 환불, 체험 한도, 정책값, 충전 상품과 주문, 그로블 웹훅, 대사 배치, 관리자 지급, 회수, 정책 오버라이드 API를 다룬다.

명세 본문과 설정값은 이 문서에 복사하지 않는다.

<br>

### 1. 문서의 역할과 읽는 순서

| 문서 | 정하는 것 |
|---|---|
| [1-BACKGROUND.md](1-BACKGROUND.md) | 배경, 역할, 주체, 용어 |
| [2-REQUIREMENTS.md](2-REQUIREMENTS.md) | 요구 주체, 기대하는 동작, 다른 주체와의 역할 분담, 제품 제약, 데이터 보존 |
| [3-1-SOFTWARE-ARCHITECTURE.md](3-1-SOFTWARE-ARCHITECTURE.md) | 개요, 배경과 목표, 품질 속성, 배포 단위, 모듈 구조, 의존 방향, 도메인 모델 |
| [3-2-DB-SCHEMA.md](3-2-DB-SCHEMA.md) | 테이블, 컬럼, 제약, 인덱스, Redis 키, 데이터 수명 |
| [3-3-CONVENTIONS.md](3-3-CONVENTIONS.md) | 이름, 계층 책임, 검증, 이벤트, 테스트 규칙 |
| [4-1-PIPELINES.md](4-1-PIPELINES.md) | 공통 처리, 적립과 차감, 체험, 소모와 환불, 엔드포인트별 처리 흐름, 배치, 관리자 지급과 회수, 정책 오버라이드 관리 |
| [4-2-CONTRACT.md](4-2-CONTRACT.md) | 클라이언트, 결제 제공자, 관리자 페이지, 다른 도메인과의 계약 |
| [5-1-SECURITY.md](5-1-SECURITY.md) | 인증 수준, 접근 판정, 계정 상태, 결제 검증, 입력 검증, 재화 보호, 비밀값과 개인정보, 수용한 한계 |
| [5-2-CONCURRENCY.md](5-2-CONCURRENCY.md) | 지갑 행 잠금, 멱등, 유니크 위반, 체험 카운터 원자성, 배치 겹침, 수용한 경쟁 |
| [5-3-ERROR-HANDLING.md](5-3-ERROR-HANDLING.md) | 응답 규칙, 앱 코드, 오류 분류, 복구, 시간 한도 |
| [5-4-OBSERVABILITY.md](5-4-OBSERVABILITY.md) | 관측 스택, 식별자, 로그, 지표, 트레이스, 알림 |
| [5-5-TEST-CASES.md](5-5-TEST-CASES.md) | 테스트 범위와 케이스 |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 배포 단위, 환경 변수, 조건, 되돌리기 |
| [DECISIONS.md](DECISIONS.md) | 결정의 이력 |

- 처음 읽을 때는 1부터 4-2까지 순서대로 읽어 배경, 요구사항, 설계, 계약을 확인한다. 5는 품질과 검증, 6은 배포를 다룬다.
- 앞 단계의 결정이 뒤 단계의 기준이다. 구현에 맞추기 위해 앞 단계의 결정을 임의로 바꾸지 않는다.
- 미정으로 표시된 항목을 추측으로 채우지 않는다.
- 관리자 인증 수준과 토큰은 ADMIN 세트가 정한다.
- 다른 도메인과의 경계는 계약 문서의 마지막 절에 있다. ([4-2-15 다른 도메인과의 경계](4-2-CONTRACT.md#4-2-15-다른-도메인과의-경계))

<br>

### 2. 작업별 참조

| 하려는 일 | 먼저 볼 곳 | 함께 볼 곳 |
|---|---|---|
| 요청, 응답 필드 변경 | [4-2 계약](4-2-CONTRACT.md) | [4-1 처리 흐름](4-1-PIPELINES.md), [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 테이블, 컬럼, Redis 키 변경 | [3-2 DB 스키마](3-2-DB-SCHEMA.md) | [3-3-5 테스트와 검증 도구](3-3-CONVENTIONS.md#3-3-5-테스트와-검증-도구), [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 새 엔드포인트 | [4-2-1 공통 규칙과 헤더](4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더) | [3-3-2 계층 책임](3-3-CONVENTIONS.md#3-3-2-계층-책임), 서버 저장소 `http/credit/`의 수동 호출 파일과 통합 테스트 |
| 원장 사유 추가 | [3-2-4 원장](3-2-DB-SCHEMA.md#3-2-4-원장) | [4-2-7 이용내역 조회](4-2-CONTRACT.md#4-2-7-이용내역-조회), [4-1-15 선차감 대사](4-1-PIPELINES.md#4-1-15-선차감-대사), [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 보상, 소모 규칙 변경 | [4-1-2 적립](4-1-PIPELINES.md#4-1-2-적립), [4-1-5 소모와 환불](4-1-PIPELINES.md#4-1-5-소모와-환불) | [5-2-2 멱등과 1회 처리](5-2-CONCURRENCY.md#5-2-2-멱등과-1회-처리), STORY와 CHAT 세트의 과금 흐름 |
| 수치 변경 | [4-2-13 정책 오버라이드 기록](4-2-CONTRACT.md#4-2-13-정책-오버라이드-기록) | [4-1-17 정책 오버라이드 관리](4-1-PIPELINES.md#4-1-17-정책-오버라이드-관리), [4-1-7 정책값 조회와 스냅샷 갱신](4-1-PIPELINES.md#4-1-7-정책값-조회와-스냅샷-갱신), [2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약) |
| 회원별 이프 보정 | [4-2-11 이프 조정](4-2-CONTRACT.md#4-2-11-이프-조정) | [4-1-16 관리자 지급과 회수](4-1-PIPELINES.md#4-1-16-관리자-지급과-회수)<br>[ADMIN 4-2-1 공통 규칙과 헤더](../../ADMIN/BACKEND/4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더) |
| 상품 변경 | [2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약) | [6-5 설정 변경](6-DEPLOYMENT.md#6-5-설정-변경), [DECISIONS.md](DECISIONS.md) |
| 결제 제공자 연동 변경 | [4-1-14 그로블 웹훅 수신](4-1-PIPELINES.md#4-1-14-그로블-웹훅-수신) | [5-1-4 결제 통지 검증](5-1-SECURITY.md#5-1-4-결제-통지-검증), [6-3 환경 변수와 시크릿](6-DEPLOYMENT.md#6-3-환경-변수와-시크릿) |
| 체험 한도 변경 | [4-1-4 체험 예약, 복원, 스냅샷](4-1-PIPELINES.md#4-1-4-체험-예약-복원-스냅샷) | [3-2-10 Redis 키](3-2-DB-SCHEMA.md#3-2-10-redis-키), ACCOUNT 세트의 로그인 후속 처리 |
| 오류 코드 추가 | [5-3-2 앱 코드](5-3-ERROR-HANDLING.md#5-3-2-앱-코드) | [3-3-3 요청 검증과 오류](3-3-CONVENTIONS.md#3-3-3-요청-검증과-오류) |
| 동시 요청 문제 | [5-2 동시성](5-2-CONCURRENCY.md) | [4-1 처리 흐름](4-1-PIPELINES.md) |
| 로그나 지표 추가 | [5-4 관측](5-4-OBSERVABILITY.md) | [5-4-8 수집 조건과 실패 처리](5-4-OBSERVABILITY.md#5-4-8-수집-조건과-실패-처리) |
| 이미 내린 결정인지 확인 | [DECISIONS.md](DECISIONS.md) | 해당 결정에서 연결한 명세 절 |

<br>

### 3. 명세와 코드의 대응

코드 경로는 `manyak-server` 저장소 루트 아래 `src/main/kotlin/com/knk/manyak/`이다. 가입과 초대의 자격 판정과 보상 요청은 ACCOUNT 세트에서 다룬다. 과금 시점과 환불 시점은 STORY와 CHAT 세트에서 다룬다.

| 구성 요소 | 구현 위치 (`manyak-server` 기준) | 사용 범위 |
|---|---|---|
| API 계층과 관리자 API 계층 | [credit/controller/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/controller/) | 4-2-2~4-2-14 |
| 지갑, 정책, 출석, 체험, 이용내역, 관리자 지급과 정책 관리 | [credit/service/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/service/) | 4-1-2~4-1-11, 4-1-16, 4-1-17, 5-2 |
| 주문, 그로블 | [credit/service/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/service/) | 4-1-12~4-1-14, 5-1-4 |
| 배치 | [credit/scheduler/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/scheduler/) | 4-1-7, 4-1-15, 5-2-5 |
| 설정과 상품 | [credit/config/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/config/), [application.yml](../../../../../manyak-server/src/main/resources/application.yml) | 2-4, 6-3 |
| 모델 | [credit/entity/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/entity/) | 3-2 DB 스키마, 3-1-7 도메인 모델 |
| 저장 계층 | [credit/repository/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/repository/) | 3-2 인덱스, 5-2-1 잠금 |
| 잔액 부족 예외, 앱 코드 | [credit/InsufficientCreditException.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/InsufficientCreditException.kt), [global/error/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/error/) | 5-3-2 |
| 보안 필터, 계정 상태 | [global/security/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/security/), [global/config/SecurityConfig.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/config/SecurityConfig.kt) | 4-1-1 공통 처리, 5-1-1, 5-1-3 |
| 관측 | [global/observability/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/observability/) | 5-4 관측 |
| 마이그레이션 | [db/migration/](../../../../../manyak-server/src/main/resources/db/migration/), [dbdoc/](../../../../../manyak-server/dbdoc/) | 3-2 DB 스키마 |
| 테스트 | [src/test/kotlin/com/knk/manyak/credit/](../../../../../manyak-server/src/test/kotlin/com/knk/manyak/credit/), [http/credit/](../../../../../manyak-server/http/credit/) | 5-5 테스트 케이스 |
| 배포 | [.github/workflows/](../../../../../manyak-server/.github/workflows/), [Dockerfile](../../../../../manyak-server/Dockerfile) | 6 배포 |

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
| 정책 오버라이드 수동 확인 | `http/credit/credits.http`의 절차 |

- 명세의 작성, 수정, 검토를 서브에이전트에 맡기지 않는다.
- 실제 비밀값, 웹훅 본문을 문서에 넣지 않는다.
- 코드와 설정에서 확인할 수 없는 정책, 필드, 계약을 추측해 적지 않는다. 결정되지 않은 항목은 미정으로 표시한다. 확인하지 못한 항목은 미확인으로 표시한다.
- 절의 제목이나 위치를 바꾸면 이 문서와 다른 문서의 링크도 고친다.

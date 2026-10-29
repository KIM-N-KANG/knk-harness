# AGENTS.md

PAYMENT 도메인 백엔드 명세를 읽고 수정할 때 필요한 문서와 코드 위치를 안내한다. 지갑과 원장, 로트 만료, 보상 적립, 선차감과 환불, 체험 한도, 정책값, 충전 상품과 주문, 그로블 웹훅, 대사 배치를 다룬다.

명세 본문과 설정값은 이 문서에 복사하지 않는다.

<br>

### 문서의 역할과 읽는 순서

| 문서 | 정하는 것 |
|---|---|
| [BACKGROUND.md](BACKGROUND.md) | 배경, 역할, 주체, 용어 |
| [REQUIREMENTS.md](REQUIREMENTS.md) | 요구 주체, 기대하는 동작, 다른 주체와의 역할 분담, 제품 제약, 데이터 보존 |
| [SOFTWARE-ARCHITECTURE.md](SOFTWARE-ARCHITECTURE.md) | 개요, 배경과 목표, 품질 속성, 배포 단위, 모듈 구조, 의존 방향, 도메인 모델 |
| [DB-SCHEMA.md](DB-SCHEMA.md) | 테이블, 컬럼, 제약, 인덱스, Redis 키, 데이터 수명 |
| [CONVENTIONS.md](CONVENTIONS.md) | 이름, 계층 책임, 검증, 이벤트, 테스트 규칙 |
| [PIPELINES.md](PIPELINES.md) | 공통 처리, 적립과 차감, 체험, 소모와 환불, 엔드포인트별 처리 흐름, 배치 |
| [CONTRACT.md](CONTRACT.md) | 클라이언트, 결제 제공자, 다른 도메인과의 계약 |
| [SECURITY.md](SECURITY.md) | 인증 수준, 접근 판정, 계정 상태, 결제 검증, 입력 검증, 재화 보호, 비밀값과 개인정보, 수용한 한계 |
| [CONCURRENCY.md](CONCURRENCY.md) | 지갑 행 잠금, 멱등, 유니크 위반, 체험 카운터 원자성, 배치 겹침, 수용한 경쟁 |
| [ERROR-HANDLING.md](ERROR-HANDLING.md) | 응답 규칙, 앱 코드, 오류 분류, 복구, 시간 한도 |
| [OBSERVABILITY.md](OBSERVABILITY.md) | 관측 스택, 식별자, 로그, 지표, 트레이스, 알림 |
| [TEST-CASES.md](TEST-CASES.md) | 테스트 범위와 케이스 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | 배포 단위, 환경 변수, 조건, 되돌리기 |
| [DECISIONS.md](DECISIONS.md) | 결정의 이력 |

- 처음에는 위 표의 순서로 배경, 요구사항, 설계와 계약을 확인하고 품질, 검증과 배포를 읽는다.
- 앞 단계의 결정이 뒤 단계의 기준이다. 구현에 맞추기 위해 앞 단계의 결정을 임의로 바꾸지 않는다.
- 미정으로 표시된 항목을 추측으로 채우지 않는다.
- 다른 도메인과의 경계는 계약 문서의 마지막 절에 있다. ([다른 도메인과의 경계](CONTRACT.md#다른-도메인과의-경계))

<br>

### 작업별 참조

| 하려는 일 | 먼저 볼 곳 | 함께 볼 곳 |
|---|---|---|
| 요청, 응답 필드 변경 | [계약](CONTRACT.md) | [처리 흐름](PIPELINES.md), [배포 조건](DEPLOYMENT.md#배포-조건) |
| 테이블, 컬럼, Redis 키 변경 | [DB 스키마](DB-SCHEMA.md) | [테스트와 검증 도구](CONVENTIONS.md#테스트와-검증-도구), [배포 조건](DEPLOYMENT.md#배포-조건) |
| 새 엔드포인트 | [공통 규칙과 헤더](CONTRACT.md#공통-규칙과-헤더) | [계층 책임](CONVENTIONS.md#계층-책임), 서버 저장소 `http/credit/`의 수동 호출 파일과 통합 테스트 |
| 원장 사유 추가 | [원장](DB-SCHEMA.md#원장) | [이용내역 조회](CONTRACT.md#이용내역-조회), [선차감 대사](PIPELINES.md#선차감-대사), [배포 조건](DEPLOYMENT.md#배포-조건) |
| 보상, 소모 규칙 변경 | [적립](PIPELINES.md#적립), [소모와 환불](PIPELINES.md#소모와-환불) | [멱등과 1회 처리](CONCURRENCY.md#멱등과-1회-처리), STORY와 CHAT 세트의 과금 흐름 |
| 수치 변경 | [설정 변경](DEPLOYMENT.md#설정-변경) | [정책값 조회와 스냅샷 갱신](PIPELINES.md#정책값-조회와-스냅샷-갱신), [제품 제약](REQUIREMENTS.md#제품-제약) |
| 상품 변경 | [제품 제약](REQUIREMENTS.md#제품-제약) | [설정 변경](DEPLOYMENT.md#설정-변경), [DECISIONS.md](DECISIONS.md) |
| 결제 제공자 연동 변경 | [그로블 웹훅 수신](PIPELINES.md#그로블-웹훅-수신) | [결제 통지 검증](SECURITY.md#결제-통지-검증), [환경 변수와 시크릿](DEPLOYMENT.md#환경-변수와-시크릿) |
| 체험 한도 변경 | [체험 예약, 복원, 스냅샷](PIPELINES.md#체험-예약-복원-스냅샷) | [Redis 키](DB-SCHEMA.md#redis-키), ACCOUNT 세트의 로그인 후속 처리 |
| 오류 코드 추가 | [앱 코드](ERROR-HANDLING.md#앱-코드) | [요청 검증과 오류](CONVENTIONS.md#요청-검증과-오류) |
| 동시 요청 문제 | [동시성](CONCURRENCY.md) | [처리 흐름](PIPELINES.md) |
| 로그나 지표 추가 | [관측](OBSERVABILITY.md) | [수집 조건과 실패 처리](OBSERVABILITY.md#수집-조건과-실패-처리) |
| 이미 내린 결정인지 확인 | [DECISIONS.md](DECISIONS.md) | 해당 결정에서 연결한 명세 절 |

<br>

### 명세와 코드의 대응

코드 경로는 `manyak-server` 저장소 루트 아래 `src/main/kotlin/com/knk/manyak/`이다. 가입과 초대의 자격 판정과 보상 요청은 ACCOUNT 세트에서 다룬다. 과금 시점과 환불 시점은 STORY와 CHAT 세트에서 다룬다.

| 구성 요소 | 구현 위치 (`manyak-server` 기준) | 사용 범위 |
|---|---|---|
| API 계층 | [credit/controller/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/controller/) | 4-2-2~4-2-10 |
| 지갑, 정책, 출석, 체험, 이용내역 | [credit/service/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/service/) | 4-1-2~4-1-11, 5-2 |
| 주문, 그로블 | [credit/service/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/service/) | 4-1-12~4-1-14, 5-1-4 |
| 배치 | [credit/scheduler/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/scheduler/) | 4-1-7, 4-1-15, 5-2-5 |
| 설정과 상품 | [credit/config/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/config/), [application.yml](../../../../../manyak-server/src/main/resources/application.yml) | 2-4, 6-3 |
| 모델 | [credit/entity/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/entity/) | DB 스키마, 3-1-7 도메인 모델 |
| 저장 계층 | [credit/repository/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/repository/) | 인덱스, 5-2-1 잠금 |
| 잔액 부족 예외, 앱 코드 | [credit/InsufficientCreditException.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/credit/InsufficientCreditException.kt), [global/error/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/error/) | 5-3-2 |
| 보안 필터, 계정 상태 | [global/security/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/security/), [global/config/SecurityConfig.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/config/SecurityConfig.kt) | 공통 처리, 5-1-1, 5-1-3 |
| 관측 | [global/observability/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/observability/) | 관측 |
| 마이그레이션 | [db/migration/](../../../../../manyak-server/src/main/resources/db/migration/), [dbdoc/](../../../../../manyak-server/dbdoc/) | DB 스키마 |
| 테스트 | [src/test/kotlin/com/knk/manyak/credit/](../../../../../manyak-server/src/test/kotlin/com/knk/manyak/credit/), [http/credit/](../../../../../manyak-server/http/credit/) | 테스트 케이스 |
| 배포 | [.github/workflows/](../../../../../manyak-server/.github/workflows/), [Dockerfile](../../../../../manyak-server/Dockerfile) | 배포 |

<br>

### 작성 규칙과 검증 명령

| 항목 | 위치 |
|---|---|
| 문서별 작성 기준 | [백엔드 명세 작성 가이드](../../../reference/BACKEND-SPEC-WRITING-GUIDE.md) |
| 문체와 파일명 | [제품 Spec 작성 가이드](../../../reference/PRODUCT-SPEC-WRITING-GUIDE.md) |
| 하네스 전체 지침 | 하네스 루트의 `AGENTS.md` |
| 코드 규칙 | `manyak-server`의 `CLAUDE.md` |
| 문서 변경 뒤 검사 | `git diff --check` 실행<br>링크, 앵커, 참조한 절 제목 확인 |
| 테스트 실행 | 서버 저장소에서 `./gradlew test` 실행<br>DB 제약은 `scripts/gen-db-docs.sh`로 실제 PostgreSQL에서 검증 |
| 정책 오버라이드 수동 확인 | `http/credit/credits.http`의 절차 |

- 명세의 작성, 수정, 검토를 서브에이전트에 맡기지 않는다.
- 실제 비밀값, 웹훅 본문을 문서에 넣지 않는다.
- 코드와 설정에서 확인할 수 없는 정책, 필드, 계약을 추측해 적지 않는다. 결정되지 않은 항목은 미정으로 표시한다. 확인하지 못한 항목은 미확인으로 표시한다.
- 절의 제목이나 위치를 바꾸면 이 문서와 다른 문서의 링크도 고친다.

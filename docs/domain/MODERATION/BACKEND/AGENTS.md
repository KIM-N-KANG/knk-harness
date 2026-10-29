# AGENTS.md

MODERATION 도메인 백엔드 명세를 읽고 수정할 때 필요한 문서와 코드 위치를 안내한다. 검수 제출본의 접수, 조회, 재제출, 취소, 선점과 실행, AI 호출과 응답 검증, 결과 반영, 재시도와 보류, 용량 예산을 다룬다.

명세 본문과 설정값은 이 문서에 복사하지 않는다.

<br>

### 1. 문서의 역할과 읽는 순서

| 문서 | 정하는 것 |
|---|---|
| [1-BACKGROUND.md](1-BACKGROUND.md) | 배경, 역할, 주체, 용어 |
| [2-REQUIREMENTS.md](2-REQUIREMENTS.md) | 요구 주체, 기대하는 동작, 다른 주체와의 역할 분담, 제품 제약, 데이터 보존 |
| [3-1-SOFTWARE-ARCHITECTURE.md](3-1-SOFTWARE-ARCHITECTURE.md) | 개요, 배경과 목표, 품질 속성, 배포 단위, 모듈 구조, 의존 방향, 도메인 모델 |
| [3-2-DB-SCHEMA.md](3-2-DB-SCHEMA.md) | 테이블, 컬럼, 제약, 인덱스, 데이터 수명 |
| [3-3-CONVENTIONS.md](3-3-CONVENTIONS.md) | 이름, 계층 책임, 검증, 이벤트, 테스트 규칙 |
| [4-1-PIPELINES.md](4-1-PIPELINES.md) | 공통 처리, 접수, 조회, 재제출, 취소, 선점과 실행, 검수 입력과 이미지 복사, AI 호출, 결과 반영, 재시도와 보류, 보류 해제 |
| [4-2-CONTRACT.md](4-2-CONTRACT.md) | 클라이언트, 다른 도메인과의 계약, 제출본 응답 구조 |
| [5-1-SECURITY.md](5-1-SECURITY.md) | 인증 수준, 소유권과 접근 판정, 계정 상태와 동의, 입력 검증, 이미지 보호, 재시도 범위, 식별자와 개인정보, 수용한 한계 |
| [5-2-CONCURRENCY.md](5-2-CONCURRENCY.md) | 행 잠금, 회차와 1회 반영, 유니크 위반, 선점과 임대, 수용한 경쟁 |
| [5-3-ERROR-HANDLING.md](5-3-ERROR-HANDLING.md) | 응답 규칙, 앱 코드, 오류 분류, 복구, 시간 한도 |
| [5-4-OBSERVABILITY.md](5-4-OBSERVABILITY.md) | 관측 스택, 식별자, 로그, 지표, 트레이스, 알림 |
| [5-5-TEST-CASES.md](5-5-TEST-CASES.md) | 테스트 범위와 케이스 |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 배포 단위, 환경 변수, 조건, 되돌리기 |
| [DECISIONS.md](DECISIONS.md) | 결정의 이력 |

- 처음 읽을 때는 1부터 4-2까지 순서대로 읽어 배경, 요구사항, 설계, 계약을 확인한다. 5는 품질과 검증, 6은 배포를 다룬다.
- 앞 단계의 결정이 뒤 단계의 기준이다. 구현에 맞추기 위해 앞 단계의 결정을 임의로 바꾸지 않는다.
- 미정으로 표시된 항목을 추측으로 채우지 않는다.
- 등록과 수정 요청의 본문과 실패 조건은 STORY 세트가 정한다. 검수 기준과 응답 의미는 AI 서버가 정한다. 검수 완료 알림은 NOTIFICATION 세트가 정한다.
- 다른 도메인과의 경계는 계약 문서의 마지막 절에 있다. ([4-2-6 다른 도메인과의 경계](4-2-CONTRACT.md#4-2-6-다른-도메인과의-경계))

<br>

### 2. 작업별 참조

| 하려는 일 | 먼저 볼 곳 | 함께 볼 곳 |
|---|---|---|
| 요청, 응답 필드 변경 | [4-2 계약](4-2-CONTRACT.md) | [4-1 처리 흐름](4-1-PIPELINES.md), [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 테이블, 컬럼 변경 | [3-2 DB 스키마](3-2-DB-SCHEMA.md) | [3-3-5 테스트와 검증 도구](3-3-CONVENTIONS.md#3-3-5-테스트와-검증-도구), [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 새 엔드포인트 | [4-2-1 공통 규칙과 헤더](4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더) | [3-3-2 계층 책임](3-3-CONVENTIONS.md#3-3-2-계층-책임), 서버 저장소 `http/story/`의 수동 호출 파일과 통합 테스트 |
| AI 요청 필드나 응답 처리 변경 | [4-1-8 AI 호출과 응답 검증](4-1-PIPELINES.md#4-1-8-ai-호출과-응답-검증) | [5-3-3 오류 분류](5-3-ERROR-HANDLING.md#5-3-3-오류-분류), [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 재시도 간격, 임대, 슬롯 변경 | [5-3-5 재시도와 시간 한도](5-3-ERROR-HANDLING.md#5-3-5-재시도와-시간-한도) | [5-2-4 선점과 임대](5-2-CONCURRENCY.md#5-2-4-선점과-임대), [6-5 설정 변경](6-DEPLOYMENT.md#6-5-설정-변경) |
| 보류 처리 | [4-1-11 보류 해제](4-1-PIPELINES.md#4-1-11-보류-해제) | [6-6 적용과 복구](6-DEPLOYMENT.md#6-6-적용과-복구) |
| 용량 예산 변경 | [4-1-2 접수](4-1-PIPELINES.md#4-1-2-접수) | [2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약) |
| 오류 코드 추가 | [5-3-2 앱 코드](5-3-ERROR-HANDLING.md#5-3-2-앱-코드) | [4-2-1 공통 규칙과 헤더](4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더) |
| 동시 요청 문제 | [5-2 동시성](5-2-CONCURRENCY.md) | [4-1 처리 흐름](4-1-PIPELINES.md) |
| 로그나 지표 추가 | [5-4 관측](5-4-OBSERVABILITY.md) | [5-4-8 수집 조건과 실패 처리](5-4-OBSERVABILITY.md#5-4-8-수집-조건과-실패-처리) |
| 이미 내린 결정인지 확인 | [DECISIONS.md](DECISIONS.md) | 해당 결정에서 연결한 명세 절 |

<br>

### 3. 명세와 코드의 대응

코드 경로는 `manyak-server` 저장소 루트 아래 `src/main/kotlin/com/knk/manyak/`이다. 등록과 수정 요청의 API 계층, 입력 검증, 승인 시 저장과 적용은 STORY 세트에 속한다. 검수 완료 푸시 리스너는 NOTIFICATION 세트에 속한다.

| 구성 요소 | 구현 위치 (`manyak-server` 기준) | 사용 범위 |
|---|---|---|
| 제출본 API | [story/controller/StorySubmissionController.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/controller/StorySubmissionController.kt) | 4-2-2~4-2-5 |
| 접수 진입 | [story/controller/StoryController.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/controller/StoryController.kt), [story/controller/StoryEditController.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/controller/StoryEditController.kt) | 4-1-2 |
| 제출 서비스, 폼 조립기, 용량 검사 | [story/submission/StorySubmissionService.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/submission/StorySubmissionService.kt), [story/submission/SubmissionFormAssembler.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/submission/SubmissionFormAssembler.kt), [story/submission/SubmissionSizeCheck.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/submission/SubmissionSizeCheck.kt) | 4-1-2~4-1-5 |
| 폴러, 선점 저장소 | [story/submission/SubmissionPoller.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/submission/SubmissionPoller.kt), [story/submission/SubmissionClaimStore.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/submission/SubmissionClaimStore.kt) | 4-1-6, 5-2-4 |
| 실행기, 종료 처리, 재시도 정책 | [story/submission/SubmissionExecution.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/submission/SubmissionExecution.kt), [story/submission/SubmissionRetryPolicy.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/submission/SubmissionRetryPolicy.kt) | 4-1-9, 4-1-10, 5-3 |
| 이미지 복사, AI 클라이언트 | [story/submission/SubmissionImages.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/submission/SubmissionImages.kt), [story/submission/StoryModerationClient.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/submission/StoryModerationClient.kt) | 4-1-7, 4-1-8 |
| 보류 알림 | [story/submission/SlackSubmissionHeldNotifier.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/submission/SlackSubmissionHeldNotifier.kt) | 4-1-10, 5-4-7 |
| 모델 | [story/submission/StorySubmission.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/submission/StorySubmission.kt) | 3-2 DB 스키마, 3-1-7 도메인 모델 |
| 설정 | [application.yml](../../../../../manyak-server/src/main/resources/application.yml) | 6-3 |
| 오류 | [global/error/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/error/) | 5-3-2 앱 코드 |
| 관측 | [global/observability/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/observability/) | 5-4 관측 |
| 마이그레이션 | [db/migration/](../../../../../manyak-server/src/main/resources/db/migration/), [dbdoc/](../../../../../manyak-server/dbdoc/) | 3-2 DB 스키마 |
| 테스트 | [src/test/kotlin/com/knk/manyak/story/submission/](../../../../../manyak-server/src/test/kotlin/com/knk/manyak/story/submission/), [story-general-create.http](../../../../../manyak-server/http/story/story-general-create.http), [story-edit.http](../../../../../manyak-server/http/story/story-edit.http) | 5-5 테스트 케이스 |
| 배포 | [.github/workflows/](../../../../../manyak-server/.github/workflows/), [Dockerfile](../../../../../manyak-server/Dockerfile) | 6 배포 |

<br>

### 4. 작성 규칙과 검증 명령

| 항목 | 위치 |
|---|---|
| 문서별 작성 기준 | [백엔드 명세 작성 가이드](../../../reference/BACKEND-SPEC-WRITING-GUIDE.md) |
| 문체와 파일명 | [제품 Spec 작성 가이드](../../../reference/PRODUCT-SPEC-WRITING-GUIDE.md) |
| 하네스 전체 지침 | 하네스 루트의 `AGENTS.md` |
| 코드 규칙 | `manyak-server`의 `CLAUDE.md` |
| 문서 변경 후 검사 | `git diff --check` 실행<br>링크, 앵커, 참조한 절 번호 확인 |
| 테스트 실행 | `./gradlew test` 실행<br>선점 PostgreSQL 테스트는 Docker 필요<br>DB 제약은 `scripts/gen-db-docs.sh`로 실제 PostgreSQL에서 검증 |

- 명세의 작성, 수정, 검토를 서브에이전트에 맡기지 않는다.
- 실제 비밀값, 웹훅 주소, 사용자 입력 원문, 이미지 URL을 문서에 넣지 않는다.
- 코드와 설정에서 확인할 수 없는 정책, 필드, 계약을 추측해 작성하지 않는다. 결정되지 않은 항목은 미정으로, 확인하지 못한 항목은 미확인으로 표시해 구분한다.
- 절의 제목이나 위치를 바꾸면 이 문서와 다른 문서의 링크도 고친다.

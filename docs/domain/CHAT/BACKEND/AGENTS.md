# AGENTS.md

CHAT 도메인 백엔드 명세를 읽고 수정할 때 필요한 문서와 코드 위치를 안내한다. 채팅 생성과 조회, 턴 진행과 재생성, 선택지, 진행 상태와 엔딩 도달, 실시간 이미지, 공유, 피드백을 다룬다.

명세 본문과 설정값은 이 문서에 복사하지 않는다.

<br>

### 1. 문서의 역할과 읽는 순서

| 문서 | 정하는 것 |
|---|---|
| [1-BACKGROUND.md](1-BACKGROUND.md) | 배경, 역할, 주체, 용어 |
| [2-REQUIREMENTS.md](2-REQUIREMENTS.md) | 요구 주체, 기대하는 동작, AI 서버와의 역할 분담, 제품 제약, 데이터 보존 |
| [3-1-SOFTWARE-ARCHITECTURE.md](3-1-SOFTWARE-ARCHITECTURE.md) | 개요, 배경과 목표, 품질 속성, 배포 단위, 모듈 구조, 의존 방향, 도메인 모델 |
| [3-2-DB-SCHEMA.md](3-2-DB-SCHEMA.md) | 테이블, 컬럼, 제약, 인덱스, 데이터 수명 |
| [3-3-CONVENTIONS.md](3-3-CONVENTIONS.md) | 이름, 계층 책임, 검증, 비동기, 테스트 규칙 |
| [4-1-PIPELINES.md](4-1-PIPELINES.md) | 엔드포인트별 처리 흐름, AI 호출, 턴 저장과 판정 반영, 실시간 이미지, 후보 이름 구분 |
| [4-2-CONTRACT.md](4-2-CONTRACT.md) | 클라이언트, 다른 도메인과의 계약, SSE 이벤트 |
| [5-1-SECURITY.md](5-1-SECURITY.md) | 인증 수준, 소유권, 계정 상태와 동의, 입력과 이미지 검증, 개인정보 |
| [5-2-CONCURRENCY.md](5-2-CONCURRENCY.md) | 채팅 행 잠금, 환불 단일 판정, 유니크 위반 처리, 읽기 격리, 선택 기록 세대, 생성 선점과 저장 시 재확인 |
| [5-3-ERROR-HANDLING.md](5-3-ERROR-HANDLING.md) | 응답 규칙, 앱 코드, 오류 분류, 복구, 시간 한도 |
| [5-4-OBSERVABILITY.md](5-4-OBSERVABILITY.md) | 관측 스택, 식별자, AI 헤더, 호출 기록, 로그, 지표, 트레이스, 알림, 분석 이벤트 |
| [5-5-TEST-CASES.md](5-5-TEST-CASES.md) | 테스트 범위와 케이스 |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 배포 단위, 환경 변수, 조건, 되돌리기 |
| [DECISIONS.md](DECISIONS.md) | 결정의 이력 |

- 처음에는 1부터 4-2까지 순서대로 읽어 배경, 요구사항, 설계, 계약을 확인한다. 5는 품질과 검증, 6은 배포를 다룬다.
- 앞 단계의 결정이 뒤 단계의 기준이다. 구현에 맞추려고 앞 단계를 임의로 바꾸지 않는다.
- 미정으로 표시된 항목을 추측으로 채우지 않는다.
- 다른 도메인과의 경계는 계약 문서의 마지막 절에 있다. ([4-2-12 다른 도메인과의 경계](4-2-CONTRACT.md#4-2-12-다른-도메인과의-경계))

<br>

### 2. 작업별 참조

| 하려는 일 | 먼저 볼 곳 | 함께 볼 곳 |
|---|---|---|
| 요청, 응답, SSE 이벤트의 필드 변경 | [4-2 계약](4-2-CONTRACT.md) | [4-1 처리 흐름](4-1-PIPELINES.md), [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 테이블이나 컬럼 변경 | [3-2 DB 스키마](3-2-DB-SCHEMA.md) | [3-3-5 테스트와 검증 도구](3-3-CONVENTIONS.md#3-3-5-테스트와-검증-도구), [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 새 엔드포인트 | [4-2-1 공통 규칙과 헤더](4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더) | [3-3-2 계층 책임](3-3-CONVENTIONS.md#3-3-2-계층-책임), 서버 저장소 `http/chat/`의 수동 호출 파일과 통합 테스트 |
| 소유권 규칙 변경 | [5-1-2 소유권 판정](5-1-SECURITY.md#5-1-2-소유권-판정) | [DECISIONS.md](DECISIONS.md) |
| AI 입력 데이터, 판정 반영 변경 | [4-1-6 이어쓰기](4-1-PIPELINES.md#4-1-6-이어쓰기), [4-1-12 턴 저장과 판정 반영](4-1-PIPELINES.md#4-1-12-턴-저장과-판정-반영) | AI 세트의 5 계약, [5-4-3 AI 서버로 전달하는 헤더](5-4-OBSERVABILITY.md#5-4-3-ai-서버로-전달하는-헤더) |
| 과금, 환불, 체험 변경 | [4-1-6 이어쓰기](4-1-PIPELINES.md#4-1-6-이어쓰기), [5-2-2 환불의 단일 판정](5-2-CONCURRENCY.md#5-2-2-환불의-단일-판정) | [5-3-4 오류별 처리](5-3-ERROR-HANDLING.md#5-3-4-오류별-처리), [6-5 설정 변경](6-DEPLOYMENT.md#6-5-설정-변경) |
| 실시간 이미지 변경 | [4-1-13 실시간 이미지](4-1-PIPELINES.md#4-1-13-실시간-이미지) | [5-1-5 실시간 이미지 검증](5-1-SECURITY.md#5-1-5-실시간-이미지-검증) |
| 오류 코드 추가 | [5-3-2 앱 코드](5-3-ERROR-HANDLING.md#5-3-2-앱-코드) | [3-3-3 요청 검증과 오류](3-3-CONVENTIONS.md#3-3-3-요청-검증과-오류) |
| 생성 중 상태와 이벤트 재연결 | [4-2-4 상세](4-2-CONTRACT.md#4-2-4-상세)와 [4-2-13 생성 스트림 재연결](4-2-CONTRACT.md#4-2-13-생성-스트림-재연결) | [4-1-15 생성 이벤트 수신과 재연결](4-1-PIPELINES.md#4-1-15-생성-이벤트-수신과-재연결), [5-2-6 생성 중 키와 저장 시 재확인](5-2-CONCURRENCY.md#5-2-6-생성-중-키와-저장-시-재확인), [6-3 환경 변수와 시크릿](6-DEPLOYMENT.md#6-3-환경-변수와-시크릿), [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 동시 요청 문제 | [5-2 동시성](5-2-CONCURRENCY.md) | [4-1-12 턴 저장과 판정 반영](4-1-PIPELINES.md#4-1-12-턴-저장과-판정-반영) |
| 로그나 지표 추가 | [5-4 관측](5-4-OBSERVABILITY.md) | [5-4-10 수집 조건과 실패 처리](5-4-OBSERVABILITY.md#5-4-10-수집-조건과-실패-처리) |
| 이미 내린 결정인지 확인 | [DECISIONS.md](DECISIONS.md) | 해당 결정에서 연결한 명세 절 |

<br>

### 3. 명세와 코드의 대응

코드 경로는 `manyak-server` 저장소 루트 아래 `src/main/kotlin/com/knk/manyak/`이다. 내 채팅 목록 엔드포인트와 게스트 이관은 ACCOUNT 세트에 속한다. 두 기능은 CHAT 세트의 서비스를 호출한다.

| 구성 요소 | 구현 위치 (`manyak-server` 기준) | 사용 범위 |
|---|---|---|
| API 계층 | [chat/controller/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/chat/controller/), [FeedbackController.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/feedback/controller/FeedbackController.kt) | 4-2 계약, 5-1-1 인증 수준 |
| 채팅 서비스 | [ChatService.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/chat/service/ChatService.kt) | 4-1-2~4-1-10, 5-2-2 환불 단일 판정, 5-4-7 지표 |
| 턴 저장 | [ChatTurnPersister.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/chat/service/ChatTurnPersister.kt), [EndingReachRecorder.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/chat/service/EndingReachRecorder.kt) | 4-1-12 턴 저장과 판정 반영, 5-2-1 채팅 행 잠금 |
| 실시간 이미지 | [ChatRealtimeImageService.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/chat/service/ChatRealtimeImageService.kt) | 4-1-13 실시간 이미지, 5-1-5 실시간 이미지 검증 |
| 후보 이름 구분 | [ChatJudgmentNameMapping.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/chat/service/ChatJudgmentNameMapping.kt) | 4-1-14 후보 이름 구분 |
| AI 호출 | [chat/client/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/chat/client/) | 4-1-1 공통 처리, 4-1-6, 4-1-8 |
| 스트림 실행기 | [ChatSseConfig.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/chat/config/ChatSseConfig.kt), [ChatTurnRefundMeters.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/chat/service/ChatTurnRefundMeters.kt) | 3-3-4 비동기, 5-4-7 지표 |
| 생성 중 상태와 이벤트 보관 | [ChatGenerationStore.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/chat/service/ChatGenerationStore.kt), [ChatGenerationDeadlines.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/chat/service/ChatGenerationDeadlines.kt), [ChatGenerationEvents.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/chat/service/ChatGenerationEvents.kt), [ChatGenerationReceivers.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/chat/service/ChatGenerationReceivers.kt) | 4-1-15 생성 이벤트 수신과 재연결, 4-2-13 생성 스트림 재연결, 5-2-6 생성 중 키와 저장 시 재확인 |
| 피드백 | [feedback/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/feedback/) | 4-1-11 피드백 등록, 4-2-11 피드백 등록 |
| 모델 | [chat/entity/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/chat/entity/) | 3-2 DB 스키마, 3-1-7 도메인 모델 |
| 내 채팅 목록, 이관 | [UserContentController.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/user/controller/UserContentController.kt), [GuestDataMigrationService.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/migration/service/GuestDataMigrationService.kt) | 4-2-12 다른 도메인과의 경계 |
| 오류와 보안 | [global/error/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/error/), [global/security/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/security/) | 5-3 오류 처리, 5-1 보안 |
| 관측 | [global/observability/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/observability/) | 5-4 관측 |
| 마이그레이션 | [db/migration/](../../../../../manyak-server/src/main/resources/db/migration/), [dbdoc/](../../../../../manyak-server/dbdoc/) | 3-2 DB 스키마 |
| 테스트 | [src/test/kotlin/com/knk/manyak/chat/](../../../../../manyak-server/src/test/kotlin/com/knk/manyak/chat/), [http/chat/](../../../../../manyak-server/http/chat/), [http/feedback/](../../../../../manyak-server/http/feedback/) | 5-5 테스트 케이스 |
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

- 명세의 작성, 수정, 검토를 서브에이전트에 맡기지 않는다.
- 실제 비밀값, 사용자 입력 원문, AI 응답 원문을 문서에 넣지 않는다.
- 코드와 설정에서 확인할 수 없는 정책, 필드, 계약을 추측해 적지 않는다. 결정되지 않은 것은 미정으로, 확인하지 못한 것은 미확인으로 구분한다.
- 절의 제목이나 위치를 바꾸면 이 문서와 다른 문서의 링크도 고친다.

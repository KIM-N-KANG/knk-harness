# AGENTS.md

NOTIFICATION 도메인 백엔드 명세를 읽고 수정할 때 필요한 문서와 코드 위치를 안내한다. 푸시 토큰, 수신 동의, 발송 자격, 스토리 완성과 검수 완료 알림, 출석 리마인드, 캠페인과 공지 알림, 관리자 캠페인과 문구 API, 아웃박스와 메시지 큐, 알림 서비스의 소비와 발송을 다룬다.

명세 본문과 설정값은 이 문서에 복사하지 않는다.

<br>

### 1. 문서의 역할과 읽는 순서

| 문서 | 정하는 것 |
|---|---|
| [1-BACKGROUND.md](1-BACKGROUND.md) | 배경, 역할, 주체, 용어 |
| [2-REQUIREMENTS.md](2-REQUIREMENTS.md) | 요구 주체, 기대하는 동작, 다른 주체와의 역할 분담, 제품 제약, 데이터 보존 |
| [3-1-SOFTWARE-ARCHITECTURE.md](3-1-SOFTWARE-ARCHITECTURE.md) | 개요, 배경과 목표, 품질 속성, 배포 단위, 모듈 구조, 의존 방향, 도메인 모델 |
| [3-2-DB-SCHEMA.md](3-2-DB-SCHEMA.md) | 테이블, 컬럼, 제약, 인덱스, Redis 키, 메시지 큐, 데이터 수명 |
| [3-3-CONVENTIONS.md](3-3-CONVENTIONS.md) | 이름, 계층 책임, 검증, 이벤트, 테스트 규칙 |
| [4-1-PIPELINES.md](4-1-PIPELINES.md) | 공통 처리, 토큰과 동의, 발송 자격, 시나리오별 발송 요청, 중계와 소비, 발송, 캠페인 관리, 문구 변경, 발송 결과 기록과 통계 |
| [4-2-CONTRACT.md](4-2-CONTRACT.md) | 클라이언트, 알림 서비스, 관리자 페이지, 다른 도메인과의 계약, 큐 메시지, 푸시 데이터, 발송 결과 보고, 알림 통계 |
| [5-1-SECURITY.md](5-1-SECURITY.md) | 인증 수준, 접근 판정, 계정 상태와 동의, 수신 동의와 법적 요건, 입력 검증, 내부 경로 보호, 비밀값과 개인정보, 수용한 한계 |
| [5-2-CONCURRENCY.md](5-2-CONCURRENCY.md) | 행 잠금, 멱등, 유니크 위반, 선점과 임대, 소비자 선점, 수용한 경쟁 |
| [5-3-ERROR-HANDLING.md](5-3-ERROR-HANDLING.md) | 응답 규칙, 앱 코드, 오류 분류, 복구, 시간 한도 |
| [5-4-OBSERVABILITY.md](5-4-OBSERVABILITY.md) | 관측 스택, 식별자, 로그, 지표, 트레이스, 알림 |
| [5-5-TEST-CASES.md](5-5-TEST-CASES.md) | 테스트 범위와 케이스 |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 배포 단위, 환경 변수, 조건, 되돌리기 |
| [DECISIONS.md](DECISIONS.md) | 결정의 이력 |

- 처음 읽을 때는 1부터 4-2까지 순서대로 읽어 배경, 요구사항, 설계, 계약을 확인한다. 5는 품질과 검증, 6은 배포를 다룬다.
- 앞 단계의 결정이 뒤 단계의 기준이다. 구현에 맞추기 위해 앞 단계의 결정을 임의로 바꾸지 않는다.
- 미정으로 표시된 항목을 추측으로 채우지 않는다.
- 관리자 인증 수준과 토큰은 ADMIN 세트가 정한다. 공지의 내용과 게시는 NOTICE 세트가 정한다.
- 다른 도메인과의 경계는 계약 문서의 마지막 절에 있다. ([4-2-22 다른 도메인과의 경계](4-2-CONTRACT.md#4-2-22-다른-도메인과의-경계))

<br>

### 2. 작업별 참조

| 하려는 일 | 먼저 볼 곳 | 함께 볼 곳 |
|---|---|---|
| 요청, 응답 필드 변경 | [4-2 계약](4-2-CONTRACT.md) | [4-1 처리 흐름](4-1-PIPELINES.md), [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 테이블, 컬럼, Redis 키 변경 | [3-2 DB 스키마](3-2-DB-SCHEMA.md) | [3-3-5 테스트와 검증 도구](3-3-CONVENTIONS.md#3-3-5-테스트와-검증-도구), [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 새 엔드포인트 | [4-2-1 공통 규칙과 헤더](4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더) | [3-3-2 계층 책임](3-3-CONVENTIONS.md#3-3-2-계층-책임), 서버 저장소 `http/push/`와 알림 서비스 저장소 `http/notifications.http`의 수동 호출 파일과 통합 테스트 |
| 푸시 데이터 변경 | [4-2-10 푸시 데이터](4-2-CONTRACT.md#4-2-10-푸시-데이터) | [4-2-9 큐 메시지](4-2-CONTRACT.md#4-2-9-큐-메시지), 웹과 Android 세트 |
| 시나리오 추가 | [4-2-9 큐 메시지](4-2-CONTRACT.md#4-2-9-큐-메시지) | [4-1-6 스토리 완성 알림](4-1-PIPELINES.md#4-1-6-스토리-완성-알림), [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 동의 규칙 변경 | [5-1-4 수신 동의와 법적 요건](5-1-SECURITY.md#5-1-4-수신-동의와-법적-요건) | [4-1-5 발송 자격 판정](4-1-PIPELINES.md#4-1-5-발송-자격-판정), [DECISIONS.md](DECISIONS.md) |
| 발송 시각 변경 | [6-5 설정 변경](6-DEPLOYMENT.md#6-5-설정-변경) | [4-1-8 출석 리마인드](4-1-PIPELINES.md#4-1-8-출석-리마인드) |
| 캠페인과 문구 관리자 API 변경 | [4-1-15 캠페인 관리](4-1-PIPELINES.md#4-1-15-캠페인-관리)<br>[4-1-16 문구 템플릿 변경](4-1-PIPELINES.md#4-1-16-문구-템플릿-변경) | [4-1-9 캠페인](4-1-PIPELINES.md#4-1-9-캠페인)<br>[ADMIN 4-2-1 공통 규칙과 헤더](../../ADMIN/BACKEND/4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더) |
| 발송 결과와 알림 통계 변경 | [4-1-17 발송 결과 기록과 통계](4-1-PIPELINES.md#4-1-17-발송-결과-기록과-통계) | [4-2-19 발송 결과 보고](4-2-CONTRACT.md#4-2-19-발송-결과-보고), [4-2-21 알림 통계](4-2-CONTRACT.md#4-2-21-알림-통계), [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건) |
| 메시지 큐, 재시도, 선점 시간 변경 | [5-3-5 재시도와 시간 한도](5-3-ERROR-HANDLING.md#5-3-5-재시도와-시간-한도) | [5-2-4 발송 요청의 선점과 임대](5-2-CONCURRENCY.md#5-2-4-발송-요청의-선점과-임대), [5-2-5 소비자 선점](5-2-CONCURRENCY.md#5-2-5-소비자-선점) |
| 발송 모드 전환 | [6-5 설정 변경](6-DEPLOYMENT.md#6-5-설정-변경) | [6-4 배포 조건](6-DEPLOYMENT.md#6-4-배포-조건), [6-6 적용과 복구](6-DEPLOYMENT.md#6-6-적용과-복구), [3-1-4 배포 단위](3-1-SOFTWARE-ARCHITECTURE.md#3-1-4-배포-단위) |
| 오류 코드 추가 | [5-3-2 앱 코드](5-3-ERROR-HANDLING.md#5-3-2-앱-코드) | [3-3-3 요청 검증과 오류](3-3-CONVENTIONS.md#3-3-3-요청-검증과-오류) |
| 동시 요청 문제 | [5-2 동시성](5-2-CONCURRENCY.md) | [4-1 처리 흐름](4-1-PIPELINES.md) |
| 로그나 지표 추가 | [5-4 관측](5-4-OBSERVABILITY.md) | [5-4-8 수집 조건과 실패 처리](5-4-OBSERVABILITY.md#5-4-8-수집-조건과-실패-처리) |
| 이미 내린 결정인지 확인 | [DECISIONS.md](DECISIONS.md) | 해당 결정에서 연결한 명세 절 |

<br>

### 3. 명세와 코드의 대응

서버 코드 경로는 `manyak-server` 저장소 루트 아래 `src/main/kotlin/com/knk/manyak/`이다. 알림 서비스 코드 경로는 `manyak-notification` 저장소 루트 아래 `src/main/kotlin/com/knk/manyak/notification/`이다. 완성과 검수 이벤트의 발행 지점은 STORY와 MODERATION 세트에서 다룬다. 탈퇴 시 토큰 삭제 호출은 ACCOUNT 세트에서 다룬다.

**1. 서버**

| 구성 요소 | 구현 위치 (`manyak-server` 기준) | 사용 범위 |
|---|---|---|
| 회원 API, 내부 API, 관리자 API | [push/controller/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/push/controller/) | 4-2-2~4-2-7<br>4-2-11~4-2-21 |
| 토큰, 동의, 자격, 발송기, 출석, 캠페인, 캠페인 관리, 템플릿, 결과 기록과 통계 | [push/service/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/push/service/) | 4-1-2~4-1-5, 4-1-8~4-1-10, 4-1-13, 4-1-15~4-1-17 |
| 완성 리스너 | [push/event/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/push/event/), [push/outbox/StoryCompletionOutboxListener.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/push/outbox/StoryCompletionOutboxListener.kt) | 4-1-6 |
| 검수 리스너 | [story/submission/ModerationPushListeners.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/submission/ModerationPushListeners.kt) | 4-1-7 |
| 아웃박스, 릴레이, 발행 어댑터 | [push/outbox/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/push/outbox/) | 4-1-11, 4-2-9, 5-2-4 |
| 스케줄러 | [push/scheduler/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/push/scheduler/) | 4-1-8~4-1-10 |
| 모델 | [push/entity/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/push/entity/), [push/repository/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/push/repository/), [auth/entity/User.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/auth/entity/User.kt) | 3-2 DB 스키마, 3-1-7 도메인 모델 |
| 발송 대상 조회 | [auth/repository/UserRepository.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/auth/repository/UserRepository.kt) | 4-1-8, 4-1-9 |
| 설정과 내부 인증 | [push/config/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/push/config/), [global/security/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/security/), [application.yml](../../../../../manyak-server/src/main/resources/application.yml) | 5-1-6, 6-3 |
| 오류 | [global/error/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/error/) | 5-3-2 앱 코드 |
| 관측 | [global/observability/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/observability/) | 5-4 관측 |
| 마이그레이션 | [db/migration/](../../../../../manyak-server/src/main/resources/db/migration/), [dbdoc/](../../../../../manyak-server/dbdoc/) | 3-2 DB 스키마 |
| 테스트 | [src/test/kotlin/com/knk/manyak/push/](../../../../../manyak-server/src/test/kotlin/com/knk/manyak/push/), [http/push/](../../../../../manyak-server/http/push/) | 5-5 테스트 케이스 |
| 배포 | [.github/workflows/](../../../../../manyak-server/.github/workflows/), [Dockerfile](../../../../../manyak-server/Dockerfile) | 6 배포 |

**2. 알림 서비스와 인프라**

| 구성 요소 | 구현 위치 (`manyak-notification` 기준, 인프라는 `manyak-terraform` 기준) | 사용 범위 |
|---|---|---|
| 소비자와 멱등 | [push/consumer/](../../../../../manyak-notification/src/main/kotlin/com/knk/manyak/notification/push/consumer/) | 4-1-12, 5-2-5 |
| 발송, 자격 조회, 결과 보고 | [push/service/](../../../../../manyak-notification/src/main/kotlin/com/knk/manyak/notification/push/service/), [push/client/](../../../../../manyak-notification/src/main/kotlin/com/knk/manyak/notification/push/client/) | 4-1-12~4-1-14 |
| API와 필터 | [push/controller/](../../../../../manyak-notification/src/main/kotlin/com/knk/manyak/notification/push/controller/), [global/](../../../../../manyak-notification/src/main/kotlin/com/knk/manyak/notification/global/) | 4-2-8, 5-1-6 |
| 메시지 큐와 운영 배치 | [envs/dev/sqs.tf](../../../../../manyak-terraform/terraform/envs/dev/sqs.tf), [envs/prod/sqs.tf](../../../../../manyak-terraform/terraform/envs/prod/sqs.tf), [envs/prod/notification.tf](../../../../../manyak-terraform/terraform/envs/prod/notification.tf) | 3-2-11, 6 배포 |
| 테스트 | [src/test/kotlin/com/knk/manyak/notification/](../../../../../manyak-notification/src/test/kotlin/com/knk/manyak/notification/), [http/notifications.http](../../../../../manyak-notification/http/notifications.http) | 5-5 테스트 케이스 |
| 배포 | [docker-image.yml](../../../../../manyak-notification/.github/workflows/docker-image.yml), [Dockerfile](../../../../../manyak-notification/Dockerfile) | 6 배포 |

<br>

### 4. 작성 규칙과 검증 명령

| 항목 | 위치 |
|---|---|
| 문서별 작성 기준 | [백엔드 명세 작성 가이드](../../../REFERENCE/BACKEND-SPEC-WRITING-GUIDE.md) |
| 문체와 파일명 | [제품 Spec 작성 가이드](../../../REFERENCE/PRODUCT-SPEC-WRITING-GUIDE.md) |
| 하네스 전체 지침 | 하네스 루트의 `AGENTS.md` |
| 코드 규칙 | `manyak-server`와 `manyak-notification`의 `CLAUDE.md` |
| 문서 변경 후 검사 | `git diff --check` 실행<br>링크, 앵커, 참조한 절 번호 확인 |
| 테스트 실행 | 두 저장소에서 각각 `./gradlew test` 실행<br>알림 서비스 통합 테스트는 Docker 필요<br>DB 제약은 서버 저장소의 `scripts/gen-db-docs.sh`로 실제 PostgreSQL에서 검증 |
| 원격 모드 수동 확인 | `http/push/push-mode-remote.http`의 절차 |

- 명세의 작성, 수정, 검토를 서브에이전트에 맡기지 않는다.
- 실제 비밀값, 푸시 토큰, FCM 자격 증명, 공유 시크릿을 문서에 넣지 않는다.
- 코드와 설정에서 확인할 수 없는 정책, 필드, 계약을 추측해 적지 않는다. 결정되지 않은 항목은 미정으로, 확인하지 못한 항목은 미확인으로 표시해 구분한다.
- 절의 제목이나 위치를 바꾸면 이 문서와 다른 문서의 링크도 고친다.

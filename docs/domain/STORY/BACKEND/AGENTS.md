# AGENTS.md

STORY 도메인 백엔드 명세를 읽고 수정할 때 필요한 문서와 코드 위치를 안내한다. 스토리 조회, 제공 장르, 간편 제작, 일반 제작 등록과 수정, 이미지, 좋아요와 신고, 삭제, 검색을 다룬다.

명세 본문과 설정값은 이 문서에 복사하지 않는다.

<br>

### 문서의 역할과 읽는 순서

| 문서 | 정하는 것 |
|---|---|
| [BACKGROUND.md](BACKGROUND.md) | 배경, 역할, 주체, 용어 |
| [REQUIREMENTS.md](REQUIREMENTS.md) | 요구 주체, 기대하는 동작, AI 서버와의 역할 분담, 제품 제약, 데이터 보존 |
| [SOFTWARE-ARCHITECTURE.md](SOFTWARE-ARCHITECTURE.md) | 개요, 배경과 목표, 품질 속성, 배포 단위, 모듈 구조, 의존 방향, 도메인 모델 |
| [DB-SCHEMA.md](DB-SCHEMA.md) | 테이블, 컬럼, 제약, 인덱스, 데이터 수명 |
| [CONVENTIONS.md](CONVENTIONS.md) | 이름, 계층 책임, 검증, 이벤트, 테스트 규칙 |
| [PIPELINES.md](PIPELINES.md) | 엔드포인트별 처리 흐름, AI 호출, 색인, 이름 토큰 치환 |
| [CONTRACT.md](CONTRACT.md) | 클라이언트, 다른 도메인과의 계약 |
| [SECURITY.md](SECURITY.md) | 인증 수준, 소유권, 계정 상태와 동의, 입력과 업로드 검증, 개인정보 |
| [CONCURRENCY.md](CONCURRENCY.md) | 멱등, 잠금, 유니크 위반 처리, 집계 |
| [ERROR-HANDLING.md](ERROR-HANDLING.md) | 응답 규칙, 앱 코드, 오류 분류, 복구, 시간 한도 |
| [OBSERVABILITY.md](OBSERVABILITY.md) | 관측 스택, 식별자, AI 헤더, 호출 기록, 로그, 지표, 트레이스, 알림, 분석 이벤트 |
| [TEST-CASES.md](TEST-CASES.md) | 테스트 범위와 케이스 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | 배포 단위, 환경 변수, 조건, 되돌리기 |
| [DECISIONS.md](DECISIONS.md) | 결정의 이력 |

- 처음에는 위 표의 순서로 배경, 요구사항, 설계와 계약을 확인하고 품질, 검증과 배포를 읽는다.
- 앞 단계의 결정이 뒤 단계의 기준이다. 구현에 맞추려고 앞 단계를 임의로 바꾸지 않는다.
- 미정이라고 적힌 항목을 추측으로 채우지 않는다.
- 다른 도메인과의 경계는 계약 문서의 마지막 절에 있다. ([다른 도메인과의 경계](CONTRACT.md#다른-도메인과의-경계))

<br>

### 작업별 참조

| 하려는 일 | 먼저 볼 곳 | 함께 볼 곳 |
|---|---|---|
| 요청이나 응답의 필드 변경 | [계약](CONTRACT.md) | [처리 흐름](PIPELINES.md), [배포 조건](DEPLOYMENT.md#배포-조건) |
| 테이블이나 컬럼 변경 | [DB 스키마](DB-SCHEMA.md) | [테스트와 검증 도구](CONVENTIONS.md#테스트와-검증-도구), [배포 조건](DEPLOYMENT.md#배포-조건) |
| 새 엔드포인트 | [공통 규칙과 헤더](CONTRACT.md#공통-규칙과-헤더) | [계층 책임](CONVENTIONS.md#계층-책임), 서버 저장소 `http/story/`의 수동 호출 파일과 통합 테스트 |
| 읽기나 소유권 규칙 변경 | [소유권과 읽기 판정](SECURITY.md#소유권과-읽기-판정) | [DECISIONS.md](DECISIONS.md) |
| 제공 장르, 화풍, 입력 검증 변경 | [제공 장르](CONTRACT.md#제공-장르), [화풍 목록](CONTRACT.md#화풍-목록) | [제품 제약](REQUIREMENTS.md#제품-제약), [카탈로그](DB-SCHEMA.md#카탈로그) |
| 이름 토큰과 치환 변경 | [이름 토큰 치환](PIPELINES.md#이름-토큰-치환) | [상세](PIPELINES.md#상세), [간편 제작 스토리라인 생성](PIPELINES.md#간편-제작-스토리라인-생성), [간편 제작 완성](PIPELINES.md#간편-제작-완성) |
| 오류 코드 추가 | [앱 코드](ERROR-HANDLING.md#앱-코드) | [요청 검증과 오류](CONVENTIONS.md#요청-검증과-오류) |
| AI 호출 변경 | [간편 제작 스토리라인 생성](PIPELINES.md#간편-제작-스토리라인-생성), [간편 제작 완성](PIPELINES.md#간편-제작-완성) | [AI 계약](../AI/CONTRACT.md), [AI 서버로 전달하는 헤더](OBSERVABILITY.md#ai-서버로-전달하는-헤더) |
| 동시 요청 문제 | [동시성](CONCURRENCY.md) | [처리 흐름](PIPELINES.md) |
| 로그나 지표 추가 | [관측](OBSERVABILITY.md) | [수집 조건과 실패 처리](OBSERVABILITY.md#수집-조건과-실패-처리) |
| 초안 저장이나 제작 탭 카드 변경 | [초안 목록](CONTRACT.md#초안-목록) | [초안 저장](PIPELINES.md#초안-저장), [생성 요청과 초안](DB-SCHEMA.md#생성-요청과-초안) |
| 이미 내린 결정인지 확인 | [DECISIONS.md](DECISIONS.md) | 해당 결정에서 연결한 명세 절 |

<br>

### 명세와 코드의 대응

코드 경로는 `manyak-server` 저장소 루트 아래 `src/main/kotlin/com/knk/manyak/`이다. `story/submission/*`는 MODERATION 세트에 속한다. 등록과 수정 요청의 API 계층과 입력 검증, 승인 시 저장과 적용만 이 세트에 속한다.

| 구성 요소 | 구현 위치 (`manyak-server` 기준) | 사용 범위 |
|---|---|---|
| API 계층 | [story/controller/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/controller/) | 계약, 5-1-1 인증 수준 |
| 조회와 소셜 | [StoryService.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/service/StoryService.kt) | 4-1-2~4-1-10 조회와 삭제, 4-1-21 좋아요, 4-1-22 신고 |
| 간편 제작 | [SimpleStoryCreationService.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/service/SimpleStoryCreationService.kt) | 4-1-11~4-1-14 간편 제작, 5-3-4 오류별 처리, 5-4-7 지표 |
| 생성 요청 기록 | [StoryCreationRequestRecorder.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/service/StoryCreationRequestRecorder.kt) | 멱등과 회수 |
| 일반 제작과 수정 | [StoryEditService.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/service/StoryEditService.kt), [GeneralStoryCreationService.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/service/GeneralStoryCreationService.kt) | 4-1-15~4-1-17 등록과 수정 |
| 제공 장르 | [GenreCatalogService.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/service/GenreCatalogService.kt), [GenreInputValidator.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/service/GenreInputValidator.kt) | 제공 장르, 5-1-4 입력 검증 |
| 이름 토큰 | [UsernameTokenRenderer.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/service/UsernameTokenRenderer.kt), [StoryTextRendering.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/service/StoryTextRendering.kt), [ProtagonistNameValidation.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/service/ProtagonistNameValidation.kt) | 공통 처리, 4-1-7 상세 |
| 이미지 | [StoryImageService.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/service/StoryImageService.kt), [StoryImageAccess.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/service/StoryImageAccess.kt), [image/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/image/) | 4-1-18~4-1-20 이미지, 5-1-5 업로드 검증 |
| 공개 스냅샷 | [StoryPublicSnapshotService.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/service/StoryPublicSnapshotService.kt), [StoryPublicSnapshot.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/entity/StoryPublicSnapshot.kt) | 공개 스냅샷 |
| 초안 | [user/draft/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/user/draft/), [StoryDraftController.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/user/controller/StoryDraftController.kt) | 4-1-23~4-1-26 초안, 4-2-23~4-2-26 초안 |
| 모델 | [story/entity/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/entity/) | DB 스키마, 3-1-7 도메인 모델 |
| AI 호출 | [StoryAiClient.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/story/client/StoryAiClient.kt) | 공통 처리, 4-1-11, 4-1-12 |
| 검색 | [search/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/search/) | 검색, 4-1-27 색인, 4-2-3 검색 |
| 오류와 보안 | [global/error/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/error/), [global/security/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/security/) | 오류 처리, 5-1 보안 |
| 관측 | [global/observability/](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/observability/), [TracingNoiseFilter.kt](../../../../../manyak-server/src/main/kotlin/com/knk/manyak/global/config/TracingNoiseFilter.kt) | 관측 |
| 마이그레이션 | [db/migration/](../../../../../manyak-server/src/main/resources/db/migration/), [dbdoc/](../../../../../manyak-server/dbdoc/) | DB 스키마 |
| 테스트 | [src/test/kotlin/com/knk/manyak/](../../../../../manyak-server/src/test/kotlin/com/knk/manyak/), [http/story/](../../../../../manyak-server/http/story/) | 테스트 케이스 |
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
| 테스트 실행 | 서버 저장소에서 `./gradlew test`, DB 제약은 `scripts/gen-db-docs.sh`로 실제 PostgreSQL에서 검증 |

- 명세의 작성, 수정, 검토를 서브에이전트에 맡기지 않는다.
- 실제 비밀값, 사용자 입력 원문, 생성 결과 원문을 문서에 넣지 않는다.
- 코드와 설정에서 확인할 수 없는 정책, 필드, 계약을 추측해 적지 않는다. 결정되지 않은 것은 미정으로, 확인하지 못한 것은 미확인으로 구분한다.
- 절의 제목이나 위치를 바꾸면 이 문서와 다른 문서의 링크도 고친다.

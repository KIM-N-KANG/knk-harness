# CLAUDE.md

간편 제작 스토리 생성 명세를 읽고 수정할 때 필요한 문서와 코드 위치를 안내한다. 대상은 스토리라인 생성, 컴파일, 인물 이미지와 썸네일 생성이다.

제품·스펙 문서는 하네스의 `docs/AI/`와 `docs/REFERENCE/` 안에서만 참조한다. 그 밖의 과거 문서와 해당 문서로 연결된 링크는 근거로 사용하지 않는다.

명세 본문과 설정값은 이 문서에 복사하지 않는다. 모델 이름, 제한 시간과 횟수는 해당 명세에서 확인한다.

<br>

### 1. 문서의 역할과 읽는 순서

| 문서 | 정하는 것 | 상태 |
|---|---|---|
| [1-BACKGROUND.md](1-BACKGROUND.md) | 배경, 흐름과 주체, 공통 용어 | 작성 |
| [2-1-USER-STORY.md](2-1-USER-STORY.md) | 사용자가 AI 결과에 기대하는 것 | 작성 |
| [2-2-OPERATION-REQUIREMENTS.md](2-2-OPERATION-REQUIREMENTS.md) | 품질, 시간과 비용의 목표 | 작성. 목표값은 대부분 미정 |
| [3-TASK-DEFINITION.md](3-TASK-DEFINITION.md) | 태스크별 입력, 출력과 결과 구분 | 작성 |
| [4-1-DESIGN-COGNITIVE-ARCHITECTURE.md](4-1-DESIGN-COGNITIVE-ARCHITECTURE.md) | 입력을 결과로 만드는 판단 구조 | 작성 |
| [4-2-DESIGN-SOFTWARE-ARCHITECTURE.md](4-2-DESIGN-SOFTWARE-ARCHITECTURE.md) | 구성 요소와 데이터 흐름 | 작성 |
| [5-CONTRACT.md](5-CONTRACT.md) | 백엔드, 모델 API와 주고받는 값과 실패 | 작성 |
| [6-1-AI-EXECUTION.md](6-1-AI-EXECUTION.md) | 요청 처리 순서, 프롬프트 조립, 모델 호출, 검증과 복구 | 작성 |
| [6-2-SOFTWARE-IMPLEMENTATION.md](6-2-SOFTWARE-IMPLEMENTATION.md) | 파일 배치, 인터페이스, 의존성, 구현 규칙과 금지 패턴 | 작성 |
| [6-3-AI-ALIGNMENT.md](6-3-AI-ALIGNMENT.md) | 품질 개선에 쓸 자료와 허용하는 방법 | 작성 |
| [6-4-AI-EVALUATION-METHOD.md](6-4-AI-EVALUATION-METHOD.md) | 평가 데이터, 채점 방법과 합격 판정 | 작성. 확정된 벤치마크 없음 |
| [6-5-AI-EVALUATION-IMPLEMENTATION.md](6-5-AI-EVALUATION-IMPLEMENTATION.md) | 평가 CLI의 실행, 저장과 재개 | 작성. 평가 CLI는 구현 예정 |
| [6-6-AI-PERFORMANCE-REPORT.md](6-6-AI-PERFORMANCE-REPORT.md) | 배포한 코드, 프롬프트와 설정 조합의 성능 기록 | 목차만 작성 |
| [7-1-ERROR-HANDLING.md](7-1-ERROR-HANDLING.md) | 단계별 오류의 처리 주체와 최종 결과 | 작성 |
| [7-2-TEST-CASES.md](7-2-TEST-CASES.md) | 단위와 통합 테스트 케이스 | 작성 |
| [7-3-OBSERVABILITY.md](7-3-OBSERVABILITY.md) | 추적 단위, 기록 항목, 지표와 알림 | 작성 |
| [7-4-DEPLOYMENT.md](7-4-DEPLOYMENT.md) | 배포 경로, 환경 변수, 운영 설정과 복구 | 작성 |
| [DECISIONS.md](DECISIONS.md) | 중요한 결정의 이력 | 작성 |

- 처음에는 1번부터 5번까지 순서대로 읽어 요구사항, 설계와 계약을 확인한다. 6번 문서들은 구현과 평가를, 7번 문서들은 운영을 다룬다.
- 앞 단계의 결정이 뒤 단계의 기준이다. 구현에 맞추려고 앞 단계의 결정을 임의로 바꾸지 않는다. 구현과 설계가 다르면 6번이나 7번 문서에 차이를 적는다.
- 앞 단계의 결정이 바뀌면 해당 문서를 먼저 고친다. 영향을 받는 이후 문서도 같은 작업에서 수정한다.
- 목차만 작성된 문서를 근거로 쓰지 않는다. 미정이라고 적힌 항목을 추측으로 채우지 않는다.
- 채팅은 별도 태스크다. 이 폴더의 문서를 채팅에 적용하지 않는다.

<br>

### 2. 작업별 참조

| 하려는 일 | 먼저 볼 곳 | 함께 볼 곳 |
|---|---|---|
| 요청이나 응답의 필드 변경 | [5-CONTRACT.md](5-CONTRACT.md) | [3-TASK-DEFINITION.md](3-TASK-DEFINITION.md), [7-4-7 배포](7-4-DEPLOYMENT.md#7-4-7-적용과-복구) |
| 프롬프트 수정 | [6-3-4 AI 정렬](6-3-AI-ALIGNMENT.md#6-3-4-개선-과정) | [6-1-4 AI 실행](6-1-AI-EXECUTION.md#6-1-4-프롬프트-조립), [6-3-6 AI 정렬](6-3-AI-ALIGNMENT.md#6-3-6-평가-데이터와-채택) |
| 모델이나 호출 옵션 변경 | [6-1-5 AI 실행](6-1-AI-EXECUTION.md#6-1-5-모델-호출) | [6-3-5 AI 정렬](6-3-AI-ALIGNMENT.md#6-3-5-허용-수단), [7-4-6 배포](7-4-DEPLOYMENT.md#7-4-6-운영-설정) |
| 검증과 보완 규칙 변경 | [6-1-6 AI 실행](6-1-AI-EXECUTION.md#6-1-6-검증과-복구) | [7-1-ERROR-HANDLING.md](7-1-ERROR-HANDLING.md), [7-2-TEST-CASES.md](7-2-TEST-CASES.md) |
| 코드 작성과 수정 | [6-2-SOFTWARE-IMPLEMENTATION.md](6-2-SOFTWARE-IMPLEMENTATION.md) | [6-2-6 소프트웨어 구현](6-2-SOFTWARE-IMPLEMENTATION.md#6-2-6-금지-패턴) |
| 오류 처리 변경 | [7-1-ERROR-HANDLING.md](7-1-ERROR-HANDLING.md) | [5-4 계약](5-CONTRACT.md#5-4-실패-계약) |
| 테스트 추가 | [7-2-TEST-CASES.md](7-2-TEST-CASES.md) | 연결된 명세의 절 |
| 품질 문제의 원인 분석 | [6-3-3 AI 정렬](6-3-AI-ALIGNMENT.md#6-3-3-원인-구분) | [7-3-OBSERVABILITY.md](7-3-OBSERVABILITY.md) |
| 평가 추가와 실행 | [6-4-AI-EVALUATION-METHOD.md](6-4-AI-EVALUATION-METHOD.md) | [6-5-AI-EVALUATION-IMPLEMENTATION.md](6-5-AI-EVALUATION-IMPLEMENTATION.md) |
| 기록 항목이나 지표 변경 | [7-3-OBSERVABILITY.md](7-3-OBSERVABILITY.md) | [7-3-7 관측](7-3-OBSERVABILITY.md#7-3-7-데이터와-수집-실패) |
| 배포와 되돌리기 | [7-4-DEPLOYMENT.md](7-4-DEPLOYMENT.md) | [7-4-7 배포](7-4-DEPLOYMENT.md#7-4-7-적용과-복구) |
| 이미 내린 결정인지 확인 | [DECISIONS.md](DECISIONS.md) | 해당 결정에서 연결한 태스크 문서 |

<br>

### 3. 명세와 코드의 대응

코드 경로는 `manyak-ai` 저장소 루트 기준이다. 아래 표는 주요 코드와 관련 명세를 연결한다. 파일별 역할은 파일 배치 절에서 확인한다. ([6-2-1 소프트웨어 구현](6-2-SOFTWARE-IMPLEMENTATION.md#6-2-1-파일-배치))

| 코드 | 명세 |
|---|---|
| `src/api/v1/story.py` | 5 계약, 6-1-1 진입과 종료, 7-3-1 추적 단위 |
| `src/schemas/` | 5 계약의 요청과 응답, 6-1-2 입력 검증 |
| `src/services/story_llm.py` | 6-1-5 모델 호출, 6-1-6 검증과 복구, 7-1 오류 처리 |
| `src/services/prompt.py`, `src/services/image/prompt.py`, `prompt/story/`, `prompt/image/` | 6-1-4 프롬프트 조립 |
| `src/services/llm/` | 5-8 모델 게이트웨이 계약, 6-1-5 모델 호출 |
| `src/services/image/` | 3-3 인물 이미지 생성, 3-4 썸네일 생성, 6-1-5의 이미지 모델 |
| `src/services/story_compile_render.py` | 6-1-7 후처리와 기록 |
| `src/core/config.py` | 7-4-5 환경 변수와 비밀 정보 |
| `src/core/sentry.py`, `src/core/langfuse.py` | 7-3 관측 |
| `src/main.py` | 6-2-3 의존성, 6-2-5의 서버 시작 검사 |
| `tests/` | 7-2 테스트 케이스 |
| `experiment/` | 6-3-6 평가 데이터와 채택, 6-4 평가 방법, 6-5 평가 구현. git에서 제외된 로컬 디렉터리 |
| `Dockerfile`, `.github/workflows/docker-image.yml` | 7-4 배포 |

`src/services/llm/`, `src/services/image/`와 `src/core/`는 채팅 태스크에서도 사용한다. 수정하면 채팅에도 영향을 준다.

<br>

### 4. 작성 규칙과 검증 명령

| 항목 | 위치 |
|---|---|
| 문서별 작성 기준과 문체 | [AI 명세 작성 가이드](../../REFERENCE/AI-SPEC-WRITING-GUIDE.md) |
| 하네스 전체의 문서 지침 | 하네스 루트의 `CLAUDE.md` |
| 코드 규칙 | `manyak-ai`의 `AGENTS.md`, `.agents/STYLEGUIDE.md` |
| 문서 변경 뒤의 검사 | `git diff --check` 실행. 링크, 앵커와 참조한 절 번호도 확인 |
| 테스트 실행 | `manyak-ai`의 `scripts/test.sh`로 실행. [7-2-7 테스트 케이스](7-2-TEST-CASES.md#7-2-7-실행-증거) |

- 명세의 작성, 수정과 검토를 서브에이전트에 맡기지 않는다.
- 실제 비밀값, 사용자 입력 원문, 프롬프트 전문과 생성 결과 원문을 문서에 넣지 않는다.
- 저장소에서 확인할 수 없는 정책, 필드와 계약을 추측해 적지 않는다. 결정되지 않은 것은 미정, 확인하지 못한 것은 미확인으로 구분한다.
- 절의 제목이나 위치를 바꾸면 해당 절을 참조하는 다른 문서의 링크도 고친다.
- 문서의 작성 상태가 바뀌면 첫 번째 표도 갱신한다.

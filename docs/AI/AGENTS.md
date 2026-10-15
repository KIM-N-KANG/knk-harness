# AGENTS.md

간편 제작 스토리 생성과 채팅 명세를 읽고 수정할 때 필요한 문서와 코드 위치를 안내한다. 이 파일의 상대경로는 `docs/AI/` 기준이다.

제품 명세 문서는 하네스의 `docs/AI/`와 `docs/REFERENCE/` 안에서만 참조한다. 그 밖의 과거 문서와 해당 문서로 연결된 링크는 근거로 사용하지 않는다.

명세 본문과 설정값은 이 문서에 복사하지 않는다. 모델 이름, 제한 시간과 횟수는 해당 태스크의 명세에서 확인한다.

<br>

### 1. 태스크 선택과 읽는 순서

| 문서 묶음 | 대상 |
|---|---|
| [SIMPLE-GENERATION-STORY](SIMPLE-GENERATION-STORY/1-BACKGROUND.md) | 스토리라인 생성, 컴파일, 인물 이미지와 썸네일 생성 |
| [CHAT](CHAT/1-BACKGROUND.md) | 채팅 응답 생성, 사건과 엔딩 판정, 실시간 이미지 생성과 선택지 생성 |

- 작업할 태스크의 폴더를 먼저 선택한다. 같은 파일명과 절 번호라도 태스크별 내용은 다르다. 한쪽의 정책과 계약을 다른 쪽에 그대로 적용하지 않는다.
- 처음에는 1번부터 5번까지 순서대로 읽어 요구사항, 설계와 계약을 확인한다. 6번 문서들은 구현과 평가를, 7번 문서들은 운영을 다룬다.
- 앞 단계의 결정이 뒤 단계의 기준이다. 구현에 맞추려고 앞 단계의 결정을 임의로 바꾸지 않는다. 구현과 설계가 다르면 6번이나 7번 문서에 차이를 적는다.
- 앞 단계의 결정이 바뀌면 해당 문서를 먼저 고친다. 영향을 받는 이후 문서도 같은 작업에서 수정한다.
- 제작 결과를 채팅 입력으로 전달하는 부분을 바꾸면 양쪽의 태스크 정의와 계약을 함께 확인한다.

<br>

### 2. 작업별 참조

아래 파일명은 선택한 태스크의 폴더 기준이다. 절 번호와 제목은 해당 문서에서 확인한다.

| 하려는 일 | 먼저 볼 곳 | 함께 볼 곳 |
|---|---|---|
| 요청이나 응답의 필드 변경 | `5-CONTRACT.md` | `3-TASK-DEFINITION.md`, `7-4-DEPLOYMENT.md` |
| 프롬프트 수정 | `6-3-AI-ALIGNMENT.md` | `6-1-AI-EXECUTION.md`, `6-4-AI-EVALUATION-METHOD.md` |
| 모델이나 호출 옵션 변경 | `6-1-AI-EXECUTION.md` | `6-3-AI-ALIGNMENT.md`, `7-4-DEPLOYMENT.md` |
| 검증과 보완 규칙 변경 | `6-1-AI-EXECUTION.md` | `7-1-ERROR-HANDLING.md`, `7-2-TEST-CASES.md` |
| 코드 작성과 수정 | `6-2-SOFTWARE-IMPLEMENTATION.md` | `4-2-DESIGN-SOFTWARE-ARCHITECTURE.md`, `6-1-AI-EXECUTION.md` |
| 오류 처리 변경 | `7-1-ERROR-HANDLING.md` | `5-CONTRACT.md` |
| 테스트 추가 | `7-2-TEST-CASES.md` | 연결된 명세의 절 |
| 품질 문제의 원인 분석 | `6-3-AI-ALIGNMENT.md` | `7-3-OBSERVABILITY.md` |
| 평가 추가와 실행 | `6-4-AI-EVALUATION-METHOD.md` | `6-5-AI-EVALUATION-IMPLEMENTATION.md` |
| 기록 항목이나 지표 변경 | `7-3-OBSERVABILITY.md` | `5-CONTRACT.md` |
| 배포와 되돌리기 | `7-4-DEPLOYMENT.md` | `7-2-TEST-CASES.md` |
| 이미 내린 결정인지 확인 | `DECISIONS.md` | 해당 결정에서 연결한 태스크 문서 |

<br>

### 3. 명세와 코드의 대응

구현 저장소는 하네스 루트 기준 `../manyak-ai`다. 아래 코드 경로는 구현 저장소 루트 기준이며, 관련 코드를 찾는 시작점으로 사용한다. 파일별 역할과 구현 규칙은 각 태스크의 소프트웨어 구현 문서에서 확인한다. ([간편 제작 소프트웨어 구현](SIMPLE-GENERATION-STORY/6-2-SOFTWARE-IMPLEMENTATION.md), [채팅 소프트웨어 구현](CHAT/6-2-SOFTWARE-IMPLEMENTATION.md))

| 범위 | 코드 진입점 | 관련 명세 |
|---|---|---|
| 간편 제작 | `src/api/v1/story.py`, `src/services/story_llm.py` | 간편 제작의 `5-CONTRACT.md`, `6-1-AI-EXECUTION.md` |
| 채팅 | `src/api/v1/chat.py`, `src/services/chat_llm.py` | 채팅의 `5-CONTRACT.md`, `6-1-AI-EXECUTION.md` |
| 요청과 응답 모델 | `src/schemas/` | 각 태스크의 `5-CONTRACT.md` |
| 모델 호출과 이미지 공통 처리 | `src/services/llm/`, `src/services/image/` | 각 태스크의 `6-1-AI-EXECUTION.md`, `7-1-ERROR-HANDLING.md` |
| 설정과 초기화 | `src/core/`, `src/main.py` | 각 태스크의 `6-2-SOFTWARE-IMPLEMENTATION.md`, `7-4-DEPLOYMENT.md` |

- 공통 코드를 수정하면 두 태스크의 영향을 확인하고 관련 테스트를 함께 실행한다.
- 코드 기본값과 실제 운영 주입값을 구분한다. 운영값은 해당 태스크의 `7-4-DEPLOYMENT.md`에서 주입 경로를 찾고, 실행 중인 배포 버전과 환경 변수, 설정 저장소의 적용 관계를 확인한다. 코드 기본값이나 Terraform 기본값만으로 운영값을 단정하지 않는다.
- 간편 제작의 로컬 평가 자료는 git에서 제외된 `experiment/`에 있다. 평가 방법과 실행 설계는 해당 태스크의 `6-4-AI-EVALUATION-METHOD.md`와 `6-5-AI-EVALUATION-IMPLEMENTATION.md`를 따른다.

<br>

### 4. 작성 규칙과 검증 명령

문서를 작성하거나 수정하기 전에 제품 Spec 작성 가이드의 공통 규칙과 AI Spec 작성 가이드의 해당 문서 기준을 읽는다. 그림을 수정하면 그림 작성 규칙도 확인한다.

| 항목 | 위치 |
|---|---|
| 공통 문체와 형식 | [PRODUCT-SPEC-WRITING-GUIDE.md](../REFERENCE/PRODUCT-SPEC-WRITING-GUIDE.md) |
| 문서별 작성 기준과 그림 규칙 | [AI-SPEC-WRITING-GUIDE.md](../REFERENCE/AI-SPEC-WRITING-GUIDE.md) |
| 하네스 전체의 문서 지침 | [AGENTS.md](../../AGENTS.md) |
| 코드 규칙 | `manyak-ai`의 `AGENTS.md`, `.agents/STYLEGUIDE.md` |
| 문서 변경 뒤의 검사 | `git diff --check`를 실행함 <br> 링크, 앵커와 참조한 절 번호도 확인함 |
| 테스트 실행 | `manyak-ai`의 `scripts/test.sh`로 실행함 <br> 대상과 검증 기준은 각 태스크의 `7-2-TEST-CASES.md`에서 확인함 |

- 명세의 작성, 수정과 검토를 서브에이전트에 맡기지 않는다.
- 실제 비밀값, 사용자 입력 원문, 프롬프트 전문과 생성 결과 원문을 문서에 넣지 않는다.
- 본문이 비어 있거나 목차만 있는 문서는 근거로 쓰지 않는다. 다른 태스크의 명세로 빈 항목을 대신하지 않는다.
- 저장소에서 확인할 수 없는 정책, 필드와 계약이나 코드만으로 알 수 없는 정책 승인 여부와 결정 이유를 추측하지 않는다. 결정되지 않은 것은 미정, 확인하지 못한 것은 미확인으로 구분한다.
- 파일이나 절의 제목과 위치를 바꾸면 해당 대상을 참조하는 다른 문서의 링크도 고친다.

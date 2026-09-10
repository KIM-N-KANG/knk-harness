# 김앤강 LLM 작업 하네스

이 저장소는 팀원이 Claude 같은 LLM 개발 도구를 같은 규칙으로 사용하도록 돕는 공용 하네스입니다.

## 워크스페이스 구조

팀원은 로컬 작업 공간을 아래 구조로 맞춥니다.

```text
knk-workspace/
├── knk-harness/
├── manyak-web/
├── manyak-android/
├── manyak-server/
├── manyak-ai/
├── manyak-terraform/
└── manyak-infra/
```

- `knk-harness/`: 공통 LLM 작업 규칙과 팀 운영 지침을 담는 저장소입니다.
- `manyak-web/`: 마냑 웹 프론트엔드 저장소입니다.
- `manyak-android/`: 마냑 안드로이드 앱 저장소입니다.
- `manyak-server/`: 마냑 백엔드 서버 저장소입니다.
- `manyak-ai/`: 마냑 AI 서버 저장소입니다.
- `manyak-terraform/`: 마냑 운영 AWS Terraform 저장소입니다.
- `manyak-infra/`: GHCR `dev` 이미지 기반 로컬·통합 Docker Compose 저장소입니다.

예시:

```bash
mkdir -p ~/Projects/knk-workspace
cd ~/Projects/knk-workspace

git clone https://github.com/KIM-N-KANG/knk-harness.git
git clone <manyak-web-repository-url>
git clone <manyak-android-repository-url>
git clone <manyak-server-repository-url>
git clone <manyak-ai-repository-url>
git clone <manyak-terraform-repository-url>
git clone <manyak-infra-repository-url>
```

## 제품 스펙 문서

제품 문서는 `docs/spec/`(배경·요구·계약), `docs/design/`(현재 내부 구조), `docs/adr/`(누적 결정 기록)로 나눕니다. 세 폴더는 `docs/` 바로 아래에 둡니다. 숫자 접두어는 각 폴더에서 독립적으로 관리합니다. 클라이언트는 Spec에서 `3-1` 공통·`3-2` 웹·`3-3` Android, Design에서 `1-1` 웹·`1-2` Android, ADR에서 `1-1` 공통·`1-2` 웹·`1-3` Android를 사용합니다. Android 모듈 구조는 Android Design에 통합하며 없는 역할의 파일을 번호를 채우려고 만들지 않습니다.

현재 파일명에 맞춰 제목·절 번호·참조를 정리하고 백엔드 Design·ADR과 AI Design을 원문에서 분리했습니다. Android 모듈 설계는 Android Design에 통합했습니다. 남은 본문 정리와 검증 범위는 [개정 계획](docs/planning/product-document-reorganization.md)을 따릅니다.

| 분류·번호 | 문서 | 역할 |
| --- | --- | --- |
| spec · 0 | [용어집](docs/spec/0-glossary.md) | 공식 용어·한영 표기·네이밍 규칙 |
| spec · 1 | [서비스 배경](docs/spec/1-background.md) | 서비스 배경, 타겟 사용자, MVP 범위 |
| spec · 2 | [유저 스토리](docs/spec/2-user-stories.md) | 화면·기능별 사용자 요구 |
| spec · 3-1 | [클라이언트 공통](docs/spec/3-1-client-spec.md) | 공통 화면·상태·사용자 흐름·API 사용 계약 |
| spec · 3-2 | [웹](docs/spec/3-2-web-spec.md) | 웹 사용자 계약·라우팅·브라우저 지원·검수 기준 |
| spec · 3-3 | [Android](docs/spec/3-3-android-spec.md) | Android 사용자 계약·플랫폼 예외·수용 기준 |
| spec · 4 | [백엔드](docs/spec/4-backend-server-spec.md) | API·데이터 모델·오류·운영 기준 |
| spec · 5 | [AI 서버](docs/spec/5-ai-server-spec.md) | AI 기능·입출력·실패 계약·평가 시스템 |
| spec · 6 | [분석](docs/spec/6-analytics.md) | 이벤트·지표·관측·검수 기준 |
| design · 1-1 | [웹 설계](docs/design/1-1-web-design.md) | 웹의 현재 기술 구조 |
| design · 1-2 | [Android 설계](docs/design/1-2-android-design.md) | Android의 현재 기술 구조 |
| design · 2 | [백엔드 설계](docs/design/2-backend-server-design.md) | 요청 경계·저장소·동시성·운영 배선 |
| design · 3 | [AI 설계](docs/design/3-ai-server-design.md) | 호출 계층·모델·프롬프트·관측 설정 |
| design · 4 | [배포 설계](docs/design/4-deployment.md) | 운영·개발·통합 배포와 복구 구조 |
| adr · 1-1 | [공통 ADR](docs/adr/1-1-client-adr.md) | 공통 결정 당시 맥락·선택·이유 |
| adr · 1-2 | [웹 ADR](docs/adr/1-2-web-adr.md) | 웹 결정 당시 맥락·선택·이유 |
| adr · 1-3 | [Android ADR](docs/adr/1-3-android-adr.md) | Android 결정 당시 맥락·선택·이유 |
| adr · 2 | [백엔드 ADR](docs/adr/2-backend-server-adr.md) | 백엔드 결정의 맥락·선택·근거 |
| adr · 3 | [AI ADR](docs/adr/3-ai-server-adr.md) | AI 설계의 배경·대안·선택 근거 |

구현 맥락이 필요하면 `knk-harness/`만 보지 말고 같은 `knk-workspace/` 아래의 서비스 저장소도 함께 확인합니다.

| 영역 | 참조 경로 |
| --- | --- |
| 웹 프론트엔드 | `../manyak-web` |
| 안드로이드 앱 | `../manyak-android` |
| 백엔드 서버 | `../manyak-server` |
| AI 서버 | `../manyak-ai` |
| 운영 Terraform | `../manyak-terraform` |
| 로컬·통합 인프라 | `../manyak-infra` |

## 계획 문서

Phase와 로드맵은 `docs/planning/roadmap.md`, 계약 적용·코드·검증·배포 근거는 추적 문서가 소유합니다. 작업 담당·일정·진행의 정본은 Jira입니다. 기능별 미래 상세 설계와 작업 순서·검증·복구 계획은 구현 저장소에 둡니다.

| 문서 | 역할 |
| --- | --- |
| `docs/planning/roadmap.md` | Phase별 개발 목표, 스프린트 일정, 작업 범위, 백로그 |
| [클라이언트 진행·추적](docs/planning/client-tracking.md) | 계약 적용·구현·검증·Jira·계획 연결 |
| [제품 문서 재구성 계획](docs/planning/product-document-reorganization.md) | 이번 경로·번호 변경 결과와 남은 본문 분리 계획 |

## 개발 레포지토리에 하네스 연결

하네스의 공통 진입점과 지침 정본은 `AGENTS.md`입니다. 하네스와 웹 레포지토리의 `CLAUDE.md`는 같은 디렉터리의 `AGENTS.md`를 가리키는 Claude Code 호환 링크입니다. 지침을 수정할 때는 정본을 수정하고 링크는 유지합니다.

### AGENTS.md

개발 레포지토리의 `AGENTS.md` 맨 위에 아래 내용을 둡니다. 레포지토리별 추가 규칙은 이 블록 아래에 작성합니다. Claude Code를 함께 쓰는 레포지토리는 `CLAUDE.md`가 이 파일을 가리키도록 연결합니다.

```markdown
# 기본 지침

작업 시작 시 `../knk-harness/AGENTS.md`를 읽으세요. 이후에는 작업과 관련된 문서와 스킬만 확인하세요.

## <레포별 독립 작업 규칙>
```

## 팀 공용 스킬

공용 스킬의 정본은 `.agents/skills/` 아래에 있습니다. 스킬을 추가하거나 수정할 때는 해당 스킬의 `SKILL.md`와 필요한 보조 파일을 이 경로에서 변경합니다. `.claude/skills/`의 스킬별 항목은 정본을 가리키는 Claude Code 호환 링크입니다.

현재 제공하는 스킬은 아래와 같습니다.

| 스킬 | 사용하는 상황 | 주요 확인 항목 |
| --- | --- | --- |
| `create-branch` | Jira 티켓 번호로 팀 브랜치 규칙에 맞는 Git 브랜치를 만들 때 | Jira 키, 브랜치 태그, 최신 `origin/dev` 기준 분기, 워크트리 변경사항 |
| `create-commit` | 로컬 변경사항을 팀 커밋 메시지 규칙에 맞게 커밋할 때 | 변경사항 diff, 브랜치의 Jira 키, 커밋 태그, 테스트 결과 |
| `create-pr` | 현재 브랜치의 변경사항으로 Draft PR을 만들거나 기존 PR에 반영할 때 | 선택한 base(기본 `dev`), 기존 PR 재사용, PR 제목·본문, 검증 결과 |
| `technical-writing` | 개발자나 제품 사용자를 위한 한국어 기술 문서를 작성, 검토, 재작성할 때 | 독자, 문서 목적, 용어 일관성, 환경/버전 맥락, Markdown 형식, 검토 체크리스트 |
| `karpathy-guidelines` | 코드를 작성, 리뷰, 리팩터링할 때 흔한 LLM 코딩 실수를 줄일 때 | 변경 최소화, 복잡성 관리, 기존 패턴 준수, 검증 |

## 스킬 사용 전 도구 확인

스킬은 저장소 규칙을 설명하지만, 실제 작업에는 로컬 도구와 외부 서비스 권한이 필요할 수 있습니다. 작업 전에 아래 항목을 확인합니다.

| 항목 | 필요한 스킬 | 확인 방법 | 없을 때 처리 |
| --- | --- | --- | --- |
| Git | 전체 | `git status --short --branch` | Git 저장소인지 먼저 확인합니다. |
| Python 3 | `create-branch` | `python3 --version` | 브랜치 이름 생성 스크립트를 실행할 수 없습니다. |
| GitHub CLI | `create-pr` | `gh auth status` | PR 생성 전에 GitHub 로그인을 설정합니다. |
| GitHub 원격 설정 | `create-pr` | `git remote -v` | 인증·원격 설정 확인은 push 권한을 보장하지 않습니다. 실제 push는 요청된 PR 생성 절차에서 수행하고, 실패하면 원인을 보고합니다. |
| Atlassian Rovo/Jira MCP | `create-branch` | Codex/Claude에서 Jira 이슈 조회 도구를 사용할 수 있는지 확인 | Jira 제목을 자동 조회할 수 없으므로 사용자가 이슈 제목을 제공해야 합니다. |

## 스킬별 외부 의존성

### create-branch

`create-branch`는 대상 저장소에서 실행하며, 새 브랜치는 기본적으로 fetch한 `origin/dev`에서 분기합니다. 원격 접근이 안 되면 로컬 `dev`로 자동 대체하지 않습니다. 사용자가 로컬 기준이나 오프라인 작업을 지정하면 `--base`로 기존 Git ref를 명시합니다. 기존 브랜치 전환은 fetch 없이 처리합니다. 가능하면 Jira 이슈를 조회하고, Jira를 사용할 수 없으면 대화에서 확정된 키와 충분한 작업 맥락으로 진행합니다.

필수:

- `git`
- `python3`

선택:

- Atlassian Rovo 또는 Jira MCP

### create-commit

`create-commit`은 로컬 Git 변경사항을 확인하고 커밋 메시지를 작성합니다. 외부 MCP는 필요하지 않습니다.

필수:

- `git`

### create-pr

`create-pr`는 요청된 변경을 원격에 push하고 Draft PR을 생성하거나 기존 PR에 반영합니다. 기본 base는 `dev`이며 사용자 지정 또는 기존 PR의 base를 존중합니다. 본문·캡처를 준비한 뒤 PR을 생성하고, 확보한 PR URL에서 이미지를 첨부합니다. GitHub CLI(`gh`)를 사용하며, 이미지 첨부에는 로그인된 브라우저가 필요합니다. 본문은 `docs/templates/pull-request/`에서 가장 가까운 템플릿을 골라 변경에 맞게 조정합니다.

필수:

- `git`
- `gh`
- GitHub 인증과 저장소 push 권한

### technical-writing

`technical-writing`은 한국어 기술 문서, 가이드, 튜토리얼, API 문서, 릴리스 노트, 회의록, 제안서를 계획, 작성, 검토, 재작성할 때 사용합니다.

필수:

- 없음

# 김앤강 LLM 작업 하네스

이 저장소는 팀원이 Claude 같은 LLM 개발 도구를 같은 규칙으로 사용하도록 돕는 공용 하네스입니다.

## 워크스페이스 구조

팀원은 로컬 작업 공간을 아래 구조로 맞춥니다.

```text
knk-workspace/
├── knk-harness/
├── <development-repo-1>/
└── <development-repo-2>/
```

- `knk-harness/`: 공통 LLM 작업 규칙과 팀 운영 지침을 담는 저장소입니다.
- `<development-repo-*>/`: 실제 제품이나 서비스 코드를 개발하는 저장소입니다.

예시:

```bash
mkdir -p ~/Projects/knk-workspace
cd ~/Projects/knk-workspace

git clone https://github.com/KIM-N-KANG/knk-harness.git
git clone <development-repository-url>
```

## 개발 레포지토리에 하네스 연결

현재 워크트리에서 하네스의 공통 진입점은 `CLAUDE.md`입니다. 각 개발 레포지토리 루트에는 도구별 지침 파일을 두고, 작업을 시작하기 전에 `../knk-harness/CLAUDE.md`를 먼저 읽게 만듭니다.

### CLAUDE.md

Claude Code를 쓰는 개발 레포지토리에서는 `CLAUDE.md` 맨 위에 아래 내용을 둡니다. 레포지토리별 추가 규칙은 이 블록 아래에 작성합니다.

```markdown
# 기본 지침

작업을 시작하기 전에 다음 문서를 먼저 확인하세요.

- `../knk-harness/CLAUDE.md`

## <레포별 독립 작업 규칙>
```

## 팀 공용 스킬

공용 스킬은 `.claude/skills/` 아래에 있습니다. 스킬을 추가하거나 수정할 때는 해당 스킬의 `SKILL.md`와 필요한 보조 파일을 이 경로에서 변경합니다.

현재 제공하는 스킬은 아래와 같습니다.

| 스킬 | 사용하는 상황 | 주요 확인 항목 |
| --- | --- | --- |
| `create-branch` | Jira 티켓 번호로 팀 브랜치 규칙에 맞는 Git 브랜치를 만들 때 | Jira 키, 브랜치 태그, `dev` 기준 분기, 워크트리 변경사항 |
| `create-commit` | 로컬 변경사항을 팀 커밋 메시지 규칙에 맞게 커밋할 때 | 변경사항 diff, 브랜치의 Jira 키, 커밋 태그, 테스트 결과 |
| `create-pr` | 현재 브랜치의 변경사항으로 Draft Pull Request를 만들 때 | base `dev`, 기존 PR 여부, PR 제목, PR 본문, 검증 결과 |
| `technical-writing` | 개발자나 제품 사용자를 위한 한국어 기술 문서를 작성, 검토, 재작성할 때 | 독자, 문서 목적, 용어 일관성, 환경/버전 맥락, Markdown 형식, 검토 체크리스트 |
| `karpathy-guidelines` | 코드를 작성, 리뷰, 리팩터링할 때 흔한 LLM 코딩 실수를 줄일 때 | 변경 최소화, 복잡성 관리, 기존 패턴 준수, 검증 |

## 문서 템플릿

PR 템플릿은 `docs/templates/pull-request/` 아래에 있습니다. `create-pr`는 PR 본문을 만들 때 작업 중인 레포지토리의 특성에 맞는 템플릿을 참고합니다.

| 템플릿 | 사용하는 상황 |
| --- | --- |
| `harness-pull-request-template.md` | 하네스 레포지토리 변경 |
| `frontend-pull-request-template.md` | 프론트엔드 화면, 브라우저 UI, 접근성, 반응형 변경 |
| `mobile-pull-request-template.md` | 모바일 앱 화면이나 모바일 플랫폼 변경 |
| `backend-server-pull-request-template.md` | API, DB, 인증, 서버 비즈니스 로직 변경 |
| `ai-server-pull-request-template.md` | Prompt, Model, RAG, Tool/Agent, Evaluation, Dataset 변경 |

## 스킬 사용 전 도구 확인

스킬은 저장소 규칙을 설명하지만, 실제 작업에는 로컬 도구와 외부 서비스 권한이 필요할 수 있습니다. 작업 전에 아래 항목을 확인합니다.

| 항목 | 필요한 스킬 | 확인 방법 | 없을 때 처리 |
| --- | --- | --- | --- |
| Git | 전체 | `git status --short --branch` | Git 저장소인지 먼저 확인합니다. |
| Python 3 | `create-branch` | `python3 --version` | 브랜치 이름 생성 스크립트를 실행할 수 없습니다. |
| GitHub CLI | `create-pr` | `gh auth status` | PR 생성 전에 GitHub 로그인을 설정합니다. |
| GitHub push 권한 | `create-pr` | `git push -u origin HEAD` | 권한이 없으면 PR을 만들 수 없습니다. |
| Atlassian Rovo/Jira MCP | `create-branch` | Codex/Claude에서 Jira 이슈 조회 도구를 사용할 수 있는지 확인 | Jira 제목을 자동 조회할 수 없으므로 사용자가 이슈 제목을 제공해야 합니다. |

## 스킬별 외부 의존성

### create-branch

`create-branch`는 가능하면 Atlassian Rovo/Jira MCP로 Jira 이슈를 조회합니다. MCP를 사용할 수 없으면 스킬은 사용자가 제공한 Jira 키와 제목으로 브랜치를 만들 수 있습니다.

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

`create-pr`는 현재 브랜치를 원격에 push하고 GitHub에 Draft Pull Request를 만듭니다. GitHub MCP는 필수가 아니며, 현재 스킬은 GitHub CLI(`gh`)를 사용합니다. PR 본문은 `docs/templates/pull-request/`의 템플릿 중 작업 레포지토리와 변경 유형에 맞는 파일을 참고해 작성합니다.

필수:

- `git`
- `gh`
- GitHub 인증과 저장소 push 권한

### technical-writing

`technical-writing`은 한국어 기술 문서, 가이드, 튜토리얼, API 문서, 릴리스 노트, 회의록, 제안서를 계획, 작성, 검토, 재작성할 때 사용합니다.

필수:

- 없음

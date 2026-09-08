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

제품 스펙 문서는 `docs/product-specs/` 아래에 번호 순서로 둡니다. 제품 정책, 기능 요구, API 계약, 이벤트 이름, 로그 필드처럼 구현에 영향을 주는 기준은 먼저 이 문서를 확인합니다.

| 순서 | 문서 | 역할 |
| --- | --- | --- |
| 1 | `docs/product-specs/1-background.md` | 서비스 배경, 타겟 사용자, MVP 범위 |
| 2 | `docs/product-specs/2-user-stories.md` | 화면·기능별 사용자 요구 |
| 3-1 | `docs/product-specs/3-1-client.md` | 클라이언트 공통 화면, 상태, 사용자 흐름, API 사용 계약 |
| 3-2 | `docs/product-specs/3-2-web-app.md` | 웹 라우팅, BFF 프록시·토큰 세션, 브라우저 지원, 웹 검수 기준 |
| 3-3 | `docs/product-specs/3-3-android-app.md` | 안드로이드 앱(Jetpack Compose) 플랫폼 구현 기준 |
| 4 | `docs/product-specs/4-backend.md` | 백엔드 API, 데이터 모델, 오류 처리, 운영 기준 |
| 5-1 | `docs/product-specs/5-1-ai-server-spec.md` | AI 기능·입출력·실패 계약·평가 시스템 |
| 5-2 | `docs/product-specs/5-2-ai-server-ard.md` | AI 설계의 배경·대안·선택 근거 |
| 6 | `docs/product-specs/6-analytics.md` | 분석 이벤트, 핵심 지표, 관측 구현, 릴리스 검수 기준 |
| 7 | `docs/product-specs/7-deployment.md` | 운영·개발·통합 배포, 인프라, CI/CD, 검수·롤백 기준 |

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

계획 문서는 `docs/planning/` 아래에 둡니다. 스펙(무엇을 어떻게 만들지)과 달리 개발 순서·기간·우선순위를 다룹니다.

| 문서 | 역할 |
| --- | --- |
| `docs/planning/roadmap.md` | Phase별 개발 목표, 스프린트 일정, 작업 범위, 백로그 |

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

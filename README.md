# 김앤강 팀 하네스 레포지토리

## 레포지토리는 하나의 워크스페이스 아래에 모읍니다

팀원은 로컬 작업 공간을 다음 구조로 맞춥니다.

```text
knk-workspace/
├── llm-wiki/
├── knk-harness/
├── <development-repo-1>/
└── <development-repo-2>/
```

- `llm-wiki/`: LLM이 참고하는 프로젝트 지식 저장소입니다.
- `knk-harness/`: 공통 LLM 작업 규칙과 팀 운영 지침을 담는 하네스 레포지토리입니다.
- `<development-repo-*>/`: 실제 제품이나 서비스 코드를 개발하는 레포지토리입니다.

예시는 다음과 같습니다.

```bash
mkdir -p ~/Projects/knk-workspace
cd ~/Projects/knk-workspace

git clone https://github.com/KIM-N-KANG/llm-wiki.git
git clone https://github.com/KIM-N-KANG/knk-harness.git
git clone <development-repository-url>
```

## 개발 레포지토리마다 LLM 지침 파일을 둡니다

각 개발 레포지토리의 루트에는 `AGENTS.md` 혹은 `CLAUDE.md`를 둡니다. 두 파일은 개발 레포지토리에서 작업하는 LLM 도구가 먼저 `../knk-harness/AGENTS.md 혹은 CLAUDE.md`를 읽게 만드는 역할을 합니다.

### `AGENTS.md`

개발 레포지토리의 `AGENTS.md`는 아래 내용을 파일 맨 위에 둡니다. 레포지토리별 추가 규칙이 있다면 이 블록 아래에 이어서 작성합니다.

```markdown
## Basic Instructions

Before starting work, review the following document first:
- `../knk-harness/AGENTS.md`
```

### `CLAUDE.md`

개발 레포지토리의 `CLAUDE.md`에는 `AGENTS.md`의 내용을 그대로 옮깁니다.

```markdown
@AGENTS.md
```

## 팀 공용 스킬을 둡니다

공용 스킬은 `knk-harness/.agents/skills/`에 둡니다. 개발 레포지토리에서 하네스의 `AGENTS.md`를 읽는 에이전트는 필요한 작업에 맞는 스킬의 `SKILL.md`를 먼저 읽고 따릅니다.

현재 제공하는 스킬:

- `create-branch`: Jira 티켓 번호를 확인하고 팀 브랜치 규칙에 맞는 Git 브랜치를 만듭니다.

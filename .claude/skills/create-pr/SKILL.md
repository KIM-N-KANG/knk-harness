---
name: create-pr
description: 사용자가 "PR 만들어줘", "draft PR 올려줘", "pull request 생성해줘", "gh pr create 해줘"처럼 현재 Git 브랜치의 변경사항으로 팀 규칙에 맞는 Draft Pull Request 생성을 요청할 때 사용합니다. GitHub CLI로 중복 PR을 확인하고 브랜치 Jira 키, 태그, 하네스 docs의 PR 템플릿을 반영합니다.
---

# Draft PR 생성

## 목적

현재 작업 브랜치의 커밋을 `dev` 대상으로 올리는 Draft Pull Request를 만듭니다. 핵심은 PR을 빨리 여는 것이 아니라, 팀 제목 규칙과 본문 템플릿을 지키고 중복 PR을 만들지 않는 것입니다.

## 팀 규칙

PR 제목 형식:

```text
[KNK-{Jira이슈번호}] {태그}: {PR 제목}
```

- 기본 base 브랜치는 `dev`입니다.
- 제목과 본문은 한국어로 작성합니다.
- 태그는 `Feat`, `Fix`, `Docs`, `Design`, `CICD`, `Refactor`, `Chore`, `Release` 중 하나를 사용합니다.
- PR 본문은 하네스 레포지토리의 `docs/templates/pull-request/`에 있는 템플릿을 참고해, 작업 중인 레포지토리의 특성과 변경 유형에 맞게 작성합니다.
- PR 본문을 작성할 때는 `technical-writing` 스킬을 함께 사용해 요약, 변경 사항, 검증 결과를 명확하고 간결하게 다듬습니다.

## 판단 기준

작업 중인 레포지토리에서 `create-pr`를 사용할 때는 먼저 하네스 레포지토리의 PR 템플릿을 확인합니다.

- 개발 레포지토리에서 실행 중이면 `../knk-harness/docs/templates/pull-request/`를 확인합니다.
- 하네스 레포지토리에서 실행 중이면 `docs/templates/pull-request/`를 확인합니다.
- 템플릿 경로를 찾을 수 없으면 추측으로 본문을 만들지 말고 사용자에게 하네스 레포지토리 위치나 사용할 템플릿을 확인합니다.

레포지토리와 변경 유형에 따라 아래 템플릿을 우선 참고합니다.

| 템플릿 | 사용하는 상황 |
|---|---|
| `harness-pull-request-template.md` | 하네스 레포지토리 변경 |
| `frontend-pull-request-template.md` | 프론트엔드 화면, 브라우저 UI, 접근성, 반응형 변경 |
| `moblie-pull-request-template.md` | 모바일 앱 화면이나 모바일 플랫폼 변경 |
| `backend-server-pull-request-template.md` | API, DB, 인증, 서버 비즈니스 로직 변경 |
| `ai-server-pull-request-template.md` | Prompt, Model, RAG, Tool/Agent, Evaluation, Dataset 변경 |

브랜치 태그를 PR 제목 태그로 바꿀 때는 아래 기준을 사용합니다.

| 브랜치 태그 | PR 태그 |
|---|---|
| `feat` | `Feat` |
| `fix` | `Fix` |
| `docs` | `Docs` |
| `design` | `Design` |
| `cicd` | `CICD` |
| `refactor` | `Refactor` |
| `chore` | `Chore` |
| `release` | `Release` |

## 작업 흐름

1. Git 상태와 브랜치를 확인합니다.
   - `git status --short --branch`
   - `git branch --show-current`
   - 현재 브랜치가 `main`, `dev`, `release/*`이면 바로 PR을 만들지 말고 사용자에게 확인합니다.
   - 커밋되지 않은 변경사항이 있으면 먼저 커밋 여부를 확인합니다. 필요하면 `create-commit`을 사용합니다.
2. Jira 키와 태그를 결정합니다.
   - 현재 브랜치가 `{tag}/KNK-{번호}-{제목}`이면 그 Jira 키와 태그를 우선 사용합니다.
   - 예: `feat/KNK-141-commit-pr-skills` -> `[KNK-141] Feat: ...`
   - 브랜치에서 Jira 키를 찾을 수 없으면 PR을 만들지 말고 Jira 키를 요청합니다.
3. base와 변경 범위를 확인합니다.
   - 기본 base는 `dev`입니다.
   - `git fetch origin dev`
   - `git log --oneline origin/dev..HEAD`
   - `git diff --stat origin/dev...HEAD`
   - `git diff --name-status origin/dev...HEAD`
   - base 대비 커밋이 없으면 PR을 만들지 않습니다.
4. 기존 PR을 확인합니다.
   - `gh auth status`
   - `gh pr view --json url,state,isDraft,title,baseRefName,headRefName`
   - 이미 열린 PR이 있으면 중복 생성하지 말고 기존 URL을 보고합니다.
5. PR 유형과 본문 템플릿을 고릅니다.
   - Web: 프론트엔드 화면, 브라우저 UI, 접근성, 반응형 변경
   - Mobile: 모바일 앱 화면이나 모바일 플랫폼 변경
   - Backend server: API, DB, 인증, 서버 비즈니스 로직 변경
   - AI server: Prompt, Model, RAG, Tool/Agent, Evaluation, Dataset 변경
   - Infra: Docker, 배포, CI/CD, 인프라 설정 변경
   - 현재 레포지토리 이름, 주요 디렉터리, 변경 파일, diff를 함께 보고 가장 가까운 `docs/templates/pull-request/` 템플릿을 선택합니다.
   - Infra처럼 전용 템플릿이 없거나 유형이 애매하면 사용자에게 사용할 템플릿을 확인합니다.
6. 검증 결과를 수집합니다.
   - 이미 실행한 테스트, 린트, 타입체크, 로컬 실행 결과를 본문에 적습니다.
   - 실행하지 않은 항목은 체크하지 말고 이유를 짧게 남깁니다.
   - UI 변경의 스크린샷이나 화면 녹화가 없으면 "첨부 필요" 또는 "해당 없음"으로 적습니다.
7. PR 제목과 본문을 만듭니다.
   - PR 본문 작성에는 `technical-writing` 스킬을 사용합니다.
   - 선택한 `docs/templates/pull-request/` 템플릿을 읽고, 템플릿의 제목, 섹션, 체크리스트 구조를 유지합니다.
   - Jira를 사용할 수 있으면 이슈 요약을 참고합니다.
   - Jira 접근이 없으면 커밋 목록과 diff를 근거로 제목을 작성합니다.
   - 요약은 변경 목적과 결과를 먼저 씁니다.
   - 변경 사항은 파일명 나열보다 리뷰어가 확인해야 할 동작, 규칙, 영향 중심으로 씁니다.
   - 검증 결과는 실행한 명령, 확인한 흐름, 실행하지 못한 이유를 사실 기반으로 씁니다.
   - 모호한 대명사, 추측성 표현, 중복 문장, 확인하지 않은 체크 표시는 제거합니다.
   - 체크리스트는 확인한 항목만 `[x]`로 표시합니다.
   - 선택한 템플릿에 없는 섹션이 꼭 필요할 때만 추가하고, 해당 레포지토리와 무관한 템플릿 섹션은 억지로 만들지 않습니다.
8. 브랜치를 push한 뒤 Draft PR을 만듭니다.
   - upstream이 없으면 `git push -u origin HEAD`를 사용합니다.
   - upstream이 있으면 `git push`를 사용합니다.
   - `gh pr create --draft --base dev --head <current-branch> --title "<title>" --body-file <body-file>`로 생성합니다.
9. 생성된 PR과 남은 로컬 상태를 확인합니다.

## 명령 사용법

기존 PR 확인:

```bash
gh pr view --json url,state,isDraft,title,baseRefName,headRefName
```

upstream이 없을 때 push:

```bash
git push -u origin HEAD
```

upstream이 있을 때 push:

```bash
git push
```

Draft PR 생성:

```bash
gh pr create --draft --base dev --head <current-branch> --title "<title>" --body-file <body-file>
```

## 금지 사항

- `main`, `dev`, `release/*`에서 사용자 확인 없이 PR을 만들지 않습니다.
- base 대비 커밋이 없으면 PR을 만들지 않습니다.
- 이미 열린 PR이 있으면 중복 PR을 만들지 않습니다.
- Jira 키가 불명확한 상태로 임의의 `KNK-*`를 만들지 않습니다.
- 선택한 템플릿을 읽지 않은 채 PR 본문을 추측으로 만들지 않습니다.
- 실행하지 않은 테스트, 린트, 타입체크를 체크리스트에 완료로 표시하지 않습니다.
- 확인하지 않은 스크린샷, API 동작, 평가 결과를 본문에 사실처럼 쓰지 않습니다.

## 완료 보고

- PR URL, 제목, base/head 브랜치를 보고합니다.
- 사용한 PR 템플릿과 Jira 키, PR 태그를 알립니다.
- 실행한 검증 명령과 결과를 알립니다.
- 검증을 실행하지 못했다면 이유를 짧게 알립니다.
- 기존 PR이 있어 새 PR을 만들지 않았다면 기존 PR URL을 보고합니다.

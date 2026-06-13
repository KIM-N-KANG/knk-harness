---
name: create-pr
description: 사용자가 "PR 만들어줘", "draft PR 올려줘", "pull request 생성해줘", "gh pr create 해줘"처럼 현재 Git 브랜치의 변경사항으로 팀 규칙에 맞는 Draft Pull Request 생성을 요청할 때 사용합니다. GitHub CLI로 중복 PR을 확인하고 브랜치 Jira 키, 태그, 팀 PR 템플릿을 반영합니다.
---

# Draft PR 생성

## 목적

현재 작업 브랜치의 커밋을 `dev` 대상으로 올리는 Draft Pull Request를 만듭니다. 핵심은 PR을 빨리 여는 것이 아니라, 팀 제목 규칙과 본문 템플릿을 지키고 중복 PR을 만들지 않는 것입니다.

## 팀 PR 규칙

제목 형식:

```text
[KNK-{Jira이슈번호}] {태그}: {PR 제목}
```

- 기본 base 브랜치는 `dev`입니다.
- 제목과 본문은 한국어로 작성합니다.
- 태그는 `Feat`, `Fix`, `Docs`, `Design`, `CICD`, `Refactor`, `Chore`, `Release` 중 하나를 사용합니다.
- PR 본문은 작업 유형에 맞는 템플릿을 사용합니다.
- 가능하면 `../llm-wiki/wiki/concepts/PR-규칙.md`와 `../llm-wiki/raw/Pull-Request-템플릿.md`를 읽어 최신 규칙을 확인합니다.

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
5. PR 유형을 고릅니다.
   - Web: 프론트엔드 화면, 브라우저 UI, 접근성, 반응형 변경
   - Mobile: 모바일 앱 화면이나 모바일 플랫폼 변경
   - Backend server: API, DB, 인증, 서버 비즈니스 로직 변경
   - AI server: Prompt, Model, RAG, Tool/Agent, Evaluation, Dataset 변경
   - Infra: Docker, 배포, CI/CD, 인프라 설정 변경
   - 유형이 애매하면 사용자에게 확인합니다.
6. 검증 결과를 수집합니다.
   - 이미 실행한 테스트, 린트, 타입체크, 로컬 실행 결과를 본문에 적습니다.
   - 실행하지 않은 항목은 체크하지 말고 이유를 짧게 남깁니다.
   - UI 변경의 스크린샷이나 화면 녹화가 없으면 "첨부 필요" 또는 "해당 없음"으로 적습니다.
7. PR 제목과 본문을 만듭니다.
   - Jira를 사용할 수 있으면 이슈 요약을 참고합니다.
   - Jira 접근이 없으면 커밋 목록과 diff를 근거로 제목을 작성합니다.
   - 체크리스트는 확인한 항목만 `[x]`로 표시합니다.
8. 브랜치를 push한 뒤 Draft PR을 만듭니다.
   - upstream이 없으면 `git push -u origin HEAD`
   - upstream이 있으면 `git push`
   - `gh pr create --draft --base dev --head <current-branch> --title "<title>" --body-file <body-file>`
9. PR URL, 제목, base/head, 검증 결과를 보고합니다.

## 태그 매핑

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

## 기본 본문 골격

최신 원본 템플릿을 읽을 수 없으면 아래 골격을 사용합니다.

```markdown
## 요약

-

## 관련 이슈

- KNK-

## 변경 사항

-

## 검증

- [ ] 테스트 실행
- [ ] 로컬 실행 확인

## 체크리스트

- [ ] PR 제목이 `[KNK-{이슈번호}] {Tag}: {제목}` 형식을 따릅니다.
- [ ] 브랜치명이 `{tag}/KNK-{이슈번호}-{브랜치-제목}` 형식을 따릅니다.
- [ ] Jira 이슈의 작업 범위와 완료 기준을 확인했습니다.
- [ ] 실제 secret 또는 로컬 전용 파일이 포함되지 않았습니다.
- [ ] 동작이나 설정이 바뀐 경우 관련 문서를 함께 수정했습니다.
```

## 금지 사항

- `main`이나 `dev`에서 바로 PR을 만들지 않습니다.
- 커밋되지 않은 변경사항이 있는데 "어차피 Draft"라는 이유로 무시하지 않습니다.
- 기존 열린 PR이 있는데 중복 Draft PR을 만들지 않습니다.
- 확인하지 않은 체크리스트를 `[x]`로 표시하지 않습니다.
- secret, 로컬 전용 파일, 대용량 바이너리가 포함된 의심이 있으면 PR을 만들기 전에 멈춥니다.

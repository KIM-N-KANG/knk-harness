---
name: create-branch
description: 사용자가 "KNK-123", "KNK-123 브랜치 만들어줘", "KNK-123 티켓 확인하고 브랜치 만들어줘", "create branch for KNK-123", "start work on this Jira ticket"처럼 Jira 이슈나 티켓 키로 브랜치 생성, 체크아웃, 작업 시작, 준비를 요청할 때 사용합니다. 가능하면 Atlassian MCP로 Jira 이슈를 확인하고 요약을 가져옵니다. Jira를 사용할 수 없으면 사용자가 제공한 제목을 씁니다.
---

# 브랜치 생성

## 목적

팀 컨벤션에 맞춰 `dev`에서 작업 브랜치 하나를 만듭니다.

```text
{tag}/{JIRA_KEY}-{title-slug}
```

예시:

```text
feat/KNK-12-add-google-login-button-ui
```

## 팀 규칙

- 기본적으로 `dev`에서 브랜치를 만듭니다.
- `main`이나 `dev`에 직접 푸시하지 않습니다.
- 태그는 `feat`, `fix`, `docs`, `design`, `cicd`, `refactor`, `chore` 중 하나를 사용합니다.
- Jira 키는 `KNK-123`처럼 대문자로 유지합니다.
- 제목 슬러그는 kebab-case를 사용합니다.
- 제목 슬러그는 영어를 우선합니다. Jira 요약이 한국어이고 의미가 분명하면 짧게 영어로 옮깁니다. 의미가 모호하면 사용자에게 짧은 영어 브랜치 제목을 요청합니다.

## 작업 흐름

1. 요청에서 Jira 키를 추출합니다. Jira 키가 없으면 사용자에게 요청합니다.
2. 브랜치 태그를 결정합니다.
   - 사용자가 명시한 태그가 있으면 그 태그를 사용합니다.
   - 그렇지 않으면 Jira 이슈 유형이나 요약에서 추론합니다. 버그는 `fix`, 문서는 `docs`, UI/스타일은 `design`, CI/CD/배포는 `cicd`, 리팩터링은 `refactor`, 의존성/설정/유지보수는 `chore`, 그 외에는 `feat`를 사용합니다.
3. Atlassian MCP/Jira 도구를 사용할 수 있으면 Jira 이슈를 확인합니다.
   - 키로 이슈를 조회합니다.
   - 확인할 수 있으면 이슈 요약, 상태, 유형, 담당자를 기록합니다.
   - 이슈가 없으면 브랜치를 만들지 말고 사용자에게 키 확인을 요청합니다.
   - Jira 접근이 불가능하면 간단히 알립니다. 사용자가 제목에 필요한 맥락을 충분히 제공한 경우에만 계속 진행하고, 그렇지 않으면 제목을 요청합니다.
4. `scripts/create_branch.py`로 브랜치 이름을 생성합니다.
5. 브랜치를 만들기 전에 `git status --short`를 확인합니다.
   - 워크트리에 커밋되지 않은 변경사항이 있으면 stash, reset, discard를 실행하지 않습니다.
   - 사용자가 기존 변경사항을 새 브랜치로 가져가겠다고 명시한 경우에만 변경 사항이 있는 워크트리(dirty worktree)에서 브랜치를 만들고, 이때 --allow-dirty를 전달합니다.
6. 스크립트로 `dev`에서 브랜치를 만듭니다.
7. 생성된 브랜치 이름과 Jira 대체 처리 여부, 워크트리의 미커밋 변경사항(dirty worktree) 관련 주의사항을 보고합니다.

## 스크립트 사용법

브랜치 이름 미리보기:

```bash
python3 .agents/skills/create-branch/scripts/create_branch.py \
  --ticket KNK-12 \
  --tag feat \
  --title "Add Google Login Button UI"
```

`dev`에서 브랜치 생성:

```bash
python3 .agents/skills/create-branch/scripts/create_branch.py \
  --ticket KNK-12 \
  --tag feat \
  --title "Add Google Login Button UI" \
  --create
```

브랜치가 이미 있으며 사용자가 그 브랜치를 쓰려는 경우:

```bash
python3 .agents/skills/create-branch/scripts/create_branch.py \
  --ticket KNK-12 \
  --tag feat \
  --title "Add Google Login Button UI" \
  --create \
  --checkout-existing
```

커밋되지 않은 기존 변경사항을 체크아웃과 함께 가져가도 된다고 사용자가 확인한 뒤에만 `--allow-dirty`를 사용합니다.

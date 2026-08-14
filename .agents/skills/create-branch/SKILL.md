---
name: create-branch
description: 사용자가 "KNK-123", "KNK-123 브랜치 만들어줘", "KNK-123 티켓 확인하고 브랜치 만들어줘", "create branch for KNK-123", "start work on this Jira ticket"처럼 Jira 이슈나 티켓 키로 브랜치 생성, 체크아웃, 작업 시작, 준비를 요청할 때 사용합니다. 가능하면 Atlassian MCP로 Jira 이슈를 확인하고, 브랜치 준비가 성공하면 해야 할 일 상태의 티켓을 진행 중으로 전환합니다. Jira를 사용할 수 없으면 사용자가 제공한 제목을 씁니다.
---

# 브랜치 생성

## 목적

팀 컨벤션에 맞춰 `dev`에서 작업 브랜치 하나를 만들고 Jira 작업을 시작 상태로 맞춥니다. 핵심은 Jira 이슈와 연결되는 브랜치명을 만들고, 기존 워크트리 변경사항을 임의로 정리하지 않는 것입니다.

## 팀 규칙

브랜치명 형식:

```text
{tag}/{JIRA_KEY}-{title-slug}
```

좋은 예:

```text
feat/KNK-12-add-google-login-button-ui
```

- 기본적으로 `dev`에서 브랜치를 만듭니다.
- `main`이나 `dev`에 직접 푸시하지 않습니다.
- Jira 키는 `KNK-123`처럼 대문자로 유지합니다.
- 제목 슬러그는 kebab-case를 사용합니다.
- 제목 슬러그는 영어를 우선합니다. Jira 요약이 한국어이고 의미가 분명하면 짧게 영어로 옮깁니다. 의미가 모호하면 사용자에게 짧은 영어 브랜치 제목을 요청합니다.
- 태그는 `feat`, `fix`, `docs`, `design`, `cicd`, `refactor`, `chore` 중 하나를 사용합니다.

## 판단 기준

- Jira 키는 사용자 요청에서 먼저 찾습니다. Jira 키가 없으면 브랜치를 만들지 말고 사용자에게 요청합니다.
- Atlassian MCP/Jira 도구를 사용할 수 있으면 Jira 이슈를 조회해 요약, 상태, 유형, 담당자를 확인합니다.
- Jira 접근이 불가능하면 간단히 알립니다. 사용자가 제목에 필요한 맥락을 충분히 제공한 경우에만 계속 진행하고, 그렇지 않으면 제목을 요청합니다.
- 사용자가 브랜치 태그를 명시했으면 그 태그를 우선 사용합니다.
- 브랜치 태그를 추론해야 하면 아래 기준을 사용합니다.

| 조건 | 브랜치 태그 |
|---|---|
| 새 기능 | `feat` |
| 버그 수정 | `fix` |
| 문서 수정 | `docs` |
| UI, 스타일, 디자인 수정 | `design` |
| 배포, CI/CD 설정 수정 | `cicd` |
| 기능 변화 없는 코드 구조 개선 | `refactor` |
| 설정, 의존성, 기타 유지보수 | `chore` |

## 작업 흐름

1. 요청에서 Jira 키를 추출합니다. Jira 키가 없으면 사용자에게 요청합니다.
2. 브랜치 태그를 결정합니다.
   - 사용자가 명시한 태그가 있으면 그 태그를 사용합니다.
   - 그렇지 않으면 Jira 이슈 유형, 요약, 변경 목적에서 추론합니다.
3. Atlassian MCP/Jira 도구를 사용할 수 있으면 Jira 이슈를 확인합니다.
   - 키로 이슈를 조회합니다.
   - 확인할 수 있으면 이슈 요약, 상태, 유형, 담당자를 기록합니다.
   - 이슈가 없으면 브랜치를 만들지 말고 사용자에게 키 확인을 요청합니다.
   - Jira 접근이 불가능하면 간단히 알립니다. 사용자가 제목에 필요한 맥락을 충분히 제공한 경우에만 계속 진행하고, 그렇지 않으면 제목을 요청합니다.
4. `scripts/create_branch.py`로 브랜치 이름을 생성합니다.
5. 브랜치를 만들기 전에 `git status --short`를 확인합니다.
   - 워크트리에 커밋되지 않은 변경사항이 있으면 stash, reset, discard를 실행하지 않습니다.
   - 사용자가 기존 변경사항을 새 브랜치로 가져가겠다고 명시한 경우에만 변경 사항이 있는 워크트리에서 브랜치를 만들고, 이때 `--allow-dirty`를 전달합니다.
6. 스크립트로 `dev`에서 브랜치를 만듭니다.
7. 브랜치 생성 또는 기존 브랜치 체크아웃이 성공한 뒤 Jira 상태를 처리합니다.
   - 최초 조회한 현재 상태가 `해야 할 일`이면 사용 가능한 전환 목록을 조회합니다.
   - 전환 이름이 아니라 전환의 목표 상태가 `진행 중`인 항목을 선택해 전환 ID로 실행합니다.
   - 이미 `진행 중`이면 상태 변경 없이 계속합니다.
   - `해야 할 일`과 `진행 중`이 아닌 상태는 임의로 변경하지 않습니다.
   - Jira 접근 실패, 권한 부족, 목표 전환 부재 등으로 상태 변경에 실패해도 생성한 브랜치를 되돌리거나 삭제하지 않습니다. 실패 이유를 보고합니다.
8. 생성된 브랜치와 워크트리 상태를 확인합니다.
9. 상태 전환을 실행했다면 Jira 이슈를 다시 조회해 `진행 중`인지 확인합니다.

## 명령 사용법

하네스 레포지토리 안에서 실행할 때는 `.claude/skills/create-branch/scripts/create_branch.py`를 사용합니다. 개발 레포지토리에서 실행 중이면 `../knk-harness/.claude/skills/create-branch/scripts/create_branch.py`를 사용합니다.

브랜치 이름 미리보기:

```bash
python3 .claude/skills/create-branch/scripts/create_branch.py \
  --ticket KNK-12 \
  --tag feat \
  --title "Add Google Login Button UI"
```

`dev`에서 브랜치 생성:

```bash
python3 .claude/skills/create-branch/scripts/create_branch.py \
  --ticket KNK-12 \
  --tag feat \
  --title "Add Google Login Button UI" \
  --create
```

브랜치가 이미 있으며 사용자가 그 브랜치를 쓰려는 경우:

```bash
python3 .claude/skills/create-branch/scripts/create_branch.py \
  --ticket KNK-12 \
  --tag feat \
  --title "Add Google Login Button UI" \
  --create \
  --checkout-existing
```

커밋되지 않은 기존 변경사항을 체크아웃과 함께 가져가도 된다고 사용자가 확인한 뒤에만 `--allow-dirty`를 사용합니다.

## 금지 사항

- Jira 키가 불명확한 상태로 임의의 `KNK-*`를 만들지 않습니다.
- Jira 이슈가 없거나 키가 잘못된 것으로 보이면 브랜치를 만들지 않습니다.
- 사용자 확인 없이 dirty worktree에서 stash, reset, discard, checkout, clean을 실행하지 않습니다.
- 사용자 확인 없이 `main`, `dev`, `release/*`에서 작업을 계속하거나 직접 푸시하지 않습니다.
- 의미가 불명확한 한국어 제목을 억지로 영어 슬러그로 바꾸지 않습니다.
- 브랜치 생성 또는 기존 브랜치 체크아웃이 실패했으면 Jira 상태를 변경하지 않습니다.
- 현재 상태가 `해야 할 일`이 아니면 완료, 중단 등 다른 상태를 `진행 중`으로 되돌리지 않습니다.
- 이름만 보고 전환 ID를 추측하지 않습니다. 사용 가능한 전환 목록의 목표 상태를 확인합니다.

## 완료 보고

- 생성 또는 체크아웃한 브랜치 이름을 보고합니다.
- 사용한 Jira 키, 브랜치 태그, 제목 슬러그를 함께 알립니다.
- Jira를 확인하지 못했거나 사용자 제공 제목으로 대체했다면 그 사실을 알립니다.
- Jira 상태가 `진행 중`으로 변경되었는지, 이미 진행 중이었는지, 변경하지 못했는지 알립니다.
- 워크트리에 남아 있는 미커밋 변경사항이 있으면 함께 보고합니다.

# ACCOUNT 공통 클라이언트

단계마다 공통 문서, 해당 플랫폼 문서 순서로 읽는다. 상위 계약은 하위 구현이나 검증 결과에 맞춰 변경하지 않는다.

```text
배경 → 유저 스토리 → 요구사항 → 화면 구성과 흐름, 배치
     → 연동 계약 → 구성 → 상태 → 실행 → 검증 → 배포
```

플랫폼 이동: [WEB](WEB/AGENTS.md), [ANDROID](ANDROID/AGENTS.md). 작성 규칙은 [클라이언트 가이드](../../../reference/CLIENT-SPEC-WRITING-GUIDE.md), 과거 결정은 [DECISIONS](DECISIONS.md)에서 확인한다.

<br>

### 문서 역할

| 문서 | 내용 |
|---|---|
| [BACKGROUND.md](BACKGROUND.md) | ACCOUNT 클라이언트 배경 |
| [USER-STORY.md](USER-STORY.md) | ACCOUNT 유저 스토리 |
| [REQUIREMENTS.md](REQUIREMENTS.md) | ACCOUNT 요구사항 |
| [INFORMATION-ARCHITECTURE.md](INFORMATION-ARCHITECTURE.md) | ACCOUNT 화면 구성 |
| [INTERACTION-FLOWS.md](INTERACTION-FLOWS.md) | ACCOUNT 화면 흐름 |
| [LAYOUT.md](LAYOUT.md) | ACCOUNT 화면 배치 |
| [CONTRACT.md](CONTRACT.md) | ACCOUNT 데이터 계약 |
| [VERIFICATION.md](VERIFICATION.md) | ACCOUNT 공통 검증 |

<br>

### 작성과 검증

- 요구사항에는 사용자 결과, 화면 설계에는 배치와 전환, 구현 설계에는 책임과 수명을 작성한다.
- 공통 본문을 플랫폼별로 복제하지 않는다. 의도된 차이는 공통 적용 범위 안에서 구체화한다.
- ADR 본문과 ID를 보존한다. 현재 계약 변경은 해당 단계에서 시작하고 이후 문서에 반영한다.
- 기존 QA 케이스와 상위 요구의 연결, 링크, 앵커, ID 중복을 검사하고 `git diff --check`를 실행한다.
- 실제 검증 결과는 PR과 CI에 기록한다. 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

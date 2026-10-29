# PAYMENT 공통 클라이언트

단계마다 공통 문서, 해당 플랫폼 문서 순서로 읽는다. 하위 구현과 검증을 이유로 상위 요구를 바꾸지 않는다.

작성 규칙은 클라이언트 가이드를 적용한다. ([작성 가이드](../../../reference/CLIENT-SPEC-WRITING-GUIDE.md))

플랫폼: [WEB](WEB/AGENTS.md), [ANDROID](ANDROID/AGENTS.md).

<br>

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [1-BACKGROUND.md](1-BACKGROUND.md) | 1 PAYMENT 클라이언트 배경 |
| [2-1-USER-STORY.md](2-1-USER-STORY.md) | 2-1 PAYMENT 유저 스토리 |
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 PAYMENT 요구사항 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 PAYMENT 화면 구성 |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 PAYMENT 화면 흐름 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 PAYMENT 화면 표현 |
| [4-1-CONTRACT.md](4-1-CONTRACT.md) | 4-1 PAYMENT 연동 계약 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 PAYMENT 공통 검증 |
| [DECISIONS.md](DECISIONS.md) | 과거 선택과 대체 관계 |

<br>

### 3 작성과 검증

- 현재 요구, 플랫폼 차이와 내부 구현을 구분한다. 채팅 모델 가격은 CHAT에서 정한다.
- 확정 ADR과 기존 QA의 조건 및 기대 결과를 보존하고, 참조와 ID를 함께 갱신한다.
- 링크, 앵커, ID 중복과 문서의 역방향 참조를 검사하고 `git diff --check`를 실행한다.
- 실행 결과와 미검증 범위는 PR과 CI에 기록한다. 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

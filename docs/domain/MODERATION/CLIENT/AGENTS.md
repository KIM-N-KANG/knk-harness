# MODERATION 공통 클라이언트

단계마다 공통 문서 다음 해당 플랫폼 문서를 읽는다. 사용자 목표, 요구사항, 화면, 연동과 구현, 검증 순서다.

플랫폼: [WEB](WEB/AGENTS.md), [ANDROID](ANDROID/AGENTS.md).

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [1-BACKGROUND.md](1-BACKGROUND.md) | 1 MODERATION 클라이언트 배경 |
| [2-1-USER-STORY.md](2-1-USER-STORY.md) | 2-1 MODERATION 유저 스토리 |
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 MODERATION 요구사항 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 MODERATION 화면 구성 |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 MODERATION 화면 흐름 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 MODERATION 화면 표현 |
| [4-1-CONTRACT.md](4-1-CONTRACT.md) | 4-1 MODERATION 클라이언트 연동 계약 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 MODERATION 공통 검증 |

### 3 작성과 검증

- 새로운 신고 기준이나 제재 결과를 구현에서 추측하지 않는다.
- 과거 ADR은 원래 소유 범위에 보존하고 현재 계약으로 대체하지 않는다.
- 링크와 앵커, ID 중복, 단계 순서를 확인하고 `git diff --check`를 실행한다.
- 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

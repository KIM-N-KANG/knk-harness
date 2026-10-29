# MODERATION 공통 클라이언트

단계마다 공통 문서 다음 해당 플랫폼 문서를 읽는다. 사용자 목표, 요구사항, 화면, 연동과 구현, 검증 순서다.

플랫폼: [WEB](WEB/AGENTS.md), [ANDROID](ANDROID/AGENTS.md).

### 문서 역할

| 문서 | 내용 |
|---|---|
| [BACKGROUND.md](BACKGROUND.md) | MODERATION 클라이언트 배경 |
| [USER-STORY.md](USER-STORY.md) | MODERATION 유저 스토리 |
| [REQUIREMENTS.md](REQUIREMENTS.md) | MODERATION 요구사항 |
| [INFORMATION-ARCHITECTURE.md](INFORMATION-ARCHITECTURE.md) | MODERATION 화면 구성 |
| [INTERACTION-FLOWS.md](INTERACTION-FLOWS.md) | MODERATION 화면 흐름 |
| [LAYOUT.md](LAYOUT.md) | MODERATION 화면 표현 |
| [CONTRACT.md](CONTRACT.md) | MODERATION 클라이언트 연동 계약 |
| [VERIFICATION.md](VERIFICATION.md) | MODERATION 공통 검증 |

### 작성과 검증

- 새로운 신고 기준이나 제재 결과를 구현에서 추측하지 않는다.
- 과거 ADR은 원래 소유 범위에 보존하고 현재 계약으로 대체하지 않는다.
- 링크와 앵커, ID 중복, 단계 순서를 확인하고 `git diff --check`를 실행한다.
- 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

# NOTIFICATION 공통 클라이언트

단계마다 공통 다음 해당 플랫폼 문서를 읽는다. 사용자 목표와 요구사항, 화면, 연동과 구현, 검증 및 배포 순서다.

플랫폼: [WEB](WEB/AGENTS.md), [ANDROID](ANDROID/AGENTS.md).

### 문서 역할

| 문서 | 내용 |
|---|---|
| [BACKGROUND.md](BACKGROUND.md) | NOTIFICATION 클라이언트 배경 |
| [USER-STORY.md](USER-STORY.md) | NOTIFICATION 유저 스토리 |
| [REQUIREMENTS.md](REQUIREMENTS.md) | NOTIFICATION 요구사항 |
| [INFORMATION-ARCHITECTURE.md](INFORMATION-ARCHITECTURE.md) | NOTIFICATION 화면 구성 |
| [INTERACTION-FLOWS.md](INTERACTION-FLOWS.md) | NOTIFICATION 화면 흐름 |
| [LAYOUT.md](LAYOUT.md) | NOTIFICATION 화면 표현 |
| [CONTRACT.md](CONTRACT.md) | NOTIFICATION 클라이언트 연동 계약 |
| [STATE-MANAGEMENT.md](STATE-MANAGEMENT.md) | NOTIFICATION 공통 상태 관리 |
| [VERIFICATION.md](VERIFICATION.md) | NOTIFICATION 공통 검증 |

### 작성과 검증

- 공지의 기기 읽음과 회원 알림의 서버 읽음을 구분한다.
- 수신 동의, OS 권한과 회원 인증을 같은 상태로 합치지 않는다.
- 확정 ADR과 QA 원문을 보존하고 과거 실행 표시와 이번 실행을 구분한다.
- 링크, 앵커, ID 중복과 단계 순서를 확인하고 `git diff --check`를 실행한다.
- 명세의 작성과 검토를 서브에이전트에 맡기지 않는다.

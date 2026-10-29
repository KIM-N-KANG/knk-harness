# NOTIFICATION 공통 클라이언트

단계마다 공통 다음 해당 플랫폼 문서를 읽는다. 사용자 목표와 요구사항, 화면, 연동과 구현, 검증 및 배포 순서다.

플랫폼: [WEB](WEB/AGENTS.md), [ANDROID](ANDROID/AGENTS.md).

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [1-BACKGROUND.md](1-BACKGROUND.md) | 1 NOTIFICATION 클라이언트 배경 |
| [2-1-USER-STORY.md](2-1-USER-STORY.md) | 2-1 NOTIFICATION 유저 스토리 |
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 NOTIFICATION 요구사항 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 NOTIFICATION 화면 구성 |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 NOTIFICATION 화면 흐름 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 NOTIFICATION 화면 표현 |
| [4-1-CONTRACT.md](4-1-CONTRACT.md) | 4-1 NOTIFICATION 클라이언트 연동 계약 |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 NOTIFICATION 공통 상태 관리 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 NOTIFICATION 공통 검증 |

### 3 작성과 검증

- 공지의 기기 읽음과 회원 알림의 서버 읽음을 구분한다.
- 수신 동의, OS 권한과 회원 인증을 같은 상태로 합치지 않는다.
- 확정 ADR과 QA 원문을 보존하고 과거 실행 표시와 이번 실행을 구분한다.
- 링크, 앵커, ID 중복과 단계 순서를 확인하고 `git diff --check`를 실행한다.
- 명세의 작성과 검토를 서브에이전트에 맡기지 않는다.

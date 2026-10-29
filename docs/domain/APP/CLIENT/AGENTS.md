# APP 클라이언트

셸, 내비게이션, 테마, 서비스 안내, 앱 안내 배너와 앱 소개 링크의 사용자 계약을 관리한다.

<br>

### 1 읽는 순서

단계마다 공통 다음 [WEB](WEB/AGENTS.md) 또는 [ANDROID](ANDROID/AGENTS.md)를 읽는다.

| 문서 | 내용 |
|---|---|
| [1-BACKGROUND.md](1-BACKGROUND.md) | 1 공용 클라이언트 배경 |
| [2-1-USER-STORY.md](2-1-USER-STORY.md) | 2-1 공용 클라이언트 유저 스토리 |
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 공용 클라이언트 요구사항 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 공용 화면 구성 |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 공용 화면 흐름 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 공용 화면 표현 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 공용 클라이언트 검증 |

<br>

### 2 공통 기반과 작성 규칙

- 기존 `CLIENT-US-001`부터 `CLIENT-US-004`까지는 이동 뒤에도 유지한다. 새 APP 목표는 사용하지 않은 `APP-US-001`부터 부여하며 폐기한 ID를 재사용하지 않는다.
- 네트워크와 전송 계약은 [CLIENT 기반](../../../platform/CLIENT/AGENTS.md), 플랫폼 구조는 [WEB](../../../platform/WEB/AGENTS.md)과 [ANDROID](../../../platform/ANDROID/AGENTS.md)에서 정의한다.
- 서비스 안내가 계정 동의, 이프 정책과 알림 권한을 다시 정의하지 않는다. 해당 도메인 문서를 연결한다.
- 문서 구조 변경 이력은 [문서 결정 기록](../../../reference/decisions/DOCUMENTATION.md), 작성 기준은 [클라이언트 작성 가이드](../../../reference/CLIENT-SPEC-WRITING-GUIDE.md)를 따른다.
- 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

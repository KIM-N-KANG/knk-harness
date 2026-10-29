# 공통 UI

UI는 사용자 인터페이스를 뜻한다. 이 세트는 여러 업무에 공통으로 쓰이는 셸, 내비게이션, 테마, 화면 상태, 서비스 안내와 앱 진입을 다룬다. 업무별 화면은 해당 도메인의 CLIENT, 공통 구현 규칙은 platform에서 관리한다.

<br>

### 1 문서 역할

플랫폼 문서: [WEB](WEB/AGENTS.md), [ANDROID](ANDROID/AGENTS.md).

| 문서 | 내용 |
|---|---|
| [1-BACKGROUND.md](1-BACKGROUND.md) | 1 배경 |
| [2-1-USER-STORY.md](2-1-USER-STORY.md) | 2-1 유저 스토리 |
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 요구사항 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 화면 구성 |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 화면 흐름 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 화면 배치 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 검증 |

<br>

### 2 공통 기반과 작성 규칙

- 기존 `CLIENT-US-001`부터 `CLIENT-US-004`까지는 이동 뒤에도 유지한다. 새 공통 UI 목표는 사용하지 않은 `CLIENT-US-005`부터 부여하며 폐기한 ID를 재사용하지 않는다.
- 네트워크와 전송 계약은 [CLIENT 기반](../platform/CLIENT/AGENTS.md), 플랫폼 구조는 [WEB](../platform/CLIENT/WEB/AGENTS.md)과 [ANDROID](../platform/CLIENT/ANDROID/AGENTS.md)에서 정의한다.
- 서비스 안내가 계정 동의, 이프 정책과 알림 권한을 다시 정의하지 않는다. 해당 도메인 문서를 연결한다.
- 문서 구조 변경 이력은 [문서 결정 기록](../reference/decisions/DOCUMENTATION.md), 작성 기준은 [클라이언트 작성 가이드](../reference/CLIENT-SPEC-WRITING-GUIDE.md)를 따른다.
- 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

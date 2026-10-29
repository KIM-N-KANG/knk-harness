# 공통 사용자 경험

셸, 내비게이션, 테마, 서비스 안내, 앱 안내 배너와 앱 소개 링크의 사용자 계약을 관리한다.

<br>

### 읽는 순서

단계마다 공통 다음 [WEB](WEB/AGENTS.md) 또는 [ANDROID](ANDROID/AGENTS.md)를 읽는다.

| 문서 | 내용 |
|---|---|
| [BACKGROUND.md](BACKGROUND.md) | 공용 클라이언트 배경 |
| [USER-STORY.md](USER-STORY.md) | 공용 클라이언트 유저 스토리 |
| [REQUIREMENTS.md](REQUIREMENTS.md) | 공용 클라이언트 요구사항 |
| [INFORMATION-ARCHITECTURE.md](INFORMATION-ARCHITECTURE.md) | 공용 화면 구성 |
| [INTERACTION-FLOWS.md](INTERACTION-FLOWS.md) | 공용 화면 흐름 |
| [LAYOUT.md](LAYOUT.md) | 공용 화면 표현 |
| [VERIFICATION.md](VERIFICATION.md) | 공용 클라이언트 검증 |

<br>

### 공통 기반과 작성 규칙

- 기존 `CLIENT-US-001`부터 `CLIENT-US-004`까지는 이동 뒤에도 유지한다. 새 공통 목표는 사용하지 않은 `CLIENT-US-005`부터 부여하며 폐기한 ID를 재사용하지 않는다.
- 네트워크와 전송 계약은 [공통 연동 계약](../platform/CLIENT-CONTRACT.md), 플랫폼 구조는 [WEB](../platform/WEB/AGENTS.md)과 [ANDROID](../platform/ANDROID/AGENTS.md)에서 정의한다.
- 서비스 안내가 계정 동의, 이프 정책과 알림 권한을 다시 정의하지 않는다. 해당 도메인 문서를 연결한다.
- 문서 구조 변경 이력은 [문서 결정 기록](../reference/decisions/DOCUMENTATION.md), 작성 기준은 [클라이언트 작성 가이드](../reference/CLIENT-SPEC-WRITING-GUIDE.md)를 따른다.
- 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

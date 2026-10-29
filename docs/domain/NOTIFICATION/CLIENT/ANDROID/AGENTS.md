# NOTIFICATION Android 클라이언트

단계마다 공통 다음 해당 플랫폼 문서를 읽는다. 사용자 목표와 요구사항, 화면, 연동과 구현, 검증 및 배포 순서다.

공통: [CLIENT](../AGENTS.md).

### 문서 역할

| 문서 | 내용 |
|---|---|
| [REQUIREMENTS.md](REQUIREMENTS.md) | Android NOTIFICATION 요구사항 |
| [INFORMATION-ARCHITECTURE.md](INFORMATION-ARCHITECTURE.md) | Android NOTIFICATION 화면 구성 |
| [INTERACTION-FLOWS.md](INTERACTION-FLOWS.md) | Android NOTIFICATION 이동 |
| [LAYOUT.md](LAYOUT.md) | Android NOTIFICATION 표현 |
| [COMPONENT-ARCHITECTURE.md](COMPONENT-ARCHITECTURE.md) | Android NOTIFICATION 구성 |
| [STATE-MANAGEMENT.md](STATE-MANAGEMENT.md) | Android NOTIFICATION 상태 관리 |
| [EXECUTION.md](EXECUTION.md) | Android NOTIFICATION 실행 |
| [VERIFICATION.md](VERIFICATION.md) | Android NOTIFICATION 검증 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Android NOTIFICATION 배포 |
| [DECISIONS.md](DECISIONS.md) | NOTIFICATION Android 결정 기록 |

### 코드 대응

- [notification/src/main/java/app/manyak/notification](../../../../../../manyak-android/notification/src/main/java/app/manyak/notification)
- [notice/src/main/java/app/manyak/notice](../../../../../../manyak-android/notice/src/main/java/app/manyak/notice)
- [notification/src/test](../../../../../../manyak-android/notification/src/test)
- [notice/src/test](../../../../../../manyak-android/notice/src/test)

첫 광고 동의 선택 항목의 대체 결정: [A-044](../../../ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-044). 앱 열기 스킴: [A-071](../../../../experience/ANDROID/DECISIONS.md#a-071).

### 작성과 검증

- 공지의 기기 읽음과 회원 알림의 서버 읽음을 구분한다.
- 수신 동의, OS 권한과 회원 인증을 같은 상태로 합치지 않는다.
- 확정 ADR과 QA 원문을 보존하고 과거 실행 표시와 이번 실행을 구분한다.
- 링크, 앵커, ID 중복과 단계 순서를 확인하고 `git diff --check`를 실행한다.
- 명세의 작성과 검토를 서브에이전트에 맡기지 않는다.

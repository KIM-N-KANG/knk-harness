# NOTIFICATION Android 클라이언트

공통: [CLIENT](../AGENTS.md).

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 요구사항: 안드로이드 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 화면 구성: 안드로이드 |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 화면 흐름: 안드로이드 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 화면 배치: 안드로이드 |
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 컴포넌트 구조: 안드로이드 |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 상태 관리: 안드로이드 |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 실행: 안드로이드 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 검증: 안드로이드 |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 6 배포: 안드로이드 |
| [DECISIONS.md](DECISIONS.md) | NOTIFICATION Android 결정 기록 |

### 2 코드 대응

- [notification/src/main/java/app/manyak/notification](../../../../../../manyak-android/notification/src/main/java/app/manyak/notification)
- [notice/src/main/java/app/manyak/notice](../../../../../../manyak-android/notice/src/main/java/app/manyak/notice)
- [notification/src/test](../../../../../../manyak-android/notification/src/test)
- [notice/src/test](../../../../../../manyak-android/notice/src/test)

첫 광고 동의 선택 항목의 대체 결정: [A-044](../../../ACCOUNT/CLIENT/ANDROID/DECISIONS.md#a-044). 앱 열기 스킴: [A-071](../../../../ui/ANDROID/DECISIONS.md#a-071).

### 3 작성과 검증

- 공지의 기기 읽음과 회원 알림의 서버 읽음을 구분한다.
- 수신 동의, OS 권한과 회원 인증을 같은 상태로 합치지 않는다.
- 확정 ADR과 QA 원문을 보존하고 과거 실행 표시와 이번 실행을 구분한다.
- 링크, 앵커, ID 중복과 단계 순서를 확인하고 `git diff --check`를 실행한다.
- 명세의 작성과 검토를 서브에이전트에 맡기지 않는다.

# NOTIFICATION 웹 클라이언트

단계마다 공통 다음 해당 플랫폼 문서를 읽는다. 사용자 목표와 요구사항, 화면, 연동과 구현, 검증 및 배포 순서다.

공통: [CLIENT](../AGENTS.md).

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 웹 NOTIFICATION 요구사항 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 웹 NOTIFICATION 경로 |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 웹 NOTIFICATION 이동 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 웹 NOTIFICATION 표현 |
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 웹 NOTIFICATION 구성 |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 웹 NOTIFICATION 상태 관리 |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 웹 NOTIFICATION 실행 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 웹 NOTIFICATION 검증 |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 6 웹 NOTIFICATION 배포 |
| [DECISIONS.md](DECISIONS.md) | NOTIFICATION 웹 결정 기록 |

### 2 코드 대응

- [src/features/notices](../../../../../../manyak-web/src/features/notices)
- [src/features/notifications](../../../../../../manyak-web/src/features/notifications)
- [src/features/my/notifications](../../../../../../manyak-web/src/features/my/notifications)
- [src/features/my/_shared/hooks/use-push-token-sync.ts](../../../../../../manyak-web/src/features/my/_shared/hooks/use-push-token-sync.ts)
- [src/lib/push](../../../../../../manyak-web/src/lib/push)
- [public/firebase-messaging-sw.js](../../../../../../manyak-web/public/firebase-messaging-sw.js)
- [tests/lib/push](../../../../../../manyak-web/tests/lib/push)
- [e2e/notifications](../../../../../../manyak-web/e2e/notifications)
- [e2e/notices](../../../../../../manyak-web/e2e/notices)

### 3 작성과 검증

- 공지의 기기 읽음과 회원 알림의 서버 읽음을 구분한다.
- 수신 동의, OS 권한과 회원 인증을 같은 상태로 합치지 않는다.
- 확정 ADR과 QA 원문을 보존하고 과거 실행 표시와 이번 실행을 구분한다.
- 링크, 앵커, ID 중복과 단계 순서를 확인하고 `git diff --check`를 실행한다.
- 명세의 작성과 검토를 서브에이전트에 맡기지 않는다.

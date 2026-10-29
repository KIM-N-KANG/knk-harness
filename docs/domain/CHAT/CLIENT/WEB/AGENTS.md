# CHAT WEB 클라이언트

단계마다 공통 문서 다음 해당 플랫폼 문서를 읽는다. 사용자 기대와 요구사항, 화면, 연동과 구현, 검증 순서로 구체화한다.

작성 규칙: [클라이언트 가이드](../../../../REFERENCE/CLIENT-SPEC-WRITING-GUIDE.md).

공통 계약: [CLIENT](../AGENTS.md).

<br>

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 CHAT 웹 요구사항 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 CHAT 웹 경로 |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 CHAT 웹 이동 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 CHAT 웹 표현 |
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 CHAT 웹 구성 |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 CHAT 웹 상태 관리 |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 CHAT 웹 실행 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 CHAT 웹 검증 |
| [DECISIONS.md](DECISIONS.md) | 확정된 결정과 대체 관계 |

<br>

### 2 코드 대응

| 구성 | 위치 |
|---|---|
| 채팅 목록과 방 | [src/features/chats](../../../../../../manyak-web/src/features/chats) |
| 공유본 | [src/features/shares](../../../../../../manyak-web/src/features/shares) |
| 피드백 | [src/features/my/feedback](../../../../../../manyak-web/src/features/my/feedback) |
| 생성 추적 | [src/features/chats/room/utils/follow-chat-generation.ts](../../../../../../manyak-web/src/features/chats/room/utils/follow-chat-generation.ts) |
| 파서 | [src/features/chats/_shared/utils/chat-message-segments.ts](../../../../../../manyak-web/src/features/chats/_shared/utils/chat-message-segments.ts) |
| 설정 | [src/features/chats/room/hooks/use-chat-model.ts](../../../../../../manyak-web/src/features/chats/room/hooks/use-chat-model.ts) |
| 그림 안무 | [src/features/chats/room/utils/realtime-image-choreography.ts](../../../../../../manyak-web/src/features/chats/room/utils/realtime-image-choreography.ts) |
| E2E | [e2e/chats](../../../../../../manyak-web/e2e/chats) |
| 단위 테스트 | [tests/features/chats](../../../../../../manyak-web/tests/features/chats) |

<br>

### 3 작성과 검증

- 공통 입력과 복구 의미를 유지하고 플랫폼의 수명, 공유 수단과 저장 위치를 구분한다.
- 새 계약 없이 구현 결과로 요구를 바꾸지 않는다. 확정 ADR과 기존 QA의 조건 및 기대 결과를 보존한다.
- 링크, 앵커, 유저 스토리와 QA ID, 단계 역참조를 검사하고 `git diff --check`를 실행한다.
- 검증 수단과 실제 실행 결과를 구분한다. 실행 환경과 결과는 PR과 CI에 남긴다.
- 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

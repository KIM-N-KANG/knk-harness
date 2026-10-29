# STORY WEB 클라이언트

단계마다 공통 문서 다음 해당 플랫폼 문서를 읽는다. 사용자 기대와 요구사항, 화면, 연동과 구현, 검증 순서로 구체화한다.

작성 규칙: [클라이언트 가이드](../../../../REFERENCE/CLIENT-SPEC-WRITING-GUIDE.md).

공통 계약: [CLIENT](../AGENTS.md).

<br>

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 웹 STORY 요구사항 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 웹 STORY 화면 구성 |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 웹 STORY 화면 흐름 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 웹 STORY 화면 표현 |
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 웹 STORY 구성 |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 웹 STORY 상태 관리 |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 웹 STORY 실행 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 웹 STORY 검증 |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 6 웹 STORY 배포 |
| [DECISIONS.md](DECISIONS.md) | STORY 웹 결정 기록 |

<br>

### 2 코드 대응

| 구성 | 위치 |
|---|---|
| 탐색과 상세 및 제작 | [src/features/stories](../../../../../../manyak-web/src/features/stories) |
| E2E | [e2e/stories](../../../../../../manyak-web/e2e/stories) |
| 단위 테스트 | [tests/features/stories](../../../../../../manyak-web/tests/features/stories) |

기존 QA 작성 시점의 코드 근거: [manyak-web 9ab592f](https://github.com/KIM-N-KANG/manyak-web/tree/9ab592f698d0baaf15d96c80161a5924e5c7f73c). 이 커밋 링크는 현재 실행 결과나 배포 증거가 아니다.

<br>

### 3 작성과 검증

- 공통 입력과 복구 의미를 유지하고 플랫폼의 수명, 공유 수단과 저장 위치를 구분한다.
- 새 계약 없이 구현 결과로 요구를 바꾸지 않는다. 확정 ADR과 기존 QA의 조건 및 기대 결과를 보존한다.
- 링크, 앵커, 유저 스토리와 QA ID, 단계 역참조를 검사하고 `git diff --check`를 실행한다.
- 검증 수단과 실제 실행 결과를 구분한다. 실행 환경과 결과는 PR과 CI에 남긴다.
- 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

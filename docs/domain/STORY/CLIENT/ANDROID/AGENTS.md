# STORY ANDROID 클라이언트

단계마다 공통 문서 다음 해당 플랫폼 문서를 읽는다. 사용자 기대와 요구사항, 화면, 연동과 구현, 검증 순서로 구체화한다.

작성 규칙: [클라이언트 가이드](../../../../reference/CLIENT-SPEC-WRITING-GUIDE.md).

공통 계약: [CLIENT](../AGENTS.md).

<br>

### 문서 역할

| 문서 | 내용 |
|---|---|
| [REQUIREMENTS.md](REQUIREMENTS.md) | Android STORY 요구사항 |
| [INFORMATION-ARCHITECTURE.md](INFORMATION-ARCHITECTURE.md) | Android STORY 화면 구성 |
| [INTERACTION-FLOWS.md](INTERACTION-FLOWS.md) | Android STORY 화면 흐름 |
| [LAYOUT.md](LAYOUT.md) | Android STORY 화면 표현 |
| [COMPONENT-ARCHITECTURE.md](COMPONENT-ARCHITECTURE.md) | Android STORY 구성 |
| [STATE-MANAGEMENT.md](STATE-MANAGEMENT.md) | Android STORY 상태 관리 |
| [EXECUTION.md](EXECUTION.md) | Android STORY 실행 |
| [VERIFICATION.md](VERIFICATION.md) | Android STORY 검증 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Android STORY 배포 |
| [DECISIONS.md](DECISIONS.md) | STORY Android 결정 기록 |

<br>

### 코드 대응

| 구성 | 위치 |
|---|---|
| 상세 | [story/src/main/java/app/manyak/story](../../../../../../manyak-android/story/src/main/java/app/manyak/story) |
| 제작 | [create/src/main/java/app/manyak/create](../../../../../../manyak-android/create/src/main/java/app/manyak/create) |
| 제작 목록 | [studio/src/main/java/app/manyak/studio](../../../../../../manyak-android/studio/src/main/java/app/manyak/studio) |
| 제작 검증 | [create/src/test/java/app/manyak/create](../../../../../../manyak-android/create/src/test/java/app/manyak/create) |
| 홈 | [home/src/main/java/app/manyak/home](../../../../../../manyak-android/home/src/main/java/app/manyak/home) |
| 디자인 토큰 | [DESIGN.md](../../../../../../manyak-android/DESIGN.md) |

<br>

### 작성과 검증

- 공통 입력과 복구 의미를 유지하고 플랫폼의 수명, 공유 수단과 저장 위치를 구분한다.
- 새 계약 없이 구현 결과로 요구를 바꾸지 않는다. 확정 ADR과 기존 QA의 조건 및 기대 결과를 보존한다.
- 링크, 앵커, 유저 스토리와 QA ID, 단계 역참조를 검사하고 `git diff --check`를 실행한다.
- 검증 수단과 실제 실행 결과를 구분한다. 실행 환경과 결과는 PR과 CI에 남긴다.
- 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

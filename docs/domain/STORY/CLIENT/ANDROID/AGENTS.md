# STORY ANDROID 클라이언트

작성 규칙: [클라이언트 가이드](../../../../reference/CLIENT-SPEC-WRITING-GUIDE.md).

공통 계약: [CLIENT](../AGENTS.md).

<br>

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
| [DECISIONS.md](DECISIONS.md) | STORY Android 결정 기록 |

<br>

### 2 코드 대응

| 구성 | 위치 |
|---|---|
| 상세 | [story/src/main/java/app/manyak/story](../../../../../../manyak-android/story/src/main/java/app/manyak/story) |
| 제작 | [create/src/main/java/app/manyak/create](../../../../../../manyak-android/create/src/main/java/app/manyak/create) |
| 제작 목록 | [studio/src/main/java/app/manyak/studio](../../../../../../manyak-android/studio/src/main/java/app/manyak/studio) |
| 제작 검증 | [create/src/test/java/app/manyak/create](../../../../../../manyak-android/create/src/test/java/app/manyak/create) |
| 홈 | [home/src/main/java/app/manyak/home](../../../../../../manyak-android/home/src/main/java/app/manyak/home) |
| 디자인 토큰 | [DESIGN.md](../../../../../../manyak-android/DESIGN.md) |

<br>

### 3 작성과 검증

- 공통 입력과 복구 의미를 유지하고 플랫폼의 수명, 공유 수단과 저장 위치를 구분한다.
- 새 계약 없이 구현 결과로 요구를 바꾸지 않는다. 확정 ADR과 기존 QA의 조건 및 기대 결과를 보존한다.
- 링크, 앵커, 유저 스토리와 QA ID, 단계 역참조를 검사하고 `git diff --check`를 실행한다.
- 검증 수단과 실제 실행 결과를 구분한다. 실행 환경과 결과는 PR과 CI에 남긴다.
- 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

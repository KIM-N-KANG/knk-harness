# PAYMENT ANDROID 클라이언트

단계마다 공통 문서, 해당 플랫폼 문서 순서로 읽는다. 하위 구현과 검증을 이유로 상위 요구를 바꾸지 않는다.

작성 규칙은 클라이언트 가이드를 적용한다. ([작성 가이드](../../../../reference/CLIENT-SPEC-WRITING-GUIDE.md))

공통 계약: [CLIENT](../AGENTS.md).

<br>

### 문서 역할

| 문서 | 내용 |
|---|---|
| [REQUIREMENTS.md](REQUIREMENTS.md) | PAYMENT Android 요구사항 |
| [INFORMATION-ARCHITECTURE.md](INFORMATION-ARCHITECTURE.md) | PAYMENT Android 화면 구성 |
| [INTERACTION-FLOWS.md](INTERACTION-FLOWS.md) | PAYMENT Android 화면 흐름 |
| [LAYOUT.md](LAYOUT.md) | PAYMENT Android 화면 표현 |
| [COMPONENT-ARCHITECTURE.md](COMPONENT-ARCHITECTURE.md) | PAYMENT Android 구성 |
| [STATE-MANAGEMENT.md](STATE-MANAGEMENT.md) | PAYMENT Android 상태 관리 |
| [EXECUTION.md](EXECUTION.md) | PAYMENT Android 실행 |
| [VERIFICATION.md](VERIFICATION.md) | PAYMENT Android 검증 |
| [DECISIONS.md](DECISIONS.md) | 과거 선택과 대체 관계 |

<br>

### 코드 대응

| 구성 | 위치 |
|---|---|
| 충전 화면과 저장소 | [my/src/main/java/app/manyak/my/credit](../../../../../../manyak-android/my/src/main/java/app/manyak/my/credit) |
| 정책과 체험 계약 | [common/src/main/java/app/manyak/common/domain/credit](../../../../../../manyak-android/common/src/main/java/app/manyak/common/domain/credit) |
| 부족 절차 | [common/src/main/java/app/manyak/common/presentation/credit/CreditShortageController.kt](../../../../../../manyak-android/common/src/main/java/app/manyak/common/presentation/credit/CreditShortageController.kt) |
| 공용 UI | [designsystem/src/main/java/app/manyak/designsystem/credit](../../../../../../manyak-android/designsystem/src/main/java/app/manyak/designsystem/credit) |
| 충전 검증 | [my/src/test/java/app/manyak/my/credit](../../../../../../manyak-android/my/src/test/java/app/manyak/my/credit) |
| 제작 부족 검증 | [create/src/test/java/app/manyak/create/additionalinfo/presentation/CreateAdditionalInfoCreditShortageTest.kt](../../../../../../manyak-android/create/src/test/java/app/manyak/create/additionalinfo/presentation/CreateAdditionalInfoCreditShortageTest.kt) |

<br>

### 작성과 검증

- 현재 요구, 플랫폼 차이와 내부 구현을 구분한다. 채팅 모델 가격은 CHAT에서 정한다.
- 확정 ADR과 기존 QA의 조건 및 기대 결과를 보존하고, 참조와 ID를 함께 갱신한다.
- 링크, 앵커, ID 중복과 문서의 역방향 참조를 검사하고 `git diff --check`를 실행한다.
- 실행 결과와 미검증 범위는 PR과 CI에 기록한다. 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

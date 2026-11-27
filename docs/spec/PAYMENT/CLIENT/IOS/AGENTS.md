# PAYMENT IOS 클라이언트

하위 구현과 검증을 이유로 상위 요구를 바꾸지 않는다.

작성 규칙은 클라이언트 가이드를 적용한다. ([작성 가이드](../../../../reference/CLIENT-SPEC-WRITING-GUIDE.md))

공통 계약: [CLIENT](../AGENTS.md). 플랫폼 기반: [IOS 기반](../../../../platform/CLIENT/IOS/AGENTS.md), [공통 UI IOS](../../../../ui/IOS/AGENTS.md).

<br>

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 요구사항: iOS |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 화면 구성: iOS |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 화면 흐름: iOS |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 화면 배치: iOS |
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 컴포넌트 구조: iOS |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 상태 관리: iOS |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 실행: iOS |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 검증: iOS |
| [DECISIONS.md](DECISIONS.md) | 과거 선택과 대체 관계 |

<br>

### 2 코드 대응

iOS 저장소 `manyak-ios`는 생성 전이다. 아래는 이 세트를 구현할 계획 모듈이며 파일 링크를 두지 않는다.

| 계획 모듈 | 맡는 범위 |
|---|---|
| `ManyakCredit` | 이프 충전 화면과 Store, 출석과 내역 API, 정책과 체험 저장소 구현. `AttendanceClaimer`와 내역, 정책, 체험 포트 구현 |
| `ManyakCommon` | `CreditPolicy`, 체험, 출석과 내역 조회 포트, 내역 줄 entity, 부족 절차 `CreditShortageController`와 내역 절차 |
| `ManyakDesignSystem` | 이프 마크와 수치, 잔액 카드, 부족 시트, 내역 행과 목록 상태 |
| `ManyakNavigation` | 이프 충전 라우트 값과 푸시 경로의 `tab` 해석 |
| 앱 타깃 `Manyak` | 정책과 체험 조회 시작, 충전 목적지 조립, 친구 초대 줄 전달, 체험 저장소 정리 등록 |
| 단위 테스트 | `ManyakCreditTests`의 충전 Store와 저장소, `ManyakCommonTests`의 부족과 내역 절차, `ManyakChatTests`의 채팅 메뉴 내역, `ManyakCreateTests`의 제작 부족 |

옮겨 올 Android 원본의 문구는 iOS 대응 조사 기준 커밋의 [`feature/credit` 문구](https://github.com/KIM-N-KANG/manyak-android/blob/ccc93f77289fd960def116184c2c86c552e4124e/feature/credit/src/main/res/values/strings.xml)와 `core/designsystem`, `core/common`의 `strings.xml`에 있다. 그중 `credit_purchase_notice`와 `credit_purchase_notice_tooltip`은 옮기지 않는다. ([I-080](DECISIONS.md#i-080))

<br>

### 3 작성과 검증

- 현재 요구, 플랫폼 차이와 내부 구현을 구분한다. 채팅 모델 가격은 CHAT에서 정한다.
- 확정 ADR과 기존 QA의 조건 및 기대 결과를 보존하고, 참조와 ID를 함께 갱신한다.
- 링크, 앵커, ID 중복과 문서의 역방향 참조를 검사하고 `git diff --check`를 실행한다.
- 실행 결과와 미검증 범위는 PR과 CI에 기록한다. 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

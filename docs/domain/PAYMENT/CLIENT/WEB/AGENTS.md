# PAYMENT WEB 클라이언트

하위 구현과 검증을 이유로 상위 요구를 바꾸지 않는다.

작성 규칙은 클라이언트 가이드를 적용한다. ([작성 가이드](../../../../reference/CLIENT-SPEC-WRITING-GUIDE.md))

공통 계약: [CLIENT](../AGENTS.md).

<br>

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 요구사항: 웹 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 화면 구성: 웹 |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 화면 흐름: 웹 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 화면 배치: 웹 |
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 컴포넌트 구조: 웹 |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 상태 관리: 웹 |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 실행: 웹 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 검증: 웹 |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 6 배포: 웹 |
| [DECISIONS.md](DECISIONS.md) | 과거 선택과 대체 관계 |

<br>

### 2 코드 대응

| 구성 | 위치 |
|---|---|
| 충전 화면 | [src/features/my/credits](../../../../../../manyak-web/src/features/my/credits) |
| 정책 | [src/hooks/use-credit-policy.ts](../../../../../../manyak-web/src/hooks/use-credit-policy.ts) |
| 체험 | [src/hooks/use-trials.ts](../../../../../../manyak-web/src/hooks/use-trials.ts) |
| 부족 시트 | [src/features/my/_shared/components/credit-shortage-sheet.tsx](../../../../../../manyak-web/src/features/my/_shared/components/credit-shortage-sheet.tsx) |
| 결제 복귀 | [src/app/(my)/my/credits/return/route.ts](../../../../../../manyak-web/src/app/%28my%29/my/credits/return/route.ts) |
| 출석 | [src/features/my/_shared/hooks/use-claim-attendance.ts](../../../../../../manyak-web/src/features/my/_shared/hooks/use-claim-attendance.ts) |
| 검증 | [e2e/my/credits.spec.ts](../../../../../../manyak-web/e2e/my/credits.spec.ts) |
| 주문과 날짜 단위 테스트 | [tests/features/my/credits/utils](../../../../../../manyak-web/tests/features/my/credits/utils) |

<br>

### 3 작성과 검증

- 현재 요구, 플랫폼 차이와 내부 구현을 구분한다. 채팅 모델 가격은 CHAT에서 정한다.
- 확정 ADR과 기존 QA의 조건 및 기대 결과를 보존하고, 참조와 ID를 함께 갱신한다.
- 링크, 앵커, ID 중복과 문서의 역방향 참조를 검사하고 `git diff --check`를 실행한다.
- 실행 결과와 미검증 범위는 PR과 CI에 기록한다. 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

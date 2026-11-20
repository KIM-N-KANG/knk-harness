# ACCOUNT Android 클라이언트

상위 계약은 하위 구현이나 검증 결과에 맞춰 변경하지 않는다.

플랫폼 이동: [공통 CLIENT](../AGENTS.md). 작성 규칙은 [클라이언트 가이드](../../../../reference/CLIENT-SPEC-WRITING-GUIDE.md), 과거 결정은 [DECISIONS](DECISIONS.md)에서 확인한다.

<br>

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 요구사항: 안드로이드 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 화면 구성: 안드로이드 |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 화면 흐름: 안드로이드 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 화면 배치: 안드로이드 |
| [4-1-CONTRACT.md](4-1-CONTRACT.md) | 4-1 연동 계약: 안드로이드 |
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 컴포넌트 구조: 안드로이드 |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 상태 관리: 안드로이드 |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 실행: 안드로이드 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 검증: 안드로이드 |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 6 배포: 안드로이드 |

<br>

### 2 코드 대응

| 구성 | 구현 |
|---|---|
| 인증과 토큰 | [auth](../../../../../../manyak-android/auth) |
| 로그인 화면 | [login](../../../../../../manyak-android/login) |
| 동의와 법적 문서 | [legal](../../../../../../manyak-android/legal) |
| 프로필과 페르소나, 초대 | [my](../../../../../../manyak-android/my) |
| 조립과 세션 종료 | [app](../../../../../../manyak-android/app) |
| 공유 계약 | [common](../../../../../../manyak-android/common) |

<br>

### 3 작성과 검증

- 요구사항에는 사용자 결과, 화면 설계에는 배치와 전환, 구현 설계에는 책임과 수명을 작성한다.
- 공통 본문을 플랫폼별로 복제하지 않는다. 의도된 차이는 공통 적용 범위 안에서 구체화한다.
- ADR 본문과 ID를 보존한다. 현재 계약 변경은 해당 단계에서 시작하고 이후 문서에 반영한다.
- 기존 QA 케이스와 상위 요구의 연결, 링크, 앵커, ID 중복을 검사하고 `git diff --check`를 실행한다.
- 실제 검증 결과는 PR과 CI에 기록한다. 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

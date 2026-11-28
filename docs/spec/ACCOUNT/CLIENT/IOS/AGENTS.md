# ACCOUNT iOS 클라이언트

상위 계약은 하위 구현이나 검증 결과에 맞춰 변경하지 않는다.

플랫폼 이동: [공통 CLIENT](../AGENTS.md). 작성 규칙은 [클라이언트 가이드](../../../../reference/CLIENT-SPEC-WRITING-GUIDE.md), 과거 결정은 [DECISIONS](DECISIONS.md)에서 확인한다. 공통 기술 규칙은 [IOS 기반](../../../../platform/CLIENT/IOS/AGENTS.md), 앱 셸과 진입은 [공통 UI IOS](../../../../ui/IOS/AGENTS.md)에 있다.

<br>

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 요구사항: iOS |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 화면 구성: iOS |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 화면 흐름: iOS |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 화면 배치: iOS |
| [4-1-CONTRACT.md](4-1-CONTRACT.md) | 4-1 연동 계약: iOS |
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 컴포넌트 구조: iOS |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 상태 관리: iOS |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 실행: iOS |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 검증: iOS |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 6 배포: iOS |

<br>

### 2 코드 위치

iOS 저장소 `manyak-ios`에는 타깃 선언만 있고 이 세트의 구현은 시작 전이다. 아래는 이 세트를 구현할 계획 모듈이며 파일 링크를 두지 않는다.

| 계획 모듈 | 맡는 범위 |
|---|---|
| `ManyakAuth` | 제공자 로그인, 가입 대기, Keychain 토큰, 세션 상태, `SessionGate`, 재발급 직렬화, 시작과 재설치 판정, 종료 저널 |
| `ManyakLogin` | 로그인 화면 |
| `ManyakLegal` | 동의 조회와 기록, 동의 시트, 법적 문서 화면 |
| `ManyakMy` | 마이, 프로필, 페르소나, 초대와 탈퇴 화면 |
| `ManyakCommon` | `UserScopedStore`, `MemberConsent`, `PersonaAccess`, `SignupOnboardingWriter`, 기기와 회원 suite |
| `ManyakDesignSystem` | 홈과 마이 하단 사업자 정보 푸터, 이미지 캐시 비우기 |
| 앱 타깃 `Manyak` | 루트 선택, `SessionTerminationCoordinator`, 등록 배열, 제공자 복귀 URL 전달 |

<br>

### 3 작성과 검증

- 요구사항에는 사용자 결과, 화면 설계에는 배치와 전환, 구현 설계에는 책임과 수명을 작성한다.
- 공통 본문을 플랫폼별로 복제하지 않는다. 의도된 차이는 공통 적용 범위 안에서 구체화한다.
- ADR 본문과 ID를 보존한다. 현재 계약 변경은 해당 단계에서 시작하고 이후 문서에 반영한다.
- 기존 QA 케이스와 상위 요구의 연결, 링크, 앵커, ID 중복을 검사하고 `git diff --check`를 실행한다.
- 실제 검증 결과는 PR과 CI에 기록한다. 명세 작성과 검토를 서브에이전트에 맡기지 않는다.

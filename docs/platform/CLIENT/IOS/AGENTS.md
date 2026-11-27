# IOS 플랫폼 기반

여러 도메인이 사용하는 컴포넌트, 데이터 상태, 실행, 관측과 빌드 규칙을 관리한다. 사용자 기능은 [도메인 목록](../../../spec/AGENTS.md)에서 선택하고 앱 셸과 진입은 [공통 UI IOS](../../../ui/IOS/AGENTS.md)에서 확인한다.

<br>

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [1-COMPONENT-ARCHITECTURE.md](1-COMPONENT-ARCHITECTURE.md) | 1 컴포넌트 구조: iOS |
| [2-STATE-MANAGEMENT.md](2-STATE-MANAGEMENT.md) | 2 상태 관리: iOS |
| [3-EXECUTION.md](3-EXECUTION.md) | 3 실행: iOS |
| [4-VERIFICATION.md](4-VERIFICATION.md) | 4 검증: iOS |
| [5-DEPLOYMENT.md](5-DEPLOYMENT.md) | 5 배포: iOS |
| [DECISIONS.md](DECISIONS.md) | IOS 결정 기록 |

공통 전송 계약은 [CLIENT 기반](../AGENTS.md), 공통 배포 절차는 [운영 문서](../../../operations/AGENTS.md)를 따른다. 이 폴더에서 사용자 목표를 새로 정의하지 않는다.

<br>

### 2 코드 위치

iOS 저장소 `manyak-ios`는 생성 전이다. 아래는 계획 위치이며 현재 존재하는 파일이 아니다.

| 대상 | 계획 위치 | Android 대응 |
|---|---|---|
| 앱 타깃 `Manyak` | Xcode 프로젝트의 앱 타깃 | `app` |
| 기반 타깃 `ManyakCommon`, `ManyakDesignSystem`, `ManyakNavigation`, `ManyakAnalytics`, `ManyakNetwork`, `ManyakAuth`, `ManyakReport`, `ManyakTesting` | 로컬 패키지 `Package.swift`의 타깃. 소스는 `Core/<타깃>` | `core/<모듈>` |
| 기능 타깃 `ManyakHome`, `ManyakChat`, `ManyakCredit`, `ManyakStudio`, `ManyakStory`, `ManyakLogin`, `ManyakLegal`, `ManyakMy`, `ManyakCreate`, `ManyakNotification`, `ManyakNotice`, `ManyakOnboarding` | 같은 패키지의 타깃. 소스는 `Feature/<타깃>` | `feature/<모듈>` |
| 단위 테스트 | 타깃마다 `<타깃>Tests` | `src/test` |
| UI 테스트 | 앱 타깃의 XCUITest 타깃 | `src/androidTest` |
| 빌드 설정 | 공용 xcconfig, 커밋하지 않는 비밀값 xcconfig와 예시 파일 | `app/build.gradle.kts`, `local.properties.example` |
| Firebase 설정 | `GoogleService-Info.plist` | `google-services.json` |
| 품질 설정 | swift-format과 SwiftLint 설정 파일 | `.editorconfig`, `config/detekt/detekt.yml` |
| CI | `.github/workflows/`의 iOS 워크플로 | `.github/workflows/android-ci.yml` |
| 에이전트 스킬 | `.agents/skills/` 원본과 `.claude/skills/` 링크 | 같은 구조 |
| 저장소 지침 | `AGENTS.md` | `AGENTS.md` |

공용 포트의 구현 타깃은 `ChatStarter`=`ManyakChat`, `CreationProgressAccess`=`ManyakCreate`, `StoryDeletion`=`ManyakStudio`, `AttendanceClaimer`=`ManyakCredit`, `PopularOriginalStories`=`ManyakHome`이며 `SessionIdAccess`는 앱 타깃이 관측에 연결한다. 그 밖에 `MemberConsent`=`ManyakLegal`, `PersonaAccess`=`ManyakMy`, `SignupOnboardingWriter`=`ManyakMy`와 `ManyakOnboarding`, 이프 정책, 체험과 내역 조회 포트=`ManyakCredit`, 제작 안내 진행 기록과 검수 결과 대기 화면 관찰 포트=`ManyakCreate`, `ManyakNetwork`의 토큰 포트=`ManyakAuth`이다. 프로토콜은 `ManyakNetwork`의 토큰 포트를 빼고 `ManyakCommon`에 둔다. `StoryReportController`는 `ManyakReport`에 두고 별도 공용 Store나 전역 싱글턴을 추가하지 않는다. `CreditShortageController`의 상태와 이벤트는 소비하는 Store가 가진다. 공유 `CreditPolicy`, `StorySummary`와 DTO는 `ManyakCommon`에 둔다.

옮겨 올 Android 원본은 iOS 대응 조사의 기준 커밋 [`ccc93f77`](https://github.com/KIM-N-KANG/manyak-android/tree/ccc93f77289fd960def116184c2c86c552e4124e)(v1.9.2)이다. 디자인 토큰은 [`core/designsystem/.../theme/`](https://github.com/KIM-N-KANG/manyak-android/tree/ccc93f77289fd960def116184c2c86c552e4124e/core/designsystem/src/main/java/app/manyak/designsystem/theme), 문구는 각 모듈의 `src/main/res/values/strings.xml`, 이미지 주소 검사는 [`CharacterImage.kt`](https://github.com/KIM-N-KANG/manyak-android/blob/ccc93f77289fd960def116184c2c86c552e4124e/core/designsystem/src/main/java/app/manyak/designsystem/component/CharacterImage.kt)에 있다.

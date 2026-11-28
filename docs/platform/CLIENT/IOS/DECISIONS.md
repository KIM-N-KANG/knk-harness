# DECISIONS.md

현재 적용 기준은 각 명세에 두고 결정 당시의 이유와 대체 관계는 이 문서에 기록한다.

<br>

### 1. 기록 규칙

- 결정 하나를 표 하나로 기록한다. 기존 ID, 날짜, 당시 상태와 근거를 유지한다.
- 상태와 구현 설명은 원본의 기록 시점을 기준으로 해석한다. 현재 적용 여부나 배포 완료를 과거 기록만으로 단정하지 않는다.
- 결정이 바뀌면 새 ID로 기록하고 대체하는 결정과 적용 범위를 명시한다.
- 원문에 구분되지 않은 배경, 대안과 영향은 추측해서 보충하지 않는다.
- 이 세트의 ID는 I-001부터 I-029까지 쓴다. 사용자가 확인하기 전의 작성 중 결정은 상태를 Proposed로 둔다.

<br>

### 2. 결정 기록

<br>

<a id="i-001"></a>
<a id="i-001-최소-배포-대상을-ios-26으로-둠"></a>

**I-001. 최소 배포 대상을 iOS 26으로 둠**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 없음 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | 새 앱의 최소 지원 iOS 버전을 정해야 했다. Firebase 13과 Google Sign-In 10의 최소 iOS는 15이고 SwiftData의 새 관찰 API는 iOS 27 전용이다. 2026년 10월 말 사용 비율은 iOS 26 약 55%, iOS 27 약 36%, iOS 18 약 7%다(TelemetryDeck 집계, Apple 공식 수치 아님, 2026-11-26 웹 확인). |
| 채택 | 최소 배포 대상을 iOS 26으로 둔다. iOS 27 전용 API는 쓰지 않는다. |
| 대안 | 원문에 별도 항목으로 구분하지 않음 |
| 이유 | 원문에 별도 항목으로 구분하지 않음 |
| 영향 | iOS 27 전용 API는 가용성 분기로 감싸서도 쓰지 않는다. 저장 방식 선택에서 SwiftData의 iOS 27 전용 기능을 제외했다([I-008](#i-008)). |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리(2026-11-26, 저장소 미포함) 7절 9번 |

<br>

<a id="i-002"></a>
<a id="i-002-swift-6-언어-모드와-xcode-27-이상을-사용"></a>

**I-002. Swift 6 언어 모드와 Xcode 27 이상을 사용**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 없음 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | Swift 6 언어 모드의 엄격한 동시성 검사를 켤지와 Xcode 최소 버전을 정해야 했다. 조사 환경은 Xcode 27.2(27B52)와 Swift 6.4.2였다. |
| 채택 | Swift 6 언어 모드로 엄격한 동시성 검사를 사용하고 Xcode 27 이상으로 빌드한다. |
| 대안 | 엄격한 동시성 검사를 켜지 않는 방식 |
| 이유 | 원문에 별도 항목으로 구분하지 않음 |
| 영향 | 액터 격리와 `Sendable` 위반이 컴파일 오류가 된다. CI 러너도 Xcode 27 이상이 필요하다([I-013](#i-013)). |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 7절 11번 |

<br>

<a id="i-003"></a>
<a id="i-003-번들-id와-android와-별개인-버전-체계"></a>

**I-003. 번들 ID와 Android와 별개인 버전 체계**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 버전 올림과 릴리스 브랜치 규칙은 [I-023](#i-023) |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | iOS 번들 ID와 버전 번호를 Android와 맞출지 정해야 했다. Android는 앱 식별자 `app.manyak`, 버전 1.9.2(코드 27)였다. |
| 채택 | 번들 ID는 `app.manyak`이다. 마케팅 버전은 Android와 별개로 1.0.0부터 시작하고 빌드 번호는 올릴 때마다 1 증가한다. |
| 대안 | 버전 번호를 Android와 맞추는 방식 |
| 이유 | 원문에 별도 항목으로 구분하지 않음 |
| 영향 | 같은 버전 숫자가 두 앱에서 다른 기능 묶음을 뜻하므로 버전별 지표와 출시 중단 기준은 플랫폼을 나눠 비교한다. |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 7절 12번 |

<br>

<a id="i-004"></a>
<a id="i-004-swift-package-manager-로컬-패키지로-모듈화"></a>

**I-004. Swift Package Manager 로컬 패키지로 모듈화**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 패키지 배치는 [I-022](#i-022) |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | Android는 앱 조립 1개, 기반 8개, 화면 기능 12개의 Gradle 모듈과 허용 의존 표를 둔다. iOS의 모듈화 도구를 정해야 했다. |
| 채택 | Swift Package Manager 로컬 패키지의 타깃으로 모듈을 나눈다. 모듈 목록과 허용 의존 표는 Android와 1대1로 같다. 서드파티 의존성도 Swift Package Manager로만 받는다. |
| 대안 | Tuist 같은 프로젝트 생성 도구(현재 상태는 간접 자료뿐이라 미확인)<br>단일 타깃에서 시작 |
| 이유 | 원문에 별도 항목으로 구분하지 않음 |
| 영향 | 타깃 이름과 허용 의존은 [1-2](1-COMPONENT-ARCHITECTURE.md#1-2-모듈과-허용-의존)에 둔다. Firebase Apple SDK는 Swift Package Manager 전용이고 Kakao SDK도 Swift Package Manager로 배포된다(2026-11-26 웹 확인). |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 1-1절, 7절 13번과 15번 |

<br>

<a id="i-005"></a>
<a id="i-005-모듈-의존은-컴파일러로-계층은-폴더-규칙과-리뷰로-지킴"></a>

**I-005. 모듈 의존은 컴파일러로 계층은 폴더 규칙과 리뷰로 지킴**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | Android [A-038](../ANDROID/DECISIONS.md#a-038)의 iOS 대응. Android의 PSI 경계 검사는 옮기지 않는다 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | Android는 `checkModuleArchitecture`가 Kotlin 소스를 파싱해 계층 경계를 검사한다. Swift에는 같은 모듈 안의 폴더 사이 참조를 막는 기본 장치가 없다. |
| 채택 | 모듈 사이 의존은 `Package.swift`의 타깃 선언으로 컴파일러가 막는다. 모듈 안의 Entity, Domain, Data, Presentation은 폴더 규칙과 PR 리뷰로 지키며 자동 검사 도구는 두지 않는다. |
| 대안 | 계층을 별도 타깃으로 쪼개 컴파일러가 막게 함<br>접근 제어(`internal`, `package`)로 좁힘<br>SwiftSyntax 스크립트나 SwiftLint 사용자 규칙으로 직접 검사 |
| 이유 | 원문에 별도 항목으로 구분하지 않음 |
| 영향 | 계층 위반은 리뷰에서만 잡힌다. 자동 검사가 필요해지면 후속 결정으로 다룬다. 작성 중 Xcode 27.2의 `swift build`에서 의존을 선언하지 않은 형제 타깃의 import가 `unable to resolve module dependency`로 실패함을 확인했다(2026-11-28). |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 1-1절, 7절 14번 |

<br>

<a id="i-006"></a>
<a id="i-006-라이브러리-없이-생성자-주입과-조립-객체를-사용"></a>

**I-006. 라이브러리 없이 생성자 주입과 조립 객체를 사용**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 없음 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | Android는 Hilt로 의존을 주입하고 멀티바인딩으로 정리 계약 구현을 모은다. iOS에는 Apple이 제공하는 의존성 주입 도구가 없다. |
| 채택 | 라이브러리 없이 생성자 주입과 앱 타깃의 조립 객체(Composition Root)를 쓴다. 정리 계약처럼 여러 구현을 모으는 묶음은 앱 타깃의 등록 배열로 둔다. |
| 대안 | Factory 또는 swift-dependencies(서드파티, 현재 상태 미확인) |
| 이유 | 원문에 별도 항목으로 구분하지 않음 |
| 영향 | 생성자 인자로 넘기므로 빠진 의존은 컴파일 오류가 된다. 등록 배열의 누락은 컴파일러가 잡지 못해 리뷰로 확인한다. |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 2절, 7절 15번 |

<br>

<a id="i-007"></a>
<a id="i-007-observation-위에-mvi-계약을-직접-구현"></a>

**I-007. Observation 위에 MVI 계약을 직접 구현**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | Android [A-005](../ANDROID/DECISIONS.md#a-005)의 iOS 대응. 효과 수집 방식은 [I-018](#i-018) |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | Android가 프레임워크 대신 직접 구현을 택한 이유는 순서 보존, 포화 시 유실 없음, 재수집 시 효과 재생 없음을 공통 기반에서 테스트로 보장하기 위해서였다. iOS에서도 같은 계약 테스트를 옮길 수 있는지가 선택 기준이었다. |
| 채택 | Observation 프레임워크의 `@Observable` 위에 Intent, 순수 reduce, State, Event, Effect의 MVI 계약(`MviStore`)을 직접 구현한다. 통로는 `AsyncStream`이다. 순서 보존, 포화 시 유실 없음, 재수집 시 효과 재생 없음, reducer 단일 쓰기의 계약 테스트 네 가지를 둔다. |
| 대안 | The Composable Architecture(Point-Free의 서드파티 단방향 아키텍처 라이브러리, 현재 버전 미확인) |
| 이유 | 원문에 별도 항목으로 구분하지 않음 |
| 영향 | `AsyncStream`에는 넘칠 때 보내는 쪽을 기다리게 하는 정책이 없어 `unbounded`만 쓴다. 계약 테스트는 [4-2](4-VERIFICATION.md#4-2-계약-테스트와-구조)에 둔다. |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 1-2절, 7절 16번 |

<br>

<a id="i-008"></a>
<a id="i-008-로컬-저장은-grdb와-분리한-userdefaults-suite와-keychain"></a>

**I-008. 로컬 저장은 GRDB와 분리한 UserDefaults suite와 Keychain**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 제작 데이터베이스의 테이블과 재전송은 STORY, Keychain 정책은 ACCOUNT의 iOS 결정 기록 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | Android는 Room 데이터베이스 1개(버전 6, 테이블 3개)와 DataStore 파일 6개를 기기 귀속과 회원 귀속으로 나눠 쓴다. 토큰은 Android Keystore로 암호화해 DataStore에 둔다. |
| 채택 | 데이터베이스는 GRDB.swift(SQLite)를 쓰고 Android 스키마 버전 6의 현재 테이블 3개만 옮기며 과거 마이그레이션은 옮기지 않는다. 키와 값은 UserDefaults를 기기 귀속 suite와 회원 귀속 suite로 나눈다. 토큰은 Keychain에 둔다. |
| 대안 | SwiftData(Apple의 영속 저장 프레임워크) |
| 이유 | SwiftData의 구획 쿼리, 뷰 밖 관찰과 변경 이력 관찰은 iOS 27 전용이다(2026-11-26 웹 확인). GRDB는 SQL을 직접 다루고 지원 OS 범위가 넓다. 테이블이 3개뿐이고 관계가 단순하다. |
| 영향 | 회원 suite를 통째로 지워 로그아웃 정리가 단순해진다. 저장 원칙은 [2-4](2-STATE-MANAGEMENT.md#2-4-로컬-저장)에 둔다. |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 1-7절, 7절 19번 |

<br>

<a id="i-009"></a>
<a id="i-009-원격-이미지-로딩에-nuke를-사용"></a>

**I-009. 원격 이미지 로딩에 Nuke를 사용**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 로그아웃 정리의 이미지 캐시 삭제는 ACCOUNT의 iOS 결정 기록 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | Android는 Coil을 사용자 정의 로더 설정 없이 쓰고 인물 이미지에 허용 호스트와 경로 검사를 둔다. |
| 채택 | 원격 이미지는 Nuke로 불러온다. |
| 대안 | SwiftUI `AsyncImage`<br>Kingfisher(서드파티) |
| 이유 | `AsyncImage`는 `URLCache`에만 의존하고 캐시 제어, 사전 로드와 교차 페이드 조절이 제한적이다(2026-11-26 웹 확인). |
| 영향 | Nuke는 12.x 계열로 보이나 최신 버전은 확인하지 않았다. 이미지 컴포넌트와 주소 검사는 `ManyakDesignSystem`에 둔다. |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 2절, 7절 21번 |

<br>

<a id="i-010"></a>
<a id="i-010-관측은-amplitude와-crashlytics만-두고-광고-귀속을-제외"></a>

**I-010. 관측은 Amplitude와 Crashlytics만 두고 광고 귀속을 제외**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | Android [A-006](../ANDROID/DECISIONS.md#a-006)의 iOS 대응. Android의 Meta SDK와 Play Install Referrer는 옮기지 않는다 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | Android는 Amplitude, Crashlytics, Meta SDK의 자동 설치 이벤트와 Play Install Referrer 유입 귀속을 쓴다. iOS에서 광고 식별자를 쓰려면 App Tracking Transparency 동의 창과 개인정보 신고가 따르고, 설치 경로 문자열을 앱이 읽는 API는 없다. AdAttributionKit은 집계형이고 지연된 데이터다. |
| 채택 | 첫 출시에서 광고 귀속을 제외한다. Meta SDK, App Tracking Transparency 요청 창, 설치 귀속과 광고 식별자를 두지 않는다. 분석은 Amplitude, 크래시는 Firebase Crashlytics만 쓴다. |
| 대안 | Meta SDK와 추적 허용 요청<br>AdAttributionKit 사용 |
| 이유 | 원문에 별도 항목으로 구분하지 않음 |
| 영향 | iOS 설치에는 `initial_utm_*` 유입 귀속 속성이 남지 않아 웹과 Android 가입과 같은 기준으로 유입 경로를 비교할 수 없다. Meta 앱 설치 캠페인의 성과 측정 대상에 iOS가 없다. |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 2절, 7절 7번 |

<br>

<a id="i-011"></a>
<a id="i-011-swift-format과-swiftlint-위반을-빌드-실패로-처리"></a>

**I-011. swift-format과 SwiftLint 위반을 빌드 실패로 처리**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 없음 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | Android는 ktlint와 detekt 위반이 빌드를 실패시킨다. swift-format과 SwiftLint는 역할이 달라 함께 쓰는 경우가 많다(2026-11-26 웹 확인). |
| 채택 | 포맷은 swift-format, 코드 스멜은 SwiftLint로 검사하고 위반하면 빌드와 CI가 실패한다. |
| 대안 | SwiftFormat(서드파티 포맷터) |
| 이유 | 원문에 별도 항목으로 구분하지 않음 |
| 영향 | swift-format은 Xcode 도구 모음에 들어 있어 별도 설치가 없다(Xcode 27.2에서 6.4.4 확인, 2026-11-28). 설정 파일 인식에 대한 마찰 보고가 있다. SwiftLint의 최신 버전은 확인하지 않았다. |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 5절, 7절 31번 |

<br>

<a id="i-012"></a>
<a id="i-012-단위-테스트는-swift-testing-ui-테스트는-xcuitest"></a>

**I-012. 단위 테스트는 Swift Testing UI 테스트는 XCUITest**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 테스트 도우미 타깃은 Android [A-094](../ANDROID/DECISIONS.md#a-094)의 iOS 대응 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | Android는 JUnit 4, 코루틴 테스트와 OkHttp 목 서버를 쓰고 기기 테스트는 CI에서 돌리지 않는다. UI 자동화와 성능 테스트는 XCTest만 지원한다(2026-11-26 웹 확인). 코루틴 테스트의 시간 건너뛰기에 대응하는 Apple 기본 수단은 약하다. |
| 채택 | 단위 테스트는 Swift Testing, UI 테스트는 XCTest의 XCUITest로 작성한다. UI 테스트는 CI에서 돌리지 않는다. HTTP 대역은 `URLProtocol` 가로채기, 시간은 시계 주입으로 다룬다. |
| 대안 | UI 테스트를 CI에서 실행 |
| 이유 | 원문에 별도 항목으로 구분하지 않음 |
| 영향 | `URLProtocol` 대역과 조작 가능한 시계는 `ManyakTesting`에 둔다. 시각을 쓰는 코드는 시계를 주입받는다. |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 5절, 7절 32번 |

<br>

<a id="i-013"></a>
<a id="i-013-ci는-github-actions-macos-러너"></a>

**I-013. CI는 GitHub Actions macOS 러너**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 없음 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | Android CI는 GitHub Actions Ubuntu 러너에서 `dev`, `main` 대상 PR과 push마다 전체 검사와 debug 빌드를 실행한다. iOS 빌드는 macOS 러너가 필요하다. |
| 채택 | GitHub Actions macOS 러너에서 `dev`와 `main` 대상 PR과 push마다 포맷 검사, 린트, 단위 테스트와 Debug 빌드를 실행한다. |
| 대안 | Xcode Cloud(Apple의 CI 서비스. 서명은 자동 처리하나 임의 작업의 자유도가 낮음) |
| 이유 | 원문에 별도 항목으로 구분하지 않음 |
| 영향 | 비공개 저장소에서 macOS 러너는 분당 과금 배수가 10배라는 자료가 있다(블로그 출처, 2026-11-26 웹 확인). Xcode 27 러너 이미지의 제공 시점은 확인하지 않았다. |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 5절, 7절 33번 |

<br>

<a id="i-014"></a>
<a id="i-014-서명과-출시-빌드는-수동"></a>

**I-014. 서명과 출시 빌드는 수동**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | Android 앱의 수동 번들 업로드와 같은 방식([운영 5-3](../../../operations/DEPLOYMENT.md#5-3-manyak-android-ci)) |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | Android는 CI가 출시 번들을 만들지 않고 담당자가 `main` 병합 커밋에서 로컬로 만들어 Play Console에 올리며 CI에 서명 키를 두지 않는다. iOS는 배포 인증서와 프로비저닝 프로파일 관리가 더해진다. |
| 채택 | 담당자가 `main` 병합 커밋에서 Xcode로 Archive한 뒤 App Store Connect에 올린다. CI에 서명 자산을 두지 않는다. |
| 대안 | fastlane 또는 Xcode Cloud로 자동화 |
| 이유 | 원문에 별도 항목으로 구분하지 않음 |
| 영향 | 인증서와 프로파일은 담당자 환경에 남는다. 서명 방식은 [I-025](#i-025)가 정한다. |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 5절, 7절 34번 |

<br>

<a id="i-015"></a>
<a id="i-015-testflight에서-같은-빌드를-승격하고-단계적-출시를-사용"></a>

**I-015. TestFlight에서 같은 빌드를 승격하고 단계적 출시를 사용**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 중단 기준은 [운영 9-3](../../../operations/DEPLOYMENT.md#9-3-android-단계적-출시와-중단-기준)과 같다 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | Android는 내부 테스트, 비공개 테스트, 프로덕션 순으로 같은 번들을 승격하고 프로덕션은 20%부터 단계적으로 출시한다. 같은 빌드를 승격하는 원칙은 TestFlight에서도 성립한다. |
| 채택 | TestFlight 내부 테스터, 외부 테스터, App Store 순으로 같은 빌드를 승격한다. App Store Connect의 단계적 출시를 쓰고 중단 기준은 Android와 같다. |
| 대안 | 단계적 출시를 쓰지 않는 방식 |
| 이유 | 원문에 별도 항목으로 구분하지 않음 |
| 영향 | iOS 단계적 출시는 비율을 고를 수 없고 일정이 고정되며 자동 업데이트에만 적용된다는 조사가 있으나 다시 확인하지 않았다. 외부 테스트와 출시에는 Apple 심사가 있다. 버전별 비교 대시보드는 iOS도 첫 출시 전에 있어야 기준이 성립한다. |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 5절, 7절 35번 |

<br>

<a id="i-016"></a>
<a id="i-016-xcode-제공-스킬은-개인-환경에만-두고-저장소-스킬을-다시-작성"></a>

**I-016. Xcode 제공 스킬은 개인 환경에만 두고 저장소 스킬을 다시 작성**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | PR 전 리뷰와 화면 검사는 Android [A-097](../ANDROID/DECISIONS.md#a-097)의 iOS 대응 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | Xcode 27.2(27B52)에서 2026-11-26에 `xcrun agent skills export`로 내보낸 스킬은 11개였고 웹 자료의 목록과 달랐다. Xcode 버전마다 목록이 바뀌고 해시로 잠그는 장치가 없으며 저장소 커밋에 대한 라이선스 언급은 찾지 못했다. |
| 채택 | Xcode 제공 스킬은 저장소에 커밋하지 않고 개인 환경에만 둔다. 저장소 스킬은 Android 구성을 iOS 도구에 맞춰 다시 작성하고 `configuration-changes`는 비적용이다. |
| 대안 | Xcode 제공 스킬을 저장소에 커밋 |
| 이유 | 원문에 별도 항목으로 구분하지 않음 |
| 영향 | 저장소 스킬은 Xcode 제공 스킬 없이도 실행되어야 하므로 `ui-review`는 `xcrun simctl`로 설치, 실행과 캡처를 하고 Xcode 제공 스킬은 보조로만 쓴다. 일부 Xcode 스킬은 Xcode가 제공하는 MCP 도구와 열린 프로젝트가 필요하다는 자료가 있다. |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 6절, 7절 36번 |

<br>

<a id="i-017"></a>
<a id="i-017-ios-명세는-하네스-문서를-기준으로-작성"></a>

**I-017. iOS 명세는 하네스 문서를 기준으로 작성**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 플랫폼 기반에 해당하는 불일치만 다룬다. 로그아웃 순서와 세션 상태 이름은 ACCOUNT의 iOS 결정 기록 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | 하네스 문서와 Android 코드가 다른 곳이 있다. |
| 채택 | iOS 본문은 하네스 문서를 기준으로 쓰고 기존 Android와 공통 본문은 고치지 않는다. |
| 대안 | 원문에 별도 항목으로 구분하지 않음 |
| 이유 | 원문에 별도 항목으로 구분하지 않음 |
| 영향 | 수정 요청 403: [공통 연동 2](../CONTRACT.md#2-응답과-날짜)는 "수정 권한이 없어요" 안내 후 상세 복귀로 정하지만 Android 구현을 찾지 못했다. iOS는 공통 연동을 따른다. 별도 티켓으로 기준 문서 정리<br>디자인 토큰: Android `DESIGN.md`와 Kotlin 토큰 파일의 값이 여섯 곳에서 다르다. iOS는 [A-101](../ANDROID/DECISIONS.md#a-101)에 따라 Kotlin 값을 옮긴다. 별도 티켓으로 기준 문서 정리<br>기기 ID 헤더: 공통 연동 1절과 분석 기준 6-2절은 일반 요청의 누락을 허용하고 필수 경로만 막지만 Android 코드는 모든 요청에 싣고 값이 없으면 요청을 막는다. iOS는 하네스 기준을 따른다. 별도 티켓으로 기준 문서 정리 |
| 근거 | [KNK-2154](https://kimandkang.atlassian.net/browse/KNK-2154), Android 현황과 iOS 대응 정리 1-4절, 1-5절, 3절, 7절 38번과 39번 |

<br>

<a id="i-018"></a>
<a id="i-018-effect는-수집마다-새-스트림으로-전달하고-store가-보관"></a>

**I-018. Effect는 수집마다 새 스트림으로 전달하고 Store가 보관**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Proposed |
| 관계 | [I-007](#i-007)의 구현 조건 |
| 승인 근거 | 작성 중 결정. 사용자 확인 전 |
| 배경 | Android는 화면이 STARTED인 동안 효과를 수집하고 정지 중 효과를 채널에 남겨 재수집에서 전달한다. SwiftUI `.task`는 화면이 사라지면 취소된다. 작성 중 Swift 6.4.2에서 순회하던 `Task`를 취소하면 `AsyncStream`이 종료되고 이후 넣은 값이 `terminated`로 거절됨을 확인했다(2026-11-28). |
| 채택 | Store가 효과 보관 대기열을 가진다. 수집을 시작할 때마다 새 스트림을 만들고 이전 수집 스트림을 닫은 뒤 보관 효과부터 전달한다. 넣은 결과가 종료이면 효과를 보관 대기열로 돌린다. |
| 대안 | Store의 내부 `AsyncStream`을 화면에 그대로 넘김: 첫 수집이 취소되면 통로가 끝나 이후 효과를 받지 못한다<br>효과를 State에 두고 소비 표시: 일회성 출력과 필수 저장 상태가 섞인다 |
| 이유 | 화면이 덮이거나 탭이 바뀌어 수집이 끊겨도 효과를 잃지 않고 한 번만 전달하는 Android 계약을 지키기 위해서이다. 작성 중 같은 방식의 시험 구현이 Swift 6 언어 모드에서 순서 보존, 보관, 재생 없음을 통과했다. |
| 영향 | 계약 테스트에 수집 중단 동안 보관 항목을 더한다. Android 테스트 "화면이 일시 정지된 동안의 효과는 남아 있다가 재수집에서 전달된다"에 대응한다. |
| 근거 | 작성 중 시험(2026-11-28, Swift 6.4.2, 저장소 미포함) |

<br>

<a id="i-019"></a>
<a id="i-019-x-manyak-app-version-헤더를-싣지-않음"></a>

**I-019. X-Manyak-App-Version 헤더를 싣지 않음**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 없음 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | [ACCOUNT 백엔드 계약](../../../spec/ACCOUNT/BACKEND/4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더)은 이 헤더를 Android 앱이 모든 요청에 싣는 앱 버전으로 정하고, 서버는 헤더가 있으면 서버 분석 이벤트의 `platform`을 `Android`로 기록한다([5-4-9 분석 이벤트](../../../spec/ACCOUNT/BACKEND/5-4-OBSERVABILITY.md#5-4-9-분석-이벤트)). |
| 채택 | iOS는 서버가 iOS를 구분하는 계약을 추가하기 전까지 이 헤더를 싣지 않는다. 헤더 값과 형식은 미정(서버 선행 변경 필요)이다. |
| 대안 | Android처럼 모든 요청에 실음: iOS 요청에서 생긴 서버 분석 이벤트가 `platform: Android`로 기록된다 |
| 이유 | 선택 헤더라 빼도 요청이 거절되지 않고 잘못된 플랫폼 값이 쌓이지 않는다. |
| 영향 | iOS 요청의 서버 분석 이벤트는 `platform`과 `app_version` 없이 기록되고 웹처럼 클라이언트 이벤트와의 병합을 따른다. 서버 계약이 바뀌면 새 결정으로 다룬다. |
| 근거 | [ACCOUNT 백엔드 계약](../../../spec/ACCOUNT/BACKEND/4-2-CONTRACT.md#4-2-1-공통-규칙과-헤더) |

<br>

<a id="i-020"></a>
<a id="i-020-디자인-토큰-값은-ios-토큰-파일을-기준으로-둠"></a>

**I-020. 디자인 토큰 값은 iOS 토큰 파일을 기준으로 둠**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Proposed |
| 관계 | Android [A-101](../ANDROID/DECISIONS.md#a-101)과 같은 배치 |
| 승인 근거 | 작성 중 결정. 사용자 확인 전 |
| 배경 | 확정 결정은 색, 타이포그래피, 간격, 모서리 토큰을 Android와 같은 값으로 둔다. Android는 Kotlin 토큰 파일을 값의 기준으로 두고 하네스에 값 표를 두지 않는다. iOS 저장소는 아직 없다. |
| 채택 | 첫 값은 Android 커밋 `ccc93f77`의 Kotlin 토큰 파일에서 옮기고 이후에는 `ManyakDesignSystem`의 토큰 파일을 기준으로 둔다. 하네스의 platform과 ui 문서에 값 표를 두지 않는다. |
| 대안 | platform 또는 ui의 IOS 문서에 값 표를 둠: 사람이 옮겨 적는 사본이 하나 더 생긴다 |
| 이유 | A-101의 배경처럼 옮겨 적은 사본은 아무도 맞추지 않다가 어긋난다. 기준을 한 곳에 두어야 어긋났을 때 판단할 수 있다. |
| 영향 | 두 앱의 값이 같은지는 자동으로 확인하지 못한다. 값을 바꾸는 PR에 다른 앱의 변경 필요를 적는다. |
| 근거 | [A-101](../ANDROID/DECISIONS.md#a-101), [Android 토큰 파일](https://github.com/KIM-N-KANG/manyak-android/tree/ccc93f77289fd960def116184c2c86c552e4124e/core/designsystem/src/main/java/app/manyak/designsystem/theme) |

<br>

<a id="i-021"></a>
<a id="i-021-firebase-설정-파일을-저장소에-커밋"></a>

**I-021. Firebase 설정 파일을 저장소에 커밋**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Proposed |
| 관계 | Android `google-services.json` 커밋과 같은 방식([운영 5-3](../../../operations/DEPLOYMENT.md#5-3-manyak-android-ci)) |
| 승인 근거 | 작성 중 결정. 사용자 확인 전 |
| 배경 | 확정 결정은 기존 Firebase 프로젝트에 iOS 앱을 추가한다. CI는 비밀값 없이 PR마다 Debug 빌드를 만든다. |
| 채택 | `GoogleService-Info.plist`를 저장소에 커밋하고 환경 구분 없는 Firebase 프로젝트 하나를 쓴다. Debug는 Crashlytics 수집을 끈다. APNs 인증 키는 Firebase 콘솔에만 등록한다. |
| 대안 | 비밀값처럼 커밋하지 않고 주입: CI와 새 작업 환경마다 파일을 따로 배포해야 한다 |
| 이유 | 파일의 값은 앱 번들에 실려 배포되며 보호는 Firebase 보안 규칙과 API 키 제한이 맡는다. |
| 영향 | 파일을 바꾸면 커밋으로 남는다. APNs 키는 저장소와 문서에 두지 않는다. |
| 근거 | [운영 5-3](../../../operations/DEPLOYMENT.md#5-3-manyak-android-ci) |

<br>

<a id="i-022"></a>
<a id="i-022-로컬-패키지-하나에-core와-feature-폴더를-둠"></a>

**I-022. 로컬 패키지 하나에 Core와 Feature 폴더를 둠**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Proposed |
| 관계 | [I-004](#i-004)의 배치. Android [A-093](../ANDROID/DECISIONS.md#a-093)의 폴더 구분에 대응 |
| 승인 근거 | 작성 중 결정. 사용자 확인 전 |
| 배경 | 확정 결정은 Swift Package Manager 로컬 패키지를 쓰지만 패키지 수와 폴더 배치는 정하지 않았다. |
| 채택 | 라이브러리 타깃 전부를 로컬 패키지 하나에 선언하고 기반 타깃 소스는 `Core/<타깃>`, 기능 타깃 소스는 `Feature/<타깃>`에 둔다. 앱 타깃은 Xcode 프로젝트에 둔다. |
| 대안 | 기반과 기능을 서로 다른 패키지로 나눔: 허용 의존 선언이 두 파일로 나뉜다 |
| 이유 | 허용 의존 표 전체를 `Package.swift` 한 파일에서 확인할 수 있다. 폴더만 보고 기반과 기능을 구분할 수 있다. |
| 영향 | `ManyakReport`는 세 기능이 함께 쓰는 기반이라 `Core/`에 둔다. |
| 근거 | [A-093](../ANDROID/DECISIONS.md#a-093) |

<br>

<a id="i-023"></a>
<a id="i-023-릴리스-브랜치와-버전-올림-규칙"></a>

**I-023. 릴리스 브랜치와 버전 올림 규칙**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Proposed |
| 관계 | [I-003](#i-003), [I-014](#i-014)의 절차. Android 앱 릴리스 절차([운영 7-2](../../../operations/DEPLOYMENT.md#7-2-android-앱-릴리스))와 같은 형식 |
| 승인 근거 | 작성 중 결정. 사용자 확인 전 |
| 배경 | 확정 결정은 `main` 병합 커밋에서 Archive하고 빌드 번호를 올릴 때마다 1 증가한다. 릴리스 브랜치와 마케팅 버전을 올리는 기준은 정하지 않았다. |
| 채택 | `release/v{버전}`을 `origin/dev`에서 만들어 버전 두 값만 커밋하고 `main`과 `dev`에 각각 PR을 낸다. 버그 수정은 patch, 기능 추가는 minor를 올린다. |
| 대안 | `dev`에서 바로 Archive: 스토어에 있는 코드가 `main`에 없게 된다 |
| 이유 | 어느 코드가 사용자 손에 있는지 `main`으로 답할 수 있어야 한다. |
| 영향 | 릴리스 커밋이 `dev`에도 돌아가야 다음 릴리스의 분기 기준이 어긋나지 않는다. |
| 근거 | [운영 7-2](../../../operations/DEPLOYMENT.md#7-2-android-앱-릴리스) |

<br>

<a id="i-024"></a>
<a id="i-024-기기-백업은-데이터베이스를-빼고-userdefaults를-포함"></a>

**I-024. 기기 백업은 데이터베이스를 빼고 UserDefaults를 포함**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | [I-008](#i-008)의 저장소별 백업 범위. 시작 판정은 [ACCOUNT I-064](../../../spec/ACCOUNT/CLIENT/IOS/DECISIONS.md#i-064) |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | Keychain 토큰은 기기 전용이라 기기 백업에서 다른 기기로 복원되지 않는다. 기능 데이터베이스와 UserDefaults의 백업 포함 여부는 정하지 않았다. |
| 채택 | 기능 데이터베이스 파일은 기기 백업에서 제외하고 UserDefaults 기기 suite와 회원 suite는 시스템 기본대로 포함한다. 복원한 기기는 설치 표시가 있고 토큰이 없어 Guest로 시작하며, 그 시작에서 복원된 회원 suite를 지운다. |
| 대안 | 모두 포함: 회원별 제작 데이터가 로그인 없이 새 기기에 복원된다<br>모두 제외: 테마 같은 기기 설정과 온보딩 완료 여부도 초기화된다 |
| 이유 | 새 기기에서는 로그아웃 상태로 시작하므로 회원 데이터는 따라가지 않게 하고 기기 설정만 따라가게 한다. |
| 영향 | 복원한 기기에는 제작 진행 기록이 없고 서버 초안에서 이어간다. 회원 suite는 파일 단위로 백업에서 뺄 수 없어 시작 정리로 지운다. |
| 근거 | [2-4 로컬 저장](2-STATE-MANAGEMENT.md#2-4-로컬-저장) |

<br>

<a id="i-025"></a>
<a id="i-025-배포-서명은-xcode-자동-서명"></a>

**I-025. 배포 서명은 Xcode 자동 서명**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | [I-014](#i-014)의 서명 방식 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | I-014는 서명과 출시 빌드를 담당자의 Mac에서 수동으로 하기로 정했고 자동 서명 사용 여부와 인증서 보관 방식은 남겼다. |
| 채택 | Xcode 자동 서명을 쓴다. 인증서와 프로비저닝 프로파일은 Xcode가 만들고 갱신하며 따로 내보내 보관하지 않는다. 담당자의 Mac을 쓸 수 없으면 Apple Developer 계정으로 다른 Mac에서 다시 발급한다. |
| 대안 | 수동 서명과 인증서 백업: 담당자가 바뀌어도 같은 인증서를 쓰지만 인증서와 프로파일을 직접 관리하고 팀 비밀 저장소에 보관해야 한다 |
| 이유 | 올리는 사람이 한 명인 동안 관리 부담이 가장 작다. |
| 영향 | 복구는 재발급이므로 Apple Developer 계정의 접근 권한이 복구 수단이다. |
| 근거 | [5-3 버전과 서명](5-DEPLOYMENT.md#5-3-버전과-서명) |

<br>

<a id="i-026"></a>
<a id="i-026-심사용-계정은-심사-전용-google-계정"></a>

**I-026. 심사용 계정은 심사 전용 Google 계정**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 로그인 제공자는 [ACCOUNT I-060](../../../spec/ACCOUNT/CLIENT/IOS/DECISIONS.md#i-060) |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | 앱은 로그인이 필수이고 Google과 Kakao 로그인만 지원하므로 App Store 심사에 로그인할 수 있는 계정을 제공해야 한다. |
| 채택 | 심사 전용 Google 계정을 만들어 운영 환경에서 가입과 로그인을 확인한 뒤 자격 증명을 App Store Connect의 심사 정보에만 적는다. 자격 증명은 문서와 저장소에 두지 않는다. |
| 대안 | 심사 전용 Kakao 계정 |
| 이유 | 앱과 서버를 바꾸지 않고 심사자가 로그인할 수 있다. |
| 영향 | 새 기기 로그인에서 Google의 추가 본인 확인이 뜨면 심사자가 로그인하지 못할 수 있어 제출 전에 다른 기기에서 로그인을 확인한다. |
| 근거 | [5-4 출시](5-DEPLOYMENT.md#5-4-출시) |

<br>

<a id="i-027"></a>
<a id="i-027-오픈소스-고지-목록은-빌드에서-자동-생성"></a>

**I-027. 오픈소스 고지 목록은 빌드에서 자동 생성**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 의존성 관리는 [I-004](#i-004) |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | 고지 대상은 Swift Package Manager 의존성과 번들 글꼴 두 종의 OFL이다. 목록을 만드는 방식은 정하지 않았다. |
| 채택 | 빌드 단계에서 Swift Package Manager 의존성의 라이선스를 모아 목록을 만들고 글꼴 두 종의 OFL은 저장소에 둔 원문을 더한다. 생성 도구는 구현에서 고른다. |
| 대안 | 수동 관리: 의존성을 바꿀 때 누락을 리뷰로만 막는다 |
| 이유 | 의존성이 바뀌어도 고지가 빠지지 않는다. |
| 영향 | 생성 도구가 빌드 의존성으로 더해진다. |
| 근거 | [5-1 빌드와 환경](5-DEPLOYMENT.md#5-1-빌드와-환경) |

<br>

<a id="i-028"></a>
<a id="i-028-개인정보-라벨과-개인정보-매니페스트는-첫-제출-전-점검-항목"></a>

**I-028. 개인정보 라벨과 개인정보 매니페스트는 첫 제출 전 점검 항목**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Accepted |
| 관계 | 없음 |
| 승인 근거 | KNK-2154 작업 대화에서 사용자가 확정했다 |
| 배경 | 앱 개인정보 라벨과 `PrivacyInfo.xcprivacy`의 내용은 실제 연결한 SDK 버전과 수집 항목이 정해져야 정확히 쓸 수 있다. |
| 채택 | 내용을 명세에 미리 적지 않고 첫 제출 전에 작성하는 점검 항목으로 둔다. 연결한 SDK 버전의 공식 문서를 기준으로 쓰고 개인정보 처리방침과 대조한다. |
| 대안 | 지금 초안을 명세에 적음: SDK 버전이 바뀌면 다시 확인해야 한다 |
| 이유 | 확인하지 않은 수집 항목을 명세에 단정하지 않는다. |
| 영향 | 첫 제출 전에 이 항목이 끝나야 제출할 수 있다. |
| 근거 | [5-1 빌드와 환경](5-DEPLOYMENT.md#5-1-빌드와-환경) |

<br>

<a id="i-029"></a>
<a id="i-029-첫-버전은-전체-출시하고-단계적-출시는-업데이트부터-사용"></a>

**I-029. 첫 버전은 전체 출시하고 단계적 출시는 업데이트부터 사용**

| 항목 | 내용 |
|---|---|
| 날짜 | 2026-11-28 |
| 상태 | Proposed |
| 관계 | [I-015](#i-015)의 적용 범위 |
| 승인 근거 | 작성 중 결정. 사용자 확인 전 |
| 배경 | I-015는 App Store Connect의 단계적 출시를 쓰기로 정했다. Apple 문서에 따르면 단계적 출시는 버전 업데이트를 제출할 때만 선택할 수 있고 버전 페이지에서 제출 전에 고른다. 자동 업데이트 대상에게 7일 동안 1%에서 100%까지 나가며 합계 30일까지 멈출 수 있다. |
| 채택 | 첫 버전 1.0.0은 전체 출시한다. 두 번째 버전부터 제출 전에 단계적 출시를 선택한다. |
| 대안 | 없음 |
| 이유 | 첫 버전에는 단계적 출시를 선택할 수 없다. |
| 영향 | 첫 버전은 비교할 직전 버전이 없어 버전 비교 중단 기준을 적용하지 않고 같은 지표를 출시 뒤 관찰한다. 문제가 있으면 수정판을 낸다. |
| 근거 | [Apple 도움말: Release a version update in phases](https://developer.apple.com/help/app-store-connect/update-your-app/release-a-version-update-in-phases/)(2026-11-28 확인) |
